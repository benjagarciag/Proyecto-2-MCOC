"""Convierte las cinco mallas IFC en ocupación de una grilla cartesiana 3D.

Recibe FundacionIFC de bim.py, pasos (dx,dy,dz) en metros y tolerancia geométrica.
Devuelve Voxelizacion: grilla, máscara bool ZYX y centros sobre la frontera.
Los centros se clasifican respecto de triángulos; el bbox solo filtra candidatos.
vertidas_voxel.py reutiliza el mismo clasificador para asignar propietarios.
Aquí ocupación significa geometría final, no activación temporal ni temperatura.
"""
from dataclasses import dataclass
from numbers import Integral, Real

import numpy as np

from .bim import FundacionIFC, analizar_malla

FUERA, FRONTERA, DENTRO = -1, 0, 1
TOLERANCIA_M = 1e-7


def _vector3(nombre, valores):
    datos = np.asarray(valores)
    if datos.shape != (3,) or datos.dtype.kind not in 'fiu' or not np.isfinite(datos).all():
        raise ValueError(f'{nombre} debe tener tres números reales finitos.')
    return np.array(datos, dtype=float, copy=True)


def _entero_positivo(nombre, valor):
    if isinstance(valor, bool) or not isinstance(valor, Integral) or valor < 1:
        raise ValueError(f'{nombre} debe ser entero positivo.')


@dataclass(frozen=True)
class GrillaCartesiana:
    """Grilla regular: origen de esquina XYZ [m], pasos XYZ [m] y forma NumPy ZYX.
    """
    origen_m: np.ndarray  # Esquina mínima, no centro de la primera celda.
    pasos_m: np.ndarray  # dx,dy,dz, sin cambiar el tamaño de la última celda.
    forma_zyx: tuple[int, int, int]

    @property
    def forma_xyz(self):
        return self.forma_zyx[::-1]

    @property
    def centros_xyz_m(self):
        """Devuelve los tres vectores de centros X,Y,Z en metros: origen+(índice+1/2)*paso.
        Se distinguen de las esquinas para aplicar el criterio de pertenencia por centros.
        """
        return tuple(o+(np.arange(n)+.5)*d for o, d, n in zip(self.origen_m, self.pasos_m, self.forma_xyz))

    @property
    def limites_superiores_m(self):
        return self.origen_m+self.pasos_m*np.array(self.forma_xyz)

    @property
    def dimensiones_m(self):
        return self.pasos_m*np.array(self.forma_xyz)

    @property
    def numero_celdas(self):
        return int(np.prod(self.forma_zyx))

    @property
    def volumen_celda_m3(self):
        """Devuelve dx*dy*dz en m³; todas las celdas mantienen el mismo volumen.
        """
        return float(np.prod(self.pasos_m))


def crear_grilla(bbox_min_m, bbox_max_m, pasos_m, *, origen_m=None, max_celdas=2_000_000):
    """Cubre el bbox con celdas completas. No redondea coordenadas IFC.

    Por defecto origen=bbox_min. ceil puede extender el dominio por el máximo;
    una diferencia real de micrómetros también puede agregar una fila vacía.
    max_celdas es una protección de memoria, no un requisito físico.

    Entradas: límites XYZ y pasos en m; origen opcional y límite de memoria.
    Devuelve GrillaCartesiana; ceil cubre el bbox sin estirar la última celda.
    """
    minimo, maximo = _vector3('bbox mínimo', bbox_min_m), _vector3('bbox máximo', bbox_max_m)
    pasos = _vector3('pasos_m', pasos_m)
    origen = minimo.copy() if origen_m is None else _vector3('origen_m', origen_m)
    _entero_positivo('max_celdas', max_celdas)
    if (maximo <= minimo).any() or (pasos <= 0).any() or (origen > minimo).any():
        raise ValueError('BBox con extensión positiva, pasos positivos y origen no mayor que bbox_min.')
    with np.errstate(over='ignore'):
        cantidades = (maximo-origen)/pasos
    if not np.isfinite(cantidades).all():
        raise ValueError('La resolución excede las dimensiones representables.')
    forma_xyz = tuple(int(np.ceil(v)) for v in cantidades)
    if forma_xyz[0]*forma_xyz[1]*forma_xyz[2] > max_celdas:
        raise ValueError('Grilla demasiado grande: aumentar pasos o revisar max_celdas.')
    origen.setflags(write=False)
    pasos.setflags(write=False)
    return GrillaCartesiana(origen, pasos, forma_xyz[::-1])


