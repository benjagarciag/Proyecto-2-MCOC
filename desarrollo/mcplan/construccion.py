"""Representa qué voxeles ya están construidos, sus edades y temperaturas iniciales.

Recibe FundacionIFC y AsignacionVertidas. Devuelve ProgramaConstruccion y estados
con máscara activa, nuevos voxeles, edad en segundos y temperaturas en °C.
El calendario procede del IFC; solo los nuevos reciben T de colocación.
Las temperaturas existentes se conservan o se reciben de un futuro solver.
Reutiliza superficies_voxel.py y entrega edades a hidratacion.py; no difunde calor.
M1 sigue siendo una etiqueta IFC: las propiedades didácticas se configuran aparte.
"""
from dataclasses import dataclass, replace
from numbers import Real

import numpy as np

from .balance_cartesiano import _caras
from .bim import FundacionIFC
from .vertidas_voxel import AsignacionVertidas
from .superficies_voxel import SuperficiesVoxel, clasificar_caras


def _solo_lectura(array):
    array.setflags(write=False)
    return array


def _real(nombre, valor):
    if isinstance(valor,(bool,np.bool_)) or not isinstance(valor,Real) or not np.isfinite(valor):
        raise ValueError(f'{nombre} debe ser un número real finito.')
    return float(valor)


@dataclass(frozen=True)
class Colocacion:
    vertida_id: int
    inicio_s: float
    temperatura_C: float
    material: str
    volumen_ifc_m3: float


@dataclass(frozen=True)
class ProgramaConstruccion:
    """Calendario y campos finales ZYX: inicio [s], T de colocación [°C] y etiqueta material.
    """
    asignacion_final: AsignacionVertidas
    colocaciones: tuple[Colocacion, ...]
    material: np.ndarray  # Etiqueta por celda, incluso aún no construida; ''=vacío.
    inicio_s: np.ndarray  # NaN en el vacío geométrico, definido en futuras vertidas.
    temperatura_colocacion_C: np.ndarray  # Dato del IFC, NO temperatura actual.
    ids_sin_voxeles: tuple[int, ...]


def preparar_construccion(fundacion: FundacionIFC, asignacion: AsignacionVertidas):
    """Relaciona propiedades IFC con los IDs existentes; no cambia su voxelización.

    Entradas: modelo IFC y asignación final. Salida: ProgramaConstruccion.
    Convierte Inicio_h a segundos, conserva T de colocación y material;
    reporta IDs sin voxeles sin inventar celdas para completarlos.
    """
    if not isinstance(fundacion,FundacionIFC) or not isinstance(asignacion,AsignacionVertidas):
        raise ValueError('Se requiere FundacionIFC y AsignacionVertidas.')
    if fundacion.sha256_ifc != asignacion.voxelizacion.sha256_ifc:
        raise ValueError('La asignación y el IFC no corresponden a la misma versión.')
    clasificar_caras(asignacion)  # Valida coherencia de IDs, máscara y grilla.
    ids_ifc = [v.vertida_id for v in fundacion.vertidas]
    if len(set(ids_ifc)) != len(ids_ifc) or not ids_ifc:
        raise ValueError('Los IDs IFC deben ser únicos.')
    presentes = set(int(i) for i in np.unique(asignacion.vertida_id) if i)
    if not presentes <= set(ids_ifc):
        raise ValueError('Existe un ID de voxel sin vertida IFC.')
    colocaciones = []
    for v in fundacion.vertidas:
        inicio = _real('Inicio_s',v.inicio_s)
        temperatura = _real('Temperatura de colocación',v.temperatura_colocacion_C)
        material = v.tipo_hormigon
        if inicio < 0 or not isinstance(material,str) or not material.strip():
            raise ValueError('Inicio no negativo y etiqueta TipoHormigon no vacía.')
        colocaciones.append(Colocacion(v.vertida_id,inicio,temperatura,material,v.volumen_m3))
    colocaciones.sort(key=lambda c:(c.inicio_s,c.vertida_id))
    forma = asignacion.vertida_id.shape
    materiales = np.full(forma,'',dtype=f'U{max(len(c.material) for c in colocaciones)}')
    inicios,temperaturas = np.full(forma,np.nan),np.full(forma,np.nan)
    for c in colocaciones:
        mascara = asignacion.vertida_id == c.vertida_id
        materiales[mascara],inicios[mascara],temperaturas[mascara] = c.material,c.inicio_s,c.temperatura_C
    return ProgramaConstruccion(asignacion,tuple(colocaciones),_solo_lectura(materiales),
                                _solo_lectura(inicios),_solo_lectura(temperaturas),
                                tuple(sorted(set(ids_ifc)-presentes)))


