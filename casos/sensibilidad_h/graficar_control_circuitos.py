"""Grafica resultado y estados de circuitos ya simulados; no calcula temperaturas."""
import json
import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
os.environ.setdefault('MPLCONFIGDIR',str(RAIZ/'.venv/cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    carpeta = RAIZ/'resultados/circuitos_histeresis'
    matriz = json.loads((carpeta/'matriz.json').read_text(encoding='utf-8'))
    f = max(matriz['corridas'],key=lambda f:f['DeltaTmax']['valor'])
    d = json.loads((carpeta/f'{f["curva"]}_{f["clima"]}.json').read_text(encoding='utf-8'))
    h = d['historia']
    fig,(ax,abajo) = plt.subplots(2,1,figsize=(12,8),sharex=True,gridspec_kw={'height_ratios':[2,1.25]})
    fig.subplots_adjust(left=.08,right=.97,top=.86,bottom=.16,hspace=.12)
    dias = [x['tiempo_h']/24 for x in h]
    for clave,label,color in [('Tmax_C','Tmax hormigón','#b54830'),('Tmin_S25_C','Tmin,S25','#1b74aa'),('DeltaT_K','ΔT','#743e99')]:
        ax.plot(dias,[x[clave] for x in h],label=label,color=color,lw=1.5)
    ax.axhline(20,color='#743e99',ls=':',label='Límite ΔT:20 °C')
    ax.set(ylabel='Temperatura / diferencia [°C]',ylim=(0,55))
    ax.legend(ncol=4,fontsize=9,loc='upper right')
    ax.grid(alpha=.15)
    fin = f['horizonte_h']/24
    for j in range(9):
        nombre = f'C{j+1:02}'
        eventos = [e for e in d['control']['eventos_circuitos'] if e['circuito']==nombre]
        abajo.broken_barh([(0,fin)],(j-.35,.7),facecolors='#e5e7eb')
        apertura = None
        intervalos = []
        for e in eventos:
            if e['abierto']:
                apertura = e['tiempo_h']/24
            elif apertura is not None:
                intervalos.append((apertura,e['tiempo_h']/24-apertura));apertura=None
        if apertura is not None: intervalos.append((apertura,fin-apertura))
        abajo.broken_barh(intervalos,(j-.35,.7),facecolors='#287b6a')
    abajo.set_yticks(range(9),[f'C{j+1:02}' for j in range(9)])
    abajo.invert_yaxis()
    abajo.set(xlabel='Días desde la primera colocación',ylabel='Circuito',xlim=(0,fin))
    abajo.grid(axis='x',alpha=.15)
    for a in (ax,abajo):
        a.axvline(14,color='#374151',ls='--',lw=1)
        a.set_xticks([t for t in [0,5,10,14,15,20,25,28] if t<=fin])
    fig.suptitle(f'Control por circuito: abre≥19 °C / cierra≤18 °C\n'
        f'Única progresiva a12 °C · agua18 °C · {f["curva"]} × {f["clima"]}',fontsize=15,ha='left',x=.08)
    fig.text(.08,.035,'Verde: circuito abierto; gris: cerrado. Línea vertical:14 días. La temperatura se muestrea junto a los tramos.\n'
        'Extracción volumétrica equivalente U=5, tope global15 kW; malla0,40 m y paso máximo300 s.\n'
        'Resultado exploratorio: no es un modelo detallado de transferencia en la pared del tubo.',fontsize=9,color='#4b5563')
    fig.savefig(carpeta/'control_y_temperaturas.png',dpi=170,bbox_inches='tight',facecolor='white')
    plt.close(fig)
    print(carpeta/'control_y_temperaturas.png')


if __name__ == '__main__':main()