def _proximos_a_triangulos(puntos, tri, tolerancia):
    """Distancia euclídea a cara proyectada o a sus tres segmentos/aristas.

    Entradas: puntos [N,3], triángulos [M,3,3] y tolerancia en metros.
    Devuelve máscara de distancia a superficie dentro de tolerancia; también considera aristas.
    """
    a, b, c = tri[:, 0], tri[:, 1], tri[:, 2]
    ab, ac = b-a, c-a
    normal = np.cross(ab, ac)
    n2 = np.sum(normal*normal, axis=1)
    w = puntos[:, None, :]-a
    plano = np.einsum('pti,ti->pt', w, normal)
    distancia_plano2 = plano**2/n2
    d00, d01, d11 = np.sum(ab*ab, axis=1), np.sum(ab*ac, axis=1), np.sum(ac*ac, axis=1)
    d20 = np.einsum('pti,ti->pt', w, ab)
    d21 = np.einsum('pti,ti->pt', w, ac)
    denominador = d00*d11-d01*d01
    u = (d11*d20-d01*d21)/denominador
    v = (d00*d21-d01*d20)/denominador
    cerca = (distancia_plano2 <= tolerancia**2) & (u >= 0) & (v >= 0) & (u+v <= 1)
    for inicio, fin in ((a, b), (b, c), (c, a)):
        arista = fin-inicio
        w = puntos[:, None, :]-inicio
        t = np.clip(np.einsum('pti,ti->pt', w, arista)/np.sum(arista*arista, axis=1), 0, 1)
        distancia2 = np.sum((w-t[..., None]*arista)**2, axis=2)
        cerca |= distancia2 <= tolerancia**2
    return cerca.any(axis=1)


def _angulos_solidos(puntos, tri):
    """Suma orientada: ~±4π dentro y ~0 fuera de una superficie cerrada.

    atan2 evita dividir por el denominador. No usa rayos ni conteos ambiguos
    al cruzar una arista. Los puntos de frontera ya se trataron por distancia.

    Entradas: puntos XYZ y triángulos en las mismas coordenadas.
    Devuelve suma angular por punto [sr, estereorradianes]; |suma|>2*pi distingue el interior tras excluir frontera.
    """
    a = tri[None, :, 0]-puntos[:, None, :]
    b = tri[None, :, 1]-puntos[:, None, :]
    c = tri[None, :, 2]-puntos[:, None, :]
    na, nb, nc = np.linalg.norm(a, axis=2), np.linalg.norm(b, axis=2), np.linalg.norm(c, axis=2)
    numerador = np.sum(a*np.cross(b, c), axis=2)
    denominador = (na*nb*nc+np.sum(a*b, axis=2)*nc+
                   np.sum(b*c, axis=2)*na+np.sum(c*a, axis=2)*nb)
    return (2*np.arctan2(numerador, denominador)).sum(axis=1)


