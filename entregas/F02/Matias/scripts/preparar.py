"""Reconstruye catálogos, cronogramas, auditoría y figuras desde insumos congelados."""
from datetime import datetime, timedelta, timezone
from itertools import product
import math
import re

import numpy as np

from agregar import (PLAN_NAMES, audit_rows, close, fingerprint, inputs, read,
                     run, sensitivities, summarize, write_csv)
from graficos import COLORS, Figure
from insumos import ROOT, provenance, source_tree


TABLES = ROOT / 'tablas'
FIG = ROOT / 'figuras'
STAMP = 'F02 · corte 18-11-2026 · GitHub 496dafa'
HIST = 'resultados/incertidumbre/enfriamiento/u5_tope12'
CURRENT = 'resultados/controles_12c/unica_15kw_12c/malla_0.5_paso900/unica_15kw_12c.json'
VARIABLES = ('temperature_2m', 'wind_speed_10m', 'shortwave_radiation')


def hydration(root):
    files = [root / 'datos/hidratacion/source_terms.txt', root / 'Enunciados e Instrucciones/source_terms.txt']
    hashes = [fingerprint(path) for path in files]
    assert all(digest == provenance()['adjunto_sha256'] for digest in hashes), 'La fuente oficial difiere de la huella del adjunto'
    source = files[0].read_text(encoding='utf-8')
    ids = [f'M{i}_{campaign}' for campaign, i in product(('SS', '22A'), range(1, 5))]
    assert next(line.split()[2:] for line in source.splitlines() if line.startswith('# time_h')) == ids
    array = np.loadtxt(files[0])
    assert array.shape == (1443, 9)
    assert np.allclose(array[:, 0], np.arange(len(array)) / 6, atol=0.00051, rtol=0)
    manifest = {row['id']: row for row in read(root / 'datos/hidratacion/manifiesto.json')['curvas']}
    records = []
    figure = Figure('Calor de hidratación de ocho probetas', 'Potencia volumétrica en β = 2,5 W/(m²·K) · edad desde la ventana retenida')
    x, y = figure.axes((100, 163, 1010, 380), [0, 30, 60, 90, 120, 150, 180, 210, 240, 250],
                       [0, 100, 200, 300, 400, 500, 600, 700], 'Edad en la ventana retenida [h]', 'Potencia [W/m³]')
    for j, curve in enumerate(ids):
        campaign = curve.split('_')[1]
        power = array[:, j + 1]
        fin = int(np.count_nonzero(np.isfinite(power)))
        assert np.all(np.isfinite(power[:fin])) and np.all(np.isnan(power[fin:]))
        power = power[:fin]
        assert np.all(power >= 0)
        age = np.arange(fin) / 6
        accumulated = np.r_[0, np.cumsum(300 * (power[:-1] + power[1:]))]
        reported = np.loadtxt(root / 'datos/hidratacion' / manifest[curve]['csv'], delimiter=',', skiprows=1)
        assert np.allclose(reported[:, 0], age, atol=1e-11, rtol=0)
        assert np.allclose(reported[:, 1], accumulated, atol=1e-6, rtol=0)
        header = re.search(rf'^#\s+{curve}\s+([\d.]+)\s*/[^/]+/\s*[\d.]+\s+([\d.]+)\s*/[^/]+/\s*[\d.]+\s+([\d.]+)', source, re.M)
        low, published, high = map(float, header.groups())
        energy = accumulated[-1] / 1e6
        assert abs(energy - published) < 0.05
        records.append(dict(curva=curve, campana=campaign, fecha='13–20 abr 2025' if j < 4 else '22 abr 2025',
                            potencia_max_W_m3=float(np.max(power)), edad_max_h=float(age[np.argmax(power)]),
                            duracion_h=float(age[-1]), muestras=fin, energia_MJ_m3=energy,
                            total_publicado_MJ_m3=published, diferencia_MJ_m3=energy - published,
                            beta_2_1_MJ_m3=low, beta_3_0_MJ_m3=high, potencia_final_W_m3=float(power[-1]),
                            calidad=('RMSE ajuste ~0,1–0,2 K' if j < 4 else
                                     'Menor confianza, RMSE ~0,4 K, un sensor ambiente')))
        figure.series(zip(age, power), x, y, COLORS[j % 4], '11 6' if j >= 4 else '')
    figure.legend([(c, COLORS[j % 4], '11 6' if j >= 4 else '') for j, c in enumerate(ids)],
                  x=92, y=124, spacing=133)
    figure.save(FIG / '01_hidratacion.svg', STAMP + ' · solo tramos finitos observados por inversión; la cola nula es un supuesto del solver.')
    write_csv(TABLES / 'M1_curvas.csv', records)
    return records, hashes[0]


