"""Barra 2D de 4 x 2 m: enfriamiento uniforme con contorno a 10 °C."""
import argparse
from dataclasses import replace
from math import ceil
import os
from pathlib import Path
import sys

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / 'desarrollo'))
os.environ.setdefault('MPLCONFIGDIR', str(RAIZ / '.venv/cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter, PillowWriter, writers
import numpy as np
from mcplan.difusion_2d import Dirichlet2D, Parametros2D, paso_maximo_s, resolver_2d


# Valores didácticos heredados del ejemplo; no son un material calibrado.
PARAMETROS = Parametros2D(
    longitud_x_m=4.0, longitud_y_m=2.0, espesor_m=1.0,
    celdas_x=40,  # dx = longitud_x_m / celdas_x = 0.10 m.
    celdas_y=20,  # dy = longitud_y_m / celdas_y = 0.10 m.
    paso_tiempo_s=1800.0,  # dt propuesto [s]: 5 minutos, 12 pasos por hora.
    conductividad_W_mK=2.0, densidad_kg_m3=2400.0,
    calor_especifico_J_kgK=900.0, seguridad=0.9,
)
TEMPERATURA_INICIAL_C = 20.0
TEMPERATURA_BORDE_C = 10.0
TOLERANCIA_K = 0.1
SALIDA = RAIZ / 'resultados/2d/base'


def simular_barra(p=PARAMETROS, tolerancia=TOLERANCIA_K):
    """Historia estable; pasos que dividen una hora y fin tras estabilización.

    Se estima un horizonte con el primer modo de Fourier y margen del 20 %;
    la aceptación se comprueba sobre TODAS las celdas, en cada paso numérico.
    El horizonte estimado nunca se presenta como tiempo de estabilización.
    """
    salto = abs(TEMPERATURA_INICIAL_C - TEMPERATURA_BORDE_C)
    if not np.isfinite(tolerancia) or not 0 < tolerancia < salto:
        raise ValueError('La tolerancia debe estar entre 0 y 10 K, sin incluir extremos.')
    limite = paso_maximo_s(p)
    propuesto = p.paso_tiempo_s if p.paso_tiempo_s is not None else p.seguridad*limite
    if propuesto > limite*(1+1e-14):
        raise ValueError(f'Paso inestable: {propuesto:g} s > {limite:g} s.')
    pasos_hora = ceil(3600/propuesto)
    dt = 3600/pasos_hora
    tasa = p.alpha_m2_s*np.pi**2*(1/p.longitud_x_m**2 + 1/p.longitud_y_m**2)
    horas = ceil(1.2*np.log(16*salto/(np.pi**2*tolerancia))/tasa/3600)
    p = replace(p, tiempo_final_s=horas*3600, paso_tiempo_s=dt)
    b = TEMPERATURA_BORDE_C
    r = resolver_2d(p, Dirichlet2D(b, b, b, b), TEMPERATURA_INICIAL_C)
    desviacion = np.max(np.abs(r.temperatura_C-b), axis=(1, 2))
    indices = np.flatnonzero(desviacion <= tolerancia)
    if not len(indices):
        raise RuntimeError('El horizonte estimado no alcanzó la tolerancia; ampliar el horizonte.')
    primero = int(indices[0])
    ultimo = ceil(primero/pasos_hora)*pasos_hora
    # Copiar solo hasta la última hora utilizada y liberar la historia sobrante.
    r.temperatura_C = r.temperatura_C[:ultimo+1].copy()
    r.tiempos_s = r.tiempos_s[:ultimo+1].copy()
    r.parametros = replace(p, tiempo_final_s=float(r.tiempos_s[-1]))
    return r, primero, pasos_hora


def temperatura_centro(r):
    """Interpolación bilineal al centro; exacto en una celda con malla impar."""
    x0 = r.parametros.longitud_x_m/2
    y0 = r.parametros.longitud_y_m/2
    filas = np.array([np.interp(x0, r.x_m, fila)
                      for campo in r.temperatura_C for fila in campo])
    filas = filas.reshape(len(r.tiempos_s), len(r.y_m))
    return np.array([np.interp(y0, r.y_m, fila) for fila in filas])


def graficar(r, primero, tolerancia):
    p = r.parametros
    horas = r.tiempos_s/3600
    centro = temperatura_centro(r)
    tmax = r.temperatura_C.max(axis=(1, 2))
    extent = (-p.longitud_x_m/2, p.longitud_x_m/2,
              -p.longitud_y_m/2, p.longitud_y_m/2)
    fig, axs = plt.subplots(2, 2, figsize=(12, 8), layout='constrained')
    for ax, campo, titulo in (
        (axs[0, 0], r.temperatura_C[0], 'Inicio: interior a 20 °C'),
        (axs[0, 1], r.temperatura_C[-1], f'Final: {horas[-1]:g} h')):
        im = ax.imshow(campo, origin='lower', extent=extent, cmap='inferno',
                       vmin=10, vmax=20, interpolation='nearest')
        ax.plot(0, 0, '+', color='cyan', markersize=9)
        ax.set(title=titulo, xlabel='x [m]', ylabel='y [m]')
        fig.colorbar(im, ax=ax, label='Temperatura [°C]')
    axs[1, 0].plot(horas, tmax, label='Máxima espacial')
    axs[1, 0].axhline(10+tolerancia, color='tab:red', ls='--', label='10 °C + tolerancia')
    axs[1, 0].axvline(horas[primero], color='gray', ls=':', label=f'{horas[primero]:.1f} h')
    axs[1, 0].set(title='Estabilización en toda la barra', xlabel='Tiempo [h]', ylabel='T máxima [°C]')
    axs[1, 0].legend()
    axs[1, 0].grid(alpha=0.3)
    axs[1, 1].plot(horas, centro, color='tab:blue')
    axs[1, 1].axhline(10, color='gray', ls='--', label='Equilibrio: 10 °C')
    axs[1, 1].set(title='T(0,0,t): centro geométrico', xlabel='Tiempo [h]', ylabel='Temperatura [°C]')
    axs[1, 1].legend()
    axs[1, 1].grid(alpha=0.3)
    fig.suptitle('Barra 4 × 2 m · contorno fijo a 10 °C · sin fuente interna')
    fig.savefig(SALIDA / 'perfiles_temperatura.png', dpi=150)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(9, 5), layout='constrained')
    ax.plot(horas, centro, label='T(0,0,t)')
    ax.axhline(10, color='gray', ls='--', label='Equilibrio: 10 °C')
    ax.axhline(10+tolerancia, color='tab:red', ls=':', label=f'Tolerancia: {tolerancia:g} °C')
    ax.axvline(horas[primero], color='tab:green', ls=':', label=f'Estabilización: {horas[primero]:.1f} h')
    ax.set(title='Enfriamiento del centro de la barra de 4 × 2 m',
           xlabel='Tiempo [h]', ylabel='T(0,0,t) [°C]', xlim=(0, horas[-1]))
    ax.grid(alpha=0.3)
    ax.legend()
    fig.savefig(SALIDA / 'temperatura_centro.png', dpi=150)
    plt.close(fig)


def graficar_punto_1_1(tiempo_final_h):
    """Valor de la cara física y=1 m, no de su celda interior vecina.

    Para la barra 4 x 2 m centrada, (1,1) pertenece al contorno Dirichlet.
    El estado previo a imponer el borde se indica aparte del valor para t>0.
    """
    fig, ax = plt.subplots(figsize=(9, 5), layout='constrained')
    ax.plot([0, tiempo_final_h], [TEMPERATURA_BORDE_C]*2,
            color='tab:blue', lw=2, label='T(1,1,t) = 10 °C para t > 0')
    ax.plot(0, TEMPERATURA_INICIAL_C, 'o', color='tab:orange',
            markerfacecolor='white', clip_on=False,
            label='Estado inicial previo a imponer el borde: 20 °C')
    ax.plot([0, 0], [TEMPERATURA_INICIAL_C, TEMPERATURA_BORDE_C],
            ':', color='tab:orange', clip_on=False)
    ax.annotate('Cambio instantáneo al aplicar el contorno',
                xy=(0, 15), xytext=(tiempo_final_h*0.12, 15),
                arrowprops={'arrowstyle': '->', 'color': 'tab:orange'})
    ax.set(title='T(1,1,t): punto del borde superior de la barra de 4 × 2 m',
           xlabel='Tiempo [h]', ylabel='T(1,1,t) [°C]',
           xlim=(0, tiempo_final_h), ylim=(9, 21))
    ax.grid(alpha=0.3)
    ax.legend(loc='upper right', fontsize=9)
    SALIDA.mkdir(parents=True, exist_ok=True)
    destino = SALIDA / 'temperatura_punto_1_1.png'
    fig.savefig(destino, dpi=150)
    plt.close(fig)
    return destino


def crear_movie(r, pasos_hora):
    """Un cuadro por hora física; 10 cuadros/s de reproducción."""
    p = r.parametros
    fig, ax = plt.subplots(figsize=(9, 5), layout='constrained')
    extent = (-p.longitud_x_m/2, p.longitud_x_m/2, -p.longitud_y_m/2, p.longitud_y_m/2)
    im = ax.imshow(r.temperatura_C[0], origin='lower', extent=extent,
                   vmin=10, vmax=20, cmap='inferno', interpolation='nearest')
    ax.plot(0, 0, '+', color='cyan', markersize=10)
    ax.set(xlabel='x [m]', ylabel='y [m]')
    fig.colorbar(im, ax=ax, label='Temperatura [°C]')
    fig.suptitle('Barra 4 × 2 m · contorno a 10 °C · un cuadro por hora')
    titulo = ax.set_title('')
    if writers.is_available('ffmpeg'):
        destino = SALIDA / 'evolucion_temperatura.mp4'
        writer = FFMpegWriter(fps=10, codec='libx264', extra_args=['-pix_fmt', 'yuv420p'])
    else:
        destino = SALIDA / 'evolucion_temperatura.gif'
        writer = PillowWriter(fps=10)
    with writer.saving(fig, str(destino), dpi=100):
        for n in range(0, len(r.tiempos_s), pasos_hora):
            campo = r.temperatura_C[n]
            im.set_data(campo)
            titulo.set_text(f't = {r.tiempos_s[n]/3600:.0f} h   |   Tmáx = {campo.max():.3f} °C')
            writer.grab_frame()
    plt.close(fig)
    return destino


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--celdas', type=int, help='Celdas en x; y usa aproximadamente la mitad')
    parser.add_argument('--dt', type=float, help='Paso propuesto [s]; se reduce para dividir una hora')
    parser.add_argument('--tolerancia', type=float, default=TOLERANCIA_K, help='Desviación máxima respecto a 10 °C [K]')
    args = parser.parse_args()
    cambios = {}
    if args.celdas is not None:
        cambios.update(celdas_x=args.celdas, celdas_y=max(2, ceil(args.celdas/2)))
    if args.dt is not None:
        cambios['paso_tiempo_s'] = args.dt
    r, primero, pasos_hora = simular_barra(replace(PARAMETROS, **cambios), args.tolerancia)
    p = r.parametros
    SALIDA.mkdir(parents=True, exist_ok=True)
    graficar(r, primero, args.tolerancia)
    if p.longitud_x_m >= 2 and p.longitud_y_m == 2:
        graficar_punto_1_1(r.tiempos_s[-1]/3600)
    print(f'Malla: {p.celdas_x} x {p.celdas_y}; dx={p.dx_m:g} m; dy={p.dy_m:g} m', flush=True)
    print(f'alpha={p.alpha_m2_s:.8g} m²/s; dt={r.dt_s:g} s; límite={r.dt_max_s:g} s', flush=True)
    print(f'Tmáx global: {r.temperatura_C.max():.3f} °C; equilibrio: 10 °C', flush=True)
    print(f'Estabilización: {r.tiempos_s[primero]/3600:.2f} h '
          f'({r.tiempos_s[primero]/86400:.2f} días), tolerancia={args.tolerancia:g} K', flush=True)
    print(f'Último cuadro: {r.tiempos_s[-1]/3600:g} h; Tmáx={r.temperatura_C[-1].max():.6f} °C', flush=True)
    print('Generando película horaria...', flush=True)
    print(f'Movie: {crear_movie(r, pasos_hora)}', flush=True)


if __name__ == '__main__':
    main()
