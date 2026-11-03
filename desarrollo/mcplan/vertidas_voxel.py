"""Asigna una única vertida IFC a cada voxel ocupado y compara volúmenes.

Recibe FundacionIFC (bim.py) y Voxelizacion (voxel.py) de la misma versión IFC.
Devuelve AsignacionVertidas con IDs 1..5, ID 0 en vacío y diagnóstico de conflictos;
comparar_volumenes entrega m³ y errores porcentuales por pieza.
Se conserva exactamente la ocupación y se resuelven fronteras por una convención
geométrica determinista. Construcción y superficies consumen estos IDs después.
El ID de vertida no es el ID de material: varias piezas pueden compartir M1.
"""
from dataclasses import dataclass
from itertools import product
from numbers import Integral

import numpy as np

from .bim import FundacionIFC
from .voxel import Voxelizacion, FUERA, FRONTERA, DENTRO, clasificar_puntos, iterar_clasificacion_malla


@dataclass(frozen=True)
class RegistroConflicto:
    indice_zyx: tuple
    centro_xyz_m: tuple
    ids_reclamantes: tuple
    clases: tuple
    id_asignado: int | None
    criterio: str


@dataclass(frozen=True)
class InformeAsignacion:
    """Conteos completos de reclamaciones y muestra acotada de decisiones; no oculta solapes.
    """
    reclamaciones_multiples: int
    interiores_multiples: int
    interior_y_frontera: int
    fronteras_compartidas: int
    registros: tuple[RegistroConflicto, ...]  # Hasta 100 muestras; conteos completos.


class ConflictoGeometrico(ValueError):
    def __init__(self, mensaje, informe):
        super().__init__(mensaje)
        self.informe = informe


@dataclass(frozen=True)
class AsignacionVertidas:
    """IDs enteros ZYX asociados a la voxelización recibida, más informe de conflictos.
    """
    voxelizacion: Voxelizacion
    vertida_id: np.ndarray  # int8 [z,y,x], 0 vacío y 1..5 vertidas.
    informe: InformeAsignacion


@dataclass(frozen=True)
class VolumenVertida:
    """Volumen N*dx*dy*dz, referencia IFC y diferencias en m³; error relativo en porcentaje.
    """
    vertida_id: int
    nombre: str
    numero_voxeles: int
    volumen_voxelizado_m3: float
    volumen_ifc_m3: float
    diferencia_firmada_m3: float
    diferencia_absoluta_m3: float
    error_relativo_pct: float


# Orden GEOMÉTRICO, no de ID: primero hacia coordenadas crecientes, con
# prioridad Z, luego Y, luego X. Las otras direcciones permiten salir de una
# junta sin salir por una arista exterior. No hay ruido aleatorio.
DIRECCIONES_FRONTERA = tuple(sorted((d for d in product((-1, 0, 1), repeat=3) if d != (0, 0, 0)),
                                    key=lambda d: (d[2], d[1], d[0]), reverse=True))


def _resolver_frontera(centro, candidatos, tolerancia):
    """Sonda solo de desempate: no mueve el voxel ni cambia su ocupación.

    Para una junta horizontal interior, selecciona el sólido del lado +Z.
    Si no hay interior inequívoco, se detiene en vez de elegir un ID arbitrario.

    Recibe centro XYZ [m], piezas reclamantes y tolerancia [m].
    Devuelve (ID o None, explicación). Las sondas no desplazan centros ni aportan
    fracciones de volumen; una geometría ambigua debe revisarse, no etiquetarse arbitrariamente.
    """
    for direccion in DIRECCIONES_FRONTERA:
        punto = np.asarray(centro)+4*tolerancia*np.array(direccion)
        dentro = [v.vertida_id for v in candidatos if
                  clasificar_puntos([punto], v.vertices_m, v.triangulos, tolerancia_m=tolerancia)[0] == DENTRO]
        if len(dentro) > 1:
            return None, 'Sonda dentro de varios sólidos: revisar solape.'
        if len(dentro) == 1:
            return dentro[0], f'Frontera: sonda 4*tol, dirección XYZ={direccion}, prioridad Z/Y/X.'
    return None, 'Ninguna dirección permite un interior único: revisar geometría/tolerancia.'


