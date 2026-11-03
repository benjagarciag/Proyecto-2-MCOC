"""Lee y muestra las cinco mallas IFC sin crear voxeles.

Papel en el proyecto: ejemplo ejecutable de la etapa correspondiente.
Recibe ruta IFC por CLI.
Entrega resumen y geometria_ifc.png.
Reutiliza mcplan.bim; no altera sus módulos ni el BIM.
Las salidas se guardan bajo resultados/e07; --solo-datos omite gráficos.
"""
import argparse
import os
from pathlib import Path
import sys

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ/'desarrollo'))
os.environ.setdefault('MPLCONFIGDIR', str(RAIZ/'.venv/cache/matplotlib'))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
import numpy as np

from mcplan.bim import extraer_fundacion_ifc

COLORES = ['#4477AA', '#EE7733', '#228833', '#AA3377', '#CCBB44']


def dibujar_geometria(fundacion):
    """Dibuja las caras extraídas; separar la vista no modifica sus datos.

    Recibe los datos geométricos/constructivos del caso y genera las figuras descritas.
    La figura no modifica coordenadas ni estados del modelo. Si hay una vista
    separada, su desplazamiento es únicamente gráfico.
    Los ejes indican las unidades; las figuras no añaden una nueva simulación física.
    """
    fig = plt.figure(figsize=(15, 8), layout='constrained')
    minimo, maximo = fundacion.bbox_min_m, fundacion.bbox_max_m
    for numero, separacion in enumerate((0., 3.), start=1):
        ax = fig.add_subplot(1, 2, numero, projection='3d')
        triangulos_vista, colores_vista = [], []
        for i, (v, color) in enumerate(zip(fundacion.vertidas, COLORES)):
            vertices_vista = v.vertices_m+np.array([0., 0., i*separacion])
            triangulos_vista.extend(vertices_vista[v.triangulos])
            colores_vista.extend([color]*len(v.triangulos))
        if not separacion:
            # Las superficies de contacto se superponen en el ensamblaje.
            # Mostrar sus aristas evita falsas oclusiones del painter de mplot3d.
            tri = np.asarray(triangulos_vista)
            segmentos = np.stack([tri[:, [0, 1]], tri[:, [1, 2]], tri[:, [2, 0]]], axis=1).reshape(-1, 2, 3)
            ax.add_collection3d(Line3DCollection(segmentos, colors=np.repeat(colores_vista, 3), linewidths=.6, alpha=.85))
        else:
            caras = Poly3DCollection(triangulos_vista, facecolors=colores_vista,
                                     edgecolors='#333333', linewidths=.22, alpha=1.)
            ax.add_collection3d(caras)
        alto = maximo[2]+(len(fundacion.vertidas)-1)*separacion
        ax.set(xlim=(minimo[0]-1, maximo[0]+1), ylim=(minimo[1]-1, maximo[1]+1),
               zlim=(minimo[2], alto+.5), xlabel='X del proyecto [m]', ylabel='Y del proyecto [m]',
               zlabel='Z [m]' if not separacion else 'Z desplazada solo para mostrar piezas [m]')
        ax.set_box_aspect((fundacion.dimensiones_m[0], fundacion.dimensiones_m[1], alto-minimo[2]))
        ax.view_init(elev=35, azim=-55)
        ax.set_title('Malla IFC ensamblada: aristas de los triángulos\nCoordenadas originales, sin desplazamiento' if not separacion
                     else 'Vista separada para identificar las cinco vertidas\nSeparación gráfica de 3 m entre piezas; IFC intacto', fontsize=11)
    leyenda = [Patch(facecolor=c, edgecolor='#333333', label=f'{v.nombre}: {v.volumen_m3:.3f} m³')
                for v, c in zip(fundacion.vertidas, COLORES)]
    fig.legend(handles=leyenda, loc='lower center', ncol=3, fontsize=10, bbox_to_anchor=(.5, -.10))
    fig.suptitle('E07 — Extracción geométrica real del IFC (sin grilla ni simulación térmica)\n'
                 f'{len(fundacion.vertidas)} vertidas · suma de volúmenes {fundacion.volumen_total_mallas_m3:.3f} m³ · '
                 f'IFC SHA256 {fundacion.sha256_ifc[:12]}', fontsize=13)
    salida = RAIZ/'resultados/e07/extraccion_ifc/geometria_ifc.png'
    salida.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(salida, dpi=150, bbox_inches='tight', pad_inches=.2)
    plt.close(fig)
    return salida


def main():
    """Lee los argumentos/configuración y ejecuta el caso con las unidades anteriores.
    No devuelve un resultado de API: imprime el resumen y guarda las salidas indicadas.
    Para reutilizar datos desde otro código, importar los módulos mcplan en vez de este main.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ifc', type=Path, default=RAIZ/'desarrollo/fundacion/fundacion.ifc')
    parser.add_argument('--solo-datos', action='store_true', help='Imprimir resumen sin guardar gráfico.')
    args = parser.parse_args()
    modelo = extraer_fundacion_ifc(args.ifc)
    print('IFC:', modelo.ruta)
    print('SHA256:', modelo.sha256_ifc)
    print('Schema/unidad/escala:', modelo.schema, modelo.unidad_longitud_ifc, modelo.escala_longitud_ifc_a_m)
    print('Coordenadas:', modelo.sistema_coordenadas)
    for v in modelo.vertidas:
        print(f'{v.nombre} | ID={v.vertida_id} | GUID={v.guid} | inicio={v.inicio_h:g} h ({v.inicio_s:g} s) '
              f'| Tcol={v.temperatura_colocacion_C:g} C | volumen={v.volumen_m3:.9f} m3 '
              f'| triangulos={v.calidad.numero_triangulos}')
        print('  BBox [m]:', v.bbox_min_m.round(6), 'a', v.bbox_max_m.round(6))
        print('  Materiales IFC:', v.materiales_asociados, '| TipoHormigon:', v.tipo_hormigon)
    print(f'Suma de volumenes de malla: {modelo.volumen_total_mallas_m3:.9f} m3')
    for aviso in modelo.advertencias:
        print('AVISO:', aviso)
    if not args.solo_datos:
        print('Figura:', dibujar_geometria(modelo))


if __name__ == '__main__':
    main()
