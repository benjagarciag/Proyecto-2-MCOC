"""Compara cronogramas a12 °C sin extracción, con colocación progresiva por estratos."""
import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace

import sin_extraccion_12c as base

PLANES = dict(unica='unica', rapida='separacion_3h', referencia='separacion_6h', lenta='separacion_9h')


def guardar(ruta, d):
    with ruta.open('x', encoding='utf-8') as archivo:
        json.dump(d, archivo, ensure_ascii=False, indent=2, allow_nan=False)


def comprobar_plan(d, plan):
    base.validar(d)
    assert d['grupos_de_activacion'], 'Se requiere activación por estratos.'
    assert d['estudio_planes']['parametros']['plan'] == plan
    assert all(g['finish_h'] >= g['start_h'] for g in d['grupos_de_activacion'])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ejecutar', action='store_true')
    p.add_argument('--comprobar-insumos', action='store_true')
    p.add_argument('--planes', nargs='+', choices=PLANES, default=['unica', 'rapida'])
    p.add_argument('--lado', type=float, choices=(.5, .25), default=.5)
    p.add_argument('--paso-max', type=int, choices=(900, 450), default=900)
    p.add_argument('--salida', type=Path, default=base.viento.RAIZ/'resultados/planes_sin_extraccion')
    args = p.parse_args()
    print('Planes:', args.planes, 'a12 °C, sin extracción y con activación progresiva.')
    print('Retiro de aislación a240/480 h de edad por estrato; madera a72 h.')
    print('24 escenarios por plan; 336/600 h, ampliables a672 h si hay alerta.')
    if not (args.ejecutar or args.comprobar_insumos):
        print('Sin simulaciones. Usar --comprobar-insumos o --ejecutar.')
        return
    base.viento._preparacion.preparar()
    meta, series, _ = base.viento.analizar(2., .14)
    insumos, motor, _, hashes = base.cargar_motor({c:s['h_W_m2K'] for c,s in series.items()})
    controles = insumos.importar_solver('exportada')[0]
    assert controles.VARIANTES['retiro_escalonado'] == (-6, .04, (240, 360))
    controles.VARIANTES['retiro_escalonado'] = (-6, .04, (240, 480))
    datos = insumos.leer(insumos.RAIZ/insumos.leer(insumos.CONFIG)['base'])
    ids, _ = insumos.leer_malla(controles, datos, args.lado, 'exportada')
    materiales = controles.materiales(datos, insumos.HIDRATACION/'manifiesto.json')
    climas = insumos.leer(insumos.CONFIG)['historias']
    pares = sorted((m['id'], c['id']) for m in materiales for c in climas)
    assert len(pares) == 24
    cfg = deepcopy(insumos.leer(insumos.CONFIGURACIONES))
    planes_originales = {p['plan']:p['vertidas'] for p in insumos.leer(insumos.RESULTADOS_LUIS/'curvas_reales/resumen.json')['planes']}
    for alias in dict.fromkeys(args.planes):
        plan = PLANES[alias]
        cronograma = planes_originales[plan]
        mascara = (ids > 0).astype(int) if plan == 'unica' else ids
        grupos, horarios, detalle = motor.allocate(mascara, cronograma, True)
        assert detalle and (grupos > 0).sum() == (ids > 0).sum()
        print(alias, ':', len(cronograma), 'vertida(s),', len(detalle),
              'estratos; D=', round(max(v['fin_h'] for v in cronograma), 3), 'h.')
    if args.comprobar_insumos:
        print('Geometría, cronogramas y activación comprobados. Sin simulaciones.')
        return
    tabla = []
    for alias in dict.fromkeys(args.planes):
        nombre = f'{alias}_12c_estratos_sin_extraccion'
        parametros = dict(plan=PLANES[alias], estratos=True, edad_inicio_h=6, temperatura_C=12)
        cfg['experimentos'][nombre] = parametros
        procedencia = dict(modelo_viento=meta, **hashes, parametros=parametros,
            retiros_aislacion_edad_h=[240, 480], espesor_por_capa_m=.04,
            retiro_moldaje_edad_h=72, referencia_edad='activación de cada estrato',
            enfriamiento_activo=False, lado_m=args.lado, paso_max_s=args.paso_max,
            script_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
        destino = args.salida/alias/f'malla_{args.lado:g}_paso{args.paso_max}'
        destino.mkdir(parents=True, exist_ok=True)
        ruta = destino/f'{nombre}.json'
        if ruta.exists():
            d = base.viento.leer(ruta)
            if d.get('estudio_planes') != procedencia:
                raise ValueError('Procedencia distinta; usar otra --salida.')
            comprobar_plan(d, PLANES[alias])
            base.comun.validar_filas(d['corridas'])
            print('Matriz conservada:', ruta)
        else:
            piezas = []
            for curva, clima in pares:
                individual = destino/f'{nombre}_{curva}_{clima}.json'
                if not individual.exists():
                    motor.ejecutar(SimpleNamespace(experimento=nombre, salida=destino,
                        modo='completo', escenario=[curva, clima], geometria='exportada',
                        lado=args.lado, paso_max=args.paso_max, traza=True), cfg)
                    d = base.viento.leer(individual)
                    d['estudio_planes'] = procedencia
                    comprobar_plan(d, PLANES[alias])
                    individual.write_text(json.dumps(d, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
                d = base.viento.leer(individual)
                if d.get('estudio_planes') != procedencia:
                    raise ValueError('Procedencia distinta: '+str(individual))
                comprobar_plan(d, PLANES[alias])
                piezas.append(d)
            filas = [f for d in piezas for f in d['corridas']]
            base.comun.validar_filas(filas)
            d = dict(piezas[0])
            d.update(corridas=filas, riesgo=controles.riesgo(filas),
                riesgo_336=controles.riesgo([dict(f['base_336h'], peso=f['peso'], clima=f['clima']) for f in filas]),
                sensibilidades_pesos={c:controles.riesgo(filas,c) for c in series},
                horizontes_h=sorted({f['horizonte_h'] for f in filas}),
                picos_no_resueltos=sum(f['pico_no_resuelto'] for f in filas),
                duracion_auditoria_s=sum(x['duracion_auditoria_s'] for x in piezas))
            guardar(ruta, d)
        filas = d['corridas']
        tabla.append(dict(plan=alias, D_h=d['D_h'],
            Tmax_C=max(f['Tmax']['valor'] for f in filas),
            DeltaTmax_K=max(f['DeltaTmax']['valor'] for f in filas),
            **d['riesgo'], alertas=d['picos_no_resueltos']))
        base.viento.csv_guardar(destino/'resumen.csv', [tabla[-1]])
        print('Plan completo:', alias, tabla[-1])
    # El nombre explicita qué subconjunto fue solicitado; no borra otra comparación.
    base.viento.csv_guardar(args.salida/('comparacion_'+'_'.join(dict.fromkeys(args.planes))+'.csv'), tabla)
    print('Comparación finalizada:', args.salida)


if __name__ == '__main__':
    main()
