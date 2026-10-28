"""Generación uniforme, localizada y con Robin: compara 2D y 3D."""
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
from mcplan.fuentes_volumetricas import fuente_desde_config


def bordes_desde_json(entrada):
    clases = {'dirichlet': Dirichlet, 'neumann': Neumann, 'robin': Robin}
    return {cara: clases[b['tipo']](**{k: v for k, v in b.items() if k != 'tipo'})
            for cara, b in entrada.items()}


def dibujar_fila(ax, dim, r, limites_T):
    campos = r.temperatura_C
    fuente = r.fuente_W_m3
    if dim == 3:
        iz = campos.shape[1]//2
        final, fuente = campos[-1, iz], fuente[iz]
        etiqueta = f'3D: corte XY, z={r.coordenadas_m[2][iz]:.3g} m'
    else:
        final, etiqueta = campos[-1], '2D: placa, espesor 1 m'
    im = ax[0].imshow(fuente, origin='lower', extent=[0, 1, 0, 1], cmap='magma', vmin=0,
                      vmax=max(1., r.fuente_W_m3.max()), interpolation='nearest')
    ax[0].figure.colorbar(im, ax=ax[0], label="q''' promedio [W/m³]", shrink=.8)
    ax[0].set(title=etiqueta+'\nGeneración interna', xlabel='x [m]', ylabel='y [m]')
    vmin, vmax = limites_T
    im = ax[1].imshow(final, origin='lower', extent=[0, 1, 0, 1], cmap='inferno',
                      vmin=vmin, vmax=vmax, interpolation='nearest')
    ax[1].figure.colorbar(im, ax=ax[1], label='Temperatura [°C]', shrink=.8)
    ax[1].set(title=f'Temperatura a {r.tiempos_s[-1]/3600:g} h', xlabel='x [m]', ylabel='y [m]')
    aplanados = campos.reshape(len(campos), -1)
    horas = r.tiempos_s/3600
    ax[2].plot(horas, aplanados.mean(axis=1), 'o-', label='Media')
    ax[2].plot(horas, aplanados.max(axis=1), '.--', label='Máxima')
    ax[2].plot(horas, aplanados.min(axis=1), '.--', label='Mínima')
    C = r.parametros.densidad_kg_m3*r.parametros.calor_especifico_J_kgK
    # Volumen total 1 m³ en estos ejemplos 2D (e=1) y 3D.
    todos_adiabaticos = all(isinstance(b, Neumann) and b.flujo_entrante_W_m2 == 0
                            for b in r.bordes.values())
    if todos_adiabaticos:
        exacta_media = aplanados[0].mean()+r.potencia_generada_W*r.tiempos_s/C
        ax[2].plot(horas, exacta_media, 'k:', label='Media exacta por balance')
    ax[2].set(title='Evolución del dominio completo', xlabel='Tiempo [h]', ylabel='Temperatura [°C]')
    ax[2].legend(fontsize=8)
    ax[2].grid(alpha=.25)
    t = r.tiempos_historia_s
    generada = r.potencia_generada_W*t
    exterior = np.r_[0., np.cumsum(r.dt_s*r.potencia_exterior_W[:-1])]
    neta = generada+exterior
    delta_E = r.energia_relativa_J-r.energia_relativa_J[0]
    ax[3].plot(t/3600, delta_E/1e6, label='Cambio de energía')
    ax[3].plot(t/3600, neta/1e6, '--', label='Generación + calor exterior')
    ax[3].plot(t/3600, generada/1e6, ':', label='Solo generación')
    ax[3].plot(t/3600, exterior/1e6, '-.', label='Solo calor exterior')
    ax[3].set(title='Balance energético', xlabel='Tiempo [h]', ylabel='Energía [MJ]')
    ax[3].legend(fontsize=8)
    ax[3].grid(alpha=.25)
    residuo = np.max(np.abs(delta_E-neta))
    print(f'{dim}D: potencia generada={r.potencia_generada_W:.8g} W; '
          f'Tmedia={aplanados[-1].mean():.8f} C; Tmax={aplanados[-1].max():.8f} C; '
          f'dt={r.dt_s:.8g}/{r.dt_max_s:.8g} s; residuo={residuo:.3g} J')
    print(f'  Generada={generada[-1]/1e6:.8f} MJ; exterior={exterior[-1]/1e6:.8f} MJ; '
          f'Delta E={delta_E[-1]/1e6:.8f} MJ')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--parametros', type=Path, default=Path(__file__).with_name('parametros.json'))
    parser.add_argument('--caso', choices=('todos', 'uniforme', 'localizada', 'robin'), default='todos')
    parser.add_argument('--celdas', type=int, help='Celdas por eje, en ambos solvers.')
    parser.add_argument('--dt', type=float, help='Paso propuesto [s].')
    args = parser.parse_args()
    entrada = json.loads(args.parametros.read_text(encoding='utf-8'))
    titulos = {'uniforme': 'Fuente uniforme y superficies adiabáticas',
               'localizada': 'Fuente localizada y superficies adiabáticas',
               'robin': 'Fuente uniforme y convección Robin'}
    for nombre, config in entrada['ejemplos'].items():
        if args.caso != 'todos' and args.caso != nombre:
            continue
        fig, ax = plt.subplots(2, 4, figsize=(19, 9), layout='constrained')
        print(nombre)
        resultados = []
        for dim in (2, 3):
            n = args.celdas if args.celdas is not None else entrada[f'celdas_{dim}d']
            valores = dict(celdas_x=n, celdas_y=n, tiempo_final_s=entrada['tiempo_final_s'],
                           paso_tiempo_s=args.dt, **entrada['material'])
            if dim == 2:
                p, solver = Parametros2D(**valores), resolver_2d_bordes
            else:
                p, solver = Parametros3D(celdas_z=n, **valores), resolver_3d_bordes
            fuente = fuente_desde_config(config[f'fuente_{dim}d'], p)
            bordes = bordes_desde_json(config[f'bordes_{dim}d'])
            r = solver(p, bordes, entrada['temperatura_inicial_C'], n_guardados=13, fuente_W_m3=fuente)
            resultados.append(r)
        minimo = min(float(r.temperatura_C.min()) for r in resultados)
        maximo = max(float(r.temperatura_C.max()) for r in resultados)
        limites_T = (minimo, max(maximo, minimo+1.))
        for fila, (dim, r) in enumerate(zip((2, 3), resultados)):
            dibujar_fila(ax[fila], dim, r, limites_T)
        fig.suptitle(titulos[nombre]+'\nEjemplos constantes didácticos, lados de 1 m; no son un modelo calibrado de hidratación', fontsize=14)
        salida = RAIZ/'resultados/fuentes'/nombre/'perfiles_temperatura.png'
        salida.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(salida, dpi=130)
        plt.close(fig)
        print(f'Figura: {salida}')


if __name__ == '__main__':
    main()
