"""Clasifica caras de la fundación voxelizada para preparar futuros intercambios.

Recibe AsignacionVertidas y examina los seis vecinos de cada celda ocupada.
Devuelve SuperficiesVoxel con exteriores, internas e interfaces entre IDs,
índices ZYX, normales XYZ y áreas en m²; contactos compartidos se guardan una vez.
construccion.py reutiliza esta clasificación con su máscara construida.
En este módulo se describe la geometría recibida, sin tiempos, flujos o convección.
"""
from dataclasses import dataclass

import numpy as np

from .vertidas_voxel import AsignacionVertidas


@dataclass(frozen=True)
class CarasVoxel:
    """Caras únicas: A/B son índices ZYX; normal XYZ va de A a B; área en m².
    """
    celda_a_zyx: np.ndarray
    celda_b_zyx: np.ndarray  # Vecino geométrico; puede estar fuera de dominio.
    id_a: np.ndarray
    id_b: np.ndarray  # Cero para vacío/exterior. No indexar el array sin verificarlo.
    normal_xyz: np.ndarray  # Desde A hacia B. Exterior: saliente de hormigón.
    area_m2: np.ndarray
    vecino_fuera_dominio: np.ndarray

    @property
    def cantidad(self):
        return len(self.id_a)

    @property
    def area_total_m2(self):
        return float(self.area_m2.sum())

    def centros_m(self, grilla):
        """Recibe la grilla y devuelve centros de caras XYZ [m], desplazando medio paso desde A.
        """
        return (grilla.origen_m+(self.celda_a_zyx[:, ::-1]+.5)*grilla.pasos_m+
                self.normal_xyz*grilla.pasos_m/2)

    def vertices_m(self, grilla):
        """Cuadriláteros orientados; (v1-v0)×(v2-v0) apunta según normal_xyz.

        Entrada: grilla. Devuelve cuadriláteros [N,4,3] en m, con orden orientado.
        Se usan para visualizar exactamente las caras clasificadas, sin crear otra geometría.
        """
        centros = self.centros_m(grilla)
        eje = np.argmax(abs(self.normal_xyz), axis=1)
        u_unitario = np.eye(3)[(eje+1)%3]
        v_unitario = np.cross(self.normal_xyz, u_unitario)
        u = u_unitario*grilla.pasos_m
        v = v_unitario*grilla.pasos_m
        return np.stack([centros-u/2-v/2, centros+u/2-v/2,
                         centros+u/2+v/2, centros-u/2+v/2], axis=1)


@dataclass(frozen=True)
class ContactoVertidas:
    par: tuple[int, int]
    cantidad_caras: int
    area_m2: float


@dataclass(frozen=True)
class SuperficiesVoxel:
    asignacion: AsignacionVertidas
    exteriores: CarasVoxel
    internas: CarasVoxel
    interfaces: CarasVoxel

    @property
    def contactos_por_par(self):
        """Agrupa interfaces por par de IDs ordenados y devuelve conteos y área única en m².
        Ordenar el par para la tabla no cambia la normal geométrica de cada cara.
        """
        if not self.interfaces.cantidad:
            return ()
        pares = np.sort(np.column_stack([self.interfaces.id_a,self.interfaces.id_b]),axis=1)
        unicos,indice = np.unique(pares,axis=0,return_inverse=True)
        return tuple(ContactoVertidas(tuple(int(i) for i in par),int(np.count_nonzero(indice==j)),
                                       float(self.interfaces.area_m2[indice==j].sum()))
                     for j,par in enumerate(unicos))

    @property
    def exterior_por_direccion(self):
        """Devuelve conteo y área exterior [m²] por x/y/z mínimo o máximo según la normal.
        """
        salida = {}
        for eje,nombre in enumerate('xyz'):
            for signo,lado in ((-1,'min'),(1,'max')):
                mascara = self.exteriores.normal_xyz[:,eje] == signo
                salida[f'{nombre}_{lado}'] = (int(mascara.sum()),float(self.exteriores.area_m2[mascara].sum()))
        return salida


@dataclass(frozen=True)
class DiagnosticoContactos:
    ids_sin_voxeles: tuple
    contactos_esperados_ausentes: tuple
    contactos_no_esperados: tuple


