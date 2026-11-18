"""Temperatura10 °C y aislación escalonada sin extracción; cálculo solo con --ejecutar."""
import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace

import sin_extraccion_12c as base

CONFIG = Path(__file__).with_suffix('.json')


def validar(d, temperatura, procedencia):
    assert d['enfriamiento']['activo'] is False and d['enfriamiento']['tope_W'] == 0
    assert all(v['colocacion_C'] == temperatura for v in d['plan'])
    assert d['grupos_de_activacion']
    if d.get('estudio_pasivo') != procedencia:
        raise ValueError('Procedencia distinta; elegir otra --salida.')
    for f in d['corridas']:
        for m in (f, f['base_336h']):
            assert m['balance_J'].get('enfriamiento', 0) == 0
            assert m['balance_J'].get('enfriamiento_pico_W', 0) == 0


def escribir(ruta, d):
    with ruta.open('x', encoding='utf-8') as archivo:
        json.dump(d, archivo, ensure_ascii=False, indent=2, allow_nan=False)


def main():
    config = base.viento.leer(CONFIG)
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ejecutar', action='store_true')
    p.add_argument('--comprobar-insumos', action='store_true')
    p.add_argument('--casos', nargs='+', choices=config['casos'], default=list(config['casos']))
    p.add_argument('--lado', type=float, choices=(.5, .25), default=.5)
    p.add_argument('--paso-max', type=int, choices=(900, 450), default=900)
    p.add_argument('--salida', type=Path, default=base.viento.RAIZ/'resultados/controles_pasivos')
    args = p.parse_args()
    for caso in dict.fromkeys(args.casos):
        c = config['casos'][caso]
        assert c['temperatura_C'] in (10,12)
        assert c['retiros_h'] == sorted(set(c['retiros_h'])) and max(c['retiros_h']) <= 480
        print(caso, c, '; capas de40 mm, sin extracción interna.')
    print('Única progresiva, madera18 mm hasta72 h; base y suelo conservados.')
    print('24 escenarios por caso; 336/600 h, ampliables a672 h si hay alerta.')
    if not (args.ejecutar or args.comprobar_insumos):
        print('Sin simulaciones. Usar --comprobar-insumos o --ejecutar.')
        return
    base.viento._preparacion.preparar()
    meta, series, _ = base.viento.analizar(2., .14)
    insumos, motor, _, hashes = base.cargar_motor({c:s['h_W_m2K'] for c,s in series.items()})
    controles = insumos.importar_solver('exportada')[0]
    assert controles.VARIANTES['retiro_escalonado'] == (-6,.04,(240,360))
    datos = insumos.leer(insumos.RAIZ/insumos.leer(insumos.CONFIG)['base'])
    ids, _ = insumos.leer_malla(controles, datos, args.lado, 'exportada')
    cfg = deepcopy(insumos.leer(insumos.CONFIGURACIONES))
    materiales = controles.materiales(datos, insumos.HIDRATACION/'manifiesto.json')
    climas = insumos.leer(insumos.CONFIG)['historias']
    pares = sorted((m['id'], c['id']) for m in materiales for c in climas)
    assert len(pares) == 24
    Capa = controles.Capa
    for caso in dict.fromkeys(args.casos):
        c = config['casos'][caso]
        capas = tuple(Capa(config['espesor_por_capa_m'],.042,h) for h in c['retiros_h'])
        assert sum(x.espesor_m for x in capas) > 0
    if args.comprobar_insumos:
        print('Máscara', ids.shape, ', fuentes, clima y capas comprobadas. Sin simulaciones.')
        return
    tabla = []
    for caso in dict.fromkeys(args.casos):
        c = config['casos'][caso]
        controles.VARIANTES['retiro_escalonado'] = (-6,config['espesor_por_capa_m'],tuple(c['retiros_h']))
        parametros = dict(plan='unica', estratos=True, edad_inicio_h=6, temperatura_C=c['temperatura_C'])
        cfg['experimentos'][caso] = parametros
        procedencia = dict(modelo_viento=meta, **hashes, parametros=parametros,
            retiros_aislacion_edad_h=c['retiros_h'], espesor_por_capa_m=config['espesor_por_capa_m'],
            madera_m=.018, retiro_madera_edad_h=72, enfriamiento_activo=False,
            referencia_edad='activación de cada estrato', lado_m=args.lado, paso_max_s=args.paso_max,
            script_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
            configuracion_sha256=sha256(CONFIG.read_bytes()).hexdigest())
        destino = args.salida/caso/f'malla_{args.lado:g}_paso{args.paso_max}'
        destino.mkdir(parents=True, exist_ok=True)
        ruta = destino/f'{caso}.json'
        if ruta.exists():
            d = base.viento.leer(ruta)
            validar(d,c['temperatura_C'],procedencia)
            base.comun.validar_filas(d['corridas'])
            print('Matriz conservada:', ruta)
        else:
            piezas = []
            for curva, clima in pares:
                individual = destino/f'{caso}_{curva}_{clima}.json'
                if not individual.exists():
                    motor.ejecutar(SimpleNamespace(experimento=caso, salida=destino,
                        modo='completo', escenario=[curva,clima], geometria='exportada',
                        lado=args.lado, paso_max=args.paso_max, traza=True),cfg)
                    d = base.viento.leer(individual)
                    d['estudio_pasivo'] = procedencia
                    validar(d,c['temperatura_C'],procedencia)
                    individual.write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
                d = base.viento.leer(individual)
                validar(d,c['temperatura_C'],procedencia)
                piezas.append(d)
            filas = [f for d in piezas for f in d['corridas']]
            base.comun.validar_filas(filas)
            d = dict(piezas[0])
            d.update(corridas=filas,riesgo=controles.riesgo(filas),
                riesgo_336=controles.riesgo([dict(f['base_336h'],peso=f['peso'],clima=f['clima']) for f in filas]),
                sensibilidades_pesos={c:controles.riesgo(filas,c) for c in series},
                horizontes_h=sorted({f['horizonte_h'] for f in filas}),
                picos_no_resueltos=sum(f['pico_no_resuelto'] for f in filas),
                duracion_auditoria_s=sum(x['duracion_auditoria_s'] for x in piezas))
            escribir(ruta,d)
        filas = d['corridas']
        tabla.append(dict(caso=caso,temperatura_C=c['temperatura_C'],capas=len(c['retiros_h']),
            Tmax_C=max(f['Tmax']['valor'] for f in filas),DeltaTmax_K=max(f['DeltaTmax']['valor'] for f in filas),
            **d['riesgo'],alertas=d['picos_no_resueltos']))
        base.viento.csv_guardar(destino/'resumen.csv',[tabla[-1]])
        print('Caso terminado:',caso,tabla[-1])
    base.viento.csv_guardar(args.salida/('comparacion_'+'_'.join(dict.fromkeys(args.casos))+'.csv'),tabla)
    print('Estudio terminado:',args.salida)


if __name__ == '__main__':
    main()
