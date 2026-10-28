"""Dos materiales homogéneos por celda, contacto perfecto y propiedades SI.

La interfaz debe coincidir con caras de la malla: no se mezclan materiales
dentro de una celda. Alpha se calcula de k/(rho*cp), nunca se prescribe aparte.
"""
from dataclasses import dataclass

import numpy as np

from .balance_cartesiano import _caras
from .bordes_termicos import coeficientes_cara
from .difusion_2d import Parametros2D, _real_finito
from .difusion_3d import Parametros3D


@dataclass(frozen=True)
class MaterialTermico:
    conductividad_W_mK: float
    densidad_kg_m3: float
    calor_especifico_J_kgK: float

    def __post_init__(self):
        for nombre, valor in vars(self).items():
            _real_finito(nombre, valor, positivo=True)

    @property
    def alpha_m2_s(self):
        return self.conductividad_W_mK/(self.densidad_kg_m3*self.calor_especifico_J_kgK)


@dataclass
class CamposMateriales:
    ids: np.ndarray
    k_W_mK: np.ndarray
    rho_kg_m3: np.ndarray
    cp_J_kgK: np.ndarray

    @property
    def alpha_m2_s(self):
        return self.k_W_mK/(self.rho_kg_m3*self.cp_J_kgK)


@dataclass(frozen=True)
class DosMateriales:
    material_0: MaterialTermico
    material_1: MaterialTermico
    ids: np.ndarray  # 0/1, forma [y,x] o [z,y,x].

    def campos(self, forma):
        if not all(isinstance(m, MaterialTermico) for m in (self.material_0, self.material_1)):
            raise ValueError('Se requieren dos objetos MaterialTermico.')
        ids = np.asarray(self.ids)
        if ids.shape != forma or ids.dtype.kind not in 'iu' or not np.isin(ids, [0, 1]).all():
            raise ValueError('ids debe tener enteros 0/1 y exactamente la forma de la grilla.')
        ids = ids.copy()
        def campo(nombre):
            tabla = np.array([getattr(self.material_0, nombre), getattr(self.material_1, nombre)])
            return tabla[ids]
        return CamposMateriales(ids, campo('conductividad_W_mK'), campo('densidad_kg_m3'),
                                campo('calor_especifico_J_kgK'))


def materiales_desde_config(config, parametros):
    """Dos bloques separados por un plano x/y/z, en una cara de la malla.

    config: eje, interfaz_m y materiales (dos diccionarios de MaterialTermico).
    Material 0 ocupa coordenadas menores que la interfaz; material 1, mayores.
    Rechaza interfaces no alineadas en vez de desplazarlas silenciosamente.
    """
    if isinstance(parametros, Parametros2D):
        ejes = 'xy'
    elif isinstance(parametros, Parametros3D):
        ejes = 'xyz'
    else:
        raise ValueError('Usar Parametros2D o Parametros3D.')
    if set(config) != {'eje', 'interfaz_m', 'materiales'} or config['eje'] not in tuple(ejes):
        raise ValueError(f'Declarar eje ({ejes}), interfaz_m y materiales.')
    eje = config['eje']
    posicion = config['interfaz_m']
    _real_finito('interfaz_m', posicion)
    L, n = getattr(parametros, f'longitud_{eje}_m'), getattr(parametros, f'celdas_{eje}')
    indice = posicion/(L/n)
    if not 0 < posicion < L or not np.isclose(indice, round(indice), rtol=0, atol=1e-10):
        raise ValueError('La interfaz debe ser interior y coincidir con una cara de la malla.')
    entrada = config['materiales']
    if not isinstance(entrada, list) or len(entrada) != 2:
        raise ValueError('materiales debe contener exactamente dos conjuntos de propiedades.')
    materiales = [MaterialTermico(**m) for m in entrada]
    forma = tuple(getattr(parametros, f'celdas_{e}') for e in reversed(ejes))
    ids = np.zeros(forma, dtype=int)
    corte = [slice(None)]*len(forma)
    corte[len(ejes)-1-ejes.index(eje)] = slice(round(indice), None)
    ids[tuple(corte)] = 1
    return DosMateriales(*materiales, ids)


def preparar_operador_materiales(forma, pasos_m, areas_m2, campos, bordes_por_eje):
    """Resistencias de media celda en serie, por cada interfaz, sin contacto extra.

    G_ij=A/[(d/2)/k_i+(d/2)/k_j]. CADA interfaz tiene UNA conductancia
    compartida. Los bordes exteriores usan el k de su propia celda.
    """
    k = campos.k_W_mK
    suma = np.zeros(forma)
    conductancias, caras = [], []
    for eje, (d, A, par) in enumerate(zip(pasos_m, areas_m2, bordes_por_eje)):
        a, b, minimo, maximo = _caras(eje, len(forma))
        G = A/((d/2)/k[a]+(d/2)/k[b])
        conductancias.append(G)
        suma[a] += G
        suma[b] += G
        for indice, borde in zip((minimo, maximo), par):
            H, B = coeficientes_cara(borde, A, d/2, k[indice])
            suma[indice] += H
            caras.append((indice, H, B))
    return tuple(conductancias), tuple(caras), suma
