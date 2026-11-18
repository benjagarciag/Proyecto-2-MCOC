"""Cota constructiva D=V/q; gráfico analítico, sin solver térmico."""
import json
import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
os.environ.setdefault('MPLCONFIGDIR',str(RAIZ/'.venv/cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def main():
    ruta = RAIZ/'resultados/controles_12c/unica_15kw_12c/malla_0.5_paso900/unica_15kw_12c.json'
    d = json.loads(ruta.read_text(encoding='utf-8'))
    volumen = sum(v['volumen_m3'] for v in d['plan'])
    limite = 60.
    minimo = volumen/limite
    fig,ax = plt.subplots(figsize=(11.5,6.3))
    fig.subplots_adjust(left=.085,right=.97,top=.82,bottom=.23)
    ax.axvspan(20,60,color='#deece3',alpha=.65)
    ax.axvspan(60,95,color='#f5e4d4',alpha=.65)
    q = np.linspace(20,60,200)
    ax.plot(q,volumen/q,color='#246e53',lw=2.8,label='Duración continua con capacidad disponible')
    q = np.linspace(60,95,140)
    ax.plot(q,volumen/q,color='#ba722e',lw=2.5,ls='--',label='Exige aumentar capacidad: fuera del supuesto')
    ax.axvline(limite,color='#273d57',lw=1.4,ls=':')
    ax.axhline(minimo,color='#273d57',lw=1.4,ls=':')
    for q,offset in [(30,(10,10)),(45,(-70,12)),(75,(-5,21)),(90,(-50,-20))]:
        t = volumen/q
        ax.scatter(q,t,color='#246e53' if q<60 else '#ba722e',s=42,zorder=4)
        ax.annotate(f'{q} m³/h → {t:.2f} h'.replace('.',','),(q,t),xytext=offset,
                    textcoords='offset points',fontsize=10,color='#334155')
    ax.scatter(limite,minimo,color='#155b8b',s=115,zorder=5)
    ax.annotate('60 m³/h → 10,61 h\nMínimo constructivo con estos recursos',
        (limite,minimo),xytext=(61.8,17.7),arrowprops=dict(arrowstyle='->',color='#155b8b'),
        fontsize=11,color='#155b8b',weight='bold')
    ax.text(36,29,'Ritmos menores:\nmayor duración',ha='center',fontsize=11,color='#246e53')
    ax.text(77,25.8,'Ritmos mayores:\nrequieren más capacidad',ha='center',fontsize=11,color='#986027')
    ax.set(xlim=(20,95),ylim=(4,33),xlabel='Caudal efectivo total q [m³/h]',
           ylabel='Duración de colocación continua D = V/q [h]')
    ax.set_xticks([20,30,40,45,50,60,75,90])
    ax.grid(alpha=.18)
    ax.legend(loc='upper right',fontsize=9,framealpha=.95)
    fig.suptitle('Por qué 10,61 horas es la cota mínima del escenario\n'
        'Volumen IFC: 636,775 m³ · capacidad total máxima supuesta: 60 m³/h',
        fontsize=15,ha='left',x=.085)
    fig.text(.085,.045,'Relación analítica de volumen y caudal; no es una curva de riesgo térmico.\n'
        '60 m³/h = dos frentes de 30 m³/h. Las esperas aumentan D.\n'
        'Alcanzar esta cota no demuestra cumplimiento térmico: confirmar colocación progresiva y enfriamiento.',
        fontsize=10,color='#4b5563')
    salida = RAIZ/'resultados/controles_12c/figuras'
    salida.mkdir(parents=True,exist_ok=True)
    for extension in ('png','svg'):
        fig.savefig(salida/f'caudal_duracion_cota_minima.{extension}',dpi=170,bbox_inches='tight',facecolor='white')
    plt.close(fig)
    print(salida/'caudal_duracion_cota_minima.png')


if __name__ == '__main__':
    main()