def weather(root, catalog):
    cfg = read(root / 'casos/incertidumbre/parametros.json')
    candidate = read(root / CURRENT)
    winds = read(root / 'resultados/sensibilidad_h/viento/series_h.json')
    start = datetime.fromisoformat(cfg['inicio'])
    metas, series, points = [], {}, []
    for item in cfg['historias']:
        climate = item['id']
        path = root / item['snapshot']
        digest = fingerprint(path)
        assert digest == candidate['clima_sha256'][climate]
        data = read(path)
        meta, returned = data['metadata'], data['respuesta']
        hourly = returned['hourly']
        clock = [datetime.fromtimestamp(t, timezone.utc) for t in hourly['time']]
        assert len(clock) == meta['muestras_horarias'] == 696
        assert all(b - a == timedelta(hours=1) for a, b in zip(clock, clock[1:]))
        assert meta['modelo_solicitado'] == 'era5' and meta['zona_horaria'] == 'UTC'
        assert meta['unidades'] == dict(zip(VARIABLES, ('°C', 'm/s', 'W/m²')))
        assert returned['utc_offset_seconds'] == 0
        aligned = datetime.fromisoformat(item['inicio'])
        assert aligned.month == start.month and aligned.day == start.day and aligned.hour == start.hour
        index = clock.index(aligned)
        available = len(clock) - index - 1
        assert index == 13 and available == 682 >= cfg['extension_max_h']
        for var in VARIABLES:
            assert len(hourly[var]) == len(clock) and all(math.isfinite(v) for v in hourly[var])
        values = {var: hourly[var][index:] for var in VARIABLES}
        n = cfg['extension_max_h'] + 1
        values['h_W_m2K'] = winds[climate]['h_W_m2K']
        assert len(values['h_W_m2K']) == n
        assert np.allclose(values['wind_speed_10m'][:n], winds[climate]['v10_m_s'], atol=1e-12, rtol=0)
        assert np.allclose(values['h_W_m2K'], 5.7 + 3.8 * np.asarray(values['wind_speed_10m'][:n]) * (2 / 10) ** 0.14)
        series[climate] = values
        coords = meta['coordenadas_solicitadas']
        latest = clock[-1].isoformat()
        metas.append(dict(clima=climate, peso=item['peso'], fuente=meta['fuente'], modelo=meta['modelo_solicitado'],
                          archivo=item['snapshot'], sha256=digest, descarga_utc=meta['descargado_utc'],
                          lat_solicitada=coords['latitud'], lon_solicitada=coords['longitud'],
                          lat_devuelta=returned['latitude'], lon_devuelta=returned['longitude'],
                          altura_devuelta_m=returned['elevation'], zona_fuente='UTC',
                          primera_marca_utc=clock[0].isoformat(), ultima_marca_utc=latest,
                          muestras_brutas=len(clock), max_h_relativo_disponible=available,
                          inicio_bloque=aligned.isoformat(), inicio_comun=start.isoformat(),
                          unidades='°C a 2 m | m/s a 10 m | W/m²', faltantes=0))
        for i in range(n):
            points.append(dict(clima=climate, hora_relativa=i, hora_utc_historica=clock[index+i].isoformat(),
                               hora_local_2026=(start+timedelta(hours=i)).isoformat(),
                               aire_C=values['temperature_2m'][i], viento10_m_s=values['wind_speed_10m'][i],
                               radiacion_W_m2=values['shortwave_radiation'][i], h_W_m2K=values['h_W_m2K'][i]))
    assert len(catalog) == 24 and close(math.fsum(catalog.values()), 1)
    entries = [dict(escenario=f'{curve}__{climate}', curva=curve, campana=curve.split('_')[1], clima=climate,
                    peso_material=0.125, peso_clima=1/3, peso_conjunto=weight, peso_exacto='1/24',
                    uso_curva='Común a todas las vertidas de esa corrida',
                    inicio_comun=start.isoformat()) for (curve, climate), weight in sorted(catalog.items())]
    assert all(close(row['peso_conjunto'], row['peso_material'] * row['peso_clima']) for row in entries)
    write_csv(TABLES / 'M2_metadatos_ERA5.csv', metas)
    write_csv(TABLES / 'M2_clima_horario.csv', points)
    write_csv(TABLES / 'M2_catalogo_24.csv', entries)

    figure = Figure('Tres historias meteorológicas del sitio', 'ERA5 histórico · hora cero alineada al 19-11-2026 10:00 de Santiago', 875)
    figure.legend([(climate, COLORS[j], '') for j, climate in enumerate(series)], x=104, y=117)
    panels = [('temperature_2m', 'Temperatura del aire a 2 m [°C]', 5),
              ('wind_speed_10m', 'Viento a 10 m [m/s]', 2), ('h_W_m2K', 'Convección estimada h [W/(m²·K)]', 10)]
    xticks = [0, 96, 192, 288, 336, 432, 528, 600, 672]
    for j, (var, ylabel, step) in enumerate(panels):
        all_values = [v for row in series.values() for v in row[var][:673]]
        yticks = list(range(step*math.floor(min(all_values)/step), step*math.ceil(max(all_values)/step)+1, step))
        x, y = figure.axes((105, 160 + 230*j, 1000, 150), xticks, yticks, 'Horas relativas' if j == 2 else '', ylabel)
        for i, row in enumerate(series.values()):
            figure.series(enumerate(row[var][:673]), x, y, COLORS[i])
        for hour in (336, 600):
            figure.line(x(hour), y(yticks[0]), x(hour), y(yticks[-1]), '#77889a', 1, '5 5')
    figure.save(FIG / '02_clima_ERA5.svg', STAMP + ' · línea discontinua en 336 y 600 h; radiación guardada aparte, sin uso en esta candidata.')

    figure = Figure('Catálogo discreto de incertidumbre', 'Cada celda conserva una curva completa de material y una historia meteorológica completa', 595)
    for j, climate in enumerate(series):
        figure.text(410 + 205*j, 146, climate, 16, 'middle', bold=True)
    for i, curve in enumerate(dict.fromkeys(row['curva'] for row in entries)):
        py = 167 + 45*i
        figure.text(270, py+24, curve, 16, 'end', bold=True)
        for j, climate in enumerate(series):
            px = 320 + 205*j
            figure.rect(px, py, 180, 35, '#f9ede2' if curve.endswith('22A') else '#deedf2')
            figure.text(px+90, py+23, '1/24', 16, 'middle')
    figure.save(FIG / '03_catalogo.svg', STAMP + ' · pesos de modelo; las filas 22A tienen menor confianza según la fuente.')


