"""Barra 4 x 2 m, 48 h y generación temporal; pulso principal de 12 h."""
from dataclasses import replace
import os
from pathlib import Path
import sys

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ/'desarrollo'))
os.environ.setdefault('MPLCONFIGDIR', str(RAIZ/'.venv/cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from mcplan.difusion_2d import Parametros2D
from mcplan.fuente_temporal_2d import PulsoTermico, resolver_fuente_temporal_2d


PARAMETROS = Parametros2D(longitud_x_m=4, longitud_y_m=2, espesor_m=1,
                         celdas_x=40, celdas_y=20, paso_tiempo_s=300,
                         tiempo_final_s=48*3600, conductividad_W_mK=2,
                         densidad_kg_m3=2400, calor_especifico_J_kgK=900)
DURACION_PRINCIPAL_H = 12
SALIDA = RAIZ/'resultados/2d/fuente_temporal'


def centro(r):
    # Simetría: media de los centros que rodean el origen en mallas pares.
    nx, ny = r.parametros.celdas_x, r.parametros.celdas_y
    ix = sorted({(nx-1)//2, nx//2})
    iy = sorted({(ny-1)//2, ny//2})
    return r.temperatura_C[:, iy, :][:, :, ix].mean(axis=(1, 2))


def respuesta_unidad(p, horas, forma='coseno'):
    r = resolver_fuente_temporal_2d(p, PulsoTermico(1., horas*3600, forma))
    subida = centro(r)-20
    qcrit = 50/subida.max()
    return r, subida, qcrit


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    respuestas = {h: respuesta_unidad(PARAMETROS, h) for h in (12, 24, 48)}
    r, subida, qcrit = respuestas[DURACION_PRINCIPAL_H]
    horas = r.tiempos_s/3600
    # Redondear hacia arriba para obtener >=70, no quedarse por debajo.
    qseleccionado = float(np.ceil(qcrit))
    tiempos_curva = np.linspace(0, 48*3600, 1201)
    fig, axs = plt.subplots(2, 2, figsize=(12, 8), layout='constrained')
    for factor in (.8, 1., 1.2):
        q = factor*qseleccionado
        pulso = PulsoTermico(q, DURACION_PRINCIPAL_H*3600)
        etiqueta = f'Qmáx = {q:.0f} W/m³'
        axs[0, 0].plot(tiempos_curva/3600, pulso.valor(tiempos_curva), label=etiqueta)
        curva = 20+q*subida
        axs[0, 1].plot(horas, curva, label=f'{etiqueta} · pico {curva.max():.2f} °C')
    axs[0, 0].set(title='Pulso cosenoidal principal: duración 12 h', ylabel='Q(t) [W/m³]')
    axs[0, 1].set(title='Temperatura central: efecto de Qmáx', ylabel='T(0,0,t) [°C]')
    for h, (rr, unidad, crit) in respuestas.items():
        pulso = PulsoTermico(qseleccionado, h*3600)
        axs[1, 0].plot(tiempos_curva/3600, pulso.valor(tiempos_curva), label=f'Duración {h} h')
        curva = 20+qseleccionado*unidad
        axs[1, 1].plot(rr.tiempos_s/3600, curva, label=f'{h} h · pico {curva.max():.1f} °C')
    axs[1, 0].set(title=f'Distintas duraciones · mismo Qmáx = {qseleccionado:.0f} W/m³', ylabel='Q(t) [W/m³]')
    axs[1, 1].set(title='Un pulso más largo aporta más energía', ylabel='T(0,0,t) [°C]')
    for ax in axs[:, 1]:
        ax.axhline(70, color='black', ls='--', lw=1, label='70 °C')
    for ax in axs.flat:
        ax.set(xlabel='Tiempo [h]', xlim=(0, 48))
        ax.grid(alpha=.25)
        ax.legend(fontsize=8)
    fig.suptitle('Generación interna uniforme · barra 4 × 2 m · inicio y contorno a 20 °C')
    fig.savefig(SALIDA/'pulsos_y_temperatura.png', dpi=150)
    plt.close(fig)

    fig, axs = plt.subplots(2, 2, figsize=(12, 8), layout='constrained')
    # 48 h permite apreciar diferencias de forma con el mismo calor aportado.
    qformas = respuestas[48][2]
    for forma in ('coseno', 'triangular', 'rectangular'):
        rr, unidad, _ = respuesta_unidad(PARAMETROS, 48, forma)
        pulso = PulsoTermico(qformas, 48*3600, forma)
        etiqueta = forma if forma != 'rectangular' else 'constante Qmáx/2'
        axs[0, 0].plot(tiempos_curva/3600, pulso.valor(tiempos_curva), label=etiqueta)
        curva = 20+qformas*unidad
        axs[0, 1].plot(rr.tiempos_s/3600, curva, label=f'{etiqueta} · pico {curva.max():.2f} °C')
    axs[0, 0].set(title='Formas distintas · duración 48 h · misma energía total', xlabel='Tiempo [h]', ylabel='Q(t) [W/m³]')
    axs[0, 1].set(title='Temperatura central: importa cuándo se aporta el calor', xlabel='Tiempo [h]', ylabel='T(0,0,t) [°C]')
    axs[0, 1].axhline(70, color='black', ls='--', lw=1)
    for ax in axs[0]:
        ax.grid(alpha=.25)
        ax.legend(fontsize=8)
        ax.set_xlim(0, 48)
    pico = int(np.argmax(subida))
    for ax, factor in zip(axs[1], (1., 1.2)):
        campo = 20+factor*qseleccionado*(r.temperatura_C[pico]-20)
        im = ax.imshow(campo, origin='lower', extent=(-2, 2, -1, 1),
                       cmap='inferno', vmin=20, vmax=81, interpolation='nearest')
        if campo.max() > 70 and campo.min() < 70:
            X, Y = np.meshgrid(r.x_m-2, r.y_m-1)
            ax.contour(X, Y, campo, levels=[70], colors='cyan', linewidths=1)
        ax.plot(0, 0, '+', color='white')
        ax.set(title=f'Pulso 12 h · Qmáx = {factor*qseleccionado:.0f} W/m³\n'
                      f't = {horas[pico]:.2f} h · Tcentro = {20+factor*qseleccionado*subida[pico]:.2f} °C',
               xlabel='x [m]', ylabel='y [m]')
        fig.colorbar(im, ax=ax, label='Temperatura [°C]')
    fig.suptitle('Comparación de formas y campos térmicos · línea cian: 70 °C')
    fig.savefig(SALIDA/'formas_y_campos.png', dpi=150)
    plt.close(fig)
    # Verificación de refinamiento conjunto; no exporta archivos adicionales.
    fino = replace(PARAMETROS, celdas_x=80, celdas_y=40, paso_tiempo_s=75)
    _, _, crit_fino = respuesta_unidad(fino, DURACION_PRINCIPAL_H)
    print('Duración [h] | Qmáx umbral [W/m³] | Hora del pico central')
    for h, (rr, unidad, crit) in respuestas.items():
        print(f'{h:12g} | {crit:19.6f} | {rr.tiempos_s[np.argmax(unidad)]/3600:.4f}')
    print(f'Principal: Qmáx elegido={qseleccionado:g} W/m³; '
          f'Tcentro pico={20+qseleccionado*subida.max():.6f} °C; '
          f'Tcentro a 48 h={20+qseleccionado*subida[-1]:.6f} °C')
    print(f'Umbral con malla 80x40 y dt=75 s: {crit_fino:.6f} W/m³; '
          f'cambio relativo={abs(crit_fino/qcrit-1)*100:.4f} %')
    print(f'Figuras: {SALIDA}')


if __name__ == '__main__':
    main()
