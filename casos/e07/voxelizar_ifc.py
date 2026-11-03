"""Visualiza la primera ocupación por centros frente a la geometría IFC.

Papel en el proyecto: ejemplo ejecutable de la etapa correspondiente.
Recibe voxelizacion.json, pasos y tolerancia en m.
Entrega conteos y geometria_y_voxeles.png.
Reutiliza mcplan.bim y mcplan.voxel; no altera sus módulos ni el BIM.
Las salidas se guardan bajo resultados/e07; --solo-datos omite gráficos.
"""
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
from matplotlib.patches import Patch
from mpl_toolkits.mplot3d.art3d import Line3DCollection
import numpy as np

from mcplan.bim import extraer_fundacion_ifc
from mcplan.voxel import voxelizar_fundacion

AZUL, NARANJA = '#4477AA', '#EE7733'


def dibujar_voxelizacion(fundacion, resultado):
    """Recibe los datos geométricos/constructivos del caso y genera las figuras descritas.
    La figura no modifica coordenadas ni estados del modelo. Si hay una vista
    separada, su desplazamiento es únicamente gráfico.
    Los ejes indican las unidades; las figuras no añaden una nueva simulación física.
    """
    g = resultado.grilla
    fig = plt.figure(figsize=(15, 10), layout='constrained')
    espacio = fig.add_gridspec(2, 2, height_ratios=[2.3, 1.])
    original = fig.add_subplot(espacio[0, 0], projection='3d')
    voxeles = fig.add_subplot(espacio[0, 1], projection='3d')
    corte = fig.add_subplot(espacio[1, :])
    tri = np.concatenate([v.vertices_m[v.triangulos] for v in fundacion.vertidas])
    segmentos = np.stack([tri[:, [0,1]], tri[:, [1,2]], tri[:, [2,0]]], axis=1).reshape(-1,2,3)
    original.add_collection3d(Line3DCollection(segmentos, colors=AZUL, linewidths=.6, alpha=.85))
    bordes = tuple(o+np.arange(n+1)*d for o,n,d in zip(g.origen_m,g.forma_xyz,g.pasos_m))
    x,y,z = bordes
    voxeles.voxels(x[:,None,None], y[None,:,None], z[None,None,:],
                   resultado.ocupacion.transpose(2,1,0), facecolors=NARANJA,
                   edgecolors='#663311', linewidth=.16, shade=True)
    for a in (original,voxeles):
        a.set(xlim=(x[0],x[-1]),ylim=(y[0],y[-1]),zlim=(z[0],z[-1]),
               xlabel='X del proyecto [m]',ylabel='Y del proyecto [m]',zlabel='Z [m]')
        a.set_box_aspect(g.dimensiones_m)
        a.view_init(elev=30,azim=-55)
    original.set_title('Geometría IFC: aristas de los triángulos\nCoordenadas originales en metros',fontsize=11)
    voxeles.set_title(f'Ocupación por centros: {resultado.numero_ocupados:,} voxeles\n'
                      f'Volumen preliminar = {resultado.volumen_ocupado_m3:.3f} m³',fontsize=11)
    centros_y = g.centros_xyz_m[1]
    iy = int(np.argmin(np.abs(centros_y)))
    corte.pcolormesh(x,z,resultado.ocupacion[:,iy,:].astype(int),
                     cmap=ListedColormap(['#F7F7F7',NARANJA]),vmin=0,vmax=1,
                     edgecolors='#BBBBBB',linewidth=.3)
    corte.set_aspect('equal')
    corte.set(xlabel='X del proyecto [m]',ylabel='Z [m]',
               title=f'Corte XZ en centro Y={centros_y[iy]:.6f} m: ocupación y celdas vacías')
    corte.legend(handles=[Patch(facecolor=NARANJA,label='Celda ocupada'),
                           Patch(facecolor='#F7F7F7',edgecolor='#BBBBBB',label='Celda vacía')],
                  loc='upper right',fontsize=9)
    dx,dy,dz = g.pasos_m
    fig.suptitle(f'E07 — Primer voxelizador 3D de la fundación\n'
                  f'Δx={dx:g}, Δy={dy:g}, Δz={dz:g} m · grilla XYZ {g.forma_xyz} · '
                  f'tolerancia {resultado.tolerancia_m:g} m\n'
                  'Geometría y ocupación únicamente: sin vertida_id por voxel ni temperaturas',fontsize=13)
    salida = RAIZ/'resultados/e07/voxelizacion/geometria_y_voxeles.png'
    salida.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(salida,dpi=140,bbox_inches='tight')
    plt.close(fig)
    return salida


def main():
    """Lee los argumentos/configuración y ejecuta el caso con las unidades anteriores.
    No devuelve un resultado de API: imprime el resumen y guarda las salidas indicadas.
    Para reutilizar datos desde otro código, importar los módulos mcplan en vez de este main.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--parametros',type=Path,default=Path(__file__).with_name('voxelizacion.json'))
    parser.add_argument('--pasos',type=float,nargs=3,metavar=('DX','DY','DZ'),help='Resolución en metros.')
    parser.add_argument('--solo-datos',action='store_true',help='Calcular e imprimir sin dibujar.')
    args = parser.parse_args()
    entrada = json.loads(args.parametros.read_text(encoding='utf-8'))
    fundacion = extraer_fundacion_ifc(RAIZ/entrada['archivo_ifc'])
    r = voxelizar_fundacion(fundacion,args.pasos if args.pasos is not None else entrada['pasos_m'],
                            origen_m=entrada['origen_m'],tolerancia_m=entrada['tolerancia_m'],
                            max_celdas=entrada['max_celdas'])
    print('IFC SHA256:',r.sha256_ifc)
    print('Grilla XYZ:',r.grilla.forma_xyz,'| array ZYX:',r.grilla.forma_zyx)
    print('Origen XYZ [m]:',r.grilla.origen_m)
    print('Dimensiones grilla XYZ [m]:',r.grilla.dimensiones_m)
    print('Pasos dx/dy/dz [m]:',r.grilla.pasos_m)
    print('Voxeles totales:',r.grilla.numero_celdas,'| ocupados:',r.numero_ocupados,
          '| vacios:',r.grilla.numero_celdas-r.numero_ocupados)
    print('Centros dentro de tolerancia de alguna malla:',int(r.centros_sobre_malla.sum()))
    print(f'Volumen preliminar ocupado: {r.volumen_ocupado_m3:.9f} m3')
    print(f'Referencia suma mallas IFC: {r.volumen_referencia_mallas_m3:.9f} m3')
    print(f'Diferencia firmada: {r.diferencia_volumen_m3:+.9f} m3; '
          f'error relativo absoluto: {100*abs(r.diferencia_volumen_m3)/r.volumen_referencia_mallas_m3:.6f} %')
    if not args.solo_datos:
        print('Figura:',dibujar_voxelizacion(fundacion,r))


if __name__ == '__main__':
    main()
