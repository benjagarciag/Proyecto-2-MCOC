"""Lectura reutilizable de la fundación BIM, sin modificar el IFC.

Recibe la ruta de fundacion.ifc. IfcOpenShell aplica los placements y entrega
vértices XYZ en metros y triángulos. Se devuelven FundacionIFC y VertidaIFC
con GUID, propiedades, unidades, calidad topológica y volúmenes en m³.
Este es el primer paso del flujo IFC → voxel → vertida → construcción → fuente.
No requiere Blender abierto, no asigna voxeles y no certifica solapes CAD.
"""
from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
from numbers import Integral, Real
from pathlib import Path

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.element
import ifcopenshell.util.unit
import numpy as np

NOMBRE_PSET = 'UANDES_HormigonMasivo'
PROPIEDADES_REQUERIDAS = frozenset({'VertidaID', 'Inicio_h', 'TemperaturaColocacion_C',
                                  'TipoHormigon', 'Moldaje', 'Aislacion', 'RetiroMoldaje_h'})


@dataclass(frozen=True)
class MaterialIFC:
    """Asociación material leída del IFC; no implica valores térmicos k, rho o cp.
    """
    nombre: str | None
    clase_ifc: str
    categoria: str | None


@dataclass(frozen=True)
class CalidadMalla:
    """Resumen topológico y métrico; áreas en m² y volúmenes en m³. No certifica autointersecciones.
    """
    numero_vertices: int
    numero_triangulos: int
    numero_aristas: int
    componentes_conexas: int
    area_superficial_m2: float
    volumen_firmado_m3: float
    volumen_m3: float
    cerrada: bool = True
    orientacion_consistente: bool = True


@dataclass(frozen=True)
class VertidaIFC:
    """Una pieza con geometría XYZ en metros, conectividad y propiedades constructivas leídas.
    """
    vertida_id: int
    guid: str
    nombre: str
    clase_ifc: str
    propiedades: dict
    materiales_asociados: tuple[MaterialIFC, ...]
    vertices_m: np.ndarray  # [n_vertices, xyz], metros en coordenadas del proyecto.
    triangulos: np.ndarray  # [n_triangulos, 3], índices desde cero.
    bbox_min_m: np.ndarray
    bbox_max_m: np.ndarray
    calidad: CalidadMalla

    @property
    def dimensiones_m(self):
        return self.bbox_max_m-self.bbox_min_m

    @property
    def volumen_m3(self):
        return self.calidad.volumen_m3

    @property
    def inicio_h(self):
        return float(self.propiedades['Inicio_h'])

    @property
    def inicio_s(self):
        return self.inicio_h*3600.

    @property
    def temperatura_colocacion_C(self):
        return float(self.propiedades['TemperaturaColocacion_C'])

    @property
    def tipo_hormigon(self):
        return self.propiedades['TipoHormigon']


@dataclass(frozen=True)
class FundacionIFC:
    """Conjunto de las cinco piezas, unidades y SHA256 de la entrada de solo lectura.
    """
    ruta: Path
    sha256_ifc: str
    schema: str
    unidad_longitud_ifc: str
    escala_longitud_ifc_a_m: float
    sistema_coordenadas: str
    vertidas: tuple[VertidaIFC, ...]
    advertencias: tuple[str, ...]

    @property
    def bbox_min_m(self):
        return np.min([v.bbox_min_m for v in self.vertidas], axis=0)

    @property
    def bbox_max_m(self):
        return np.max([v.bbox_max_m for v in self.vertidas], axis=0)

    @property
    def dimensiones_m(self):
        return self.bbox_max_m-self.bbox_min_m

    @property
    def volumen_total_mallas_m3(self):
        """Suma por vertida, no unión booleana validada entre sólidos."""
        return sum(v.volumen_m3 for v in self.vertidas)


