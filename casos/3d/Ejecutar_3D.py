"""Cortes XY/XZ/YZ del enfriamiento 3D y verificación sinusoidal exacta."""
import argparse
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
from mcplan.difusion_3d import Parametros3D, Dirichlet3D, resolver_3d


# PARÁMETROS DEL EJEMPLO: editar aquí. Propiedades didácticas, sin calibración.
PARAMETROS = Parametros3D(
    longitud_x_m=1.0,
    longitud_y_m=1.0,
    longitud_z_m=1.0,
    celdas_x=21,
    celdas_y=21,
    celdas_z=21,
    conductividad_W_mK=2.0,
    densidad_kg_m3=2400.0,
    calor_especifico_J_kgK=900.0,
    tiempo_final_s=86400.0,
    paso_tiempo_s=None,  # None: calcular automáticamente un paso estable.
    seguridad=0.9,
)
TEMPERATURA_BORDE_C = 20.0  # T_0: misma temperatura en las seis caras.
AMPLITUD_INICIAL_K = 50.0   # A: amplitud del perfil sinusoidal inicial.
INSTANTANEAS = 7           # Campos 3D conservados en memoria, incluido inicio y final.


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--celdas', type=int)
    parser.add_argument('--dt', type=float)
    args = parser.parse_args()
    p = PARAMETROS
    cambios = {}
    if args.celdas is not None:
        cambios.update(celdas_x=args.celdas, celdas_y=args.celdas, celdas_z=args.celdas)
    if args.dt is not None:
        cambios['paso_tiempo_s'] = args.dt
    p = replace(p, **cambios)
    base, amplitud = TEMPERATURA_BORDE_C, AMPLITUD_INICIAL_K
    if not np.isfinite([base, amplitud]).all():
        raise ValueError('Borde y amplitud deben ser finitos.')

    #Condiciones de borde e inicial
    forma = lambda X, Y, Z: (np.sin(np.pi*X/p.longitud_x_m)*np.sin(np.pi*Y/p.longitud_y_m)
                            * np.sin(np.pi*Z/p.longitud_z_m))
    inicial = lambda X, Y, Z: base + amplitud*forma(X, Y, Z)

    #Ejecutar el solver
    r = resolver_3d(p, Dirichlet3D(base, base, base, base, base, base), inicial,
                    n_guardados=INSTANTANEAS)
    Z, Y, X = np.meshgrid(r.z_m, r.y_m, r.x_m, indexing='ij')
    lambda_3d = ((np.pi/p.longitud_x_m)**2 + (np.pi/p.longitud_y_m)**2
                 + (np.pi/p.longitud_z_m)**2)
    tasa = p.alpha_m2_s*lambda_3d

    #Solución exacta y error
    exacta = base+amplitud*forma(X, Y, Z)*np.exp(-tasa*p.tiempo_final_s)
    error = r.temperatura_C[-1]-exacta
    ix, iy, iz = p.celdas_x//2, p.celdas_y//2, p.celdas_z//2
    cortes = [
        (lambda T: T[iz, :, :], (0, p.longitud_x_m, 0, p.longitud_y_m), 'x [m]', 'y [m]', f'XY, z={r.z_m[iz]:.3g} m'),
        (lambda T: T[:, iy, :], (0, p.longitud_x_m, 0, p.longitud_z_m), 'x [m]', 'z [m]', f'XZ, y={r.y_m[iy]:.3g} m'),
        (lambda T: T[:, :, ix], (0, p.longitud_y_m, 0, p.longitud_z_m), 'y [m]', 'z [m]', f'YZ, x={r.x_m[ix]:.3g} m'),
    ]

    #Graficar resultados: cortes XY/XZ/YZ de temperatura inicial, final y error, y evolución de la zona central.
    fig = plt.figure(figsize=(14, 12), layout='constrained')
    grid = fig.add_gridspec(3, 3)
    for fila, (T, titulo) in enumerate(((r.temperatura_C[0], 'Inicio'),
                                      (r.temperatura_C[-1], f'Final: {p.tiempo_final_s/3600:g} h'))):
        for columna, (cortar, extent, xlabel, ylabel, plano) in enumerate(cortes):
            ax = fig.add_subplot(grid[fila, columna])
            im = ax.imshow(cortar(T), origin='lower', extent=extent, cmap='inferno',
                           vmin=min(base, base+amplitud), vmax=max(base, base+amplitud))
            ax.set(title=f'{titulo} · {plano}', xlabel=xlabel, ylabel=ylabel)
            fig.colorbar(im, ax=ax, label='Temperatura [°C]', shrink=0.85)
    ax = fig.add_subplot(grid[2, :2])
    centrales = tuple(sorted({(n-1)//2, n//2}) for n in p.forma_zyx)
    forma_central = forma(X, Y, Z)[np.ix_(*centrales)].mean()
    ax.plot(r.tiempos_historia_s/3600, r.temperatura_central_C, label='Numérica: centros más cercanos al centro')
    ax.plot(r.tiempos_historia_s/3600, base+amplitud*forma_central*np.exp(-tasa*r.tiempos_historia_s),
            '--', label='Exacta en los mismos centros')
    ax.set(title='Evolución de la zona central', xlabel='Tiempo [h]', ylabel='Temperatura [°C]')
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    ax = fig.add_subplot(grid[2, 2])
    limite = max(float(np.abs(error).max()), 1e-12)
    im = ax.imshow(error[iz], origin='lower', extent=cortes[0][1], cmap='RdBu_r', vmin=-limite, vmax=limite)
    ax.set(title='Error final numérico − exacto · XY', xlabel='x [m]', ylabel='y [m]')
    fig.colorbar(im, ax=ax, label='Diferencia [K]', shrink=0.85)
    fig.suptitle('Difusión 3D verificada · seis caras a temperatura fija · sin fuente', fontsize=15)
    salida = RAIZ/'resultados/3d/base/perfiles_temperatura.png'
    salida.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(salida, dpi=140)
    plt.close(fig)
    print(f'Malla: {p.celdas_x} x {p.celdas_y} x {p.celdas_z}; pasos: {r.n_pasos}; volúmenes guardados: {len(r.tiempos_s)}')
    print(f'dt={r.dt_s:.8g} s; dt máximo={r.dt_max_s:.8g} s; alpha={p.alpha_m2_s:.8g} m²/s')
    print(f'Centro inicial={r.temperatura_central_C[0]:.8f} °C; final={r.temperatura_central_C[-1]:.8f} °C')
    print(f'Error máximo absoluto final en todo el volumen={np.abs(error).max():.8g} K; PNG: {salida}')


if __name__ == '__main__':
    main()