@dataclass(frozen=True)
class EstadoConstruccion:
    """Instantánea: conserva ocupación final y separa activos/nuevos; edad [s], T [°C].
    """
    programa: ProgramaConstruccion
    tiempo_s: float
    activos: np.ndarray  # Construcción actual; subconjunto de ocupacion_final.
    nuevos: np.ndarray  # Activados en la última transición, no en toda la historia.
    temperatura_C: np.ndarray  # NaN en TODO voxel no activo: nunca hormigón a 0 °C.
    edad_s: np.ndarray  # t-inicio solo si activo; NaN antes de colocación y en vacío.

    @property
    def ocupacion_final(self):
        return self.programa.asignacion_final.voxelizacion.ocupacion

    @property
    def vertida_id(self):
        return self.programa.asignacion_final.vertida_id

    @property
    def ids_activos(self):
        return _solo_lectura(np.where(self.activos,self.vertida_id,0))


def iniciar_construccion(programa):
    """Estado previo a toda colocación, t=-1 s; la primera se incorpora al avanzar a 0.

    Recibe programa y devuelve estado previo a construir, t=-1 s.
    No colocado no significa hormigón a 0 °C: temperatura y edad son NaN.
    """
    if not isinstance(programa,ProgramaConstruccion):
        raise ValueError('Usar preparar_construccion antes de iniciar.')
    forma = programa.asignacion_final.vertida_id.shape
    return EstadoConstruccion(programa,-1.,_solo_lectura(np.zeros(forma,dtype=bool)),
                              _solo_lectura(np.zeros(forma,dtype=bool)),
                              _solo_lectura(np.full(forma,np.nan)),_solo_lectura(np.full(forma,np.nan)))


def avanzar_construccion(estado, tiempo_s, *, temperatura_actual_C=None):
    """Activa si inicio<=t. Conserva T vieja y asigna T_col SOLO a nuevos.

    temperatura_actual_C permite recibir un campo actualizado por un futuro
    solver. Debe ser finito en las celdas ya activas. En las demás se ignora
    y se mantiene NaN o se asigna T_col si acaba de colocarse esa vertida.
    Esta función no difunde ni enfría: sin solver, las T existentes no cambian.

    Entradas: estado previo, nuevo tiempo global [s] y campo T opcional [°C].
    Devuelve otro estado. activo=ocupado_final AND inicio<=t; nuevo=activo AND NOT activo_previo.
    Edad=t-inicio solo en activos. No muta entradas ni vuelve a inicializar T de celdas antiguas.
    """
    if not isinstance(estado,EstadoConstruccion):
        raise ValueError('Usar EstadoConstruccion.')
    t = _real('tiempo_s',tiempo_s)
    if t < estado.tiempo_s:
        raise ValueError('No se permite retroceder el estado de construcción.')
    p = estado.programa
    entrada = estado.temperatura_C if temperatura_actual_C is None else np.asarray(temperatura_actual_C)
    if entrada.shape != estado.activos.shape or entrada.dtype.kind not in 'fiu':
        raise ValueError('Temperatura actual: campo numérico ZYX con la forma de la grilla.')
    if not np.isfinite(entrada[estado.activos]).all():
        raise ValueError('La temperatura debe ser finita en las celdas ya activas.')
    activos = estado.ocupacion_final & (p.inicio_s<=t)
    # Solo esta diferencia recibe T_col: una nueva colocación no borra la historia.
    nuevos = activos & ~estado.activos
    temperatura = np.full(activos.shape,np.nan)
    temperatura[estado.activos] = entrada[estado.activos]
    temperatura[nuevos] = p.temperatura_colocacion_C[nuevos]
    edad = np.full(activos.shape,np.nan)
    # Cada vertida tiene su propio reloj; los no colocados conservan edad NaN.
    edad[activos] = t-p.inicio_s[activos]
    return EstadoConstruccion(p,t,_solo_lectura(activos),_solo_lectura(nuevos),
                              _solo_lectura(temperatura),_solo_lectura(edad))


