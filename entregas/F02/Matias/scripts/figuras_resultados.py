"""Plotea métricas publicadas y el campo histórico conservado en el viewer."""
import json
import re

import numpy as np

from agregar import close, read
from graficos import COLORS, Figure
from insumos import ROOT


FIG = ROOT / 'figuras'
STAMP = 'F02 · corte 18-11-2026 · GitHub 496dafa'
CURRENT = '12 °C / tope 15 kW · h horario · 0,50 m / 900 s · máximo por escenario hasta 600 h'


def duration_risk(summary, historical=None):
    if historical:
        figure = Figure('Duración y riesgo en las familias históricas', 'Tope de 12 kW · 24 escenarios por plan · 0,50 m / 900 s')
        ymax = 50
        filename = 'H01_duracion_riesgo_12kW.svg'
    else:
        figure = Figure('Duración y riesgo de la familia candidata', CURRENT)
        ymax = 10
        filename = '05_duracion_riesgo_15kW.svg'
    ticks = list(range(0, ymax+1, 5 if historical else 1))
    x, y = figure.axes((107, 172, 1000, 325), list(range(0, 41, 5)), ticks,
                       'Fin de colocación D [h]', 'Probabilidad conjunta P_f [%]')
    figure.line(x(0), y(5), x(40), y(5), '#ae3d3d', 2.5, '8 5')
    figure.text(x(39.7), y(5)-9, 'Límite 5 %', 14, 'end', '#ae3d3d', True)
    if historical:
        for j, group in enumerate(dict.fromkeys(row['familia'] for row in historical)):
            points = [(row['duracion_h'], 100*row['P_f']) for row in historical if row['familia'] == group]
            for dx, risk in points:
                figure.point(x(dx), y(risk), COLORS[j], 6)
                figure.text(x(dx)+8, y(risk)-9, f'{risk:.2f} %'.replace('.', ','), 14, color=COLORS[j])
        figure.legend([('h constante', COLORS[0], ''), ('h horario', COLORS[1], '')], y=126)
        note = ' · antecedente de 12 kW con temperaturas de colocación de la configuración histórica.'
    else:
        for row in summary:
            dx, risk, label = row['duracion_h'], row['P_f'], row['plan']
            if risk is None:
                figure.line(x(dx), y(0)+23, x(dx), y(0)+33, '#7a8898', 2)
                figure.text(x(dx), y(0)+88, label, 14, 'middle', bold=True)
                figure.text(x(dx), y(0)+106, 'Sin matriz', 13, 'middle', '#596b7d')
            else:
                figure.point(x(dx), y(100*risk), COLORS[0], 8)
                figure.text(x(dx)+12, y(100*risk)-12, f'{label} · {risk:.2%}'.replace('.', ','), 15, bold=True)
        note = ' · debajo del eje se marcan las duraciones de los planes cuyo riesgo sigue pendiente.'
    figure.save(FIG / filename, STAMP + note)


