"""Calcula superficies geométricas y contactos de la fundación completa.

Papel en el proyecto: ejemplo ejecutable de la etapa correspondiente.
Recibe superficies.json, pasos en m y pares esperados.
Entrega áreas en m², dos PNG y areas_superficies.json.
Reutiliza mcplan.superficies_voxel; no altera sus módulos ni el BIM.
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
sys.path.insert(0, str(RAIZ/'desarrollo'))
os.environ.setdefault('MPLCONFIGDIR', str(RAIZ/'.venv/cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Patch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
import numpy as np

from mcplan.bim import extraer_fundacion_ifc
from mcplan.voxel import voxelizar_fundacion
from mcplan.vertidas_voxel import asignar_vertidas
from mcplan.superficies_voxel import clasificar_caras, diagnosticar_contactos

SALIDA = RAIZ/'resultados/e07/superficies'
PARES = {(1,2): '#377eb8', (2,3): '#e41a1c', (3,4): '#4daf4a',
         (4,5): '#984ea3', (1,3): '#ff7f00'}


def preparar_3d(ax, g):
    lo, hi = g.origen_m, g.limites_superiores_m
    ax.set(xlim=(lo[0],hi[0]), ylim=(lo[1],hi[1]), zlim=(lo[2],hi[2]),
           xlabel='X [m]', ylabel='Y [m]', zlabel='Z [m]')
    ax.set_box_aspect(hi-lo)
    ax.view_init(elev=28, azim=-55)


def quads(ax, vertices, colores, alpha=1, aristas='#555555', ancho=.15):
    ax.add_collection3d(Poly3DCollection(vertices, facecolors=colores,
                       edgecolors=aristas, linewidths=ancho, alpha=alpha))


def guardar(fig, nombre):
    """Recibe una figura Matplotlib y su nombre PNG; guarda en la carpeta fija de esta etapa.
    Solo cambia la salida gráfica del caso, no datos, geometría ni parámetros.
    """
    fig.savefig(SALIDA/nombre, dpi=140, bbox_inches='tight')
    plt.close(fig)
    print('Figura:', SALIDA/nombre)


def graficar(s, h):
    """Recibe los datos geométricos/constructivos del caso y genera las figuras descritas.
    La figura no modifica coordenadas ni estados del modelo. Si hay una vista
    separada, su desplazamiento es únicamente gráfico.
    Los ejes indican las unidades; las figuras no añaden una nueva simulación física.
    """
    g = s.asignacion.voxelizacion.grilla
    iy = int(np.argmin(abs(g.centros_xyz_m[1])))
    y = g.centros_xyz_m[1][iy]
    exterior = s.exteriores.vertices_m(g)
    fig = plt.figure(figsize=(14,10), layout='constrained')
    rejilla = fig.add_gridspec(2,1, height_ratios=[2,1])
    ax = fig.add_subplot(rejilla[0], projection='3d')
    preparar_3d(ax,g)
    quads(ax,exterior,'#ed9b40')
    ax.set_title(f'Exterior del modelo completo: {s.exteriores.cantidad} caras · '
                 f'{s.exteriores.area_total_m2:g} m²')
    ax = fig.add_subplot(rejilla[1])
    for caras, color, ancho, nombre in (
            (s.internas,'#8798a5',.7,'Interna: misma vertida'),
            (s.exteriores,'#d67800',2,'Exterior: hormigón–vacío'),
            (s.interfaces,'#ab1598',2.5,'Interfaz: distinta vertida')):
        centros = caras.centros_m(g)
        seleccion = (caras.celda_a_zyx[:,1]==iy)&(caras.normal_xyz[:,1]==0)
        segmentos = []
        for centro, normal in zip(centros[seleccion],caras.normal_xyz[seleccion]):
            # Caras X: segmento vertical; caras Z: segmento horizontal.
            mitad = np.array([0,g.pasos_m[2]/2]) if normal[0] else np.array([g.pasos_m[0]/2,0])
            punto = centro[[0,2]]
            segmentos.append([punto-mitad,punto+mitad])
        ax.add_collection(LineCollection(segmentos,colors=color,linewidths=ancho,label=nombre))
    ax.autoscale()
    ax.set_aspect('equal')
    ax.set(xlabel='X [m]', ylabel='Z [m]', title=f'Corte XZ en Y={y:.3f} m; sin caras perpendiculares a Y')
    ax.legend(loc='upper right', fontsize=9)
    fig.suptitle(f'E07 · Superficies geométricas · h={h:g} m\n'
                 'No representan todavía exposición al ambiente durante la construcción')
    guardar(fig,'superficies_exteriores_y_corte.png')

    fig = plt.figure(figsize=(15,7), layout='constrained')
    ax = fig.add_subplot(121,projection='3d')
    preparar_3d(ax,g)
    aristas = exterior[:,[0,1,2,3,0],:]
    ax.add_collection3d(Line3DCollection(aristas,colors='#999999',linewidths=.15,alpha=.15))
    pares = np.sort(np.column_stack([s.interfaces.id_a,s.interfaces.id_b]),axis=1)
    colores = [PARES.get(tuple(p),'#333333') for p in pares]
    quads(ax,s.interfaces.vertices_m(g),colores,aristas='#333333',ancho=.1)
    ax.set_title(f'Interfaces: {s.interfaces.cantidad} caras · {s.interfaces.area_total_m2:g} m²')
    leyenda = [Patch(facecolor=PARES.get(c.par,'#333333'),
                     label=f'{c.par[0]:02d}–{c.par[1]:02d}: {c.area_m2:g} m²')
               for c in s.contactos_por_par]
    ax.legend(handles=leyenda,loc='upper left',fontsize=9)
    ax = fig.add_subplot(122,projection='3d')
    preparar_3d(ax,g)
    seleccion = (s.internas.celda_a_zyx[:,1]==iy)&(s.internas.normal_xyz[:,1]==0)
    quads(ax,s.internas.vertices_m(g)[seleccion],'#80b1d3',alpha=.6,aristas='#235478',ancho=.5)
    ax.set_title(f'Caras internas: muestra en franja Y={y:.3f} m\n'
                 f'{seleccion.sum()} mostradas de {s.internas.cantidad} clasificadas')
    fig.suptitle('Contactos únicos, sin duplicar A–B y B–A\n'
                 'Coordenadas originales, sin separar vertidas ni modificar el IFC')
    guardar(fig,'interfaces_y_caras_internas.png')


def main():
    """Lee los argumentos/configuración y ejecuta el caso con las unidades anteriores.
    No devuelve un resultado de API: imprime el resumen y guarda las salidas indicadas.
    Para reutilizar datos desde otro código, importar los módulos mcplan en vez de este main.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,default=Path(__file__).with_name('superficies.json'))
    parser.add_argument('--solo-datos',action='store_true')
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding='utf-8'))
    fundacion = extraer_fundacion_ifc(RAIZ/config['archivo_ifc'])
    SALIDA.mkdir(parents=True,exist_ok=True)
    tablas = []
    for h in config['resoluciones_m']:
        voxel = voxelizar_fundacion(fundacion,(h,h,h),origen_m=config['origen_m'],
                                   tolerancia_m=config['tolerancia_m'],max_celdas=config['max_celdas'])
        superficies = clasificar_caras(asignar_vertidas(fundacion,voxel))
        diagnostico = diagnosticar_contactos(superficies,[v.vertida_id for v in fundacion.vertidas],
                                             config['contactos_ifc_esperados'])
        fila = {'h_m':h,'voxeles_ocupados':voxel.numero_ocupados,
                'categorias':{nombre:{'caras':getattr(superficies,nombre).cantidad,
                                      'area_m2':getattr(superficies,nombre).area_total_m2}
                              for nombre in ('exteriores','internas','interfaces')},
                'exterior_por_direccion':superficies.exterior_por_direccion,
                'contactos':[asdict(c) for c in superficies.contactos_por_par],
                'diagnostico':asdict(diagnostico)}
        tablas.append(fila)
        print(json.dumps(fila,ensure_ascii=False,indent=2))
        if not args.solo_datos and h==config['resolucion_vista_m']:
            graficar(superficies,h)
    informe = {'sha256_ifc':fundacion.sha256_ifc,
               'referencia_contactos_explicita':config['contactos_ifc_esperados'],
               'nota':'Áreas de caras de voxel; no superficies CAD exactas ni exposición temporal.',
               'resoluciones':tablas}
    (SALIDA/'areas_superficies.json').write_text(json.dumps(informe,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    main()