def schedules_report(root, schedules):
    config = read(root / 'casos/incertidumbre/parametros.json')
    current = read(root / 'casos/sensibilidad_h/colocacion_12c.json')
    base = read(root / 'resultados/incertidumbre/curvas_reales/resumen.json')
    capacity = config['capacidad_m3_h']
    tick = config['paso_inicios_h']
    t0 = datetime.fromisoformat(config['inicio'])
    data, summary = [], []
    for key, events in schedules.items():
        nominal = 0 if key == 'unica' else int(key.split('_')[1][:-1])
        preset = next(v for v in current['casos'].values() if v['plan'] == key)
        assert preset['temperatura_C'] == 12 and preset['tope_W'] == 15000 and preset['edad_inicio_h'] == 6
        prior = None
        for v in events:
            start = v['inicio_h']
            duration = v['volumen_m3'] / capacity
            end = start + duration
            assert close(duration, v['duracion_h']) and close(end, v['fin_h'])
            if prior:
                earliest = max(prior['inicio_h']+nominal, prior['fin_h']+config['espera_min_h'])
                assert close(start, tick*math.ceil(earliest/tick-1e-12))
            data.append(dict(plan=PLAN_NAMES[key], vertida=v['id'], volumen_ifc_m3=v['volumen_m3'],
                             caudal_m3_h=capacity, inicio_relativo_h=start, fin_relativo_h=end,
                             duracion_h=duration, intervalo_desde_inicio_previo_h=start-prior['inicio_h'] if prior else None,
                             espera_desde_fin_previo_h=start-prior['fin_h'] if prior else None,
                             inicio_local=(t0+timedelta(hours=start)).isoformat(), fin_local=(t0+timedelta(hours=end)).isoformat(),
                             T_colocacion_nueva_C=preset['temperatura_C']))
            prior = v
        volume = math.fsum(v['volumen_m3'] for v in events)
        assert close(volume, base['volumen_ifc_m3'])
        duration = events[-1]['fin_h']
        waits = math.fsum(r['espera_desde_fin_previo_h'] or 0 for r in data if r['plan'] == PLAN_NAMES[key])
        assert close(duration, volume/capacity + waits)
        summary.append(dict(plan=PLAN_NAMES[key], n_vertidas=len(events), volumen_m3=volume,
                            D_h=duration, colocacion_activa_h=volume/capacity, esperas_h=waits,
                            intervalo_nominal_h=nominal or None))
    write_csv(TABLES / 'M3_cronograma.csv', data)
    write_csv(TABLES / 'M3_planes.csv', summary)
    figure = Figure('Cronogramas de colocación de la fundación',
                    'Inicio común 19-11-2026 10:00 Santiago · 636,775 m³ · capacidad efectiva supuesta 60 m³/h', 550)
    x, _ = figure.axes((206, 154, 912, 291), list(range(0, 40, 3)) + [42], [0, 1], 'Horas desde el inicio común', '')
    figure.rect(120, 143, 82, 325, 'white')
    for k, (key, events) in enumerate(schedules.items()):
        y = 177 + 67*k
        figure.text(184, y+23, PLAN_NAMES[key], 18, 'end', bold=True)
        for j, v in enumerate(events):
            x0, x1 = x(v['inicio_h']), x(v['fin_h'])
            figure.rect(x0, y, x1-x0, 34, COLORS[j])
            if x1-x0 >= 14:
                figure.text((x0+x1)/2, y+23, 'V'+str(v['id']) if x1-x0 >= 31 else str(v['id']), 13, 'middle', 'white')
        dur = events[-1]['fin_h']
        figure.text(x(dur)+9, y+23, f'{dur:.3f} h'.replace('.', ','), 15, bold=True)
    figure.save(FIG / '04_gantt.svg', STAMP + ' · barras: colocación; espacios: esperas; D termina al terminar la última barra.')
    return summary


