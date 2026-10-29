"""Demo 2D: modo sinusoidal con solución exacta y cuatro caras a T fija."""
import argparse
from dataclasses import replace
import os
from pathlib import Path
import sys

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / 'desarrollo'))
os.environ.setdefault('MPLCONFIGDIR', str(RAIZ / '.venv/cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from mcplan.difusion_2d import Dirichlet2D, Parametros2D, resolver_2d


# PARÁMETROS DEL EJEMPLO: editar aquí. Propiedades didácticas, sin calibración.
PARAMETROS = Parametros2D(
    longitud_x_m=1.0,
    longitud_y_m=1.0,
    espesor_m=1.0,
    celdas_x=30,
    celdas_y=30,
    conductividad_W_mK=2.0,
    densidad_kg_m3=2400.0,
    calor_especifico_J_kgK=900.0,
    tiempo_final_s=86400.0,  # 24 h
    paso_tiempo_s=None,  # None: calcular automáticamente un paso estable.
    seguridad=0.9,
)
TEMPERATURA_BORDE_C = 20.0
AMPLITUD_INICIAL_K = 50.0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--celdas', type=int, help='Número de celdas en cada eje')
    parser.add_argument('--dt', type=float, help='Paso temporal propuesto [s]')
    args = parser.parse_args()
    cambios = {}
    if args.celdas is not None:
        cambios.update(celdas_x=args.celdas, celdas_y=args.celdas)
    if args.dt is not None:
        cambios['paso_tiempo_s'] = args.dt
    p = replace(PARAMETROS, **cambios)
    base, amplitud = TEMPERATURA_BORDE_C, AMPLITUD_INICIAL_K
    if not np.isfinite([base, amplitud]).all():
        raise ValueError('Temperatura de borde y amplitud deben ser finitas.')
    bordes = Dirichlet2D(base, base, base, base)
    inicial = lambda X, Y: base + amplitud*np.sin(np.pi*X/p.longitud_x_m)*np.sin(np.pi*Y/p.longitud_y_m)
    r = resolver_2d(p, bordes, inicial)
    X, Y = np.meshgrid(r.x_m, r.y_m)
    forma = np.sin(np.pi*X/p.longitud_x_m)*np.sin(np.pi*Y/p.longitud_y_m)
    lambda_2d = (np.pi/p.longitud_x_m)**2 + (np.pi/p.longitud_y_m)**2
    tasa = p.alpha_m2_s*lambda_2d
    exacta = base + amplitud*forma*np.exp(-tasa*p.tiempo_final_s)
    error = r.temperatura_C[-1] - exacta

    fig, axs = plt.subplots(2, 2, figsize=(11, 8), layout='constrained')
    extent = (0, p.longitud_x_m, 0, p.longitud_y_m)
    for ax, campo, titulo in ((axs[0, 0], r.temperatura_C[0], 'Temperatura inicial'),
                              (axs[0, 1], r.temperatura_C[-1], f'Temperatura a {p.tiempo_final_s/3600:g} h')):
        im = ax.imshow(campo, origin='lower', extent=extent, vmin=min(base, base+amplitud),
                       vmax=max(base, base+amplitud), cmap='inferno')
        ax.set(title=titulo, xlabel='x [m]', ylabel='y [m]')
        fig.colorbar(im, ax=ax, label='Temperatura [°C]')
    limite = max(float(np.abs(error).max()), 1e-12)
    im = axs[1, 0].imshow(error, origin='lower', extent=extent, cmap='RdBu_r', vmin=-limite, vmax=limite)
    axs[1, 0].set(title='Error numérico − exacto al final', xlabel='x [m]', ylabel='y [m]')
    fig.colorbar(im, ax=axs[1, 0], label='Diferencia [K]')
    ix = sorted({(p.celdas_x-1)//2, p.celdas_x//2})
    iy = sorted({(p.celdas_y-1)//2, p.celdas_y//2})
    centro = r.temperatura_C[:, iy, :][:, :, ix].mean(axis=(1, 2))
    centro_exacto = base + amplitud*forma[np.ix_(iy, ix)].mean()*np.exp(-tasa*r.tiempos_s)
    axs[1, 1].plot(r.tiempos_s/3600, centro, label='Numérica: celdas centrales')
    axs[1, 1].plot(r.tiempos_s/3600, centro_exacto, '--', label='Exacta en los mismos centros')
    axs[1, 1].set(title='Evolución de la zona central', xlabel='Tiempo [h]', ylabel='Temperatura [°C]')
    axs[1, 1].legend(fontsize=8)
    axs[1, 1].grid(alpha=0.3)
    fig.suptitle('Difusión 2D verificada · ejemplo matemático, sin fuente interna')
    salida = RAIZ / 'resultados/2d/base/perfiles_temperatura.png'
    salida.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(salida, dpi=150)
    plt.close(fig)
    print(f'Malla: {p.celdas_x} x {p.celdas_y} celdas; dx={p.dx_m:.6g} m; dy={p.dy_m:.6g} m')
    print(f'alpha={p.alpha_m2_s:.8g} m²/s; dt={r.dt_s:.8g} s; dt máximo={r.dt_max_s:.8g} s')
    print(f'Pasos: {len(r.tiempos_s)-1}; centro inicial={centro[0]:.8f} °C; final={centro[-1]:.8f} °C')
    print(f'Error máximo final={limite:.8g} K; PNG: {salida}')


if __name__ == '__main__':
    main()