def scenario_peaks(rows):
    rows = sorted(rows, key=lambda r: (r['curva'], r['clima']))
    figure = Figure('Máximos térmicos de los 24 escenarios de la única', CURRENT, 850)
    climates = sorted({r['clima'] for r in rows})
    figure.legend([(c, COLORS[j], '') for j, c in enumerate(climates)], x=110, y=125)
    peak_specs = [('Tmax_C', 70, [0, 10, 20, 30, 40, 50, 60, 70, 80], 'Tmax [°C]', 'Límite 70 °C'),
                  ('DeltaTmax_K', 20, [0, 4, 8, 12, 16, 20, 24], 'ΔTmax [K]', 'Límite 20 K')]
    max_idx = len(rows) - 1
    for j, (key, limit, yticks, label, limit_label) in enumerate(peak_specs):
        x, y = figure.axes((110, 170 + 318*j, 1000, 235), list(range(0, max_idx, 3))+[max_idx],
                           yticks, '', label, label_xticks=False)
        figure.line(x(0), y(limit), x(max_idx), y(limit), '#ae3d3d', 2, '8 5')
        figure.text(x(max_idx), y(limit)-9, limit_label, 14, 'end', '#ae3d3d', True)
        for i, row in enumerate(rows):
            figure.point(x(i), y(row[key]), COLORS[climates.index(row['clima'])], 5.5)
        for i in range(0, len(rows), 3):
            figure.text(x(i + 1), y(0)+27, rows[i]['curva'], 13, 'middle')
    figure.save(FIG / '06_maximos_24_15kW.svg', STAMP + ' · cada grupo de tres puntos corresponde a una curva de hidratación.')

    critical = max(rows, key=lambda r: r['DeltaTmax_K'])
    hot, cold = critical['T_caliente_en_DeltaTmax_C'], critical['T_S25_en_DeltaTmax_C']
    hour = critical['DeltaTmax_h']
    figure = Figure('Dos temperaturas en el instante del mayor diferencial',
                    f'{critical["curva"]} × {critical["clima"]} · única · hora {hour:g} · 12 °C / tope 15 kW · h horario', 490)
    x, _ = figure.axes((180, 163, 900, 218), list(range(0, 71, 10)), [0, 1], 'Temperatura [°C]', '')
    figure.rect(122, 150, 54, 243, 'white')
    figure.line(x(cold), 242, x(hot), 242, '#456379', 4)
    for value, color, label, height in ((cold, COLORS[1], 'S25 mínimo', 291), (hot, COLORS[0], 'Máximo en hormigón', 290)):
        figure.point(x(value), 242, color, 10)
        figure.text(x(value), height, label, 16, 'middle', color, True)
        figure.text(x(value), height+25, f'{value:.3f} °C'.replace('.', ','), 16, 'middle', color)
    figure.text((x(cold)+x(hot))/2, 214, f'ΔT = {hot-cold:.3f} K'.replace('.', ','), 20, 'middle', bold=True)
    peak = critical['Tmax_C']
    figure.point(x(peak), 242, '#7e8894', 7)
    figure.text(x(peak), 290, 'Pico térmico de esta corrida', 16, 'middle', '#596777')
    figure.text(x(peak), 315, f'{peak:.3f} °C a {critical["Tmax_h"]:.2f} h'.replace('.', ','), 15, 'middle', '#596777')
    figure.save(FIG / '07_diferencial_critico_15kW.svg', STAMP + ' · las dos temperaturas coloreadas corresponden al mismo instante.')


