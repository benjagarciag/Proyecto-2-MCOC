"""Documenta las ocho fuentes existentes; no ejecuta simulaciones térmicas."""
from pathlib import Path
import csv
import hashlib
import json
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np

BASE = Path(__file__).resolve().parent
REPO = BASE.parents[2]
sys.path.insert(0, str(REPO / 'desarrollo'))
from mcplan.hidratacion_tabular import CurvaTabular

datos = REPO / 'datos/hidratacion'
original = datos / 'source_terms.txt'
raw = np.loadtxt(original)
manifiesto = json.loads((datos / 'manifiesto.json').read_text(encoding='utf-8'))
plt.rcParams.update({'font.size': 9, 'font.family': 'DejaVu Sans'})
fig = plt.figure(figsize=(9, 6.5), layout='constrained')
gs = fig.add_gridspec(2, 2)
ax0 = fig.add_subplot(gs[0, :])
ax1 = fig.add_subplot(gs[1, 0])
ax2 = fig.add_subplot(gs[1, 1])
colores = ['#0072B2', '#D55E00', '#009E73', '#8B56A5']
filas = []
for j, c in enumerate(manifiesto['curvas'], 1):
    valido = np.isfinite(raw[:, j])
    n = int(valido.sum())
    assert valido[:n].all() and not valido[n:].any(), 'Faltantes internos no previstos'
    q = raw[:n, j]
    assert (q >= 0).all()
    t_s = np.arange(n, dtype=float) * 600
    assert np.max(np.abs(raw[:n, 0] - t_s / 3600)) < 0.00034
    acumulado = np.r_[0., np.cumsum((q[:-1] + q[1:]) * 300)]
    archivado = np.genfromtxt(datos / c['csv'], delimiter=',', names=True)
    error_csv = float(np.max(np.abs(acumulado - archivado['acumulado'])))
    assert error_csv < 1e-6
    np.testing.assert_allclose(archivado['edad_h'] * 3600, t_s, rtol=0, atol=1e-8)
    curva = CurvaTabular(t_s, acumulado, c['rho_kg_m3'] * c['cp_J_kgK'])
    cortes = np.unique(np.r_[np.arange(0, t_s[-1], 300.), t_s[-1]])
    energia_solver = float(curva.energia_intervalo_J_m3(cortes[:-1], cortes[1:]).sum())
    error_integral = abs(energia_solver - acumulado[-1])
    assert error_integral < 1e-6
    color, estilo = colores[(j - 1) % 4], '-' if c['id'].endswith('_SS') else '--'
    etiqueta = c['id'].replace('_', ' ')
    ax0.plot(t_s / 3600, q, color=color, ls=estilo, lw=1.2, label=etiqueta)
    temprano = t_s <= 48 * 3600
    ax1.step(t_s[temprano] / 3600, curva.valor(t_s[temprano]), where='post',
             color=color, ls=estilo, lw=1.1)
    ax2.plot(t_s / 3600, acumulado / 1e6, color=color, ls=estilo, lw=1.2)
    filas.append(dict(curva=c['id'],muestras=n,fin_h=t_s[-1]/3600,
                      qmax_tabulado_W_m3=float(q.max()),ultima_fuente_W_m3=float(q[-1]),
                      calor_MJ_m3=float(acumulado[-1]/1e6),
                      error_max_csv_J_m3=error_csv,error_integral_J_m3=error_integral,
                      csv_sha256=hashlib.sha256((datos/c['csv']).read_bytes()).hexdigest()))
ax0.set(title='(a) Ocho fuentes tabuladas', ylabel='Fuente [W/m³]',
        xlabel='Edad desde inicio de ventana [h]', xlim=(0,245), ylim=(0,None))
ax0.legend(ncol=4, fontsize=8, frameon=False)
ax1.set(title='(b) Fuente efectiva: primeras 48 h', ylabel='Fuente [W/m³]',
        xlabel='Edad desde inicio de ventana [h]', xlim=(0,48), ylim=(0,None))
ax2.set(title='(c) Calor acumulado', ylabel='Calor [MJ/m³]',
        xlabel='Edad desde inicio de ventana [h]', xlim=(0,245), ylim=(0,None))
for ax in (ax0, ax1, ax2):
    ax.grid(alpha=.2)
    ax.spines[['top', 'right']].set_visible(False)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x,p: f'{x:g}'.replace('.', ',')))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x,p: f'{x:g}'.replace('.', ',')))
(BASE/'Imagenes').mkdir(exist_ok=True)
fig.savefig(BASE/'Imagenes/hidratacion_fuentes_calor.png', dpi=230, facecolor='white')
plt.close(fig)
(BASE/'datos').mkdir(exist_ok=True)
with (BASE/'datos/hidratacion_resumen.csv').open('w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(filas[0])); w.writeheader(); w.writerows(filas)
(BASE/'datos/hidratacion_verificacion.json').write_text(json.dumps(dict(
    original=str(original.relative_to(REPO)), sha256_original=hashlib.sha256(original.read_bytes()).hexdigest(),
    paso_fuente_s=600, paso_comprobacion_s=300, filas=filas,
    alcance='Comprobación de conversión tabular e integral; sin solver de conducción ni ajuste inverso nuevo.'
), ensure_ascii=False, indent=2), encoding='utf-8')
for fila in filas:
    print(fila['curva'], fila['fin_h'], fila['calor_MJ_m3'])
print('Máxima diferencia con CSV [J/m3]:', max(f['error_max_csv_J_m3'] for f in filas))
print('Máximo residuo de integral [J/m3]:', max(f['error_integral_J_m3'] for f in filas))