def clasificar_puntos(puntos_m, vertices_m, triangulos, *, tolerancia_m=TOLERANCIA_M, tamano_lote=256):
    """Devuelve int8: FUERA=-1, FRONTERA=0, DENTRO=1. No modifica entradas.

    Es necesario que la malla cumpla los requisitos de analizar_malla.
    El bbox ampliado solo descarta candidatos; la decisión usa los triángulos.

    Entradas: puntos y vértices XYZ en m, índices de triángulos, tolerancia y lote.
    Devuelve una clase por punto; el tamaño de lote limita memoria, no cambia la decisión física.
    """
    puntos = np.asarray(puntos_m, dtype=float)
    if puntos.ndim != 2 or puntos.shape[1] != 3 or not np.isfinite(puntos).all():
        raise ValueError('puntos_m requiere matriz finita [n,3].')
    if isinstance(tolerancia_m, bool) or not isinstance(tolerancia_m, Real) or not np.isfinite(tolerancia_m) or tolerancia_m <= 0:
        raise ValueError('tolerancia_m debe ser real finita positiva.')
    _entero_positivo('tamano_lote', tamano_lote)
    analizar_malla(vertices_m, triangulos)
    vertices = np.asarray(vertices_m, dtype=float)
    tri = vertices[np.asarray(triangulos)]
    minimo, maximo = vertices.min(axis=0), vertices.max(axis=0)
    candidatos = np.flatnonzero(((puntos >= minimo-tolerancia_m) & (puntos <= maximo+tolerancia_m)).all(axis=1))
    salida = np.full(len(puntos), FUERA, dtype=np.int8)
    # Acota los arrays punto×triángulo, sin asignar todos los pares del dominio.
    lote = min(tamano_lote, max(1, 200_000//len(tri)))
    for inicio in range(0, len(candidatos), lote):
        ids = candidatos[inicio:inicio+lote]
        p = puntos[ids]
        frontera = _proximos_a_triangulos(p, tri, tolerancia_m)
        salida[ids[frontera]] = FRONTERA
        otros = ids[~frontera]
        suma = _angulos_solidos(p[~frontera], tri)
        salida[otros[np.abs(suma) > 2*np.pi]] = DENTRO
    return salida


@dataclass(frozen=True)
class Voxelizacion:
    """Resultado geométrico de solo lectura; ocupacion[Z,Y,X] no es una máscara de construcción.
    """
    grilla: GrillaCartesiana
    ocupacion: np.ndarray  # bool [z,y,x]; NO es actividad temporal.
    centros_sobre_malla: np.ndarray  # Dentro de tolerancia de alguna cara IFC, incluidas juntas.
    tolerancia_m: float
    sha256_ifc: str
    volumen_referencia_mallas_m3: float

    @property
    def numero_ocupados(self):
        return int(self.ocupacion.sum())

    @property
    def volumen_ocupado_m3(self):
        return self.numero_ocupados*self.grilla.volumen_celda_m3

    @property
    def diferencia_volumen_m3(self):
        return self.volumen_ocupado_m3-self.volumen_referencia_mallas_m3


def iterar_clasificacion_malla(grilla, vertida, tolerancia_m):
    """Bloques de selección/clase, compartidos por ocupación e identificación.

    No asigna IDs. Mantiene el filtro bbox y el clasificador triangular de
    Etapa 2 sin duplicarlos en el módulo de atribución de vertidas.

    Recibe grilla, una VertidaIFC y tolerancia en m. Produce selección ZYX y clases
    por plano Z. Compartir este recorrido evita criterios distintos para ocupación e IDs.
    """
    x, y, z = grilla.centros_xyz_m
    indices = [np.flatnonzero((c >= lo-tolerancia_m) & (c <= hi+tolerancia_m))
               for c, lo, hi in zip((z, y, x), vertida.bbox_min_m[::-1], vertida.bbox_max_m[::-1])]
    if any(len(i) == 0 for i in indices):
        return
    iy, ix = indices[1:]
    Y, X = np.meshgrid(y[iy], x[ix], indexing='ij')
    for iz in indices[0]:
        puntos = np.column_stack((X.ravel(), Y.ravel(), np.full(X.size, z[iz])))
        clase = clasificar_puntos(puntos, vertida.vertices_m, vertida.triangulos, tolerancia_m=tolerancia_m)
        yield np.ix_([iz], iy, ix), clase.reshape(1, len(iy), len(ix))


def voxelizar_fundacion(fundacion: FundacionIFC, pasos_m=(.5, .5, .5), *,
                        origen_m=None, tolerancia_m=TOLERANCIA_M, max_celdas=2_000_000):
    """Unión de los sólidos: un centro se ocupa si pertenece a cualquiera.

    Incluye frontera; las juntas compartidas no duplican celdas ni requieren
    decidir un propietario. No conserva ni asigna IDs por voxel en esta etapa.

    Entradas: modelo IFC y pasos en m; salida Voxelizacion.
    La unión OR ocupa cada centro una vez aunque varias piezas lo reclamen;
    la atribución única se realiza después, sin alterar esta máscara.
    """
    if not isinstance(fundacion, FundacionIFC):
        raise ValueError('Se requiere FundacionIFC producido por bim.py.')
    # 1. Se crea la grilla una vez; los centros conservan las coordenadas IFC.
    grilla = crear_grilla(fundacion.bbox_min_m, fundacion.bbox_max_m, pasos_m,
                          origen_m=origen_m, max_celdas=max_celdas)
    if isinstance(tolerancia_m, bool) or not isinstance(tolerancia_m, Real) or not np.isfinite(tolerancia_m) or not 0 < tolerancia_m < min(grilla.pasos_m)*1e-3:
        raise ValueError('Usar tolerancia positiva menor que 0.001 del menor paso.')
    # 2. La máscara OR une sólidos sin contar dos veces las juntas compartidas.
    ocupada = np.zeros(grilla.forma_zyx, dtype=bool)
    frontera = np.zeros_like(ocupada)
    for vertida in fundacion.vertidas:
        for seleccion, clase in iterar_clasificacion_malla(grilla, vertida, tolerancia_m):
            ocupada[seleccion] |= clase >= FRONTERA
            frontera[seleccion] |= clase == FRONTERA
    ocupada.setflags(write=False)
    frontera.setflags(write=False)
    return Voxelizacion(grilla, ocupada, frontera, float(tolerancia_m), fundacion.sha256_ifc,
                         fundacion.volumen_total_mallas_m3)
