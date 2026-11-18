"""Gráfico del estudio de suelo ya calculado; no ejecuta simulaciones."""
import csv
import os
from pathlib import Path

RAIZ=Path(__file__).resolve().parents[2]
os.environ.setdefault('MPLCONFIGDIR',str(RAIZ/'.venv/cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def main():
    carpeta=RAIZ/'resultados/sensibilidad_suelo'
    with (carpeta/'comparacion_malla_0.5_paso900.csv').open(encoding='utf-8',newline='') as archivo:
        filas={f['variante']:f for f in csv.DictReader(archivo)}
    nombres=['base','temperatura_12','temperatura_18','temperatura_22','resistencia_mitad','resistencia_doble']
    if set(filas)!=set(nombres):
        raise ValueError('Primero completar las cinco variantes y la referencia.')
    etiquetas=['Base\n15 °C / R₀','12 °C\nR₀','18 °C\nR₀','22 °C\nR₀','15 °C\nR₀/2','15 °C\n2R₀']
    colores=['#52647e']+['#168278']*3+['#b67b28']*2
    x=np.arange(6)
    fig,axes=plt.subplots(1,2,figsize=(12,5.5))
    for ax,col,titulo,unidad,factor,limite in zip(axes,
            ['DeltaTmax_K','P_f'],['Peor diferencial térmico','Probabilidad conjunta'],
            ['ΔT máximo [°C]','P conjunta [%]'],[1,100],[20,5]):
        valores=[float(filas[n][col])*factor for n in nombres]
        ax.bar(x,valores,color=colores,width=.65)
        ax.axhline(limite,color='#a04040',ls='--',lw=1.2,label=f'Límite: {limite}'+(' °C' if factor==1 else ' %'))
        for i,v in enumerate(valores):
            ax.text(i,v+max(valores)*.018,f'{v:.2f}',ha='center',fontsize=10)
        ax.set(xticks=x,xticklabels=etiquetas,ylabel=unidad,title=titulo,
               ylim=(0,max(max(valores),limite)*1.18))
        ax.tick_params(axis='x',labelsize=9)
        ax.spines[['top','right']].set_visible(False)
        ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
        ax.legend(frameon=False,fontsize=9)
    fig.suptitle('Sensibilidad al suelo | Vertida única, h horario',fontsize=15,fontweight='bold')
    fig.text(.5,.045,'R₀ = 0,4167 m²·K/W. Temperatura y resistencia varían por separado.\n'
             '24 escenarios por caso; malla 0,50 m / paso máximo 900 s. Protecciones y extracción sin cambios.\n'
             'Estos casos cuantifican sensibilidad del reservorio equivalente; no validan el suelo del sitio.',
             ha='center',fontsize=9,color='#444')
    fig.subplots_adjust(left=.07,right=.985,top=.84,bottom=.27,wspace=.28)
    salida=carpeta/'figuras';salida.mkdir(exist_ok=True)
    fig.savefig(salida/'sensibilidad_suelo.png',dpi=170,facecolor='white')
    plt.close(fig)
    print(salida/'sensibilidad_suelo.png')


if __name__=='__main__':
    main()
