"""Muestra la secuencia constructiva y las caras expuestas en cada instante.

Papel en el proyecto: ejemplo ejecutable de la etapa correspondiente.
Recibe activacion.json; horarios [h] y T [°C] leídos del IFC.
Entrega estados, tres PNG y resumen_construccion.json.
Reutiliza mcplan.construccion y mcplan.superficies_voxel; no altera sus módulos ni el BIM.
Las salidas se guardan bajo resultados/e07; --solo-datos omite gráficos.
--solo-datos conserva la escritura del JSON del caso.
"""
import argparse
from dataclasses import asdict
import json
import os
from pathlib import Path
import sys

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(RAIZ/'desarrollo'))
os.environ.setdefault('MPLCONFIGDIR',str(RAIZ/'.venv/cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection,Line3DCollection
import numpy as np

from mcplan.bim import extraer_fundacion_ifc
from mcplan.voxel import voxelizar_fundacion
from mcplan.vertidas_voxel import asignar_vertidas
from mcplan.superficies_voxel import clasificar_caras
from mcplan.construccion import (preparar_construccion,iniciar_construccion,
                                avanzar_construccion,superficies_construidas)
from extraer_ifc import COLORES

SALIDA = RAIZ/'resultados/e07/activacion_temporal'


def titulo(e):
    return 'Antes de construir (t = −1 s)' if e.tiempo_s<0 else f't = {e.tiempo_s/3600:g} h'


def guardar(fig,nombre):
    """Recibe una figura Matplotlib y su nombre PNG; guarda en la carpeta fija de esta etapa.
    Solo cambia la salida gráfica del caso, no datos, geometría ni parámetros.
    """
    fig.savefig(SALIDA/nombre,dpi=130,bbox_inches='tight')
    plt.close(fig)
    print('Figura:',SALIDA/nombre)


def dibujar(estados,superficies):
    """Recibe los datos geométricos/constructivos del caso y genera las figuras descritas.
    La figura no modifica coordenadas ni estados del modelo. Si hay una vista
    separada, su desplazamiento es únicamente gráfico.
    Los ejes indican las unidades; las figuras no añaden una nueva simulación física.
    """
    g = estados[0].programa.asignacion_final.voxelizacion.grilla
    lo,hi = g.origen_m,g.limites_superiores_m
    final = clasificar_caras(estados[0].programa.asignacion_final).exteriores.vertices_m(g)
    columnas = 3
    filas = int(np.ceil(len(estados)/columnas))
    fig = plt.figure(figsize=(18,5*filas),layout='constrained')
    for i,(e,s) in enumerate(zip(estados,superficies),1):
        ax = fig.add_subplot(filas,columnas,i,projection='3d')
        ax.add_collection3d(Line3DCollection(final[:,[0,1,2,3,0]],colors='#999999',linewidths=.12,alpha=.12))
        caras = s.caras.exteriores
        if caras.cantidad:
            ax.add_collection3d(Poly3DCollection(caras.vertices_m(g),
                                facecolors=[COLORES[ident-1] for ident in caras.id_a],
                                edgecolors='#444444',linewidths=.12))
        ids = sorted(set(e.ids_activos.ravel())-{0})
        ax.set_title(f'{titulo(e)} · activas: '+(', '.join(f'{x:02d}' for x in ids) or 'ninguna')+
                     f'\n{int(e.activos.sum())} voxeles · V={e.activos.sum()*g.volumen_celda_m3:g} m³',fontsize=11)
        ax.set(xlim=(lo[0],hi[0]),ylim=(lo[1],hi[1]),zlim=(lo[2],hi[2]),
               xlabel='X [m]',ylabel='Y [m]',zlabel='Z [m]')
        ax.set_box_aspect(hi-lo)
        ax.view_init(elev=30,azim=-55)
    fig.legend(handles=[Patch(facecolor=c,label=f'Vertida {i:02d}') for i,c in enumerate(COLORES,1)],
               loc='lower center',ncol=5,bbox_to_anchor=(.5,-.02))
    fig.suptitle('E07 — Construcción progresiva · pasos XYZ = '+
                 ' × '.join(f'{d:g}' for d in g.pasos_m)+' m\n'+
                 'Gris tenue: geometría final prevista. Colores: vertidas construidas, no temperaturas.')
    guardar(fig,'secuencia_constructiva.png')

    x,y,z = tuple(o+np.arange(n+1)*d for o,n,d in zip(g.origen_m,g.forma_xyz,g.pasos_m))
    iy = int(np.argmin(abs(g.centros_xyz_m[1])))
    fig,axes = plt.subplots(filas,columnas,figsize=(18,3.5*filas),layout='constrained',squeeze=False)
    for ax,e,s in zip(axes.ravel(),estados,superficies):
        campo = e.ids_activos[:,iy,:].copy()
        campo[e.ocupacion_final[:,iy,:]&~e.activos[:,iy,:]] = -1
        ax.pcolormesh(x,z,campo,cmap=ListedColormap(['#e9e9e9','white',*COLORES]),
                      vmin=-1.5,vmax=5.5,edgecolors='#cccccc',linewidth=.12)
        for caras,mascara,color,ancho in (
                (s.caras.exteriores,~s.expuestas_a_no_colocado,'#bc6500',1.7),
                (s.caras.exteriores,s.expuestas_a_no_colocado,'#e60026',2.7),
                (s.caras.interfaces,np.ones(s.caras.interfaces.cantidad,dtype=bool),'#751a91',2.7)):
            centros = caras.centros_m(g)
            seleccion = mascara&(caras.celda_a_zyx[:,1]==iy)&(caras.normal_xyz[:,1]==0)
            for centro,normal in zip(centros[seleccion],caras.normal_xyz[seleccion]):
                mitad = np.array([0,g.pasos_m[2]/2]) if normal[0] else np.array([g.pasos_m[0]/2,0])
                segmento = np.array([centro[[0,2]]-mitad,centro[[0,2]]+mitad])
                ax.plot(segmento[:,0],segmento[:,1],color=color,linewidth=ancho)
        ax.set(title=titulo(e),xlabel='X [m]',ylabel='Z [m]',xlim=(lo[0],hi[0]),ylim=(lo[2],hi[2]))
        ax.set_aspect('equal')
    for ax in axes.ravel()[len(estados):]:
        ax.set_visible(False)
    fig.legend(handles=[Patch(facecolor='#e9e9e9',label='Previsto, aún no colocado'),
                        Line2D([],[],color='#bc6500',label='Expuesto a vacío final'),
                        Line2D([],[],color='#e60026',label='Expuesto hacia futura vertida'),
                        Line2D([],[],color='#751a91',label='Interfaz entre vertidas activas')],
               loc='lower center',ncol=2,bbox_to_anchor=(.5,-.05))
    fig.suptitle(f'Caras construidas en corte XZ, Y={g.centros_xyz_m[1][iy]:.3f} m\n'
                 'Expuesto no prescribe aire, suelo ni moldaje. Se omiten en el corte las caras normales a Y.')
    guardar(fig,'superficies_durante_construccion.png')

    tiempos = [e.tiempo_s/3600 for e in estados]
    fig,axes = plt.subplots(1,2,figsize=(14,5),layout='constrained')
    axes[0].step(tiempos,[e.activos.sum()*g.volumen_celda_m3 for e in estados],where='post',color='#235c8b')
    axes[0].plot(tiempos,[e.activos.sum()*g.volumen_celda_m3 for e in estados],'o',color='#235c8b')
    axes[0].set(xlabel='Tiempo desde primera colocación [h]',ylabel='Volumen construido voxelizado [m³]',title='La geometría se incorpora por eventos')
    for valores,nombre,color in (
            ([s.caras.exteriores.area_total_m2 for s in superficies],'Expuesto total','#bc6500'),
            ([s.caras.interfaces.area_total_m2 for s in superficies],'Interfaces activas','#751a91'),
            ([s.caras.exteriores.area_m2[s.expuestas_a_no_colocado].sum() for s in superficies],
             'Expuesto hacia futura vertida','#e60026')):
        axes[1].step(tiempos,valores,where='post',label=nombre,color=color)
        axes[1].plot(tiempos,valores,'o',color=color)
    axes[1].set(xlabel='Tiempo desde primera colocación [h]',ylabel='Área de caras de voxel [m²]',title='Exposición e interfaces cambian al colocar')
    axes[1].legend(fontsize=9)
    for ax in axes:ax.grid(alpha=.2)
    fig.suptitle('Estado constructivo sin difusión, hidratación ni enfriamiento\n'
                 'Áreas y volúmenes discretizados: la resolución no está certificada.')
    guardar(fig,'volumen_y_areas_construidas.png')


def main():
    """Lee los argumentos/configuración y ejecuta el caso con las unidades anteriores.
    No devuelve un resultado de API: imprime el resumen y guarda las salidas indicadas.
    Para reutilizar datos desde otro código, importar los módulos mcplan en vez de este main.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--parametros',type=Path,default=Path(__file__).with_name('activacion.json'))
    parser.add_argument('--solo-datos',action='store_true')
    args = parser.parse_args()
    config = json.loads(args.parametros.read_text(encoding='utf-8'))
    f = extraer_fundacion_ifc(RAIZ/config['archivo_ifc'])
    a = asignar_vertidas(f,voxelizar_fundacion(f,config['pasos_m'],origen_m=config['origen_m'],
                         tolerancia_m=config['tolerancia_m'],max_celdas=config['max_celdas']))
    programa = preparar_construccion(f,a)
    instantes = config['instantes_h']
    if not instantes or not all(isinstance(t,(int,float)) and not isinstance(t,bool) and np.isfinite(t) for t in instantes):
        raise ValueError('Declarar instantes horarios finitos.')
    if any(t*3600 < -1 for t in instantes) or any(b<=a for a,b in zip(instantes,instantes[1:])):
        raise ValueError('Los instantes deben aumentar y comenzar después o en t=-1 s.')
    if programa.ids_sin_voxeles:
        print('ADVERTENCIA: IDs sin voxeles:',programa.ids_sin_voxeles,'No se corrige la grilla.')
    e = iniciar_construccion(programa)
    estados,superficies,filas = [],[],[]
    for hora in instantes:
        e = avanzar_construccion(e,hora*3600)
        s = superficies_construidas(e)
        estados.append(e);superficies.append(s)
        fila = {'tiempo_h':hora,'ids_activos':sorted(int(i) for i in np.unique(e.ids_activos) if i),
                'voxeles_activos':int(e.activos.sum()),'voxeles_nuevos_desde_estado_anterior':int(e.nuevos.sum()),
                'volumen_construido_m3':float(e.activos.sum()*a.voxelizacion.grilla.volumen_celda_m3),
                'caras':{n:{'cantidad':getattr(s.caras,n).cantidad,'area_m2':getattr(s.caras,n).area_total_m2}
                         for n in ('exteriores','internas','interfaces')},
                'area_expuesta_hacia_no_colocado_m2':float(s.caras.exteriores.area_m2[s.expuestas_a_no_colocado].sum()),
                'contactos':[asdict(c) for c in s.caras.contactos_por_par],
                'edad_vertidas_h':{str(c.vertida_id):(e.tiempo_s-c.inicio_s)/3600
                                  for c in programa.colocaciones if c.inicio_s<=e.tiempo_s}}
        filas.append(fila)
        print(f't={hora:g} h | IDs={fila["ids_activos"]} | N={fila["voxeles_activos"]} | '
              f'V={fila["volumen_construido_m3"]:g} m3 | '
              f'expuesto={s.caras.exteriores.area_total_m2:g} m2 | interfaces={s.caras.interfaces.area_total_m2:g} m2')
    SALIDA.mkdir(parents=True,exist_ok=True)
    informe = {'sha256_ifc':f.sha256_ifc,'pasos_m':config['pasos_m'],'ids_sin_voxeles':programa.ids_sin_voxeles,
               'calendario':[asdict(c) for c in programa.colocaciones],
               'nota':'Solo activación y geometría. Temperaturas de colocación inicializadas, sin evolución térmica. M1 es etiqueta IFC.',
               'estados':filas}
    (SALIDA/'resumen_construccion.json').write_text(json.dumps(informe,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if not args.solo_datos:dibujar(estados,superficies)


if __name__=='__main__':
    main()
