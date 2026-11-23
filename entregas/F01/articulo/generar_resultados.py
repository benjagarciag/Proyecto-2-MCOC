"""Prepara tablas y copia figuras verificadas; no importa ni ejecuta el solver."""
from pathlib import Path
import csv
import hashlib
import json
import shutil

ART = Path(__file__).resolve().parent
ROOT = ART.parents[2]
SRC = ROOT / 'entregas/F02/cierre_revision_final'
DATA = ART / 'datos'


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def num(value, digits=3):
    value = float(value)
    if abs(value) < 0.5 * 10 ** (-digits):
        value = 0.0
    return f'{value:.{digits}f}'.replace('.', '{,}')


def xyz(raw):
    return '(' + ';'.join(num(x) for x in json.loads(raw)) + ')'


def table(caption, label, columns, header, rows):
    return '\n'.join([
        (r'\begin{table}[H]' if label.startswith('tab:cronograma-') else r'\begin{table}[htbp]'), r'  \centering',
        r'  \caption{' + caption + '}', r'  \label{' + label + '}',
        r'  \small', r'  \setlength{\tabcolsep}{4pt}',
        r'  \begin{tabular}{' + columns + '}', r'    \toprule',
        '    ' + header + r' \\', r'    \midrule',
        *['    ' + row + r' \\' for row in rows],
        r'    \bottomrule', r'  \end{tabular}',
        r'  \captionsetup{skip=2pt}',
        r'  \caption*{Fuente: elaboración propia a partir del cronograma y los resultados archivados de simulación.}',
        r'\end{table}', ''])


def main():
    records = list(csv.DictReader((SRC / 'METRICAS_144_FILAS.csv').open(encoding='utf-8-sig', newline='')))
    capas = load(ROOT / 'resultados/diseno_circuitos_colocacion/esquema.json')['capas']
    schedule = []
    for q in (60, 55):
        rows = []
        for c in capas:
            ini = c['inicio_h'] * 60 / q
            fin = c['fin_h'] * 60 / q
            row = dict(q_m3_h=q, capa=c['id'], inicio_h=ini, fin_h=fin,
                       duracion_h=fin-ini, retiro_madera_h=ini+72,
                       retiro_manta1_h=ini+240, retiro_manta2_h=ini+504)
            schedule.append(row)
            rows.append(' & '.join(['$'+str(c['id'])+'$'] + [
                '$'+num(row[k])+'$' for k in ('inicio_h','fin_h','duracion_h','retiro_madera_h','retiro_manta1_h','retiro_manta2_h')]))
        text = table(
            f'Cronograma por capa del plan de ${q}'+r'\,\mathrm{m^3/h}$',
            f'tab:cronograma-{q}', 'ccccccc',
            r'Capa & Inicio [h] & Fin [h] & Duración [h] & Madera [h] & Manta 1 [h] & Manta 2 [h]', rows)
        (DATA / f'tabla_cronograma_{q}.tex').write_text(text, encoding='utf8')
    extremes = []
    rows = []
    for q, h, name in ((60, .4, 'Propuesta base'), (55, .4, 'Variante lenta'), (60, .2, 'Propuesta fina')):
        subset = [r for r in records if float(r['q_m3_h']) == q and float(r['malla_m']) == h and int(r['horizonte_h']) == 672]
        assert len(subset) == 24
        for metric in ('M_T_C', 'M_Delta_K'):
            r = max(subset, key=lambda r: float(r[metric]))
            extremes.append(dict(r, nombre_plan=name, metrica=metric))
            is_t = metric == 'M_T_C'
            loc_t = '$'+xyz(r['xyz_Tmax_m'] if is_t else r['xyz_Tmax_en_Delta_m'])+'$'
            loc_25 = '---' if is_t else '$'+xyz(r['xyz_S25_en_Delta_m'])+'$'
            rows.append(' & '.join([
                name, r'$M_T$' if is_t else r'$M_\Delta$', '$'+num(r[metric],4)+'$',
                '$'+num(r['t_Tmax_h'] if is_t else r['t_Delta_h'])+'$',
                r'\texttt{'+r['curva'].replace('_', r'\_')+'}, ERA5-$'+r['clima'][-4:]+'$', loc_t, loc_25]))
    (DATA / 'tabla_localizacion_maximos.tex').write_text(table(
        r'Escenarios, tiempos y posiciones de los extremos a $672\,\mathrm h$ ($M_T$ en $^\circ\mathrm C$ y $M_\Delta$ en $\mathrm K$)',
        'tab:localizacion-maximos', 'L{1.5cm}L{1.2cm}L{1.15cm}L{1.2cm}L{1.8cm}L{3.3cm}L{3.3cm}',
        r'Plan & Métrica & Valor & Tiempo [h] & Escenario & $\vec x_T$ [m] & $\vec x_{25}$ [m]', rows), encoding='utf8')
    figures = {}
    for name in ('01_D_VS_PROBABILIDAD.png','02_CRONOGRAMAS.png','03_CURVAS_COMPARABLES.png',
                 '04_CORTES_COMPARABLES_672H.png','05_SENSIBILIDAD_24_PARES.png'):
        src = SRC / name
        dst = ART / 'Imagenes' / ('resultados_' + name)
        shutil.copy2(src, dst)
        figures[name] = dict(fuente=src.relative_to(ROOT).as_posix(),
                             destino=dst.relative_to(ART).as_posix(),
                             sha256=hashlib.sha256(src.read_bytes()).hexdigest())
    (DATA / 'resultados_trazabilidad.json').write_text(json.dumps(dict(
        metodo='Postproceso documental sin solver; cifras completas en CSV de origen',
        fuente_metricas=(SRC/'METRICAS_144_FILAS.csv').relative_to(ROOT).as_posix(),
        cronogramas=schedule, extremos=extremes, figuras=figures), ensure_ascii=False, indent=2)+'\n', encoding='utf8')
    print(f'Preparadas {len(schedule)} filas de cronograma, {len(extremes)} extremos y {len(figures)} figuras existentes.')


if __name__ == '__main__':
    main()
