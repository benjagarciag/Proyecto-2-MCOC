"""Extensión aditiva 2D/3D: bordes mixtos, fuente y dos materiales opcionales.

Reutiliza Parametros2D/3D y el balance cartesiano. No reemplaza las API
anteriores. Todas las caras deben declararse explícitamente, sin defaults
silenciosos. Una cara admite un tipo constante, uniforme en toda su área.
"""
from dataclasses import dataclass
from math import ceil
from numbers import Integral

import numpy as np

from .bordes_termicos import Dirichlet, Neumann, Robin, preparar_operador, potencia_con_bordes_W
from .difusion_2d import Parametros2D, _real_finito
from .difusion_3d import Parametros3D
from .fuentes_volumetricas import preparar_fuente_W_m3
from .materiales_termicos import CamposMateriales, DosMateriales, preparar_operador_materiales


def geometria_y_bordes(p, bordes):
    """Áreas de las caras de UNA celda, incluyendo espesor en 2D."""
    if isinstance(p, Parametros2D):
        forma = (p.celdas_y, p.celdas_x)
        pasos = (p.dy_m, p.dx_m)
        areas = (p.dx_m*p.espesor_m, p.dy_m*p.espesor_m)
        C = p.capacidad_celda_J_K
        nombres = ('y_min', 'y_max', 'x_min', 'x_max')
    elif isinstance(p, Parametros3D):
        dx, dy, dz = p.pasos_espaciales_m
        forma, pasos = p.forma_zyx, (dz, dy, dx)
        areas = (dx*dy, dx*dz, dy*dz)
        C = p.capacidad_voxel_J_K
        nombres = ('z_min', 'z_max', 'y_min', 'y_max', 'x_min', 'x_max')
    else:
        raise ValueError('Usar Parametros2D o Parametros3D.')
    if set(bordes) != set(nombres):
        raise ValueError(f'Declarar exactamente estas caras: {", ".join(nombres)}.')
    if not all(isinstance(b, (Dirichlet, Neumann, Robin)) for b in bordes.values()):
        raise ValueError('Cada cara debe ser Dirichlet, Neumann o Robin.')
    pares = tuple((bordes[nombres[i]], bordes[nombres[i+1]]) for i in range(0, len(nombres), 2))
    return forma, pasos, areas, C, pares


def _preparar_balance(parametros, bordes, materiales):
    forma, pasos, areas, C, pares = geometria_y_bordes(parametros, bordes)
    volumen = float(np.prod(pasos))*(parametros.espesor_m if len(forma) == 2 else 1.)
    campos = None
    if materiales is None:
        G, caras, suma = preparar_operador(forma, pasos, areas, parametros.conductividad_W_mK, pares)
    else:
        if not isinstance(materiales, DosMateriales):
            raise ValueError('materiales debe ser DosMateriales o None.')
        campos = materiales.campos(forma)
        C = campos.rho_kg_m3*campos.cp_J_kgK*volumen
        G, caras, suma = preparar_operador_materiales(forma, pasos, areas, campos, pares)
    return forma, pasos, C, volumen, G, caras, suma, campos


def paso_maximo_bordes_s(parametros, bordes, *, materiales=None):
    """Límite suficiente de monotonía explícita, incluyendo todos los bordes.

    Un flujo Neumann constante no agrega extracción proporcional a T.
    Robin agrega H=A/(d/(2k)+1/h); Dirichlet agrega 2*k*A/d.
    """
    _, _, C, _, _, _, suma, _ = _preparar_balance(parametros, bordes, materiales)
    return float(np.min(C/suma))


@dataclass
class ResultadoBordes:
    parametros: Parametros2D | Parametros3D
    bordes: dict
    coordenadas_m: tuple  # (x,y) o (x,y,z), centros de celdas.
    tiempos_s: np.ndarray  # Solo los campos guardados.
    temperatura_C: np.ndarray  # [instantánea,y,x] o [instantánea,z,y,x].
    tiempos_historia_s: np.ndarray
    energia_relativa_J: np.ndarray  # C*sum(T-0°C), referencia arbitraria.
    potencia_exterior_W: np.ndarray  # En cada t; último valor no integra un paso.
    dt_s: float
    dt_max_s: float
    n_pasos: int
    fuente_W_m3: np.ndarray | None = None  # Promedio de generación por celda.
    potencia_generada_W: float = 0.0  # Constante: sum(q'''_i*V_i).
    capacidad_J_K: np.ndarray | None = None  # Local, por celda, incluso con un material.
    materiales: CamposMateriales | None = None  # None si se usan propiedades de p.


