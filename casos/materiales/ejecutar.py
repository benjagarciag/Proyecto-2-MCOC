"""Contacto de dos bloques: 2D, 3D, control homogéneo y solución estacionaria."""
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
from matplotlib.colors import ListedColormap
import numpy as np

from mcplan.bordes_termicos import Dirichlet, Neumann
from mcplan.difusion_2d import Parametros2D
from mcplan.difusion_3d import Parametros3D
from mcplan.difusion_bordes import resolver_2d_bordes, resolver_3d_bordes
from mcplan.materiales_termicos import materiales_desde_config


COLORES = ['#4C78A8', '#F58518']


def caras_adiabaticas(dim):
    return {f'{e}_{lado}': Neumann() for e in 'xyz'[:dim] for lado in ('min', 'max')}


def corte_xy(campo):
    return campo if campo.ndim == 2 else campo[campo.shape[0]//2]


def perfil_x(campo):
    return campo.mean(axis=tuple(range(campo.ndim-1)))


def interfaz(r, posicion):
    dx = r.coordenadas_m[0][1]-r.coordenadas_m[0][0]
    i = round(posicion/dx)-1
    Ti, Tj = r.temperatura_C[..., i], r.temperatura_C[..., i+1]
    ki, kj = r.materiales.k_W_mK[..., i], r.materiales.k_W_mK[..., i+1]
    q = (Ti-Tj)/(dx/2/ki+dx/2/kj)  # Positivo de izquierda a derecha.
    Tsi, Tsj = Ti-q*dx/2/ki, Tj+q*dx/2/kj
    ejes = tuple(range(1, q.ndim))
    return q.mean(axis=ejes), Tsi.mean(axis=ejes), Tsj.mean(axis=ejes)


def figura_transiente(dim, r, homogeneo, entrada):
    posicion = entrada['materiales']['interfaz_m']
    fig = plt.figure(figsize=(15, 9), layout='constrained')
    ax = [fig.add_subplot(2, 3, i+1, projection='3d' if dim == 3 and i == 0 else None) for i in range(6)]
    if dim == 2:
        ax[0].imshow(r.materiales.ids, origin='lower', extent=[0, 1, 0, 1],
                      cmap=ListedColormap(COLORES), vmin=0, vmax=1, interpolation='nearest')
        ax[0].axvline(posicion, color='k', linestyle='--')
        ax[0].set(xlabel='x [m]', ylabel='y [m]', title='Material A (azul) y B (naranja)')
    else:
        ax[0].bar3d(0, 0, 0, posicion, 1, 1, color=COLORES[0], alpha=.45, edgecolor='k', linewidth=.4)
        ax[0].bar3d(posicion, 0, 0, 1-posicion, 1, 1, color=COLORES[1], alpha=.45, edgecolor='k', linewidth=.4)
        ax[0].set(xlabel='x [m]', ylabel='y [m]', zlabel='z [m]', title=f'Dos bloques, interfaz x={posicion:g} m')
        ax[0].view_init(elev=22, azim=-55)
    vmin, vmax = r.temperatura_C.min(), r.temperatura_C.max()
    for a, campo, titulo in ((ax[1], r.temperatura_C[0], 'Temperatura inicial'),
                              (ax[2], r.temperatura_C[-1], f'Temperatura a {r.tiempos_s[-1]/3600:g} h')):
        im = a.imshow(corte_xy(campo), origin='lower', extent=[0, 1, 0, 1],
                       vmin=vmin, vmax=vmax, cmap='inferno', interpolation='nearest')
        a.axvline(posicion, color='cyan', linestyle='--', label='Interfaz')
        a.set(title=titulo+(' (corte XY)' if dim == 3 else ''), xlabel='x [m]', ylabel='y [m]')
        fig.colorbar(im, ax=a, label='Temperatura [°C]', shrink=.8)
    x = r.coordenadas_m[0]
    q, Tsi, Tsj = interfaz(r, posicion)
    for i in (0, len(r.tiempos_s)//2, len(r.tiempos_s)-1):
        ax[3].plot(x, perfil_x(r.temperatura_C[i]), label=f'Dos materiales, {r.tiempos_s[i]/3600:.1f} h')
    ax[3].plot(homogeneo.coordenadas_m[0], perfil_x(homogeneo.temperatura_C[-1]), 'k--', label='Solo material A, final')
    ax[3].plot(posicion, Tsi[-1], 'ro', label='T superficial común, final')
    ax[3].axvline(posicion, color='gray', linestyle=':')
    ax[3].set(xlabel='x [m]', ylabel='Temperatura [°C]', title='Perfil normal a la interfaz')
    ax[3].legend(fontsize=8)
    media_aritmetica = r.temperatura_C.reshape(len(r.tiempos_s), -1).mean(axis=1)
    media_energetica = r.energia_relativa_J/r.capacidad_J_K.sum()
    ax[4].plot(r.tiempos_s/3600, media_aritmetica, 'o-', label='Dos materiales: media aritmética')
    ax[4].plot(r.tiempos_historia_s/3600, media_energetica, label='Dos materiales: media ponderada C')
    ax[4].plot(homogeneo.tiempos_historia_s/3600, homogeneo.energia_relativa_J/homogeneo.capacidad_J_K.sum(), 'k--', label='Solo A: media ponderada C')
    ax[4].set(xlabel='Tiempo [h]', ylabel='Temperatura [°C]', title='Energía conservada: ponderar por C')
    ax[4].legend(fontsize=8)
    ax[5].plot(r.tiempos_s/3600, q, 'o-')
    residuo = np.max(np.abs(r.energia_relativa_J-r.energia_relativa_J[0]))
    ax[5].set(xlabel='Tiempo [h]', ylabel='Flujo hacia +x [W/m²]', title='Flujo compartido en la interfaz')
    ax[5].text(.04, .86, f'Máximo |ΔE|: {residuo:.2g} J\nContacto: |Ts,A−Ts,B| ≤ {np.max(abs(Tsi-Tsj)):.2g} K',
               transform=ax[5].transAxes, fontsize=9)
    for a in ax[3:]:
        a.grid(alpha=.25)
    fig.suptitle(f'{dim}D: contacto térmico perfecto, exterior adiabático\nPropiedades didácticas; comparación homogénea con todo el dominio de material A', fontsize=13)
    guardar(fig, f'{dim}d')
    print(f'{dim}D: dt={r.dt_s:.8g} s / máximo {r.dt_max_s:.8g} s; '
          f'pasos={r.n_pasos}; equilibrio energético={media_energetica[0]:.8f} C; '
          f'flujo final interfaz={q[-1]:.8f} W/m²; Ts={Tsi[-1]:.8f} C; '
          f'conservación |Delta E| máx={residuo:.3g} J')


def guardar(fig, caso):
    salida = RAIZ/'resultados/materiales'/caso/'perfiles_temperatura.png'
    salida.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(salida, dpi=140)
    plt.close(fig)
    print(f'Figura: {salida}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--parametros', type=Path, default=Path(__file__).with_name('parametros.json'))
    parser.add_argument('--celdas', type=int, help='Celdas por eje (interfaz debe coincidir con una cara).')
    parser.add_argument('--dt', type=float, help='Paso propuesto [s].')
    args = parser.parse_args()
    entrada = json.loads(args.parametros.read_text(encoding='utf-8'))
    if entrada['materiales']['eje'] != 'x':
        raise ValueError('Este ejecutor ilustra un plano normal a x; la API también admite y/z.')
    posicion = entrada['materiales']['interfaz_m']
    izquierda, derecha = entrada['temperatura_izquierda_C'], entrada['temperatura_derecha_C']
    figura, ax = plt.subplots(2, 2, figsize=(12, 9), layout='constrained')
    for fila, dim in enumerate((2, 3)):
        n = args.celdas if args.celdas is not None else entrada[f'celdas_{dim}d']
        valores = dict(celdas_x=n, celdas_y=n, tiempo_final_s=entrada['tiempo_final_s'],
                       paso_tiempo_s=args.dt, **entrada['materiales']['materiales'][0])
        if dim == 2:
            p, solver = Parametros2D(**valores), resolver_2d_bordes
        else:
            p, solver = Parametros3D(celdas_z=n, **valores), resolver_3d_bordes
        m = materiales_desde_config(entrada['materiales'], p)
        b = caras_adiabaticas(dim)
        inicial = lambda *xyz: np.where(xyz[0] < posicion, izquierda, derecha)
        r = solver(p, b, inicial, n_guardados=13, materiales=m)
        homogeneo = solver(p, b, inicial, n_guardados=13)
        figura_transiente(dim, r, homogeneo, entrada)
        # Verificación estacionaria independiente: fronteras Dirichlet en x,
        # inicialización con solución matemática exacta, otras caras adiabáticas.
        b.update(x_min=Dirichlet(izquierda), x_max=Dirichlet(derecha))
        k0, k1 = m.material_0.conductividad_W_mK, m.material_1.conductividad_W_mK
        q_exacta = (izquierda-derecha)/(posicion/k0+(1-posicion)/k1)
        Tf = izquierda-q_exacta*posicion/k0
        def exacta(*xyz):
            x = xyz[0]
            return np.where(x < posicion, izquierda-q_exacta*x/k0, Tf-q_exacta*(x-posicion)/k1)
        s = solver(p, b, exacta, n_guardados=2, materiales=m)
        x = s.coordenadas_m[0]
        ax[fila, 0].plot([0, posicion, 1], [izquierda, Tf, derecha], label='Solución exacta, dos materiales')
        ax[fila, 0].plot(x, perfil_x(s.temperatura_C[-1]), '.', label='Solver al final')
        ax[fila, 0].plot([0, 1], [izquierda, derecha], 'k--', label='Homogéneo: solución exacta')
        ax[fila, 0].axvline(posicion, color='gray', linestyle=':')
        ax[fila, 0].set(title=f'{dim}D: perfil estacionario (iniciado exacto)', xlabel='x [m]', ylabel='Temperatura [°C]')
        ax[fila, 0].legend(fontsize=8)
        dx = 1/n
        k = s.materiales.k_W_mK
        T = s.temperatura_C[-1]
        q_cara = (T[..., :-1]-T[..., 1:])/(dx/2/k[..., :-1]+dx/2/k[..., 1:])
        ax[fila, 1].plot(np.arange(1, n)/n, perfil_x(q_cara), 'o', label='Flujo del solver')
        ax[fila, 1].axhline(q_exacta, label='Flujo exacto, dos materiales')
        ax[fila, 1].axhline(k0*(izquierda-derecha), color='k', linestyle='--', label='Homogéneo: flujo exacto')
        ax[fila, 1].axvline(posicion, color='gray', linestyle=':')
        ax[fila, 1].set(title=f'Continuidad del flujo: {q_exacta:g} W/m²', xlabel='Posición de cara x [m]', ylabel='Flujo hacia +x [W/m²]')
        ax[fila, 1].legend(fontsize=8)
        print(f'{dim}D estacionario: q exacta={q_exacta:.8f} W/m²; T interfaz={Tf:.8f} C; '
              f'error T final={np.max(np.abs(s.temperatura_C[-1]-s.temperatura_C[0])):.3g} K; '
              f'error flujo={np.max(np.abs(q_cara-q_exacta)):.3g} W/m²')
    for a in ax.flat:
        a.grid(alpha=.25)
    figura.suptitle('Verificación de interfaz: cambia la pendiente, el flujo permanece continuo\nContacto perfecto, sin fuente; comparación con solución homogénea', fontsize=13)
    guardar(figura, 'verificacion_interfaz')


if __name__ == '__main__':
    main()
