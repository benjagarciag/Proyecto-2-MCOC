"""Figuras y tablas de sensibilidad radiativa; solo lee corridas terminadas."""
import os,json,csv
from pathlib import Path
import numpy as np
RAIZ=Path(__file__).resolve().parents[2]
os.environ.setdefault('MPLCONFIGDIR',str(RAIZ/'.venv/cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ORIGEN=RAIZ/'resultados/sensibilidad_radiacion'
DESTINO=RAIZ/'entregas/F02/evidencia_radiacion'
NOMBRES={'sin_radiacion':'Sin radiación','solar':'Solo solar','larga':'Solo onda larga','ambas':'Solar + onda larga','clara':'Absortancia 0,2','oscura':'Absortancia 0,9','despejado':'Cielo despejado','giro90':'Orientación +90°'}
COLORES={'sin_radiacion':'#64748b','solar':'#d58b0c','larga':'#247bb3','ambas':'#be3e55'}


def leer(p):return json.loads(p.read_text(encoding='utf-8'))
def guardar(fig,nombre):
    fig.savefig(DESTINO/f'{nombre}.png',dpi=170,bbox_inches='tight');plt.close(fig)


def main():
    DESTINO.mkdir(parents=True,exist_ok=True)
    filas=[]
    for ruta in sorted(ORIGEN.glob('*/malla*/M*.json')):
        if not ruta.name.startswith('M'):continue
        d=leer(ruta);p=d['procedencia'];r=d['corrida']
        filas.append(dict(variante=p['variante'],curva=r['curva'],clima=r['clima'],malla_m=p['lado_m'],dtmax_s=p['paso_max_s'],Tmax_336_C=r['base_336h']['Tmax']['valor'],Delta_336_K=r['base_336h']['DeltaTmax']['valor'],Tmax_ext_C=r['Tmax']['valor'],Delta_ext_K=r['DeltaTmax']['valor'],horizonte_h=r['horizonte_h'],alerta=r['pico_no_resuelto']))
    with (DESTINO/'resultados.csv').open('w',encoding='utf-8-sig',newline='') as archivo:
        w=csv.DictWriter(archivo,fieldnames=list(filas[0]));w.writeheader();w.writerows(filas)
    fig,axs=plt.subplots(3,1,figsize=(11,9),sharex=True,layout='constrained')
    for v in ['sin_radiacion','solar','larga','ambas']:
        d=leer(ORIGEN/'ventana_comun_672'/f'{v}.json');hi=d['historia']
        t=np.array([x['tiempo_h'] for x in hi])/24
        for ax,k in zip(axs,['Tmax_C','Tmin_S25_C','DeltaT_K']):
            ax.plot(t,[x[k] for x in hi],label=NOMBRES[v],color=COLORES[v],lw=1)
    for ax,y in zip(axs,['Tmax hormigón [°C]','Tmin S25 [°C]','Diferencial [K]']):
        ax.set_ylabel(y);ax.grid(alpha=.2);ax.axvline(14,color='black',ls='--',lw=1)
        ax.axvspan(14,28,color='#64748b',alpha=.07)
    axs[0].legend(ncol=4,fontsize=9);axs[2].axhline(20,color='#be3e55',ls='--')
    axs[2].set(xlabel='Días desde primera colocación',xlim=(0,28))
    fig.suptitle('Efectos separados · M4_SS × ERA5-2024 · 0,40 m / 300 s\nFranja gris: seguimiento adicional al horizonte docente14d')
    guardar(fig,'01_historias_comparadas')
    m=leer(ORIGEN/'ambas/malla_0.4_paso300/matriz.json');rows=m['corridas']
    fig,axs=plt.subplots(2,1,figsize=(12,8),sharex=True,layout='constrained')
    for ax,campo in zip(axs,['base_336h',None]):
        antes=[];despues=[];etiquetas=[]
        for r in rows:
            old=leer(RAIZ/f"resultados/circuitos_histeresis/{r['curva']}_{r['clima']}.json")['corrida']
            antes.append((old[campo] if campo else old)['DeltaTmax']['valor'])
            despues.append((r[campo] if campo else r)['DeltaTmax']['valor'])
            etiquetas.append(r['curva']+'\n'+r['clima'][-4:])
        x=np.arange(24)
        if campo:
            ax.bar(x-.19,antes,.38,label='Sin radiación',color='#64748b');ax.bar(x+.19,despues,.38,label='Solar + onda larga',color='#be3e55')
        else:ax.bar(x,despues,.7,label='Solar + onda larga',color='#be3e55')
        ax.axhline(20,color='black',ls='--');ax.set_ylabel('Máximo diferencial [K]');ax.grid(axis='y',alpha=.2)
        ax.set_title('Horizonte docente:336h' if campo else 'Seguimiento extendido:600–672h')
    axs[0].legend();axs[1].set_xticks(range(24),etiquetas,rotation=60,ha='right',fontsize=8)
    fig.suptitle('24 pares · comparación homogénea a336h arriba; diagnóstico radiativo extendido abajo')
    guardar(fig,'02_catalogo_pareado')
    crit=max(rows,key=lambda r:r['DeltaTmax']['valor']);seleccion=[r for r in filas if r['curva']==crit['curva'] and r['clima']==crit['clima'] and r['variante'] in ['ambas','clara','oscura','despejado','giro90']]
    fig,ax=plt.subplots(figsize=(10,5),layout='constrained');x=np.arange(len(seleccion))
    ax.bar(x-.18,[r['Delta_336_K'] for r in seleccion],.36,label='336h',color='#247bb3')
    ax.bar(x+.18,[r['Delta_ext_K'] for r in seleccion],.36,label='Extendido',color='#be3e55')
    etiquetas=[NOMBRES[r['variante']]+f"\n{r['malla_m']:g}m/{r['dtmax_s']}s" for r in seleccion]
    ax.set_xticks(x,etiquetas,rotation=25,ha='right',fontsize=9);ax.axhline(20,color='black',ls='--');ax.set_ylabel('Máximo diferencial [K]');ax.grid(axis='y',alpha=.2);ax.legend()
    ax.set_title(f"Contrastes deterministas · {crit['curva']} × {crit['clima']}\nMalla 0,40 m / paso máximo 300 s")
    guardar(fig,'03_contrastes_y_refinamiento')
    seleccion=[r for r in filas if (r['curva'],r['clima'],r['variante'])==('M4_SS','ERA5-2024','ambas')]
    fig,axs=plt.subplots(1,2,figsize=(10,4.5),layout='constrained');x=np.arange(len(seleccion))
    for ax,k,y in zip(axs,['Delta_336_K','Delta_ext_K'],['336h','Extendido']):
        ax.bar(x,[r[k] for r in seleccion],color='#247bb3');ax.axhline(20,color='black',ls='--')
        ax.set_xticks(x,[f"{r['malla_m']:g}m\n{r['dtmax_s']}s" for r in seleccion]);ax.set(ylabel='Máximo diferencial [K]',title=y);ax.grid(axis='y',alpha=.2)
    fig.suptitle('Confirmación selectiva · M4_SS × ERA5-2024 · solar + onda larga')
    guardar(fig,'04_confirmacion_selectiva')
    print('Guardadas tablas y cuatro figuras en',DESTINO)


if __name__=='__main__':main()