def historical_curves(root):
    data = read(root / 'resultados/f02_verificaciones/trazas_c6.json')
    scenario = ' × '.join(data['escenario'])
    figure = Figure('Curvas núcleo y S25 para un escenario común',
                    f'Histórico · {scenario} · 12 kW, h constante · malla 0,50 m, paso máximo 900 s', 920)
    styles = [('nucleo_C', 'Núcleo', COLORS[0], ''), ('Tmin_S25_C', 'S25 mínimo', COLORS[1], ''),
              ('Tmax_C', 'Máximo del hormigón', COLORS[2], '7 5')]
    figure.legend([(label, color, dash) for _, label, color, dash in styles] + [('ΔT', COLORS[3], '')],
                  x=105, y=122, spacing=230)
    for i, (plan, page) in enumerate(data['planes'].items()):
        trace = page['muestras_horarias']
        assert len(trace) == 601 and [r['tiempo_h'] for r in trace] == list(range(601))
        assert all(close(r['DeltaT_K'], r['Tmax_C']-r['Tmin_S25_C']) for r in trace)
        for j in range(2):
            left, top = 106 + 580*(i % 2), 187 + 355*(i // 2) + 162*j
            yticks = list(range(0, 71, 10)) if j == 0 else list(range(0, 21, 5))
            x, y = figure.axes((left, top, 424, 110), list(range(0, 601, 120)), yticks,
                               'Horas desde t₀' if j else '', (plan.title()+' · T [°C]') if j == 0 else 'ΔT [K]')
            figure.line(x(0), y(yticks[-1]), x(600), y(yticks[-1]), '#ae3d3d', 1.7, '6 4')
            for key, _, color, dash in styles if j == 0 else [('DeltaT_K', 'ΔT', COLORS[3], '')]:
                figure.series(((r['tiempo_h'], r[key]) for r in trace), x, y, color, dash)
    figure.save(FIG / 'H02_nucleo_S25_12kW.svg', STAMP + ' · límites 70 °C y 20 K; líneas muestreadas cada hora; máximos exactos en los JSON.')


def historical_cut(root):
    relative = 'resultados/incertidumbre/enfriamiento/u5_tope12/unica/tras_colocacion/visualizador.html'
    html = (root / relative).read_text(encoding='utf-8')
    data = json.loads(re.search(r'id="campo-datos" type="application/json">(.*?)</script>', html, re.S).group(1))
    field = np.asarray(data['campo'], dtype=float).reshape(data['forma'])
    assert np.isfinite(field).sum() == 5140 and np.allclose([np.nanmin(field), np.nanmax(field)], data['extremos'])
    step, origin = data['paso'], data['origen']
    indices = [int((value-base)/step) for value, base in zip(data['puntos'][0], origin)]
    ix, iy, iz = indices
    coords = [base + step*(index+0.5) for base, index in zip(origin, indices)]
    low, high = 17, 31
    stops = np.array([[31, 63, 112], [70,152,170], [240,224,137], [181,56,45]])

    def color(value):
        t = max(0, min(1, (value-low)/(high-low))) * 3
        k = min(2, int(t))
        components = (stops[k]+(stops[k+1]-stops[k])*(t-k)).astype(int)
        return '#' + ''.join(f'{v:02x}' for v in components)

    figure = Figure('Cortes ortogonales del campo térmico histórico',
                    'Única · M4_SS × ERA5-2024 · 428 h · 12,23 °C, tope 12 kW desde el término de la colocación', 650)
    cuts = [(field[iz,:,:], 100, 150, f'XY · z = {coords[2]:.2f} m', 'x [m]', 'y [m]'),
            (field[:,iy,:], 600, 170, f'XZ · y = {coords[1]:.2f} m', 'x [m]', 'z [m]'),
            (field[:,:,ix], 600, 365, f'YZ · x = {coords[0]:.2f} m', 'y [m]', 'z [m]')]
    cell = 10
    for arr, left, top, title, xlabel, ylabel in cuts:
        ny, nx = arr.shape
        figure.text(left, top-14, title.replace('.', ','), 17, bold=True)
        figure.rect(left, top, cell*nx, cell*ny, '#f0f4f8', '#c7d4df')
        for row, col in zip(*np.where(np.isfinite(arr))):
            figure.rect(left+cell*col, top+cell*(ny-row-1), cell+0.02, cell+0.02, color(arr[row,col]))
        figure.text(left+nx*cell/2, top+ny*cell+38, xlabel, 14, 'middle')
        figure.text(left-35, top+ny*cell/2, ylabel, 13, 'middle')
        y0 = 0 if ylabel.startswith('z') else -9
        for j in ([0, 4, 8] if ny == 9 else [0, 18, 36]):
            value = y0+j*step
            figure.text(left-6, top+ny*cell-j*cell+4, f'{value:g}', 11, 'end')
        for j in [0, 18, 36]:
            figure.text(left+j*cell, top+ny*cell+18, f'{-9+j*step:g}', 11, 'middle')
    left, bar_y = 625, 537
    for i in range(200):
        figure.rect(left+i*1.8, bar_y, 1.81, 17, color(low+(high-low)*i/199))
    for value in [17, 20, 23, 26, 29, 31]:
        figure.text(left+(value-low)/(high-low)*360, bar_y+37, f'{value} °C', 12, 'middle')
    figure.save(FIG / 'H03_cortes_12kW_428h.svg', STAMP + ' · centros de voxel de 0,50 m; S25 se evalúa aparte. Escala térmica común.')


def render(root, rows, summary, historic):
    duration_risk(summary)
    scenario_peaks(rows)
    duration_risk(summary, historical=historic)
    historical_curves(root)
    historical_cut(root)
