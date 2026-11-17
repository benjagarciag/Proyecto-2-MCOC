"""Fuente derivada de una curva acumulada completa, con interpolación lineal."""
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class CurvaTabular:
    edad_s: np.ndarray
    acumulado_J_m3: np.ndarray
    capacidad_volumetrica_J_m3K: float

    def __post_init__(self):
        edad = np.array(self.edad_s, dtype=float, copy=True)
        energia = np.array(self.acumulado_J_m3, dtype=float, copy=True)
        if (edad.ndim != 1 or len(edad) < 2 or energia.shape != edad.shape
                or not np.isfinite(edad).all() or not np.isfinite(energia).all()
                or edad[0] != 0 or energia[0] != 0 or (np.diff(edad) <= 0).any()
                or (np.diff(energia) < 0).any()):
            raise ValueError("Se requiere edad creciente desde cero y acumulado no decreciente desde cero.")
        if not np.isfinite(self.capacidad_volumetrica_J_m3K) or self.capacidad_volumetrica_J_m3K <= 0:
            raise ValueError("Capacidad térmica volumétrica inválida.")
        for nombre, valores in (("edad_s", edad), ("acumulado_J_m3", energia)):
            valores.flags.writeable = False
            object.__setattr__(self, nombre, valores)
        tasas = np.diff(energia) / np.diff(edad)
        if not np.isfinite(tasas).all():
            raise ValueError("Tasa tabular fuera de rango.")
        tasas.flags.writeable = False
        object.__setattr__(self, "_tasas", tasas)

    def valor(self, edad_s):
        edad = np.asarray(edad_s)
        indices = np.searchsorted(self.edad_s, edad, side="right") - 1
        dentro = (indices >= 0) & (indices < len(self._tasas))
        return np.where(dentro, self._tasas[np.clip(indices, 0, len(self._tasas)-1)], 0.)

    def energia_intervalo_J_m3(self, edad_inicio_s, edad_fin_s):
        if np.any(np.asarray(edad_fin_s) < np.asarray(edad_inicio_s)):
            raise ValueError("El intervalo de edad no puede retroceder.")
        return (np.interp(edad_fin_s, self.edad_s, self.acumulado_J_m3)
                - np.interp(edad_inicio_s, self.edad_s, self.acumulado_J_m3))
