"""Ejemplos de clase: Neumann, Robin oscilante y calor interno.

Conservan las entradas y actualizaciones de los scripts de casos/1d/codigos/.
Solo se guardan en memoria los perfiles seleccionados y una historia muestreada.
"""
from dataclasses import dataclass
from math import ceil, isfinite
import numpy as np


@dataclass
class Ejemplo1D:
    nombre: str
    x_m: np.ndarray
    tiempos_perfiles_s: np.ndarray
    perfiles_C: np.ndarray
    tiempos_historia_s: np.ndarray
    historia_C: np.ndarray  # Columnas: izquierda, centro, derecha.
    dt_s: float
    fourier: float
    nota: str


def resolver_ejemplo(nombre, n_intervalos=None, paso_tiempo_s=None, tiempo_final_s=None):
    """Resolver uno de los tres ejemplos sin escribir archivos ni abrir ventanas."""
    if nombre not in ("neumann", "robin", "calor_interno"):
        raise ValueError("Ejemplo no reconocido.")
    n = (80 if nombre == "robin" else 100) if n_intervalos is None else n_intervalos
    if isinstance(n, bool) or not isinstance(n, (int, np.integer)) or n < 2:
        raise ValueError("Los intervalos deben ser un entero mayor o igual a 2.")
    final = {"neumann": 18000., "robin": 172800., "calor_interno": 4500.}[nombre]
    if tiempo_final_s is not None:
        final = tiempo_final_s
    if not isfinite(final) or final < 0:
        raise ValueError("El tiempo final debe ser finito y no negativo.")
    x = np.linspace(0, 1, n + 1)
    dx = x[1] - x[0]
    k, rho, cp, h = 2., 2400., 900., 12.
    alpha = k/(rho*cp) if nombre == "robin" else 1e-4
    if nombre == "robin":
        propuesto = min(0.40*dx**2/alpha, 0.40*rho*cp*dx/(2*h))
        maximo = 1/(2*alpha/dx**2 + 2*h/(rho*cp*dx))
    else:
        propuesto = 0.45*dx**2/alpha
        maximo = dx**2/(2*alpha)
    if paso_tiempo_s is not None:
        propuesto = paso_tiempo_s
    if not isfinite(propuesto) or propuesto <= 0 or propuesto > maximo*(1+1e-14):
        raise ValueError(f"Paso inestable o inválido para {nombre}; usar dt <= {maximo:.8g} s.")
    pasos = ceil(final/propuesto)
    dt = final/pasos if pasos else 0.
    r = alpha*dt/dx**2
    limite_perfiles = min(final, 10*3600) if nombre == "robin" else final
    seleccion = (np.unique(np.rint(np.linspace(0, limite_perfiles, 20)/dt).astype(int))
                 if pasos else np.array([0]))
    seleccion = np.clip(seleccion, 0, pasos)
    guardar = set(seleccion.tolist())
    T = np.full(n + 1, 0. if nombre == "calor_interno" else 20.)
    perfiles = {0: T.copy()}
    tiempos, historia = [], []
    frecuencia = max(1, pasos//400)

    for paso in range(pasos + 1):
        if paso % frecuencia == 0 or paso == pasos:
            tiempos.append(paso*dt)
            historia.append([T[0], np.interp(0.5, x, T), T[-1]])
        if paso == pasos:
            break
        anterior = T.copy()
        T[1:-1] = anterior[1:-1] + r*(anterior[2:] - 2*anterior[1:-1] + anterior[:-2])
        if nombre == "neumann":
            # Como el script: el contacto a 60 °C se impone en el primer update.
            T[0] = 60.
            T[-1] = anterior[-1] + 2*r*(anterior[-2] - anterior[-1])
        elif nombre == "robin":
            aire = 20 + 10*np.sin(2*np.pi*(paso*dt)/(12*3600))
            T[0] = anterior[0] + dt*(2*k/(rho*cp*dx**2)*(anterior[1]-anterior[0])
                                     + 2*h/(rho*cp*dx)*(aire-anterior[0]))
            T[-1] = anterior[-1] + dt*(2*k/(rho*cp*dx**2)*(anterior[-2]-anterior[-1])
                                       + 2*h/(rho*cp*dx)*(20-anterior[-1]))
        else:
            # Q0 está dentro del paréntesis multiplicado por r en el script.
            T[1:-1] += r*(5./6000)
            T[0] = T[-1] = 0.
        if paso + 1 in guardar:
            perfiles[paso + 1] = T.copy()

    notas = {
        "neumann": "Izquierda a 60 °C; derecha adiabática. El perfil inicial incluye 20 °C en ambos extremos, como el script.",
        "robin": "Convección con h=12 W/(m²·K). Aire izquierdo: 20±10 °C, período 12 h; derecho: 20 °C. Perfiles de las primeras 10 h; historia de toda la simulación.",
        "calor_interno": f"Extremos a 0 °C y aporte r*Q0, Q0=5/6000. Tasa efectiva alpha*Q0/dx²={alpha*(5/6000)/dx**2:.8g} K/s; cambia al refinar si Q0 se mantiene fijo.",
    }
    return Ejemplo1D(nombre, x, seleccion*dt, np.array([perfiles[i] for i in seleccion]),
                     np.array(tiempos), np.array(historia), dt, r, notas[nombre])
