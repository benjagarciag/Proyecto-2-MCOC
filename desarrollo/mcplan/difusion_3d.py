"""Difusión 3D explícita, homogénea y sin fuente; seis caras Dirichlet.

T[k,j,i] corresponde al centro del voxel (z,y,x). Se guardan instantáneas,
no todos los campos temporales. Los parámetros por defecto son didácticos.
"""
from dataclasses import dataclass
from math import ceil
from numbers import Integral
from typing import Callable

import numpy as np

from .difusion_2d import _real_finito  # Reutiliza la validación sin modificar el 2D.
from .balance_cartesiano import potencia_dirichlet_W, suma_conductancias_dirichlet_W_K


@dataclass(frozen=True)
class Dirichlet3D:
    """Temperaturas constantes en las seis caras físicas, en °C."""
    x_min_C: float = 20.0
    x_max_C: float = 20.0
    y_min_C: float = 20.0
    y_max_C: float = 20.0
    z_min_C: float = 20.0
    z_max_C: float = 20.0

    def __post_init__(self):
        for nombre, valor in vars(self).items():
            _real_finito(nombre, valor)

    @property
    def por_ejes_zyx(self):
        return ((self.z_min_C, self.z_max_C), (self.y_min_C, self.y_max_C),
                (self.x_min_C, self.x_max_C))


@dataclass(frozen=True)
class Parametros3D:
    longitud_x_m: float = 1.0
    longitud_y_m: float = 1.0
    longitud_z_m: float = 1.0
    celdas_x: int = 21
    celdas_y: int = 21
    celdas_z: int = 21
    conductividad_W_mK: float = 2.0
    densidad_kg_m3: float = 2400.0
    calor_especifico_J_kgK: float = 900.0
    tiempo_final_s: float = 86400.0
    paso_tiempo_s: float | None = None
    seguridad: float = 0.9

    def __post_init__(self):
        for nombre in ('longitud_x_m', 'longitud_y_m', 'longitud_z_m',
                       'conductividad_W_mK', 'densidad_kg_m3', 'calor_especifico_J_kgK'):
            _real_finito(nombre, getattr(self, nombre), positivo=True)
        for nombre in ('celdas_x', 'celdas_y', 'celdas_z'):
            valor = getattr(self, nombre)
            if isinstance(valor, bool) or not isinstance(valor, Integral) or valor < 2:
                raise ValueError(f'{nombre} debe ser un entero >= 2.')
        _real_finito('tiempo_final_s', self.tiempo_final_s)
        if self.tiempo_final_s < 0:
            raise ValueError('tiempo_final_s debe ser >= 0.')
        _real_finito('seguridad', self.seguridad, positivo=True)
        if self.seguridad > 1:
            raise ValueError('seguridad debe ser <= 1.')
        if self.paso_tiempo_s is not None:
            _real_finito('paso_tiempo_s', self.paso_tiempo_s, positivo=True)

    @property
    def pasos_espaciales_m(self):
        return (self.longitud_x_m/self.celdas_x, self.longitud_y_m/self.celdas_y,
                self.longitud_z_m/self.celdas_z)

    @property
    def forma_zyx(self):
        return (self.celdas_z, self.celdas_y, self.celdas_x)

    @property
    def alpha_m2_s(self):
        return self.conductividad_W_mK / (self.densidad_kg_m3*self.calor_especifico_J_kgK)

    @property
    def capacidad_voxel_J_K(self):
        dx, dy, dz = self.pasos_espaciales_m
        return self.densidad_kg_m3*self.calor_especifico_J_kgK*dx*dy*dz

    @property
    def conductancias_zyx_W_K(self):
        dx, dy, dz = self.pasos_espaciales_m
        k = self.conductividad_W_mK
        return (k*dx*dy/dz, k*dx*dz/dy, k*dy*dz/dx)


