"""Única a 12 °C sin sumidero interno; solo --ejecutar inicia el cálculo."""
import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from types import ModuleType, SimpleNamespace

import conductividad as comun
import viento

NOMBRE = 'unica_12c_sin_extraccion'


def cargar_motor(series):
    insumos, _, solver, hashes = viento.cargar_motor(series)
    ruta = viento.COPIA / 'casos/f02_verificaciones/ejecutar.py'
    fuente = ruta.read_text(encoding='utf-8')
    inicio = fuente.index('    cooling = Cooling(')
    fin = fuente.index('    if side == reference["lado_m"]:', inicio)
    fuente = fuente[:inicio] + '    cooling = None\n' + fuente[fin:]
    fuente = viento.cambiar(fuente,
        'air[:hours+1], base["nucleo_xyz_m"], enfriamiento=cooling)',
        'air[:hours+1], base["nucleo_xyz_m"], enfriamiento=None, h_aire_horario_W_m2K=SERIES_H[weather["id"]][:hours+1])')
    fuente = viento.cambiar(fuente, '        final = solve(horizon)', '''        final = solve(horizon)
        while (controls.alertas_cola(final, horizon, duration, cfg['inicio_tardio_edad_min_h'])
               and horizon < cfg['extension_max_h']):
            horizon = min(horizon + 72, cfg['extension_max_h'])
            final = solve(horizon)''')
    fuente = viento.cambiar(fuente,
        '        assert 0 <= final.balance_J["enfriamiento_pico_W"] <= cooling.tope_W',
        '        assert final.balance_J.get("enfriamiento_pico_W", 0) == 0\n'
        '        assert final.balance_J.get("enfriamiento", 0) == 0')
    inicio = fuente.index('        enfriamiento=dict(')
    fin = fuente.index('        clima_sha256=', inicio)
    fuente = (fuente[:inicio] + '        enfriamiento=dict(activo=False, U_W_m3K=0, tope_W=0),\n'
              + fuente[fin:])
    motor = ModuleType('f02_sin_extraccion')
    motor.__file__ = str(ruta)
    motor.SERIES_H = series
    exec(compile(fuente, str(ruta), 'exec'), motor.__dict__)
    hashes['ejecutor_sin_extraccion_sha256'] = sha256(fuente.encode()).hexdigest()
    return insumos, motor, solver, hashes


def validar(d):
    assert d['enfriamiento']['activo'] is False
    assert d['enfriamiento']['tope_W'] == 0
    assert all(v['colocacion_C'] == 12 for v in d['plan'])
    for f in d['corridas']:
        for metricas in (f, f['base_336h']):
            assert metricas['balance_J'].get('enfriamiento', 0) == 0
            assert metricas['balance_J'].get('enfriamiento_pico_W', 0) == 0


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ejecutar', action='store_true')
    p.add_argument('--comprobar-insumos', action='store_true')
    p.add_argument('--lado', type=float, choices=(.5, .25), default=.5)
    p.add_argument('--paso-max', type=int, choices=(900, 450), default=900)
    p.add_argument('--salida', type=Path, default=viento.RAIZ/'resultados/sin_extraccion_12c')
    args = p.parse_args()
    print('Única a 12 °C, sin extracción interna; h horario y protecciones anteriores.')
    print('24 pares, 336/600 h y extensión hasta 672 h si hay alerta.')
    if not (args.ejecutar or args.comprobar_insumos):
        print('Sin simulaciones. Usar --comprobar-insumos o --ejecutar.')
        return
    viento._preparacion.preparar()
    meta, series, _ = viento.analizar(2., .14)
    insumos, motor, solver, hashes = cargar_motor({c:s['h_W_m2K'] for c,s in series.items()})
    controles, _, _, _, _, _ = insumos.importar_solver('exportada')
    datos = insumos.leer(insumos.RAIZ/insumos.leer(insumos.CONFIG)['base'])
    ids, _ = insumos.leer_malla(controles, datos, args.lado, 'exportada')
    cfg = deepcopy(insumos.leer(insumos.CONFIGURACIONES))
    cfg['experimentos'][NOMBRE] = dict(plan='unica', edad_inicio_h=6, temperatura_C=12)
    # edad_inicio_h solo sirve a la selección del comparador histórico;
    # la adaptación pasa None y no habilita ningún enfriamiento.
    materiales = controles.materiales(datos, insumos.HIDRATACION/'manifiesto.json')
    climas = insumos.leer(insumos.CONFIG)['historias']
    pares = sorted((m['id'], c['id']) for m in materiales for c in climas)
    assert len(pares) == 24
    if args.comprobar_insumos:
        print('Adaptación compilada, 8 fuentes/3 climas y máscara', ids.shape,
              'comprobadas. Enfriamiento=None; sin simulaciones.')
        return
    destino = args.salida/f'malla_{args.lado:g}_paso{args.paso_max}'
    procedencia = dict(modelo_viento=meta, **hashes, temperatura_C=12,
        enfriamiento_activo=False, lado_m=args.lado, paso_max_s=args.paso_max,
        script_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        configuracion_experimento=cfg['experimentos'][NOMBRE], trazas=True)
    destino.mkdir(parents=True, exist_ok=True)
    ruta = destino/f'{NOMBRE}.json'
    if ruta.exists():
        d = viento.leer(ruta)
        if d.get('estudio_sin_extraccion') != procedencia:
            raise ValueError('Procedencia distinta; elegir otra --salida.')
        validar(d)
        comun.validar_filas(d['corridas'])
        print('Matriz existente conservada:', ruta)
        return
    piezas = []
    for curva, clima in pares:
        individual = destino/f'{NOMBRE}_{curva}_{clima}.json'
        if not individual.exists():
            motor.ejecutar(SimpleNamespace(experimento=NOMBRE, salida=destino,
                modo='completo', escenario=[curva, clima], geometria='exportada',
                lado=args.lado, paso_max=args.paso_max, traza=True), cfg)
            d = viento.leer(individual)
            validar(d)
            d['estudio_sin_extraccion'] = procedencia
            individual.write_text(json.dumps(d, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
        d = viento.leer(individual)
        if d.get('estudio_sin_extraccion') != procedencia:
            raise ValueError('Procedencia distinta: '+str(individual))
        validar(d)
        piezas.append(d)
    filas = [f for d in piezas for f in d['corridas']]
    comun.validar_filas(filas)
    d = dict(piezas[0])
    d.update(corridas=filas, riesgo=controles.riesgo(filas),
        riesgo_336=controles.riesgo([dict(f['base_336h'], peso=f['peso'], clima=f['clima']) for f in filas]),
        sensibilidades_pesos={c:controles.riesgo(filas,c) for c in series},
        horizontes_h=sorted({f['horizonte_h'] for f in filas}),
        picos_no_resueltos=sum(f['pico_no_resuelto'] for f in filas),
        duracion_auditoria_s=sum(x['duracion_auditoria_s'] for x in piezas))
    with ruta.open('x', encoding='utf-8') as archivo:
        json.dump(d, archivo, ensure_ascii=False, indent=2, allow_nan=False)
    viento.csv_guardar(destino/'resumen.csv', [dict(plan=NOMBRE, D_h=d['D_h'],
        Tmax_C=max(f['Tmax']['valor'] for f in filas),
        DeltaTmax_K=max(f['DeltaTmax']['valor'] for f in filas),
        **d['riesgo'], alertas=d['picos_no_resueltos'])])
    print('Matriz completa y resumen guardados en:', destino)


if __name__ == '__main__':
    main()
