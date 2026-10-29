"""Demostración didáctica: pasos sobre la cota conservadora de 1800 s.

Solo esta demo omite deliberadamente el rechazo de pasos inestables.
No modifica el solver ni los parámetros del ejecutor principal.
"""
from dataclasses import replace

from Barra_Enfriamiento_2D import PARAMETROS, RAIZ
import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter, PillowWriter, writers
from matplotlib.colors import SymLogNorm
import numpy as np
from mcplan.difusion_2d import Dirichlet2D, paso_maximo_s, potencia_neta_W, resolver_2d


def ejecutar_sin_rechazo(p, dt):
    pasos = round(p.tiempo_final_s/dt)
    if not np.isclose(pasos*dt, p.tiempo_final_s):
        raise ValueError('En esta demo dt debe dividir el horizonte exactamente.')
    historia = np.empty((pasos+1, p.celdas_y, p.celdas_x))
    historia[0] = 20.0
    bordes = Dirichlet2D(10, 10, 10, 10)
    for n in range(pasos):
        anterior = historia[n]
        historia[n+1] = anterior + dt*potencia_neta_W(p, bordes, anterior)/p.capacidad_celda_J_K
    return np.arange(pasos+1)*dt/3600, historia


def crear_movie_inestabilidad(resultados):
    """Cuadros horarios comparables; escala fija propia para cada panel."""
    horas, inestable = resultados[3600]
    estable = resultados[300][1][::12]
    np.testing.assert_allclose(resultados[300][0][::12], horas)
    fig, axs = plt.subplots(1, 2, figsize=(12, 5), layout='constrained')
    extent = (-2, 2, -1, 1)
    im_estable = axs[0].imshow(estable[0], origin='lower', extent=extent,
                              vmin=10, vmax=20, cmap='inferno', interpolation='nearest')
    fig.colorbar(im_estable, ax=axs[0], label='Temperatura [°C] · escala fija')
    # La escala simétrica logarítmica permite ver tanto el inicio como la
    # divergencia sin cambiar los colores de referencia entre cuadros.
    limite = 10**np.ceil(np.log10(np.max(np.abs(inestable-10))))
    norm = SymLogNorm(linthresh=1, vmin=-limite, vmax=limite, base=10)
    im_inestable = axs[1].imshow(inestable[0]-10, origin='lower', extent=extent,
                                norm=norm, cmap='RdBu_r', interpolation='nearest')
    fig.colorbar(im_inestable, ax=axs[1], label='T − 10 °C [K] · escala logarítmica simétrica fija')
    for ax in axs:
        ax.set(xlabel='x [m]', ylabel='y [m]')
    fig.supxlabel('Un cuadro por hora · 2 cuadros/s · el panel derecho muestra inestabilidad numérica',
                   fontsize=10)
    titulo = fig.suptitle('')
    destino = RAIZ / 'resultados/2d/base/movie_inestabilidad.mp4'
    if writers.is_available('ffmpeg'):
        writer = FFMpegWriter(fps=2, codec='libx264', extra_args=['-pix_fmt', 'yuv420p'])
    else:
        destino = destino.with_suffix('.gif')
        writer = PillowWriter(fps=2)
    with writer.saving(fig, str(destino), dpi=100):
        for n, hora in enumerate(horas):
            im_estable.set_data(estable[n])
            im_inestable.set_data(inestable[n]-10)
            axs[0].set_title(f'Estable: Δt = 300 s\n'
                             f'Tmín = {estable[n].min():.2f} °C · Tmáx = {estable[n].max():.2f} °C')
            axs[1].set_title(f'Inestable: Δt = 3600 s\n'
                             f'Tmín = {inestable[n].min():.2f} °C · Tmáx = {inestable[n].max():.2f} °C')
            titulo.set_text(f'Barra 4 × 2 m · Δx = Δy = 0,10 m · t = {hora:g} h')
            writer.grab_frame()
    plt.close(fig)
    return destino