def historical(root, catalog):
    files = {'h constante · 12 kW': [f'{HIST}/unica/resumen.json', f'{HIST}/separacion_3h/resumen.json',
                                     f'{HIST}/resumen.json', 'resultados/f02_verificaciones/matrices/lenta_12kw.json'],
             'h horario · 12 kW': [f'resultados/sensibilidad_h/viento/horario/malla_0.5_paso900/{f}.json'
                                    for f in ('publicada_unica', 'publicada_rapida', 'publicada_referencia', 'lenta_12kw')]}
    totals, detail, sensitivity = [], [], []
    for group, paths in files.items():
        group_control = None
        for plan, p in zip(PLAN_NAMES.values(), paths):
            data = read(root / p)
            c = data['enfriamiento']
            control = tuple(c.get(a, c.get(b)) for a, b in (('U_W_m3K','u_W_m3K'),('referencia_C','referencia_C'),
                            ('tope_W','tope_W'),('comienzo_edad_h','edad_inicio_h'),('apagado_h','fin_h')))
            assert control == (5, 18, 12000, 6, 432)
            if group_control is None:
                group_control = (data['lado_m'], data.get('paso_max_s', data.get('dt_tope_s')), data['clima_sha256'], data['manifiesto_sha256'])
            assert group_control == (data['lado_m'], data.get('paso_max_s', data.get('dt_tope_s')), data['clima_sha256'], data['manifiesto_sha256'])
            rows = audit_rows(plan, data, catalog, p)
            detail.extend(dict(familia=group, **r) for r in rows)
            totals.append(dict(familia=group, **summarize(plan, data['D_h'], rows),
                               T_colocacion_C=' / '.join(str(v['colocacion_C']) for v in data['plan']),
                               archivo=p, sha256=fingerprint(root / p)))
            sensitivity.extend(dict(familia=group, **r) for r in sensitivities(plan, rows))
    write_csv(TABLES / 'HISTORICO_12kW_comparaciones.csv', totals)
    write_csv(TABLES / 'HISTORICO_12kW_escenarios.csv', detail)
    write_csv(TABLES / 'HISTORICO_12kW_sensibilidad.csv', sensitivity)
    return totals