def asignar_vertidas(fundacion: FundacionIFC, voxelizacion: Voxelizacion) -> AsignacionVertidas:
    """Preserva EXACTAMENTE la máscara recibida y asigna un único propietario.

    Un interior único prevalece sobre reclamaciones de banda de frontera.
    Dos interiores inequívocos producen error, no una asignación silenciosa.

    Entradas: FundacionIFC y Voxelizacion con el mismo SHA256.
    Salida: AsignacionVertidas. Rechaza interiores múltiples y conserva ids>0==ocupacion;
    no confundir escoger una etiqueta de frontera con corregir el volumen geométrico.
    """
    if not isinstance(fundacion, FundacionIFC) or not isinstance(voxelizacion, Voxelizacion):
        raise ValueError('Usar FundacionIFC y Voxelizacion de las etapas anteriores.')
    if fundacion.sha256_ifc != voxelizacion.sha256_ifc:
        raise ValueError('La voxelización corresponde a otra versión IFC.')
    vertidas = sorted(fundacion.vertidas, key=lambda v: v.vertida_id)
    ids = [v.vertida_id for v in vertidas]
    if not ids or any(isinstance(i, bool) or not isinstance(i, Integral) or i not in range(1, 6) for i in ids) or len(set(ids)) != len(ids):
        raise ValueError('Se requieren IDs únicos del 1 al 5.')
    g = voxelizacion.grilla
    if voxelizacion.ocupacion.shape != g.forma_zyx or voxelizacion.ocupacion.dtype != bool:
        raise ValueError('La máscara no corresponde a la grilla booleana ZYX.')
    clases = np.full((len(vertidas), *g.forma_zyx), FUERA, dtype=np.int8)
    for i, v in enumerate(vertidas):
        for seleccion, valores in iterar_clasificacion_malla(g, v, voxelizacion.tolerancia_m):
            clases[i][seleccion] = valores
    reclamaciones = clases >= FRONTERA
    cantidad = reclamaciones.sum(axis=0)
    interiores = (clases == DENTRO).sum(axis=0)
    if not np.array_equal(cantidad > 0, voxelizacion.ocupacion):
        raise ValueError('La clasificación no reproduce la ocupación recibida; no se corrige silenciosamente.')
    multiples = cantidad > 1
    n_multi = int(multiples.sum())
    n_solape = int((interiores > 1).sum())
    n_mixto = int((multiples & (interiores == 1)).sum())
    n_borde = int((multiples & (interiores == 0)).sum())
    centros = g.centros_xyz_m
    registros = []
    def registro(indice, elegido, criterio):
        indice = tuple(int(i) for i in indice)
        xyz = tuple(float(c[i]) for c, i in zip(centros, indice[::-1]))
        reivindican = np.flatnonzero(reclamaciones[(slice(None), *indice)])
        return RegistroConflicto(indice, xyz, tuple(ids[i] for i in reivindican),
                                 tuple(int(clases[(i, *indice)]) for i in reivindican), elegido, criterio)
    def informe():
        return InformeAsignacion(n_multi, n_solape, n_mixto, n_borde, tuple(registros))
    # Diagnóstico completo antes de intentar resolver cualquier frontera.
    if n_solape:
        for indice in np.argwhere(interiores > 1)[:100]:
            registros.append(registro(indice, None, 'Varios interiores: solape no resuelto.'))
        raise ConflictoGeometrico(f'{n_solape} centros interiores a varias vertidas. No se asignaron IDs.', informe())
    tabla_ids = np.array(ids, dtype=np.int8)
    asignados = np.zeros(g.forma_zyx, dtype=np.int8)
    unico = cantidad == 1
    asignados[unico] = tabla_ids[np.argmax(reclamaciones, axis=0)[unico]]
    interior_unico = interiores == 1
    asignados[interior_unico] = tabla_ids[np.argmax(clases == DENTRO, axis=0)[interior_unico]]
    for indice in np.argwhere(multiples):
        indice = tuple(int(i) for i in indice)
        if interiores[indice] == 1:
            elegido, criterio = int(asignados[indice]), 'Interior inequívoco prevalece sobre banda de frontera.'
        else:
            candidatos = [v for i, v in enumerate(vertidas) if reclamaciones[(i, *indice)]]
            centro = tuple(c[i] for c, i in zip(centros, indice[::-1]))
            elegido, criterio = _resolver_frontera(centro, candidatos, voxelizacion.tolerancia_m)
            if elegido is not None:
                asignados[indice] = elegido
        if len(registros) < 100:
            registros.append(registro(indice, elegido, criterio))
        elif elegido is None:
            registros[-1] = registro(indice, elegido, criterio)
        if elegido is None:
            raise ConflictoGeometrico('Frontera compartida no resoluble sin revisar geometría.', informe())
    if not np.array_equal(asignados > 0, voxelizacion.ocupacion):
        raise RuntimeError('Asignación incompleta: se perdió o agregó ocupación.')
    asignados.setflags(write=False)
    return AsignacionVertidas(voxelizacion, asignados, informe())


def comparar_volumenes(fundacion, asignacion) -> tuple[VolumenVertida, ...]:
    """N por volumen de celda, referencia IFC completa sin redondearla.

    Recibe modelo y asignación; devuelve una fila VolumenVertida por ID.
    V_h=N*V_celda [m³]; error=100*abs(V_h-V_IFC)/V_IFC [%].
    La suma por ID debe recuperar todos los ocupados, sin compensar errores locales.
    """
    if fundacion.sha256_ifc != asignacion.voxelizacion.sha256_ifc:
        raise ValueError('Referencias de IFC incompatibles.')
    volumen_celda = asignacion.voxelizacion.grilla.volumen_celda_m3
    filas = []
    for v in sorted(fundacion.vertidas, key=lambda v: v.vertida_id):
        n = int(np.count_nonzero(asignacion.vertida_id == v.vertida_id))
        volumen = n*volumen_celda
        diferencia = volumen-v.volumen_m3
        filas.append(VolumenVertida(v.vertida_id, v.nombre, n, volumen, v.volumen_m3,
                                    diferencia, abs(diferencia), 100*abs(diferencia)/v.volumen_m3))
    if sum(f.numero_voxeles for f in filas) != asignacion.voxelizacion.numero_ocupados:
        raise RuntimeError('La suma por vertida no conserva el total de ocupados.')
    return tuple(filas)