def diagnosticar_contactos(superficies, ids_esperados, contactos_esperados):
    """Contrasta con una referencia explícita, no inventa contactos desde IDs.

    La referencia se documenta en el caso; no es una intersección CAD automática.
    No agrega caras perdidas ni corrige el IFC o la voxelización.

    Recibe superficies y listas explícitas de IDs/pares esperados.
    Devuelve ausencias y contactos inesperados; no repara capas sin voxeles ni infiere contactos CAD.
    """
    ids = set(ids_esperados)
    esperados = set()
    for par in contactos_esperados:
        if len(par)!=2 or par[0]==par[1] or not set(par)<=ids:
            raise ValueError('Los contactos esperados requieren dos IDs distintos de la referencia.')
        esperados.add(tuple(sorted(par)))
    presentes = set(int(i) for i in np.unique(superficies.asignacion.vertida_id) if i)
    observados = {c.par for c in superficies.contactos_por_par}
    return DiagnosticoContactos(tuple(sorted(ids-presentes)),tuple(sorted(esperados-observados)),
                                tuple(sorted(observados-esperados)))


def _concatenar(bloques):
    formatos = [(np.int64,(0,3)),(np.int64,(0,3)),(np.int8,(0,)),(np.int8,(0,)),
                 (np.int8,(0,3)),(float,(0,)),(bool,(0,))]
    arrays = []
    for i,(dtype,forma) in enumerate(formatos):
        datos = np.concatenate([b[i] for b in bloques],axis=0) if bloques else np.empty(forma,dtype=dtype)
        datos.setflags(write=False)
        arrays.append(datos)
    return CarasVoxel(*arrays)


def clasificar_caras(asignacion: AsignacionVertidas) -> SuperficiesVoxel:
    """Examina seis vecinos; no hay envoltura periódica ni caras de celdas vacías.

    En internas/interfaces solo se recorre el sentido +X/+Y/+Z para no duplicar.
    La normal de contacto no implica que ID_a sea menor que ID_b.

    Entrada: AsignacionVertidas. Salida: SuperficiesVoxel.
    Área perpendicular a X=dy*dz, a Y=dx*dz y a Z=dx*dy.
    Exterior mira hacia vacío; en contactos solo se almacena la dirección positiva
    para cumplir 6*Nocupados=Nexteriores+2*(Ninternas+Ninterfaces).
    """
    if not isinstance(asignacion,AsignacionVertidas):
        raise ValueError('Usar AsignacionVertidas de la etapa anterior.')
    ids = np.asarray(asignacion.vertida_id)
    voxel = asignacion.voxelizacion
    g = voxel.grilla
    if (ids.shape!=g.forma_zyx or ids.dtype.kind not in 'iu' or
        not np.isin(ids,[0,1,2,3,4,5]).all() or
        not np.array_equal(ids>0,voxel.ocupacion)):
        raise ValueError('IDs 0..5 y ocupación deben coincidir con la grilla ZYX.')
    if np.shape(g.pasos_m)!=(3,) or not np.isfinite(g.pasos_m).all() or (g.pasos_m<=0).any():
        raise ValueError('La grilla debe tener pasos XYZ finitos positivos.')
    forma = np.array(g.forma_zyx)
    exteriores,internas,interfaces = [],[],[]
    for eje_xyz in range(3):
        eje = 2-eje_xyz
        area = g.volumen_celda_m3/g.pasos_m[eje_xyz]
        for signo in (-1,1):
            desplazamiento = np.zeros(3,dtype=int)
            desplazamiento[eje] = signo
            normal = np.zeros(3,dtype=np.int8)
            normal[eje_xyz] = signo
            vecinos = np.zeros_like(ids)
            destino,origen = [slice(None)]*3,[slice(None)]*3
            destino[eje] = slice(None,-1) if signo==1 else slice(1,None)
            origen[eje] = slice(1,None) if signo==1 else slice(None,-1)
            vecinos[tuple(destino)] = ids[tuple(origen)]
            mascaras = [((ids>0)&(vecinos==0),exteriores)]
            if signo==1:
                mascaras += [((ids>0)&(vecinos>0)&(ids==vecinos),internas),
                              ((ids>0)&(vecinos>0)&(ids!=vecinos),interfaces)]
            for mascara,coleccion in mascaras:
                a = np.argwhere(mascara)
                if not len(a):
                    continue
                b = a+desplazamiento
                fuera = ((b<0)|(b>=forma)).any(axis=1)
                coleccion.append((a,b,ids[mascara].astype(np.int8),vecinos[mascara].astype(np.int8),
                                   np.broadcast_to(normal,(len(a),3)).copy(),np.full(len(a),area),fuera))
    resultado = SuperficiesVoxel(asignacion,_concatenar(exteriores),_concatenar(internas),_concatenar(interfaces))
    # Cada cara ocupada-ocupada consume dos incidencias, pero se almacena una vez.
    n = voxel.numero_ocupados
    if 6*n != resultado.exteriores.cantidad+2*(resultado.internas.cantidad+resultado.interfaces.cantidad):
        raise RuntimeError('El balance de incidencias de caras no cierra.')
    return resultado
