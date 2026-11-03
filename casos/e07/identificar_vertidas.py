"""Compara IDs y volúmenes para tres resoluciones, sin modificar el IFC.

Papel en el proyecto: ejemplo ejecutable de la etapa correspondiente.
Recibe vertidas_volumenes.json y las cinco mallas.
Entrega tablas en m³/% y tres PNG comparativos.
Reutiliza mcplan.voxel y mcplan.vertidas_voxel; no altera sus módulos ni el BIM.
Las salidas se guardan bajo resultados/e07; --solo-datos omite gráficos.
En este caso las tablas solo se imprimen; no se guarda un JSON de volúmenes.
"""
import argparse
import json
import os
from pathlib import Path
import sys
from time import perf_counter

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(RAIZ/'desarrollo'))
os.environ.setdefault('MPLCONFIGDIR',str(RAIZ/'.venv/cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, to_rgba
from matplotlib.patches import Patch
import numpy as np

from mcplan.bim import extraer_fundacion_ifc
from mcplan.voxel import voxelizar_fundacion
from mcplan.vertidas_voxel import asignar_vertidas, comparar_volumenes, ConflictoGeometrico
from extraer_ifc import COLORES


def leyenda(fundacion):
    return [Patch(facecolor=c,edgecolor='#333333',label=f'{v.nombre} (ID {v.vertida_id})')
            for v,c in zip(sorted(fundacion.vertidas,key=lambda v:v.vertida_id),COLORES)]


def bordes(grilla):
    return tuple(o+np.arange(n+1)*d for o,n,d in zip(grilla.origen_m,grilla.forma_xyz,grilla.pasos_m))


def dibujar_voxeles(ax,a,separada=False):
    g = a.voxelizacion.grilla
    x,y,z = bordes(g)
    if not separada:
        paleta = np.array([to_rgba('white'), *[to_rgba(c) for c in COLORES]])
        ax.voxels(x[:,None,None],y[None,:,None],z[None,None,:],a.voxelizacion.ocupacion.transpose(2,1,0),
                   facecolors=paleta[a.vertida_id.transpose(2,1,0)],edgecolors='#333333',linewidth=.13,shade=True)
    else:
        for ident,color in enumerate(COLORES,1):
            mascara = a.vertida_id == ident
            posiciones = np.argwhere(mascara)
            if not len(posiciones):
                continue
            lo,hi = posiciones.min(axis=0),posiciones.max(axis=0)+1
            iz,iy,ix = [slice(int(l),int(h)) for l,h in zip(lo,hi)]
            xx,yy = x[ix.start:ix.stop+1],y[iy.start:iy.stop+1]
            zz = z[iz.start:iz.stop+1]+(ident-1)*3.
            ax.voxels(xx[:,None,None],yy[None,:,None],zz[None,None,:],mascara[iz,iy,ix].transpose(2,1,0),
                       facecolors=color,edgecolors='#333333',linewidth=.15,shade=True)
    alto = z[-1]+(12 if separada else 0)
    ax.set(xlim=(x[0],x[-1]),ylim=(y[0],y[-1]),zlim=(z[0],alto),
           xlabel='X del proyecto [m]',ylabel='Y del proyecto [m]',
           zlabel='Z gráfica [m]' if separada else 'Z [m]')
    ax.set_box_aspect((x[-1]-x[0],y[-1]-y[0],alto-z[0]))
    ax.view_init(elev=30,azim=-55)


def dibujar_corte(ax,a):
    x,y,z = bordes(a.voxelizacion.grilla)
    centros_y = a.voxelizacion.grilla.centros_xyz_m[1]
    iy = int(np.argmin(abs(centros_y)))
    ax.pcolormesh(x,z,a.vertida_id[:,iy,:],cmap=ListedColormap(['#F7F7F7',*COLORES]),
                   vmin=-.5,vmax=5.5,edgecolors='#BBBBBB',linewidth=.2)
    ax.set_aspect('equal')
    ax.set(xlabel='X del proyecto [m]',ylabel='Z [m]',title=f'Corte XZ, Y={centros_y[iy]:.6f} m; blanco=vacío')


def guardar(fig,nombre):
    """Recibe una figura Matplotlib y su nombre PNG; guarda en la carpeta fija de esta etapa.
    Solo cambia la salida gráfica del caso, no datos, geometría ni parámetros.
    """
    salida = RAIZ/'resultados/e07/vertidas_volumenes'/nombre
    salida.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(salida,dpi=130,bbox_inches='tight')
    plt.close(fig)
    print('Figura:',salida)


def graficar(fundacion,estudio,vista):
    """Recibe los datos geométricos/constructivos del caso y genera las figuras descritas.
    La figura no modifica coordenadas ni estados del modelo. Si hay una vista
    separada, su desplazamiento es únicamente gráfico.
    Los ejes indican las unidades; las figuras no añaden una nueva simulación física.
    """
    _,principal,_,_ = estudio[vista]
    fig = plt.figure(figsize=(15,11),layout='constrained')
    rejilla = fig.add_gridspec(2,2,height_ratios=[2.3,1.])
    a,b = fig.add_subplot(rejilla[0,0],projection='3d'),fig.add_subplot(rejilla[0,1],projection='3d')
    dibujar_voxeles(a,principal)
    dibujar_voxeles(b,principal,separada=True)
    a.set_title('Fundación voxelizada, un color por vertida')
    b.set_title('Vista separada: 3 m gráficos por nivel\nSin modificar grilla o IFC')
    dibujar_corte(fig.add_subplot(rejilla[1,:]),principal)
    fig.legend(handles=leyenda(fundacion),loc='lower center',ncol=3,bbox_to_anchor=(.5,-.05))
    fig.suptitle(f'E07 — Identificación de vertidas · h={vista:g} m\n'
                 'IDs geométricos 1–5; sin materiales, actividad o temperaturas por voxel',fontsize=13)
    guardar(fig,'vertidas_y_corte.png')

    fig = plt.figure(figsize=(18,9),layout='constrained')
    rejilla = fig.add_gridspec(2,len(estudio),height_ratios=[2.4,1.])
    for columna,(h,(r,a,filas,tiempo)) in enumerate(estudio.items()):
        ax = fig.add_subplot(rejilla[0,columna],projection='3d')
        dibujar_voxeles(ax,a)
        ax.set_title(f'h={h:g} m · N={r.numero_ocupados}\nV={r.volumen_ocupado_m3:g} m³; error global={100*abs(r.diferencia_volumen_m3)/r.volumen_referencia_mallas_m3:.3f} %')
        dibujar_corte(fig.add_subplot(rejilla[1,columna]),a)
    fig.legend(handles=leyenda(fundacion),loc='lower center',ncol=3,bbox_to_anchor=(.5,-.08))
    fig.suptitle('Comparación de resolución: misma geometría y origen IFC\n'
                 'Con h=1 m, la Vertida 02 no contiene centros de voxel',fontsize=13)
    guardar(fig,'comparacion_resoluciones.png')

    fig,ax = plt.subplots(1,2,figsize=(14,5),layout='constrained')
    hs = np.array(list(estudio))
    errores = [100*abs(r.diferencia_volumen_m3)/r.volumen_referencia_mallas_m3 for r,a,filas,t in estudio.values()]
    ax[0].plot(hs,errores,'ko-',label='Error global absoluto')
    for h,e,(r,_,_,_) in zip(hs,errores,estudio.values()):
        ax[0].annotate(f'{e:.3f}%\nΔV={r.diferencia_volumen_m3:+.3f} m³',(h,e),xytext=(5,10),textcoords='offset points',fontsize=9)
    for i,(v,color) in enumerate(zip(sorted(fundacion.vertidas,key=lambda v:v.vertida_id),COLORES)):
        ax[1].plot(hs,[datos[2][i].error_relativo_pct for datos in estudio.values()], 'o-',color=color,label=v.nombre)
    for a in ax:
        a.invert_xaxis()
        a.set_xticks(hs)
        a.set(xlabel='Tamaño de voxel h [m] (refinamiento hacia la derecha)',ylabel='Error relativo absoluto [%]')
        a.grid(alpha=.3)
    ax[0].set(title='Global: puede ocultar compensación entre vertidas')
    ax[0].margins(y=.3,x=.15)
    ax[1].set(title='Por vertida: comportamiento no monótono')
    ax[1].legend()
    fig.suptitle('Errores respecto de volúmenes de malla IFC, sin redondear la referencia',fontsize=13)
    guardar(fig,'errores_volumen.png')


def main():
    """Lee los argumentos/configuración y ejecuta el caso con las unidades anteriores.
    No devuelve un resultado de API: imprime el resumen y guarda las salidas indicadas.
    Para reutilizar datos desde otro código, importar los módulos mcplan en vez de este main.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--parametros',type=Path,default=Path(__file__).with_name('vertidas_volumenes.json'))
    parser.add_argument('--solo-datos',action='store_true',help='Tablas sin generar gráficos.')
    args = parser.parse_args()
    config = json.loads(args.parametros.read_text(encoding='utf-8'))
    fundacion = extraer_fundacion_ifc(RAIZ/config['archivo_ifc'])
    estudio = {}
    for h in config['resoluciones_m']:
        inicio = perf_counter()
        r = voxelizar_fundacion(fundacion,(h,)*3,origen_m=config['origen_m'],
                                tolerancia_m=config['tolerancia_m'],max_celdas=config['max_celdas'])
        try:
            a = asignar_vertidas(fundacion,r)
        except ConflictoGeometrico as error:
            print('CONFLICTO GEOMETRICO:',error)
            print(error.informe)
            raise
        filas = comparar_volumenes(fundacion,a)
        segundos = perf_counter()-inicio
        estudio[h] = (r,a,filas,segundos)
        print(f'\nh={h:g} m; grilla XYZ={r.grilla.forma_xyz}; total={r.grilla.numero_celdas}; '
              f'ocupados={r.numero_ocupados}; V={r.volumen_ocupado_m3:.6f} m3; '
              f'error global={100*abs(r.diferencia_volumen_m3)/r.volumen_referencia_mallas_m3:.6f}%; '
              f'tiempo geometrico={segundos:.4f} s')
        print('ID | N voxeles | V voxel [m3] | V IFC [m3] | diferencia absoluta [m3] | error [%]')
        for f in filas:
            print(f'{f.vertida_id} | {f.numero_voxeles} | {f.volumen_voxelizado_m3:.6f} | {f.volumen_ifc_m3:.6f} | '
                  f'{f.diferencia_absoluta_m3:.6f} | {f.error_relativo_pct:.6f}')
            if f.numero_voxeles == 0:
                print('  SIN CENTROS ASIGNADOS:',f.nombre,'a esta resolucion; la capa no esta resuelta.')
        print('Diagnostico:',a.informe)
        print('SUMAS:',sum(f.numero_voxeles for f in filas),'voxeles;',sum(f.volumen_voxelizado_m3 for f in filas),'m3')
    if not args.solo_datos:
        if config['resolucion_vista_m'] not in estudio:
            raise ValueError('resolucion_vista_m debe estar incluida en resoluciones_m.')
        graficar(fundacion,estudio,config['resolucion_vista_m'])


if __name__ == '__main__':
    main()
