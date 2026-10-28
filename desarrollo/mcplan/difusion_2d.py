"""Difusión 2D explícita por balances de celdas, material homogéneo y Dirichlet.

T[j, i] vive en el centro de una celda. El dominio representa una placa de
espesor uniforme. Esta primera etapa no implementa fuentes, Robin ni Neumann.
Los valores predeterminados son didácticos: no son mediciones del hormigón G6.
"""
from dataclasses import dataclass
from math import ceil, isfinite
from numbers import Integral, Real
from typing import Callable

import numpy as np


def _real_finito(nombre, valor, *, positivo=False):
    if isinstance(valor, bool) or not isinstance(valor, Real) or not isfinite(valor):
        raise ValueError(f"{nombre} debe ser un número real finito.")
    if positivo and valor <= 0:
        raise ValueError(f"{nombre} debe ser positivo.")


@dataclass(frozen=True)
class Dirichlet2D:
    """Temperaturas constantes en las cuatro caras físicas, en °C."""
    izquierda_C: float = 20.0
    derecha_C: float = 20.0
    inferior_C: float = 20.0
    superior_C: float = 20.0

    def __post_init__(self):
        for nombre, valor in vars(self).items():
            _real_finito(nombre, valor)


@dataclass(frozen=True)
class Parametros2D:
    longitud_x_m: float = 1.0
    longitud_y_m: float = 1.0
    espesor_m: float = 1.0
    celdas_x: int = 20
    celdas_y: int = 20
    conductividad_W_mK: float = 2.0
    densidad_kg_m3: float = 2400.0
    calor_especifico_J_kgK: float = 900.0
    tiempo_final_s: float = 86400.0
    paso_tiempo_s: float | None = None
    seguridad: float = 0.9

    def __post_init__(self):
        positivos = ("longitud_x_m", "longitud_y_m", "espesor_m",
                     "conductividad_W_mK", "densidad_kg_m3", "calor_especifico_J_kgK")
        for nombre in positivos:
            _real_finito(nombre, getattr(self, nombre), positivo=True)
        for nombre in ("celdas_x", "celdas_y"):
            valor = getattr(self, nombre)
            if isinstance(valor, bool) or not isinstance(valor, Integral) or valor < 2:
                raise ValueError(f"{nombre} debe ser un entero >= 2.")
        _real_finito("tiempo_final_s", self.tiempo_final_s)
        if self.tiempo_final_s < 0:
            raise ValueError("tiempo_final_s debe ser >= 0.")
        _real_finito("seguridad", self.seguridad, positivo=True)
        if self.seguridad > 1:
            raise ValueError("seguridad debe ser <= 1.")
        if self.paso_tiempo_s is not None:
            _real_finito("paso_tiempo_s", self.paso_tiempo_s, positivo=True)

    @property
    def dx_m(self):
        return self.longitud_x_m / self.celdas_x

    @property
    def dy_m(self):
        return self.longitud_y_m / self.celdas_y

    @property
    def alpha_m2_s(self):
        return self.conductividad_W_mK / (self.densidad_kg_m3 * self.calor_especifico_J_kgK)

    @property
    def capacidad_celda_J_K(self):
        volumen = self.dx_m * self.dy_m * self.espesor_m
        return self.densidad_kg_m3 * self.calor_especifico_J_kgK * volumen

    @property
    def Gx_W_K(self):
        return self.conductividad_W_mK * self.dy_m * self.espesor_m / self.dx_m

    @property
    def Gy_W_K(self):
        return self.conductividad_W_mK * self.dx_m * self.espesor_m / self.dy_m


def suma_conductancias_W_K(p: Parametros2D):
    """Suma de conductancias que extraen calor de cada celda.

    Entre centros: G=kA/dx. Centro a cara Dirichlet: 2G (distancia dx/2).
    En las esquinas se suman ambas caras, sin imponer temperaturas incompatibles.
    """
    suma = np.zeros((p.celdas_y, p.celdas_x))
    suma[:, :-1] += p.Gx_W_K
    suma[:, 1:] += p.Gx_W_K
    suma[:-1, :] += p.Gy_W_K
    suma[1:, :] += p.Gy_W_K
    suma[:, 0] += 2 * p.Gx_W_K
    suma[:, -1] += 2 * p.Gx_W_K
    suma[0, :] += 2 * p.Gy_W_K
    suma[-1, :] += 2 * p.Gy_W_K
    return suma


