"""FTCS propio para difusión 1D sin fuente, con Dirichlet independientes.

Caso base: script 01 del video. Verificación: perfil sinusoidal de la guía §7.
"""
from dataclasses import dataclass, fields
from math import ceil, isfinite
from numbers import Integral, Real
from typing import Callable
import numpy as np


@dataclass(frozen=True)
class Parametros1D:
    """Unidades SI. Alpha se ingresa directamente, como en el video.

    No se inventan k, rho o cp. Si paso_tiempo_s es None, se calcula desde
    fourier_objetivo. El paso estable se ajusta uniformemente al tiempo final.
    """
    longitud_m: float = 1.0
    n_intervalos: int = 100
    difusividad_m2_s: float = 1e-4
    tiempo_final_s: float = 4500.0
    temperatura_izquierda_C: float = 0.0
    temperatura_derecha_C: float = 10.0
    temperatura_inicial_C: float = 20.0
    amplitud_inicial_K: float = 0.0
    perfil_inicial: str = "uniforme"
    fourier_objetivo: float = 0.45
    paso_tiempo_s: float | None = None

    def __post_init__(self):
        if self.perfil_inicial not in ("uniforme", "seno"):
            raise ValueError("perfil_inicial debe ser 'uniforme' o 'seno'.")
        for field in fields(self):
            value = getattr(self, field.name)
            if field.name == "perfil_inicial" or (field.name == "paso_tiempo_s" and value is None):
                continue
            if isinstance(value, bool) or not isinstance(value, Real) or not isfinite(value):
                raise ValueError(f"{field.name} debe ser un número real finito.")
        if not isinstance(self.n_intervalos, Integral) or self.n_intervalos < 2:
            raise ValueError("n_intervalos debe ser un entero mayor o igual a 2.")
        for name in ("longitud_m", "difusividad_m2_s", "fourier_objetivo"):
            if getattr(self, name) <= 0:
                raise ValueError(f"{name} debe ser positivo.")
        if self.paso_tiempo_s is not None and self.paso_tiempo_s <= 0:
            raise ValueError("paso_tiempo_s debe ser positivo.")
        if self.tiempo_final_s < 0:
            raise ValueError("tiempo_final_s debe ser mayor o igual a cero.")

    @property
    def alpha_m2_s(self):
        return self.difusividad_m2_s

    @property
    def dx_m(self):
        return self.longitud_m / self.n_intervalos

    @property
    def dt_propuesto_s(self):
        if self.paso_tiempo_s is not None:
            return self.paso_tiempo_s
        return self.fourier_objetivo * self.dx_m**2 / self.alpha_m2_s

    @property
    def n_pasos(self):
        return ceil(self.tiempo_final_s / self.dt_propuesto_s)

    @property
    def dt_s(self):
        return self.tiempo_final_s / self.n_pasos if self.n_pasos else 0.0

    @property
    def fourier(self):
        return self.alpha_m2_s * self.dt_s / self.dx_m**2

    @property
    def dt_max_s(self):
        return self.dx_m**2 / (2 * self.alpha_m2_s)


@dataclass
class Resultado1D:
    """temperatura_C[n, i]: temperatura en el tiempo n y el nodo i."""
    parametros: Parametros1D
    x_m: np.ndarray
    tiempos_s: np.ndarray
    temperatura_C: np.ndarray


def perfil_estacionario(parametros: Parametros1D, x_m):
    """Recta de equilibrio; no es la solución transiente del video."""
    p = parametros
    x = np.asarray(x_m, dtype=float)
    return p.temperatura_izquierda_C + (
        p.temperatura_derecha_C - p.temperatura_izquierda_C
    ) * x / p.longitud_m


def perfil_inicial(parametros: Parametros1D, x_m):
    """Crear el perfil y después imponer los extremos, igual que el profesor.

    'uniforme': Tini + A*sin(pi*x/L), con A=0 en el video.
    'seno': recta estacionaria + A*sin(pi*x/L), compatible en los bordes.
    """
    p = parametros
    x = np.asarray(x_m, dtype=float)
    base = (np.full_like(x, p.temperatura_inicial_C) if p.perfil_inicial == "uniforme"
            else perfil_estacionario(p, x))
    inicial = base + p.amplitud_inicial_K * np.sin(np.pi * x / p.longitud_m)
    return np.where(x == 0, p.temperatura_izquierda_C,
                    np.where(x == p.longitud_m, p.temperatura_derecha_C, inicial))


def solucion_exacta(parametros: Parametros1D, x_m, tiempo_s):
    """Referencia transiente solo para el perfil 'seno', con broadcasting NumPy.

    No corresponde al perfil uniforme del video ni a perfiles personalizados.
    """
    p = parametros
    if p.perfil_inicial != "seno":
        raise ValueError("La solución exacta sinusoidal no corresponde al caso uniforme del video.")
    x = np.asarray(x_m, dtype=float)
    t = np.asarray(tiempo_s, dtype=float)
    return perfil_estacionario(p, x) + p.amplitud_inicial_K * np.sin(
        np.pi * x / p.longitud_m
    ) * np.exp(-p.alpha_m2_s * (np.pi / p.longitud_m)**2 * t)


def resolver_1d(
    parametros: Parametros1D,
    temperatura_inicial: Callable[[np.ndarray], np.ndarray] | None = None,
) -> Resultado1D:
    """Resolver sin fuente, con temperaturas fijas independientes en los extremos.

    El paso propuesto inestable se rechaza antes de ajustar uniformemente los
    tiempos. Se imponen los bordes desde t=0 aunque difieran del interior.
    Se conserva la historia completa para estudiar este caso 1D.
    """
    p = parametros
    fo_propuesto = p.alpha_m2_s * p.dt_propuesto_s / p.dx_m**2
    if fo_propuesto > 0.5 + 8 * np.finfo(float).eps:
        raise ValueError(
            f"Paso inestable: r propuesto={fo_propuesto:.6g} > 0.5. "
            f"Usar paso_tiempo_s <= {p.dt_max_s:.6g} s."
        )
    x = np.linspace(0.0, p.longitud_m, p.n_intervalos + 1)
    inicial = (perfil_inicial(p, x) if temperatura_inicial is None else
               np.array(temperatura_inicial(x.copy()), dtype=float, copy=True))
    if inicial.shape != x.shape or not np.all(np.isfinite(inicial)):
        raise ValueError("El perfil inicial debe tener un valor finito por nodo.")

    tiempos = np.arange(p.n_pasos + 1) * p.dt_s
    tiempos[-1] = p.tiempo_final_s
    temperaturas = np.empty((p.n_pasos + 1, x.size), dtype=float)
    temperaturas[0] = inicial
    temperaturas[:, 0] = p.temperatura_izquierda_C
    temperaturas[:, -1] = p.temperatura_derecha_C
    r = p.fourier
    for n in range(p.n_pasos):
        anterior = temperaturas[n]
        # Todos los vecinos provienen del mismo instante n.
        temperaturas[n + 1, 1:-1] = anterior[1:-1] + r * (
            anterior[2:] - 2 * anterior[1:-1] + anterior[:-2]
        )
    return Resultado1D(p, x, tiempos, temperaturas)