def inventory(root):
    records = []
    for path in sorted((root / 'resultados').rglob('*.json'), key=lambda p: p.as_posix()):
        d = read(path)
        if not isinstance(d, dict) or not isinstance(d.get('corridas'), list):
            continue
        placement = d.get('plan', [])
        if not isinstance(placement, list):
            placement = []
        cooling = d.get('enfriamiento') or {}
        study = d.get('estudio_controles') or {}
        origin = path.relative_to(root).as_posix()
        records.append(dict(archivo=origin, n_corridas=len(d['corridas']),
                            modelo='12 °C / 15 kW' if origin.startswith('resultados/controles_12c/') else 'Antecedente o sensibilidad',
                            plan=d.get('plan_id') or study.get('caso') or d.get('experimento') or '',
                            colocacion_C=' / '.join(str(v.get('colocacion_C', '')) for v in placement),
                            tope_W=cooling.get('tope_W'), lado_m=d.get('lado_m'),
                            paso_max_s=d.get('paso_max_s', d.get('dt_tope_s')), registros_de_un_solo_escenario=len(d['corridas']) == 1))
    write_csv(TABLES / 'M4_inventario_matrices_GitHub.csv', records)
    return records


def main():
    from figuras_resultados import render

    with source_tree() as root:
        catalog, schedules = inputs(root)
        hyd, digest = hydration(root)
        weather(root, catalog)
        plans = schedules_report(root, schedules)
        rows, summary, sensitivity = run(root)
        hist = historical(root, catalog)
        matrices = inventory(root)
        render(root, rows, summary, hist)
    print(f'{len(hyd)} curvas; hash común {digest}; 24 escenarios; {len(plans)} cronogramas')
    print(f'{len(rows)} escenarios actuales; {len(sensitivity)} sensibilidades actuales; {len(matrices)} matrices o fragmentos inventariados')
    for row in summary + hist:
        print(row['plan'], row['Tmax_C'], row['DeltaTmax_K'], row['P_f'])


if __name__ == '__main__':
    main()