def _resolver(parametros, bordes, temperatura_inicial, n_guardados, fuente_W_m3, materiales):
    p = parametros
    forma, pasos_m, C, volumen_m3, G, caras, suma, campos_materiales = _preparar_balance(p, bordes, materiales)
    if isinstance(n_guardados, bool) or not isinstance(n_guardados, Integral) or n_guardados < 2:
        raise ValueError('n_guardados debe ser un entero >= 2.')
    dt_max = float(np.min(C/suma))
    propuesto = p.paso_tiempo_s if p.paso_tiempo_s is not None else p.seguridad*dt_max
    if propuesto > dt_max*(1+1e-14):
        raise ValueError(f'Paso inestable: {propuesto:.8g} s > {dt_max:.8g} s.')
    n_pasos = ceil(p.tiempo_final_s/propuesto)
    dt = p.tiempo_final_s/n_pasos if n_pasos else 0.0
    centros = tuple((np.arange(n)+0.5)*d for n, d in zip(forma, pasos_m))
    fuente = preparar_fuente_W_m3(fuente_W_m3, forma, centros)
    potencia_fuente = fuente*volumen_m3  # W/m³ * m³ = W por celda.
    if callable(temperatura_inicial):
        grillas = np.meshgrid(*centros, indexing='ij')
        T = np.array(temperatura_inicial(*reversed(grillas)), dtype=float, copy=True)
    else:
        _real_finito('temperatura_inicial', temperatura_inicial)
        T = np.full(forma, temperatura_inicial, dtype=float)
    if T.shape != forma or not np.isfinite(T).all():
        raise ValueError('La condición inicial debe dar un valor finito por celda.')
    seleccion = np.unique(np.rint(np.linspace(0, n_pasos, min(n_guardados, n_pasos+1))).astype(int))
    posiciones = {int(n): i for i, n in enumerate(seleccion)}
    campos = np.empty((len(seleccion), *forma))
    tiempos = np.arange(n_pasos+1)*dt
    tiempos[-1] = p.tiempo_final_s
    energias = np.empty(n_pasos+1)
    potencias = np.empty(n_pasos+1)
    for n in range(n_pasos+1):
        energias[n] = np.sum(C*T)
        potencia, potencias[n] = potencia_con_bordes_W(T, G, caras)
        if n in posiciones:
            campos[posiciones[n]] = T
        if n < n_pasos:
            T = T + dt*(potencia + potencia_fuente)/C
    return ResultadoBordes(p, dict(bordes), tuple(reversed(centros)), tiempos[seleccion],
                           campos, tiempos, energias, potencias, dt, dt_max, n_pasos,
                           fuente, float(potencia_fuente.sum()),
                           np.broadcast_to(C, forma).copy(), campos_materiales)


def resolver_2d_bordes(parametros: Parametros2D, bordes, temperatura_inicial=20., n_guardados=7, *, fuente_W_m3=0., materiales=None):
    """Cuatro caras x_min/x_max/y_min/y_max; inicial escalar o f(X,Y).

    Las dos caras normales al espesor no intercambian calor (modelo 2D).
    fuente_W_m3 es escalar/campo/función f(X,Y), constante en el tiempo.
    materiales=None conserva las propiedades homogéneas de parametros.
    """
    if not isinstance(parametros, Parametros2D):
        raise ValueError('resolver_2d_bordes requiere Parametros2D.')
    return _resolver(parametros, bordes, temperatura_inicial, n_guardados, fuente_W_m3, materiales)


def resolver_3d_bordes(parametros: Parametros3D, bordes, temperatura_inicial=20., n_guardados=7, *, fuente_W_m3=0., materiales=None):
    """Seis caras; inicial f(X,Y,Z), fuente_W_m3 escalar/campo/f(X,Y,Z)."""
    if not isinstance(parametros, Parametros3D):
        raise ValueError('resolver_3d_bordes requiere Parametros3D.')
    return _resolver(parametros, bordes, temperatura_inicial, n_guardados, fuente_W_m3, materiales)
