"""Agregación F02 de matrices precalculadas. Ejecutable sin solver ni paquetes externos."""
import argparse
from contextlib import nullcontext
import csv
from hashlib import sha256
import json
import math
from pathlib import Path

from insumos import ROOT, source_tree

LIMIT = 0.05
PLAN_NAMES = {'unica': 'Única', 'separacion_3h': 'Rápida',
              'separacion_6h': 'Referencia', 'separacion_9h': 'Lenta'}
CASES = dict(zip(PLAN_NAMES, ('unica_15kw_12c', 'rapida_15kw_12c',
                            'referencia_15kw_12c', 'lenta_15kw_12c')))


def read(path):
    return json.loads(Path(path).read_bytes())


def fingerprint(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def write_csv(path, rows):
    if not rows:
        raise ValueError(f'No hay filas para {path}')
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8-sig', newline='') as out:
        writer = csv.DictWriter(out, list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def close(a, b, tolerance=1e-9):
    return math.isclose(a, b, rel_tol=0, abs_tol=tolerance)


def calc(rows, multiplier=lambda r: 1):
    terms = [(r, r['peso'] * multiplier(r)) for r in rows]
    total = math.fsum(w for _, w in terms)
    if not (math.isfinite(total) and total > 0 and all(w >= 0 for _, w in terms)):
        raise ValueError('Pesos de sensibilidad inválidos')
    return {key: math.fsum(w for row, w in terms if row[flag]) / total
            for key, flag in (('P_T', 'excede_70'), ('P_delta', 'excede_20'), ('P_f', 'falla_union'))}


def row_record(plan, scenario, src, origin):
    peak, diff = src['Tmax'], src['DeltaTmax']
    hot, cold = diff['Tmax_C'], diff['Tmin_S25_C']
    if not close(peak['valor'], peak['Tmax_C']) or not close(diff['valor'], hot - cold):
        raise ValueError(f'Máximos incoherentes: {plan} {scenario}')
    if peak['valor'] + 1e-9 < hot or any(not 0 <= m['tiempo_h'] <= src['horizonte_h'] for m in (peak, diff)):
        raise ValueError(f'Máximos fuera de dominio o intervalo: {plan} {scenario}')
    temp_flag, diff_flag = peak['valor'] > 70, diff['valor'] > 20
    if (temp_flag, diff_flag) != (src['excede_70'], src['excede_20']):
        raise ValueError(f'Indicadores publicados incoherentes: {plan} {scenario}')
    return dict(plan=plan, curva=scenario[0], clima=scenario[1], peso=src['peso'],
                Tmax_C=peak['valor'], Tmax_h=peak['tiempo_h'], Tmax_fase=peak['fase'],
                Tmax_x_m=peak['xyz_Tmax_m'][0], Tmax_y_m=peak['xyz_Tmax_m'][1],
                Tmax_z_m=peak['xyz_Tmax_m'][2], Tmax_vertida=peak['vertida_Tmax'],
                DeltaTmax_K=diff['valor'], DeltaTmax_h=diff['tiempo_h'], DeltaTmax_fase=diff['fase'],
                T_caliente_en_DeltaTmax_C=hot, T_S25_en_DeltaTmax_C=cold,
                Delta_caliente_x_m=diff['xyz_Tmax_m'][0], Delta_caliente_y_m=diff['xyz_Tmax_m'][1],
                Delta_caliente_z_m=diff['xyz_Tmax_m'][2], Delta_caliente_vertida=diff['vertida_Tmax'],
                S25_x_m=diff['xyz_S25_m'][0], S25_y_m=diff['xyz_S25_m'][1],
                S25_z_m=diff['xyz_S25_m'][2], S25_vertida=diff['vertida_S25'],
                excede_70=temp_flag, excede_20=diff_flag, falla_union=temp_flag or diff_flag,
                horizonte_h=src['horizonte_h'], alerta_cola=src.get('pico_no_resuelto', False),
                origen=origin)


def audit_rows(plan, data, catalog, path):
    rows = []
    seen = set()
    for source in data['corridas']:
        scenario = (source.get('curva', source.get('material')), source['clima'])
        if scenario in seen or scenario not in catalog or not close(source['peso'], catalog[scenario]):
            raise ValueError(f'Catálogo, peso o duplicado incompatible: {plan} {scenario}')
        rows.append(row_record(plan, scenario, source, str(path)))
        seen.add(scenario)
    if seen != set(catalog) or not close(math.fsum(r['peso'] for r in rows), 1):
        raise ValueError(f'Matriz incompleta o pesos no normalizados: {plan}')
    nominal = calc(rows)
    official = data.get('riesgo', data.get('agregado'))
    if official and any(not close(nominal[key], official[published]) for key, published in
                        (('P_T', 'P_T'), ('P_delta', 'P_delta'), ('P_f', 'P_union'))):
        raise ValueError(f'Agregado publicado incompatible: {plan}')
    return rows


def plan_signature(placements):
    return [(v['id'], round(v['inicio_h'], 10), round(v['fin_h'], 10), round(v['volumen_m3'], 8))
            for v in placements]


def compatible(plan, data, known, schedules):
    case = data.get('estudio_controles', {})
    physical = ('U_W_m3K', 'k_hormigon_W_mK', 'rho_kg_m3', 'cp_J_kgK',
                'solver_adaptado_sha256', 'ejecutor_adaptado_sha256', 'referencia_sha256', 'modelo_viento')
    signature = ('U_W_m3K', 'referencia_C', 'tope_W', 'comienzo_edad_h', 'apagado_h', 'volumen_m3')
    common = ('lado_m', 'paso_max_s', 'S25_m', 'capacidad_m3_h', 'clima_sha256',
              'manifiesto_sha256', 'configuracion_sha256', 'modo', 'geometria')
    control = known['estudio_controles']
    horizons = sorted({row['horizonte_h'] for row in data['corridas']})
    if not (all(data.get(k) == known[k] for k in common)
            and all(case.get(k) == control[k] for k in physical)
            and horizons and set(horizons) <= {600, 672} and data['horizontes_h'] == horizons
            and data['picos_no_resueltos'] == sum(row['pico_no_resuelto'] for row in data['corridas'])
            and all(data['enfriamiento'][k] == known['enfriamiento'][k] for k in signature)
            and plan_signature(data['plan']) == plan_signature(schedules[plan])
            and close(data['D_h'], schedules[plan][-1]['fin_h'])
            and all(v['colocacion_C'] == 12 for v in data['plan'])
            and not data['grupos_de_activacion']):
        raise ValueError(f'{plan}: matriz ajena a la familia congelada, revisar antes de comparar')


def summarize(plan, duration, rows):
    return dict(plan=plan, duracion_h=duration,
                Tmax_C=max((r['Tmax_C'] for r in rows), default=None),
                DeltaTmax_K=max((r['DeltaTmax_K'] for r in rows), default=None),
                **(calc(rows) if rows else dict.fromkeys(('P_T', 'P_delta', 'P_f'))),
                cumple=('Pendiente: falta matriz' if not rows else
                        'Indeterminado: cola sin resolver' if any(r['alerta_cola'] for r in rows) else
                        'Sí, en la resolución publicada' if calc(rows)['P_f'] <= LIMIT else 'No'),
                n_escenarios=len(rows))


def inputs(root):
    cfg = read(root / 'casos/incertidumbre/parametros.json')
    mat = read(root / 'datos/hidratacion/manifiesto.json')
    catalog = {(m['id'], c['id']): m['peso'] * c['peso'] for m in mat['curvas'] for c in cfg['historias']}
    base = read(root / 'resultados/incertidumbre/curvas_reales/resumen.json')
    schedules = {p['plan']: p['vertidas'] for p in base['planes']}
    return catalog, schedules


def sensitivities(plan, rows):
    alternatives = [('pesos publicados', lambda r: 1),
                    ('solo SS (exploración por menor confianza de 22A)', lambda r: int(r['curva'].endswith('_SS')))]
    alternatives.extend((f'doble peso a {climate}', lambda r, c=climate: 2 if r['clima'] == c else 1)
                        for climate in sorted({r['clima'] for r in rows}))
    return [dict(plan=plan, sensibilidad=name, **(p := calc(rows, weight)),
                 n_con_peso=sum(weight(row) > 0 for row in rows),
                 cumple=('Indeterminado: cola sin resolver' if any(row['alerta_cola'] and weight(row) > 0 for row in rows)
                         else 'Sí' if p['P_f'] <= LIMIT else 'No')) for name, weight in alternatives]


def self_test():
    def make(temp, diff):
        return dict(peso=1 / 24, excede_70=temp, excede_20=diff, falla_union=temp or diff)
    clean = [make(False, False) for _ in range(22)]
    assert close(calc(clean + [make(True, True), make(False, False)])['P_f'], 1 / 24)
    assert close(calc(clean + [make(True, False), make(False, True)])['P_f'], 2 / 24)
    assert calc([dict(make(True, False), peso=0.05), dict(make(False, False), peso=0.95)])['P_f'] <= LIMIT
    assert calc([dict(make(True, False), peso=0.05004), dict(make(False, False), peso=0.94996)])['P_f'] > LIMIT


def run(root, out=ROOT / 'tablas', supplied=None):
    self_test()
    catalog, schedules = inputs(root)
    current = root / 'resultados/controles_12c'
    paths = {plan: current / case / 'malla_0.5_paso900' / f'{case}.json' for plan, case in CASES.items()}
    paths.update(supplied or {})
    known = read(current / 'unica_15kw_12c/malla_0.5_paso900/unica_15kw_12c.json')
    per_scenario, totals, sensitivity, provenance = [], [], [], []
    for plan, name in PLAN_NAMES.items():
        path = paths[plan]
        rows = []
        if path.is_file():
            data = read(path)
            compatible(plan, data, known, schedules)
            origin = path.relative_to(root).as_posix() if path.is_relative_to(root) else path
            rows = audit_rows(name, data, catalog, origin)
            sensitivity.extend(sensitivities(name, rows))
            provenance.append(dict(plan=name, origen=str(origin), sha256=fingerprint(path)))
        elif supplied and plan in supplied:
            raise FileNotFoundError(path)
        per_scenario.extend(rows)
        totals.append(summarize(name, schedules[plan][-1]['fin_h'], rows))
    for filename, rows in [('M4_por_escenario.csv', per_scenario), ('M4_comparacion.csv', totals),
                           ('M4_sensibilidad.csv', sensitivity), ('M4_procedencia_matrices.csv', provenance)]:
        write_csv(out / filename, rows)
    return per_scenario, totals, sensitivity


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--insumos', type=Path, help='Usa una copia compatible de los insumos en lugar del historial Git')
    parser.add_argument('--salida', type=Path, default=ROOT / 'tablas')
    parser.add_argument('--matriz', action='append', default=[], metavar='PLAN=JSON',
                        help=f'Sustituye una matriz de la familia congelada. Planes: {", ".join(PLAN_NAMES)}')
    args = parser.parse_args()
    supplied = {}
    for val in args.matriz:
        key, sep, path = val.partition('=')
        if not sep or key not in PLAN_NAMES or key in supplied:
            parser.error(f'Argumento de matriz inválido o repetido: {val}')
        supplied[key] = Path(path).resolve()
    with nullcontext(args.insumos.resolve()) if args.insumos else source_tree() as root:
        rows, totals, _ = run(root, args.salida, supplied)
    print(f'{len(rows)} escenarios auditados, {sum(r["n_escenarios"] > 0 for r in totals)} de {len(totals)} matrices disponibles')


if __name__ == '__main__':
    main()
