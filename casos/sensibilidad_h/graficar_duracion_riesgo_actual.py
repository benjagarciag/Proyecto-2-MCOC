"""Duración–riesgo: única calculada y comparación pendiente, sin inventar puntos."""
import json
import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
os.environ.setdefault('MPLCONFIGDIR',str(RAIZ/'.venv/cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    ruta = RAIZ/'resultados/controles_12c/unica_15kw_12c/malla_0.5_paso900/unica_15kw_12c.json'
    d = json.loads(ruta.read_text(encoding='utf-8'))
    volumen = sum(v['volumen_m3'] for v in d['plan'])
    minimo = volumen/d['capacidad_m3_h']
    fig,ax = plt.subplots(figsize=(11,6))
    fig.subplots_adjust(left=.09,right=.97,top=.82,bottom=.34)
    ax.axvspan(0,minimo,color='#e8b9b1',alpha=.5)
    ax.text(minimo/2,17,'Menos de 10,61 h\nrequiere más de 60 m³/h',ha='center',va='center',fontsize=10,color='#7b3325')
    ax.axvline(minimo,color='#384b5d',ls='--',lw=1.4)
    ax.axhspan(0,5,color='#a8ceb4',alpha=.25)
    ax.axhline(5,color='#42835c',ls=':',label='Máximo admisible: 5 %')
    ax.scatter([d['D_h']],[100*d['riesgo']['P_union']],s=100,color='#17678d',zorder=5)
    ax.annotate('Única calculada: 10,61 h; 0/24 excedencias\nResultado exploratorio; falta confirmación',
        (d['D_h'],0),xytext=(15,10),arrowprops=dict(arrowstyle='->',color='#17678d'),fontsize=10,color='#17678d')
    ax.text(27,21,'Aún faltan los riesgos de las otras duraciones\ncon los mismos 12 °C / 15 kW.\nNo se dibuja una frontera térmica sin esos datos.',
        ha='center',va='center',fontsize=10,color='#4b5563')
    ax.set(xlim=(0,40),ylim=(-1.5,28),xlabel='Tiempo total de colocación D [h]',ylabel='Probabilidad conjunta de excedencia [%]')
    ax.set_xticks([0,10.6129,15.6396,24.6396,36.6396],['0','10,61','15,64','24,64','36,64'])
    ax.grid(alpha=.15)
    ax.legend(loc='upper left',fontsize=9)
    fig.suptitle('¿Cuál es el menor tiempo de colocación factible?\nCapacidad total supuesta: 60 m³/h · volumen: 636,775 m³',fontsize=15,x=.09,ha='left')
    tabla = ax.table(cellText=[['Única','10,61','0 % (exploratorio)'],['Rápida','15,64','Pendiente'],
        ['Referencia','24,64','Pendiente'],['Lenta','36,64','Pendiente']],
        colLabels=['Plan','D [h]','Riesgo a 12 °C / 15 kW'],cellLoc='center',bbox=[0,-.57,1,.37])
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(10)
    fig.text(.09,.018,'El punto usa activación instantánea, h horario, malla 0,50 m y paso máximo 900 s.\n'
        'No certifica todavía operación construible, resolución final ni riesgo real. El mínimo V/q depende del caudal supuesto.',fontsize=9,color='#4b5563')
    salida = RAIZ/'resultados/controles_12c/figuras'
    salida.mkdir(parents=True,exist_ok=True)
    png = salida/'duracion_riesgo_estado_actual.png'
    fig.savefig(png,dpi=160,bbox_inches='tight',facecolor='white')
    plt.close(fig)
    print(png)


if __name__ == '__main__':
    main()
