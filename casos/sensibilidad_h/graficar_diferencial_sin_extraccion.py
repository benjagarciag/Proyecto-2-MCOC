"""Grafica tres métricas de evidencia existente; no ejecuta el solver."""
import json
import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
os.environ.setdefault('MPLCONFIGDIR', str(RAIZ/'.venv/cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    ruta = RAIZ/'resultados/planes_sin_extraccion/unica/malla_0.5_paso900/unica_12c_estratos_sin_extraccion.json'
    d = json.loads(ruta.read_text(encoding='utf-8'))
    f = max(d['corridas'], key=lambda x:x['DeltaTmax']['valor'])
    historia = f['historia']
    x = [h['tiempo_h']/24 for h in historia]
    fig, ax = plt.subplots(figsize=(12, 7.2))
    fig.subplots_adjust(left=.075, right=.98, top=.85, bottom=.21)
    colores = {'Tmax_C':'#ba432d', 'Tmin_S25_C':'#166eac', 'DeltaT_K':'#7439a1'}
    etiquetas = {'Tmax_C':'Tmax del hormigón', 'Tmin_S25_C':'Tmin en S25 (≈25 mm)', 'DeltaT_K':'ΔT = Tmax − Tmin,S25'}
    for k in colores:
        ax.plot(x, [h[k] for h in historia], color=colores[k], lw=2, label=etiquetas[k])
    ax.axhline(20, color='#7439a1', ls=':', lw=1.5, label='Límite de ΔT: 20 °C')
    ax.axvline(14, color='#202b38', ls='--', lw=1.5)
    ax.axvspan(0, 14, color='#8cabc3', alpha=.07)
    ax.text(14.15, 54, '14 días\n(336 h)', va='top', fontsize=10, color='#202b38')
    for retiro, texto in [(240, 'Retiro de 1.ª capa'), (480, 'Retiro de 2.ª capa')]:
        comienzos = [g['start_h']+retiro for g in d['grupos_de_activacion']]
        a, b = min(comienzos)/24, max(comienzos)/24
        ax.axvspan(a, b, color='#d49a37', alpha=.23)
        ax.text(a-.12, 54, texto, rotation=90, va='top', ha='right', fontsize=9, color='#795318')
    pico = f['DeltaTmax']
    dia = pico['tiempo_h']/24
    for k, valor in [('Tmax_C',pico['Tmax_C']), ('Tmin_S25_C',pico['Tmin_S25_C']), ('DeltaT_K',pico['valor'])]:
        ax.scatter([dia], [valor], color=colores[k], s=34, zorder=5)
        ax.annotate(f'{valor:.2f} °C', (dia, valor), xytext=(-7, 9), textcoords='offset points',
                    ha='right', fontsize=10, color=colores[k], weight='bold')
    ax.set(xlim=(0,max(x)), ylim=(0,56), xlabel='Días desde el inicio de la primera vertida',
           ylabel='Temperatura / diferencia de temperatura [°C]')
    ax.set_xticks([0,3,5,10,14,15,20,25])
    ax.grid(alpha=.17)
    ax.legend(loc='lower left', fontsize=9, framealpha=.95, ncol=2)
    ax.set_title('Cómo se forma el diferencial térmico\n'
                 f'Única progresiva · colocación 12 °C · sin extracción · {f["curva"]} × {f["clima"]}',
                 fontsize=14, loc='left', pad=14)
    fig.text(.02, .035,
        'Escenario con mayor ΔT del catálogo; no es una curva promedio. Malla 0,50 m / paso máximo 900 s.\n'
        'Bandas: retiros por edad de cada estrato. Curvas de historia guardada; puntos: máximo registrado por paso.\n'
        'Tmax y Tmin pueden cambiar de ubicación. Límite de Tmax = 70 °C (fuera de la escala).', fontsize=9, color='#4b5563')
    salida = RAIZ/'resultados/planes_sin_extraccion/figuras'
    salida.mkdir(parents=True, exist_ok=True)
    png = salida/'tmax_tmin_s25_delta_unica.png'
    fig.savefig(png, dpi=170, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(png)
    print('Mismo escenario a336 h:', f['base_336h']['DeltaTmax'])


if __name__ == '__main__':
    main()