def main():
    p = replace(PARAMETROS, longitud_x_m=4, longitud_y_m=2,
                celdas_x=40, celdas_y=20, tiempo_final_s=24*3600,
                paso_tiempo_s=300)
    pasos = (300, 1800, 2000, 3600)
    # 2000 s no divide 24 h: se usa su último paso anterior, sin reducir dt.
    resultados = {}
    for dt in pasos:
        pp = replace(p, tiempo_final_s=(int(p.tiempo_final_s//dt))*dt)
        resultados[dt] = ejecutar_sin_rechazo(pp, dt)
    # Comprobar el balance de la demo contra el solver protegido con dt estable.
    referencia = resolver_2d(p, Dirichlet2D(10, 10, 10, 10), 20)
    np.testing.assert_allclose(resultados[300][1], referencia.temperatura_C)

    fig, axs = plt.subplots(2, 2, figsize=(13, 9), layout='constrained')
    colores = {300: 'tab:blue', 1800: 'tab:green', 2000: 'tab:orange', 3600: 'tab:red'}
    for dt, (horas, campos) in resultados.items():
        axs[0, 0].plot(horas, campos[:, 0, 0], '.-', color=colores[dt],
                       label=f'Δt = {dt} s', markersize=4)
    axs[0, 0].axhline(10, color='gray', ls='--')
    axs[0, 0].set(xlim=(0, 5), ylim=(-15, 30),
                  title='Primeras horas: celda interior junto a la esquina',
                  xlabel='Tiempo [h]', ylabel='Temperatura [°C]')
    axs[0, 0].legend()
    axs[0, 0].grid(alpha=0.3)

    for dt in (300, 2000, 3600):
        horas, campos = resultados[dt]
        desv = np.max(np.abs(campos-10), axis=(1, 2))
        axs[0, 1].semilogy(horas, desv, '.-', color=colores[dt],
                           label=f'Δt = {dt} s', markersize=3)
    axs[0, 1].set(title='Desviación máxima respecto al equilibrio',
                  xlabel='Tiempo [h]', ylabel='máx |T − 10 °C| [K] · escala logarítmica')
    axs[0, 1].legend()
    axs[0, 1].grid(alpha=0.3)

    extent = (-2, 2, -1, 1)
    estable = resultados[300][1][-1]
    inestable = resultados[3600][1][-1]
    im = axs[1, 0].imshow(estable, origin='lower', extent=extent,
                          vmin=10, vmax=20, cmap='inferno', interpolation='nearest')
    axs[1, 0].set(title='Δt = 300 s · campo a 24 h', xlabel='x [m]', ylabel='y [m]')
    fig.colorbar(im, ax=axs[1, 0], label='Temperatura [°C]')
    limite = np.max(np.abs(inestable-10))
    im = axs[1, 1].imshow(inestable-10, origin='lower', extent=extent,
                          vmin=-limite, vmax=limite, cmap='RdBu_r', interpolation='nearest')
    axs[1, 1].set(title='Δt = 3600 s · oscilaciones artificiales a 24 h',
                  xlabel='x [m]', ylabel='y [m]')
    fig.colorbar(im, ax=axs[1, 1], label='T − 10 °C [K] · escala distinta')
    fig.suptitle('Demostración de inestabilidad · barra 4 × 2 m · Δx = Δy = 0,10 m\n'
                 'Interior inicial: 20 °C · contorno: 10 °C · cota conservadora: 1800 s')
    salida = RAIZ / 'resultados/2d/base/demostracion_inestabilidad.png'
    salida.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(salida, dpi=150)
    plt.close(fig)
    print(f'Cota conservadora: {paso_maximo_s(p):g} s')
    for dt, (horas, campos) in resultados.items():
        print(f'dt={dt} s; primer paso, celda de esquina={campos[1, 0, 0]:.6g} °C; '
              f'a {horas[-1]:g} h: Tmin={campos[-1].min():.6g} °C, '
              f'Tmax={campos[-1].max():.6g} °C')
    print(f'Figura: {salida}')
    print(f'Movie: {crear_movie_inestabilidad(resultados)}')


if __name__ == '__main__':
    main()