def proxima_colocacion_s(estado):
    """Recibe estado y devuelve el próximo instante global de colocación [s], o None.
    """
    pendientes = [c.inicio_s for c in estado.programa.colocaciones if c.inicio_s>estado.tiempo_s]
    return min(pendientes) if pendientes else None


def limitar_paso_por_colocacion_s(estado, paso_propuesto_s):
    """Recorta el paso al siguiente evento; no sustituye el límite de estabilidad.

    Recibe estado y paso positivo [s]; devuelve min(paso, tiempo hasta el evento).
    El límite de estabilidad térmica debe imponerse además al acoplar un solver.
    """
    paso = _real('paso_propuesto_s',paso_propuesto_s)
    if paso <= 0:
        raise ValueError('El paso debe ser positivo.')
    siguiente = proxima_colocacion_s(estado)
    return min(paso,siguiente-estado.tiempo_s) if siguiente is not None else paso


def mascaras_contactos_activos(estado):
    """Tres máscaras (Z,Y,X) con la misma forma de enlaces que G en E04.

    Son AND de ambos extremos activos. Nunca usar 0*NaN para excluir una celda:
    un futuro operador debe indexar exclusivamente estos pares válidos.

    Entrada: estado. Salida: tres máscaras booleanas de enlaces Z,Y,X.
    Ambos extremos deben estar activos; filtrar índices evita el error numérico 0*NaN.
    """
    salida = []
    for eje in range(3):
        a,b,_,_ = _caras(eje,3)
        salida.append(_solo_lectura(estado.activos[a]&estado.activos[b]))
    return tuple(salida)


@dataclass(frozen=True)
class SuperficiesConstruidas:
    caras: SuperficiesVoxel
    id_vecino_final: np.ndarray  # Para cada exterior: 0=vacío, ID>0=no colocado.
    expuestas_a_no_colocado: np.ndarray


def superficies_construidas(estado):
    """Reutiliza Etapa 4 con máscara construida, sin modificar la asignación final.

    Expuesta significa celda activa frente a vacío/no colocado; no prescribe
    convección, suelo, moldaje o aislación. Se mantiene la normal saliente.

    Recibe estado y devuelve SuperficiesConstruidas con áreas en m².
    La máscara final no cambia: se clasifica una vista construida. Una cara hacia
    una futura vertida queda expuesta hasta que ambos extremos estén activos;
    expuesta no prescribe aire, suelo ni un coeficiente de convección.
    """
    final = estado.programa.asignacion_final
    referencia_activa = sum(c.volumen_ifc_m3 for c in estado.programa.colocaciones if c.inicio_s<=estado.tiempo_s)
    voxel_activo = replace(final.voxelizacion,ocupacion=estado.activos,
                           centros_sobre_malla=_solo_lectura(final.voxelizacion.centros_sobre_malla&estado.activos),
                           volumen_referencia_mallas_m3=referencia_activa)
    asignacion_activa = replace(final,voxelizacion=voxel_activo,vertida_id=estado.ids_activos)
    caras = clasificar_caras(asignacion_activa)
    exterior = caras.exteriores
    id_vecino = np.zeros(exterior.cantidad,dtype=np.int8)
    dentro = ~exterior.vecino_fuera_dominio
    indices = exterior.celda_b_zyx[dentro]
    id_vecino[dentro] = final.vertida_id[tuple(indices.T)]
    return SuperficiesConstruidas(caras,_solo_lectura(id_vecino),_solo_lectura(id_vecino>0))