def paso_maximo_3d_s(p: Parametros3D):
    """Límite suficiente C/max(sum G) incluyendo caras, aristas y esquinas."""
    suma = suma_conductancias_dirichlet_W_K(p.forma_zyx, p.conductancias_zyx_W_K)
    return float(p.capacidad_voxel_J_K / suma.max())


@dataclass
class Resultado3D:
    parametros: Parametros3D
    bordes: Dirichlet3D
    x_m: np.ndarray
    y_m: np.ndarray
    z_m: np.ndarray
    tiempos_s: np.ndarray  # Solo los tiempos de los volúmenes guardados.
    temperatura_C: np.ndarray  # [instantánea, z, y, x]
    tiempos_historia_s: np.ndarray  # Un valor por paso.
    temperatura_central_C: np.ndarray  # Media de los centros más cercanos al centro.
    dt_s: float
    dt_max_s: float
    n_pasos: int


def resolver_3d(
    parametros: Parametros3D,
    bordes: Dirichlet3D,
    temperatura_inicial: float | Callable = 20.0,
    n_guardados: int = 7,
) -> Resultado3D:
    """Balance por voxel: T_nuevo = T_anterior + dt*potencia_entrante/C.

    n_guardados limita el número de campos en memoria, incluyendo inicio y final.
    No realiza E/S. Una condición inicial funcional recibe X,Y,Z con forma (Nz,Ny,Nx).
    """
    p = parametros
    if isinstance(n_guardados, bool) or not isinstance(n_guardados, Integral) or n_guardados < 2:
        raise ValueError('n_guardados debe ser un entero >= 2.')
    dt_max = paso_maximo_3d_s(p)
    propuesto = p.paso_tiempo_s if p.paso_tiempo_s is not None else p.seguridad*dt_max
    if propuesto > dt_max*(1+1e-14):
        raise ValueError(f'Paso inestable: {propuesto:.8g} s > {dt_max:.8g} s.')
    pasos = ceil(p.tiempo_final_s/propuesto)
    dt = p.tiempo_final_s/pasos if pasos else 0.0
    dx, dy, dz = p.pasos_espaciales_m
    x = (np.arange(p.celdas_x)+0.5)*dx
    y = (np.arange(p.celdas_y)+0.5)*dy
    z = (np.arange(p.celdas_z)+0.5)*dz
    if callable(temperatura_inicial):
        Z, Y, X = np.meshgrid(z, y, x, indexing='ij')
        T = np.array(temperatura_inicial(X, Y, Z), dtype=float, copy=True)
    else:
        _real_finito('temperatura_inicial', temperatura_inicial)
        T = np.full(p.forma_zyx, temperatura_inicial, dtype=float)
    if T.shape != p.forma_zyx or not np.isfinite(T).all():
        raise ValueError('La condición inicial debe tener un valor finito por voxel.')
    seleccion = np.unique(np.rint(np.linspace(0, pasos, min(n_guardados, pasos+1))).astype(int))
    posiciones = {int(n): i for i, n in enumerate(seleccion)}
    campos = np.empty((len(seleccion), *p.forma_zyx))
    campos[0] = T
    tiempos = np.arange(pasos+1)*dt
    tiempos[-1] = p.tiempo_final_s
    centro = tuple(sorted({(n-1)//2, n//2}) for n in p.forma_zyx)
    historial_centro = np.empty(pasos+1)
    historial_centro[0] = T[np.ix_(*centro)].mean()
    G = p.conductancias_zyx_W_K
    for n in range(1, pasos+1):
        potencia = potencia_dirichlet_W(T, G, bordes.por_ejes_zyx)
        T = T + dt*potencia/p.capacidad_voxel_J_K  # Todos los flujos usan el instante anterior.
        historial_centro[n] = T[np.ix_(*centro)].mean()
        if n in posiciones:
            campos[posiciones[n]] = T
    return Resultado3D(p, bordes, x, y, z, tiempos[seleccion], campos, tiempos,
                       historial_centro, dt, dt_max, pasos)