def paso_maximo_s(p: Parametros2D):
    """Límite suficiente de estabilidad/monotonicidad para este balance lineal."""
    return float(p.capacidad_celda_J_K / suma_conductancias_W_K(p).max())


def potencia_neta_W(p: Parametros2D, bordes: Dirichlet2D, T):
    """Potencia entrante por celda [W]. No modifica T.

    Cada cara interior se evalúa una vez y entrega potencias opuestas a sus dos
    celdas. En el borde, T_b > T_celda introduce calor; T_b < T_celda lo extrae.
    """
    potencia = np.zeros_like(T, dtype=float)
    flujo_x = p.Gx_W_K * (T[:, 1:] - T[:, :-1])
    potencia[:, :-1] += flujo_x
    potencia[:, 1:] -= flujo_x
    flujo_y = p.Gy_W_K * (T[1:, :] - T[:-1, :])
    potencia[:-1, :] += flujo_y
    potencia[1:, :] -= flujo_y
    potencia[:, 0] += 2*p.Gx_W_K * (bordes.izquierda_C - T[:, 0])
    potencia[:, -1] += 2*p.Gx_W_K * (bordes.derecha_C - T[:, -1])
    potencia[0, :] += 2*p.Gy_W_K * (bordes.inferior_C - T[0, :])
    potencia[-1, :] += 2*p.Gy_W_K * (bordes.superior_C - T[-1, :])
    return potencia


@dataclass
class Resultado2D:
    parametros: Parametros2D
    bordes: Dirichlet2D
    x_m: np.ndarray
    y_m: np.ndarray
    tiempos_s: np.ndarray
    temperatura_C: np.ndarray  # [tiempo, fila y, columna x]
    dt_s: float
    dt_max_s: float


def resolver_2d(
    parametros: Parametros2D,
    bordes: Dirichlet2D,
    temperatura_inicial: float | Callable[[np.ndarray, np.ndarray], np.ndarray] = 20.0,
) -> Resultado2D:
    """Resuelve sin fuentes, con un material constante y cuatro bordes Dirichlet.

    La condición inicial puede ser un escalar o una función de las coordenadas
    X,Y de los centros. Se guarda la historia completa para estas demos pequeñas.
    """
    p = parametros
    dt_max = paso_maximo_s(p)
    propuesto = p.paso_tiempo_s if p.paso_tiempo_s is not None else p.seguridad * dt_max
    if propuesto > dt_max * (1 + 1e-14):
        raise ValueError(f"Paso inestable: {propuesto:.8g} s > {dt_max:.8g} s.")
    x = (np.arange(p.celdas_x) + 0.5) * p.dx_m
    y = (np.arange(p.celdas_y) + 0.5) * p.dy_m
    X, Y = np.meshgrid(x, y)
    if callable(temperatura_inicial):
        inicial = np.array(temperatura_inicial(X, Y), dtype=float, copy=True)
    else:
        _real_finito("temperatura_inicial", temperatura_inicial)
        inicial = np.full(X.shape, temperatura_inicial, dtype=float)
    if inicial.shape != X.shape or not np.isfinite(inicial).all():
        raise ValueError("La condición inicial debe tener un valor finito por celda.")
    pasos = ceil(p.tiempo_final_s / propuesto)
    dt = p.tiempo_final_s / pasos if pasos else 0.0
    tiempos = np.arange(pasos + 1) * dt
    tiempos[-1] = p.tiempo_final_s
    historia = np.empty((pasos + 1, p.celdas_y, p.celdas_x))
    historia[0] = inicial
    for n in range(pasos):
        anterior = historia[n]
        historia[n+1] = anterior + dt * potencia_neta_W(p, bordes, anterior) / p.capacidad_celda_J_K
    return Resultado2D(p, bordes, x, y, tiempos, historia, dt, dt_max)
