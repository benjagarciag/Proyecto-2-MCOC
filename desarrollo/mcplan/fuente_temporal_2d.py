"""Fuente volumétrica uniforme dependiente del tiempo, sin dependencia de T."""
from dataclasses import dataclass
from math import ceil

import numpy as np

from .difusion_2d import (Dirichlet2D, Resultado2D, _real_finito,
                         paso_maximo_s, potencia_neta_W)


@dataclass(frozen=True)
class PulsoTermico:
    qmax_W_m3: float
    duracion_s: float
    forma: str = 'coseno'

    def __post_init__(self):
        _real_finito('qmax_W_m3', self.qmax_W_m3)
        _real_finito('duracion_s', self.duracion_s, positivo=True)
        if self.qmax_W_m3 < 0:
            raise ValueError('qmax_W_m3 debe ser >= 0.')
        if self.forma not in ('coseno', 'triangular', 'rectangular'):
            raise ValueError('Forma de pulso desconocida.')

    def valor(self, t_s):
        t = np.asarray(t_s, dtype=float)
        u = np.clip(t/self.duracion_s, 0, 1)
        if self.forma == 'coseno':
            q = self.qmax_W_m3/2*(1-np.cos(2*np.pi*u))
        elif self.forma == 'triangular':
            q = self.qmax_W_m3*(1-np.abs(2*u-1))
        else:
            # Media amplitud: misma energía que coseno y triángulo.
            q = np.full_like(t, self.qmax_W_m3/2)
        return np.where((t >= 0) & (t < self.duracion_s), q, 0.)

    def acumulada_J_m3(self, t_s):
        """Integral exacta desde t=0, saturada al terminar el pulso."""
        u = np.clip(np.asarray(t_s, dtype=float)/self.duracion_s, 0, 1)
        if self.forma == 'coseno':
            area = (u-np.sin(2*np.pi*u)/(2*np.pi))/2
        elif self.forma == 'triangular':
            area = np.where(u <= .5, u*u, 2*u-u*u-.5)
        else:
            area = u/2
        return self.qmax_W_m3*self.duracion_s*area


def resolver_fuente_temporal_2d(p, pulso, temperatura_borde_C=20.):
    """Euler explícito en conducción e integral exacta de Q en cada paso.

    rho*cp*dT/dt = k*∇²T + Q(t). Inicio uniforme igual al contorno.
    El incremento de fuente es integral(Q dt)/(rho cp), en K.
    """
    _real_finito('temperatura_borde_C', temperatura_borde_C)
    limite = paso_maximo_s(p)
    propuesto = p.paso_tiempo_s if p.paso_tiempo_s is not None else p.seguridad*limite
    if propuesto > limite*(1+1e-14):
        raise ValueError(f'Paso inestable: {propuesto:g} s > {limite:g} s.')
    pasos = ceil(p.tiempo_final_s/propuesto)
    dt = p.tiempo_final_s/pasos if pasos else 0.
    tiempos = np.linspace(0, p.tiempo_final_s, pasos+1)
    x = (np.arange(p.celdas_x)+.5)*p.dx_m
    y = (np.arange(p.celdas_y)+.5)*p.dy_m
    historia = np.empty((pasos+1, p.celdas_y, p.celdas_x))
    historia[0] = temperatura_borde_C
    b = Dirichlet2D(*[temperatura_borde_C]*4)
    incrementos = np.diff(pulso.acumulada_J_m3(tiempos))/(p.densidad_kg_m3*p.calor_especifico_J_kgK)
    for n in range(pasos):
        anterior = historia[n]
        historia[n+1] = anterior + dt*potencia_neta_W(p, b, anterior)/p.capacidad_celda_J_K + incrementos[n]
    return Resultado2D(p, b, x, y, tiempos, historia, dt, limite)
