"""Cuatro ejemplos de bordes, una figura fija por caso; sin fuentes internas."""
import argparse
import json
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

from mcplan.bordes_termicos import Dirichlet, Neumann, Robin
from mcplan.difusion_2d import Parametros2D
from mcplan.difusion_3d import Parametros3D
from mcplan.difusion_bordes import resolver_2d_bordes, resolver_3d_bordes


def leer_bordes(entrada):
    clases = {'dirichlet': Dirichlet, 'neumann': Neumann, 'robin': Robin}
    return {cara: clases[b['tipo']](**{k: v for k, v in b.items() if k != 'tipo'})
            for cara, b in entrada.items()}


def graficar(nombre, r, C):
    T = r.temperatura_C
    dim = T.ndim-1
    fig, ax = plt.subplots(2, 3, figsize=(15, 9), layout='constrained')
    horas = r.tiempos_s/3600
    if dim == 2:
        indices = (0, len(T)//2, len(T)-1)
        paneles = [(T[i], f't = {horas[i]:.2f} h', 'x [m]', 'y [m]') for i in indices]
    else:
        iz, iy = T.shape[1]//2, T.shape[2]//2
        z, y = r.coordenadas_m[2][iz], r.coordenadas_m[1][iy]
        paneles = [(T[0, iz], f'XY inicial, z={z:.2f} m', 'x [m]', 'y [m]'),
                   (T[-1, iz], f'XY a {horas[-1]:.1f} h, z={z:.2f} m', 'x [m]', 'y [m]'),
                   (T[-1, :, iy, :], f'XZ a {horas[-1]:.1f} h, y={y:.2f} m', 'x [m]', 'z [m]')]
    minimo, maximo = float(T.min()), float(T.max())
    # Mostrar ambiente 20°C en la escala de los enfriamientos.
    if 'robin' in nombre:
        minimo = min(minimo, *(b.ambiente_C for b in r.bordes.values() if isinstance(b, Robin)))
    for a, (campo, titulo, xlabel, ylabel) in zip(ax[0], paneles):
        im = a.imshow(campo, origin='lower', extent=[0, 1, 0, 1],
                      vmin=minimo, vmax=maximo, cmap='inferno', interpolation='nearest')
        a.set(title=titulo, xlabel=xlabel, ylabel=ylabel)
    fig.colorbar(im, ax=list(ax[0]), label='Temperatura [°C]', shrink=.85)
    planos = T.reshape(len(T), -1)
    ax[1, 0].plot(horas, planos.mean(axis=1), 'o-', label='Media')
    ax[1, 0].plot(horas, planos.max(axis=1), '.--', label='Máxima')
    ax[1, 0].plot(horas, planos.min(axis=1), '.--', label='Mínima')
    volumen = T[0].size
    if nombre == '3d_neumann':
        media_exacta = planos[0].mean()+r.potencia_exterior_W[0]*r.tiempos_s/(C*volumen)
        ax[1, 0].plot(horas, media_exacta, 'k:', label='Media exacta por energía')
    ax[1, 0].set(xlabel='Tiempo [h]', ylabel='Temperatura [°C]', title='Evolución en todo el dominio')
    ax[1, 0].legend()
    th = r.tiempos_historia_s/3600
    ax[1, 1].plot(th, r.potencia_exterior_W)
    ax[1, 1].set(xlabel='Tiempo [h]', ylabel='Potencia entrante [W]', title='Fronteras: positivo calienta')
    ax[1, 1].axhline(0, color='gray', linewidth=.7)
    calor = np.r_[0., np.cumsum(r.potencia_exterior_W[:-1]*r.dt_s)]
    delta_E = r.energia_relativa_J-r.energia_relativa_J[0]
    escala = 1. if nombre == '2d_adiabatico' else 1e6
    unidad = 'J' if escala == 1 else 'MJ'
    ax[1, 2].plot(th, delta_E/escala, label='Cambio de energía')
    ax[1, 2].plot(th, calor/escala, '--', label='Calor exterior acumulado')
    ax[1, 2].set(xlabel='Tiempo [h]', ylabel=f'Energía [{unidad}]', title='Balance: ΔE = calor entrante')
    if nombre == '2d_adiabatico' and np.max(np.abs(delta_E)) < 1:
        ax[1, 2].set_ylim(-1, 1)
        ax[1, 2].text(.03, .05, f'Redondeo máximo: {np.max(np.abs(delta_E)):.2g} J', transform=ax[1, 2].transAxes)
    ax[1, 2].legend()
    for a in ax[1]:
        a.grid(alpha=.3)
    etiquetas = {
        '2d_adiabatico': '2D adiabático: redistribuye calor y conserva energía',
        '2d_robin': '2D Robin: cuatro caras convectivas',
        '3d_neumann': '3D Neumann: flujos impuestos por cara',
        '3d_robin': '3D Robin: seis caras convectivas'}
    if 'robin' in nombre:
        h = sorted({b.h_W_m2K for b in r.bordes.values() if isinstance(b, Robin)})
        ambiente = sorted({b.ambiente_C for b in r.bordes.values() if isinstance(b, Robin)})
        h_texto, ambiente_texto = ', '.join(f'{v:g}' for v in h), ', '.join(f'{v:g}' for v in ambiente)
        etiquetas[nombre] += f'; h={h_texto} W/(m²·K), ambiente={ambiente_texto} °C'
    if nombre == '3d_neumann':
        etiquetas[nombre] += f'; x_min={r.bordes["x_min"].flujo_entrante_W_m2:g} W/m² entrantes'
    fig.suptitle(etiquetas[nombre]+'\nMaterial didáctico homogéneo, dominio 1 m por dirección', fontsize=13)
    salida = RAIZ/'resultados/bordes'/nombre/'perfiles_temperatura.png'
    salida.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(salida, dpi=140)
    plt.close(fig)
    residual = np.max(np.abs(delta_E-calor))
    print(f'{nombre}: pasos={r.n_pasos}, dt={r.dt_s:.8g} s, máximo={r.dt_max_s:.8g} s; '
          f'Tmedia {planos[0].mean():.8f} -> {planos[-1].mean():.8f} °C; '
          f'Delta E={delta_E[-1]:.8g} J; residuo balance={residual:.3g} J')
    print(f'  Figura: {salida}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--parametros', type=Path, default=Path(__file__).with_name('parametros.json'))
    parser.add_argument('--caso', choices=('todos', '2d_adiabatico', '2d_robin', '3d_neumann', '3d_robin'), default='todos')
    parser.add_argument('--dt', type=float, help='Paso propuesto [s]; se rechaza si excede el límite estable.')
    parser.add_argument('--celdas', type=int, help='Número de celdas por dirección.')
    args = parser.parse_args()
    entrada = json.loads(args.parametros.read_text(encoding='utf-8'))
    for nombre, config in entrada['casos'].items():
        if args.caso != 'todos' and nombre != args.caso:
            continue
        dim, n = config['dimension'], args.celdas if args.celdas is not None else config['celdas']
        valores = dict(celdas_x=n, celdas_y=n, tiempo_final_s=config['tiempo_final_s'],
                       paso_tiempo_s=args.dt, **entrada['material'])
        if dim == 2:
            p, solver = Parametros2D(**valores), resolver_2d_bordes
            C = p.capacidad_celda_J_K
        else:
            p, solver = Parametros3D(celdas_z=n, **valores), resolver_3d_bordes
            C = p.capacidad_voxel_J_K
        inicial = config['temperatura_inicial_C']
        if config['inicial'] == 'coseno':
            inicial = lambda X, Y: config['temperatura_inicial_C']+config['amplitud_K']*np.cos(np.pi*X)*np.cos(np.pi*Y)
        elif config['inicial'] != 'uniforme':
            raise ValueError('Inicial debe ser uniforme o coseno.')
        r = solver(p, leer_bordes(config['bordes']), inicial)
        graficar(nombre, r, C)


if __name__ == '__main__':
    main()
