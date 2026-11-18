"""Planes con colocación uniforme a 12 °C; apertura sin cálculo y salidas propias."""
import json
import argparse
from pathlib import Path
import sys

import controles_obra


def comprobar(configuracion):
    """Comprueba los cuatro cronogramas sin la restricción de única del estudio original."""
    p=argparse.ArgumentParser()
    p.add_argument('--comprobar-insumos',action='store_true')
    p.add_argument('--ejecutar',action='store_true')
    p.add_argument('--resumir',action='store_true')
    p.add_argument('--casos',nargs='+',choices=configuracion['casos'],default=list(configuracion['casos']))
    p.add_argument('--lado',type=float,choices=(.5,.25),default=.5)
    p.add_argument('--paso-max',type=int,choices=(900,450),default=900)
    p.add_argument('--salida',type=Path)
    args=p.parse_args()
    from conductividad import revisar_base, ruta_base
    import viento
    viento._preparacion.preparar()
    meta,series,_=viento.analizar(2.,.14)
    insumos,_,_,hashes=viento.cargar_motor({c:s['h_W_m2K'] for c,s in series.items()})
    revisar_base(ruta_base(args.lado,args.paso_max),meta,hashes,args.lado,args.paso_max)
    controles,*_=insumos.importar_solver('exportada')
    base=insumos.leer(insumos.RAIZ/insumos.leer(insumos.CONFIG)['base'])
    ids,_=insumos.leer_malla(controles,base,args.lado,'exportada')
    planes={p['plan']:p['vertidas'] for p in insumos.leer(insumos.RESULTADOS_LUIS/'curvas_reales/resumen.json')['planes']}
    for nombre in args.casos:
        c=configuracion['casos'][nombre]
        assert c['plan'] in planes and c['temperatura_C']==12 and c['tope_W']==15000 and c['edad_inicio_h']==6
        print(nombre,':',len(planes[c['plan']]),'vertida(s), todas a 12 °C.')
    print('Configuraciones, referencias y máscara',ids.shape,'comprobadas. Sin simulaciones.')


if __name__ == '__main__':
    configuracion=json.loads(Path(__file__).with_suffix('.json').read_text(encoding='utf-8'))
    if any(c['temperatura_C']!=configuracion['temperatura_colocacion_C'] for c in configuracion['casos'].values()):
        raise ValueError('Todos los planes deben conservar 12 °C en sus vertidas.')
    controles_obra.CASOS=configuracion['casos']
    if '--comprobar-insumos' in sys.argv:
        comprobar(configuracion)
        sys.exit(0)
    # Solo adapta la etiqueta de consola del ejecutor original, que nació
    # para la única. El cálculo y las configuraciones se mantienen explícitos.
    def mostrar(*valores,**opciones):
        if valores and str(valores[0]).startswith('Única con h horario'):
            valores=('Planes a 12 °C con h horario, suelo 15 °C/R0 y k=2. Mantas/retiros sin cambios.',)+valores[1:]
        print(*valores,**opciones)
    controles_obra.print=mostrar
    # La tabla compara cada plan con la única anterior a 12,231833 °C;
    # los cambios por par incluyen también cronograma si se elige otro plan.
    # Los parámetros efectivos de cada plan se guardan completos en sus JSON.
    if not any(a=='--salida' or a.startswith('--salida=') for a in sys.argv[1:]):
        sys.argv.extend(['--salida',str(controles_obra.RAIZ/'resultados/controles_12c')])
    controles_obra.main()