def analizar_malla(vertices_m, triangulos) -> CalidadMalla:
    """Exige superficie conexa, cerrada y orientada, sin caras degeneradas.

    Calcula volumen mediante tetraedros firmados, con origen próximo para
    reducir cancelación. No certifica ausencia de autointersecciones.

    Entradas: vertices_m [N,3] y triangulos [M,3]. Devuelve CalidadMalla.
    El volumen se integra con tetraedros firmados respecto de un origen cercano;
    se exige una superficie conexa, cerrada y orientada antes de clasificar centros.
    """
    vertices = np.asarray(vertices_m, dtype=float)
    caras = np.asarray(triangulos)
    if vertices.ndim != 2 or vertices.shape[1] != 3 or len(vertices) < 4 or not np.isfinite(vertices).all():
        raise ValueError('Vértices: se requiere una matriz finita [n,3], con n>=4.')
    if caras.ndim != 2 or caras.shape[1] != 3 or len(caras) < 4 or caras.dtype.kind not in 'iu':
        raise ValueError('Triángulos: se requieren índices enteros [n,3], con n>=4.')
    if caras.min() < 0 or caras.max() >= len(vertices):
        raise ValueError('Índices de triángulos fuera del rango de vértices.')
    if len(np.unique(np.sort(caras, axis=1), axis=0)) != len(caras):
        raise ValueError('La malla contiene triángulos duplicados.')
    if len(np.unique(caras)) != len(vertices):
        raise ValueError('La malla contiene vértices sin utilizar.')
    tri = vertices[caras]
    area_doble = np.linalg.norm(np.cross(tri[:, 1]-tri[:, 0], tri[:, 2]-tri[:, 0]), axis=1)
    escala = float(np.ptp(vertices, axis=0).max())
    if (area_doble <= np.finfo(float).eps*escala**2*16).any():
        raise ValueError('La malla contiene triángulos degenerados.')
    dirigidas = Counter((int(a), int(b)) for t in caras
                        for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])))
    aristas = Counter()
    for (a, b), cantidad in dirigidas.items():
        aristas[tuple(sorted((a, b)))] += cantidad
    if any(c != 2 for c in aristas.values()):
        raise ValueError('Malla abierta o no manifold: cada arista debe pertenecer a dos triángulos.')
    if any(c != dirigidas.get((b, a), 0) for (a, b), c in dirigidas.items()):
        raise ValueError('La orientación de los triángulos es inconsistente.')
    # Dos superficies que se tocan solo en un vértice pueden tener todas sus
    # aristas dobles. El enlace de cada vértice debe formar UN ciclo cerrado.
    enlaces = [[] for _ in vertices]
    for a, b, c in caras:
        enlaces[a].append((int(b), int(c)))
        enlaces[b].append((int(c), int(a)))
        enlaces[c].append((int(a), int(b)))
    for pares in enlaces:
        anillo = {}
        for a, b in pares:
            anillo.setdefault(a, []).append(b)
            anillo.setdefault(b, []).append(a)
        if any(len(v) != 2 for v in anillo.values()):
            raise ValueError('La malla tiene un vértice no manifold.')
        vistos, pila = set(), [next(iter(anillo))]
        while pila:
            i = pila.pop()
            if i not in vistos:
                vistos.add(i)
                pila.extend(j for j in anillo[i] if j not in vistos)
        if len(vistos) != len(anillo):
            raise ValueError('La malla tiene superficies que solo comparten un vértice.')
    vecinos = [set() for _ in vertices]
    for a, b in aristas:
        vecinos[a].add(b)
        vecinos[b].add(a)
    visitados, pendientes = set(), [0]
    while pendientes:
        i = pendientes.pop()
        if i not in visitados:
            visitados.add(i)
            pendientes.extend(vecinos[i]-visitados)
    if len(visitados) != len(vertices):
        raise ValueError('Se requiere un sólido conexo por vertida; hay componentes separadas.')
    local = tri-vertices.mean(axis=0)
    firmado = float(np.einsum('ij,ij->i', local[:, 0], np.cross(local[:, 1], local[:, 2])).sum()/6)
    if abs(firmado) <= np.finfo(float).eps*escala**3*16:
        raise ValueError('La malla no encierra un volumen numéricamente significativo.')
    return CalidadMalla(len(vertices), len(caras), len(aristas), 1,
                        float(area_doble.sum()/2), firmado, abs(firmado))


def _propiedades_vertida(producto):
    """Lee UANDES_HormigonMasivo de un producto IFC y devuelve su diccionario validado.
    Horarios en horas, temperatura de colocación en °C e ID entero; no completa datos faltantes.
    """
    propiedades = ifcopenshell.util.element.get_psets(producto).get(NOMBRE_PSET, {})
    propiedades = {k: v for k, v in propiedades.items() if k != 'id'}
    faltantes = PROPIEDADES_REQUERIDAS-propiedades.keys()
    if faltantes:
        raise ValueError(f'{producto.Name}: propiedades faltantes: {sorted(faltantes)}.')
    ident = propiedades['VertidaID']
    if isinstance(ident, bool) or not isinstance(ident, Integral):
        raise ValueError(f'{producto.Name}: VertidaID debe ser entero.')
    for nombre in ('Inicio_h', 'TemperaturaColocacion_C', 'RetiroMoldaje_h'):
        valor = propiedades[nombre]
        if isinstance(valor, bool) or not isinstance(valor, Real) or not np.isfinite(valor):
            raise ValueError(f'{producto.Name}: {nombre} debe ser real finito.')
    if propiedades['Inicio_h'] < 0 or propiedades['RetiroMoldaje_h'] < 0:
        raise ValueError(f'{producto.Name}: los horarios deben ser no negativos.')
    for nombre in ('TipoHormigon', 'Moldaje', 'Aislacion'):
        if not isinstance(propiedades[nombre], str) or not propiedades[nombre].strip():
            raise ValueError(f'{producto.Name}: {nombre} debe ser texto no vacío.')
    return propiedades


