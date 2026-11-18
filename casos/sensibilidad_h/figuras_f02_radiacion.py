"""Tablas y gráficos de F02 actualizada; solo lee resultados con radiación336h."""
import os,csv,json
from pathlib import Path
import numpy as np
import familia_radiacion as motor

R=motor.RAIZ;S=motor.SALIDA
D=R/'entregas/F02/evidencia_f02_radiacion'
os.environ.setdefault('MPLCONFIGDIR',str(R/'.venv/cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'Segoe UI','font.size':12})
C={60:'#166c65',55:'#247bb3',50:'#b08416',45:'#a54369'}


def guardar(fig,nombre):
    fig.savefig(D/f'{nombre}.png',dpi=180,bbox_inches='tight',facecolor='white');plt.close(fig)


def tabla(nombre,filas):
    with (D/f'{nombre}.csv').open('w',encoding='utf-8-sig',newline='') as a:
        w=csv.DictWriter(a,fieldnames=list(filas[0]));w.writeheader();w.writerows(filas)


def main():
    D.mkdir(parents=True,exist_ok=True)
    resumen=motor.leer(S/'resumen.json');assert resumen['estado']=='APROBADA'
    planes=[];escenarios=[]
    for p in resumen['planes']:
        m=motor.leer(S/f"q{p['q']}"/f"malla_{p['h']:g}_paso300/matriz.json")
        planes.append(dict(q=p['q'],malla_m=p['h'],D_h=p['D_h'],horizonte_h=336,Tmax_C=p['Tmax'],DeltaTmax_K=p['Delta'],**p['riesgo']))
        for r in m['corridas']:
            escenarios.append(dict(q=p['q'],malla_m=p['h'],curva=r['curva'],clima=r['clima'],peso=r['peso'],Tmax_C=r['Tmax']['valor'],t_Tmax_h=r['Tmax']['tiempo_h'],DeltaTmax_K=r['DeltaTmax']['valor'],t_Delta_h=r['DeltaTmax']['tiempo_h'],Tmax_simultanea_C=r['DeltaTmax']['Tmax_C'],Tmin_S25_simultanea_C=r['DeltaTmax']['Tmin_S25_C'],P_f_indicador=int(r['excede_20'] or r['excede_70'])))
    tabla('comparacion_planes',planes);tabla('escenarios',escenarios)
    tabla('sensibilidad_espacial',resumen['cambios_espaciales']);tabla('sensibilidad_temporal',resumen['cambios_temporales'])
    tabla('refinos_alternativas',resumen['alternativas_finas'])
    d=motor.leer(S/'q60/malla_0.4_paso300/M4_SS_ERA5-2024.json');hist=d['historia'];t=np.array([r['tiempo_h'] for r in hist])
    fig,axs=plt.subplots(2,1,figsize=(11,7),sharex=True,layout='constrained')
    axs[0].plot(t,[r['Tmax_C'] for r in hist],label='Tmax hormigón',color='#b54830')
    axs[0].plot(t,[r['Tmin_S25_C'] for r in hist],label='Tmin S25',color='#247bb3');axs[0].legend();axs[0].set_ylabel('Temperatura [°C]')
    axs[1].plot(t,[r['DeltaT_K'] for r in hist],color='#743e99',label='ΔT simultáneo');axs[1].axhline(20,color='black',ls='--')
    e=d['corrida']['DeltaTmax'];axs[1].scatter([e['tiempo_h']],[e['valor']],color='#743e99')
    axs[1].set(xlim=(0,336),xlabel='Horas desde primera colocación',ylabel='Diferencial [K]')
    for a in axs:a.grid(alpha=.2)
    fig.suptitle('M4_SS × ERA5-2024 · solar + onda larga · 0,40 m / 300 s · 14 días')
    guardar(fig,'01_historia_336h')
    fig,axs=plt.subplots(1,2,figsize=(11,4.5),layout='constrained')
    for q in [60,55,50,45]:
        m=next(p for p in planes if p['q']==q and p['malla_m']==.4)
        axs[0].scatter(m['D_h'],100*m['P_union'],color=C[q],s=65,label=f'{q} m³/h')
        axs[1].bar(str(q),m['DeltaTmax_K'],color=C[q])
    axs[0].axhline(5,color='black',ls='--');axs[0].set(xlabel='Duración colocación [h]',ylabel='P(unión) del catálogo [%]',ylim=(-.5,6));axs[0].legend()
    axs[1].axhline(20,color='black',ls='--');axs[1].set(xlabel='Caudal [m³/h]',ylabel='Mayor ΔT336h [K]',ylim=(0,22))
    fig.suptitle('Cuatro planes con radiación · ventana común336h · 24 pares por plan')
    guardar(fig,'02_planes_riesgo_y_diferencial')
    cambios=resumen['cambios_espaciales'];fig,ax=plt.subplots(figsize=(11,6),layout='constrained')
    x=np.arange(len(cambios));ax.barh(x,[r['Delta'] for r in cambios],color='#743e99');ax.axvline(0,color='black',lw=.8)
    ax.set_yticks(x,[f"{r['curva']} / {r['clima'][-4:]}" for r in cambios],fontsize=9)
    ax.set(xlabel='ΔTmax(0,20 m) − ΔTmax(0,40 m) [K]',title='Sensibilidad espacial pareada · candidata60 · 24 pares · 336h')
    guardar(fig,'03_sensibilidad_espacial')
    fig,axs=plt.subplots(4,1,figsize=(11,10),sharex=True,layout='constrained')
    for ax,q in zip(axs,[60,55,50,45]):
        for p in sorted((S/f'q{q}/malla_0.4_paso300').glob('*.json')):
            if not p.name.startswith('M'):continue
            dd=motor.leer(p);hh=dd['historia'];ax.plot([r['tiempo_h'] for r in hh],[r['DeltaT_K'] for r in hh],lw=.7,alpha=.65)
        ax.axhline(20,color='black',ls='--');ax.set(ylabel=f'{q} m³/h\nΔT [K]',ylim=(0,22));ax.grid(alpha=.2)
    axs[-1].set(xlabel='Horas desde primera colocación',xlim=(0,336))
    fig.suptitle('24 historias por rendimiento · solar + onda larga · misma resolución')
    guardar(fig,'04_historias_por_plan')
    campos=np.load(S/'q60/malla_0.4_paso300/M4_SS_ERA5-2024.npz')
    ids=campos['ids'];origen=campos['origen_m'];h=float(campos['lado_m']);j=int(np.argmin(abs(origen[1]+(np.arange(ids.shape[1])+.5)*h)))
    xs=origen[0]+h*np.arange(ids.shape[2]+1);zs=origen[2]+h*np.arange(ids.shape[0]+1)
    fig,ax=plt.subplots(figsize=(12,5.5));A=np.where(ids[:,j,:]>0,campos['diferencial_T_C'][:,j,:],np.nan)
    im=ax.pcolormesh(xs,zs,A,cmap='inferno',vmin=20,vmax=45,shading='flat');ax.set(aspect='equal',xlim=(-9.2,9.2),ylim=(0,4.5),xlabel='x [m]',ylabel='z [m]')
    cb=fig.colorbar(im,ax=ax,orientation='horizontal',fraction=.1,pad=.3,aspect=40);cb.set_label('Temperatura de centro [°C]')
    guardar(fig,'05_corte_evento_267h')
    fig,axs=plt.subplots(1,4,figsize=(14,3.7),sharey=True,layout='constrained')
    for ax,q in zip(axs,[60,55,50,45]):
        npz=np.load(S/f'q{q}/malla_0.4_paso300/M4_SS_ERA5-2024.npz');A=np.where(ids[:,j,:]>0,npz['final_T_C'][:,j,:],np.nan)
        im=ax.pcolormesh(xs,zs,A,cmap='inferno',vmin=20,vmax=40,shading='flat');ax.set(title=f'{q} m³/h · 336h',aspect='equal',xlabel='x [m]',ylim=(0,4.5));ax.set_xticks([-9,0,9])
    axs[0].set_ylabel('z [m]');fig.colorbar(im,ax=axs,location='bottom',fraction=.12,aspect=50,label='Temperatura de centro [°C]')
    fig.suptitle('Mismo instante y escala · M4_SS × ERA5-2024 · corte y≈0')
    guardar(fig,'06_cortes_comunes_336h')
    fig,axs=plt.subplots(3,1,figsize=(12,6.6),sharex=True,layout='constrained')
    cfg=motor.leer(R/'casos/incertidumbre/parametros.json');manifest=motor.leer(R/'datos/clima/radiacion/manifiesto.json')
    from datetime import datetime
    for c in cfg['historias']:
        hr=motor.leer(R/manifest[c['id']]['snapshot'])['respuesta']['hourly']
        i=hr['time'].index(int(datetime.fromisoformat(c['inicio']).timestamp()))
        t=np.arange(337);aire=np.array(hr['temperature_2m'][i:i+337]);v=np.array(hr['wind_speed_10m'][i:i+337])
        ghi=np.array(hr['shortwave_radiation'][i+1:i+338])
        for ax,y in zip(axs,[aire,5.7+3.8*v*(2/10)**.14,ghi]):ax.plot(t,y,label=c['id'],lw=1)
    for ax,label in zip(axs,['Aire [°C]','h [W/(m² K)]','GHI [W/m²]']):ax.set_ylabel(label);ax.grid(alpha=.2)
    axs[0].legend(ncol=3,fontsize=10);axs[-1].set(xlabel='Horas desde primera colocación',xlim=(0,336))
    guardar(fig,'07_clima_radiacion')
    # Datos específicos de la presentación, con evidencia y gráficos editables.
    datos=dict(resumen=resumen,planes=planes,escenarios=escenarios,evento=e,pico=d['corrida']['Tmax'],historia=hist,
        fuentes=motor.leer(R/'entregas/F02/presentacion/recursos/datos.json')['fuentes'],
        fuentes_t=motor.leer(R/'entregas/F02/presentacion/recursos/datos.json')['fuentes_t'])
    (D/'datos_presentacion.json').write_text(json.dumps(datos,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Actualizadas tablas,7 figuras y datos de presentación en',D)


if __name__=='__main__':main()
