"""Intercambios conservativos por ejes, válidos para arreglos 2D o 3D.

Cada eje recibe su G entre centros [W/K] y sus temperaturas de cara min/max.
En una cara Dirichlet la distancia es media celda: la conductancia es 2G.
"""
import numpy as np


def _caras(eje, dimensiones):
    anterior, siguiente = [slice(None)] * dimensiones, [slice(None)] * dimensiones
    anterior[eje], siguiente[eje] = slice(None, -1), slice(1, None)
    minimo, maximo = [slice(None)] * dimensiones, [slice(None)] * dimensiones
    minimo[eje], maximo[eje] = 0, -1
    return tuple(anterior), tuple(siguiente), tuple(minimo), tuple(maximo)


def suma_conductancias_dirichlet_W_K(forma, conductancias):
    """Suma de los coeficientes de extracción por celda, incluidas las caras."""
    suma = np.zeros(forma, dtype=float)
    for eje, G in enumerate(conductancias):
        a, b, minimo, maximo = _caras(eje, len(forma))
        suma[a] += G
        suma[b] += G
        suma[minimo] += 2*G
        suma[maximo] += 2*G
    return suma


def potencia_dirichlet_W(T, conductancias, temperaturas_caras):
    """Devuelve potencia entrante [W] sin modificar T; un flujo por interfaz."""
    potencia = np.zeros_like(T, dtype=float)
    for eje, (G, (T_min, T_max)) in enumerate(zip(conductancias, temperaturas_caras)):
        a, b, minimo, maximo = _caras(eje, T.ndim)
        flujo = G * (T[b] - T[a])
        potencia[a] += flujo
        potencia[b] -= flujo  # El mismo intercambio sale de la otra celda.
        potencia[minimo] += 2*G * (T_min - T[minimo])
        potencia[maximo] += 2*G * (T_max - T[maximo])
    return potencia