def extraer_fundacion_ifc(ruta) -> FundacionIFC:
    """Lee las cinco IfcFooting; devuelve datos, no escribe ni imprime.

    Aplica placements con use-world-coords. Geometría en SI: la escala IFC
    se informa, NO se multiplica de nuevo. No aplica IfcMapConversion.

    Entrada: ruta a un IFC estable. Salida: FundacionIFC con cinco VertidaIFC.
    IfcOpenShell entrega geometría en SI: no se multiplica otra vez por la escala
    IFC. Se verifica SHA256 antes/después y se informa la ausencia de IfcMaterial.
    """
    ruta = Path(ruta).resolve(strict=True)
    hash_inicial = sha256(ruta.read_bytes()).hexdigest()
    modelo = ifcopenshell.open(str(ruta))
    productos = modelo.by_type('IfcFooting')
    if len(productos) != 5:
        raise ValueError(f'Se esperaban exactamente cinco IfcFooting; encontrados {len(productos)}.')
    nombrados = [p for p in modelo.by_type('IfcProduct') if (p.Name or '').startswith('Vertida_')]
    nombres = {f'Vertida_{i:02d}' for i in range(1, 6)}
    if len(nombrados) != 5 or {p.Name for p in nombrados} != nombres:
        raise ValueError('Se esperaban exactamente los nombres Vertida_01 a Vertida_05.')
    settings = ifcopenshell.geom.settings()
    settings.set('use-world-coords', True)
    settings.set('weld-vertices', True)
    vertidas, ids, guids, avisos = [], set(), set(), []
    for producto in productos:
        props = _propiedades_vertida(producto)
        ident, guid = int(props['VertidaID']), producto.GlobalId
        if ident in ids or not guid or guid in guids:
            raise ValueError(f'{producto.Name}: identificador o GUID duplicado/vacío.')
        if ident not in range(1, 6) or producto.Name != f'Vertida_{ident:02d}':
            raise ValueError(f'{producto.Name}: VertidaID no corresponde al nombre esperado.')
        ids.add(ident)
        guids.add(guid)
        shape = ifcopenshell.geom.create_shape(settings, producto)
        vertices = np.array(shape.geometry.verts, dtype=float).reshape(-1, 3)
        triangulos = np.array(shape.geometry.faces, dtype=np.int64).reshape(-1, 3)
        try:
            calidad = analizar_malla(vertices, triangulos)
        except ValueError as error:
            raise ValueError(f'{producto.Name}: {error}') from error
        materiales = tuple(MaterialIFC(m.Name, m.is_a(), getattr(m, 'Category', None))
                           for m in ifcopenshell.util.element.get_materials(producto))
        if not materiales:
            avisos.append(f'{producto.Name}: sin asociación IfcMaterial; TipoHormigon={props["TipoHormigon"]} es una etiqueta, no propiedades térmicas.')
        if any(props[k].strip().upper() == 'TBD' for k in ('Moldaje', 'Aislacion')):
            avisos.append(f'{producto.Name}: moldaje/aislación con valores TBD.')
        vertices.setflags(write=False)
        triangulos.setflags(write=False)
        lo, hi = vertices.min(axis=0), vertices.max(axis=0)
        lo.setflags(write=False)
        hi.setflags(write=False)
        vertidas.append(VertidaIFC(ident, guid, producto.Name, producto.is_a(), props,
                                  materiales, vertices, triangulos, lo, hi, calidad))
    unidad = ifcopenshell.util.unit.get_project_unit(modelo, 'LENGTHUNIT')
    if unidad is None:
        raise ValueError('El IFC no declara unidad de longitud.')
    nombre_unidad = ' '.join(str(v) for v in (getattr(unidad, 'Prefix', None), getattr(unidad, 'Name', None)) if v)
    escala = float(ifcopenshell.util.unit.calculate_unit_scale(modelo))
    if not np.isfinite(escala) or escala <= 0:
        raise ValueError('Escala de longitud IFC inválida.')
    coordenadas = 'Proyecto IFC, placements aplicados, XYZ en metros; sin recentrar ni aplicar conversión cartográfica.'
    if modelo.by_type('IfcMapConversion'):
        avisos.append('Existe IfcMapConversion: se informa pero no se aplica; vértices en coordenadas del proyecto.')
    if sha256(ruta.read_bytes()).hexdigest() != hash_inicial:
        raise RuntimeError('El IFC cambió durante la lectura; repetir sobre una versión estable.')
    return FundacionIFC(ruta, hash_inicial, modelo.schema, nombre_unidad, escala,
                         coordenadas, tuple(sorted(vertidas, key=lambda v: v.vertida_id)), tuple(avisos))
