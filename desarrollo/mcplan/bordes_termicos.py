"""Bordes constantes por cara para un material homogéneo, en SI.

Neumann: q_entrante > 0 introduce calor en CUALQUIER cara (no cambia con
la orientación). En notación de normal exterior: q_entrante = k*dT/dn.
Robin incluye conducción de media celda y película convectiva en serie.
"""
from dataclasses import dataclass

import numpy as np

from .balance_cartesiano import _caras
from .difusion_2d import _real_finito


@dataclass(frozen=True)
class Dirichlet:
    temperatura_C: float

    def __post_init__(self):
        _real_finito('temperatura_C', self.temperatura_C)


@dataclass(frozen=True)
class Neumann:
    """Flujo superficial entrante [W/m²]; cero es adiabático."""
    flujo_entrante_W_m2: float = 0.0

    def __post_init__(self):
        _real_finito('flujo_entrante_W_m2', self.flujo_entrante_W_m2)


@dataclass(frozen=True)
class Robin:
    h_W_m2K: float
    ambiente_C: float

    def __post_init__(self):
        _real_finito('h_W_m2K', self.h_W_m2K)
        _real_finito('ambiente_C', self.ambiente_C)
        if self.h_W_m2K < 0:
            raise ValueError('h_W_m2K debe ser >= 0; cero es adiabático.')


def coeficientes_cara(borde, area_m2, distancia_centro_cara_m, k_W_mK):
    """Devuelve (H [W/K], B [W]): potencia entrante P = B - H*T_celda.

    Dirichlet: H=kA/(d/2). Neumann: H=0, B=q_entrante*A.
    Robin: H=A/((d/2)/k+1/h), B=H*T_ambiente.
    La forma equivalente evita dividir por cero cuando h=0.
    """
    if isinstance(borde, Neumann):
        return 0.0, borde.flujo_entrante_W_m2*area_m2
    if isinstance(borde, Dirichlet):
        H = k_W_mK*area_m2/distancia_centro_cara_m
        return H, H*borde.temperatura_C
    if isinstance(borde, Robin):
        H = area_m2/(distancia_centro_cara_m/k_W_mK + 1/borde.h_W_m2K) if borde.h_W_m2K else 0.0
        return H, H*borde.ambiente_C
    raise ValueError('Cada cara debe ser Dirichlet, Neumann o Robin.')


def preparar_operador(forma, pasos_m, areas_m2, k_W_mK, bordes_por_eje):
    """Orden de ejes NumPy: (y,x) o (z,y,x); min/max por cada eje.

    Calcula una vez las conductancias y el coeficiente de extracción que
    determina el límite suficiente de estabilidad C/max(suma_G).
    """
    conductancias = tuple(k_W_mK*A/d for A, d in zip(areas_m2, pasos_m))
    suma = np.zeros(forma)
    caras = []
    for eje, (G, A, d, par) in enumerate(zip(conductancias, areas_m2, pasos_m, bordes_por_eje)):
        a, b, minimo, maximo = _caras(eje, len(forma))
        suma[a] += G
        suma[b] += G
        for indice, borde in zip((minimo, maximo), par):
            H, B = coeficientes_cara(borde, A, d/2, k_W_mK)
            suma[indice] += H
            caras.append((indice, H, B))
    return conductancias, tuple(caras), suma


def potencia_con_bordes_W(T, conductancias, caras):
    """Un intercambio por interfaz; suma interna cero hasta redondeo.

    Retorna potencia por celda [W] y potencia exterior neta entrante [W].
    Todas las potencias usan T del mismo instante anterior.
    """
    potencia = np.zeros_like(T, dtype=float)
    for eje, G in enumerate(conductancias):
        a, b, _, _ = _caras(eje, T.ndim)
        intercambio = G*(T[b]-T[a])
        potencia[a] += intercambio
        potencia[b] -= intercambio
    exterior = 0.0
    for indice, H, B in caras:
        flujo = B-H*T[indice]
        potencia[indice] += flujo
        exterior += float(np.sum(np.broadcast_to(flujo, T[indice].shape)))
    return potencia, exterior
