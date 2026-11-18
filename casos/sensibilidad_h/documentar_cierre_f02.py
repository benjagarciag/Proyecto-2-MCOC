"""Prepara evidencia de F02 §§4–6 sin modificar presentacion ni guion personalizado."""
from pathlib import Path
import csv,json,os,sys
from hashlib import sha256
import numpy as np

R=Path(__file__).resolve().parents[2];S=R/'resultados/cierre_f02';D=R/'entregas/F02/cierre_revision_final'
os.environ.setdefault('MPLCONFIGDIR',str(R/'.venv/cache/matplotlib'))


def leer(p):return json.loads(p.read_text(encoding='utf8'))


def tabla(nombre,rs):
    with (D/nombre).open('w',encoding='utf-8-sig',newline='') as a:
        w=csv.DictWriter(a,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)


def main():
    resumen=leer(S/'resumen.json');assert resumen['estado']=='APROBADA'
    D.mkdir(parents=True,exist_ok=True)
    configuracion=leer(D/'CONFIGURACION_FINAL_REVISADA.json')
    origenes={'familia':'Supuesto docente de capacidad y familia de decision declarada',
        'tiempo':'F02 y configuracion de inicio; duracion calculada por volumen/caudal',
        'geometria':'IFC/IfcOpenShell, esquema de capas y aproximacion de activacion',
        'hormigon':'rho/cp del archivo del profesor; k=2 supuesto no calibrado',
        'protecciones':'Espesores/conductividades de referencia docente; retiros son decisiones ensayadas',
        'sombra':'Hipotesis de ensayo; no producto o montaje acreditados',
        'ambiente':'Snapshots ERA5/Open-Meteo; correlacion h y restantes hipotesis radiativas declaradas',
        'suelo':'Reservorio equivalente supuesto, sin inercia ni medicion de sitio',
        'frio':'Anteproyecto y transferencia equivalente idealizados, no dimensionamiento real',
        'fuentes':'Ocho fuentes completas del profesor y procesamiento tabular conservativo',
        'probabilidad':'Hipotesis de escenarios/pesos y criterios docentes de F02',
        'numerico':'Balance propio, limites del esquema y sensibilidad numerica',
        'limitaciones':'Alcance declarado del modelo'}
    parametros=[]
    def recorrer(valor,ruta):
        if isinstance(valor,dict):
            for k,v in valor.items():recorrer(v,ruta+[k])
        else:parametros.append(dict(parametro='.'.join(ruta),valor=json.dumps(valor,ensure_ascii=False),
            procedencia_o_estado=origenes.get(ruta[0],'Configuracion final del proyecto')))
    recorrer(configuracion,[]);tabla('PARAMETROS_FINAL.csv',parametros)
    filas=[];planes=[];balances=[]
    for q,h in [(60,.4),(55,.4),(60,.2)]:
        carpeta=S/f'q{q}/malla_{h:g}_paso300';m=leer(carpeta/'matriz.json')
        planes.append(dict(plan=f'{q}m3h_malla{h}',q_m3_h=q,malla_m=h,D_h=m['D_h'],horizonte_h=672,
            Tmax_C=m['Tmax'],DeltaT_K=m['Delta'],**m['riesgo'],cumple=m['riesgo']['P_union']<=.05,alertas=m['alertas']))
        for a in m['archivos']:
            d=leer(R/a['ruta']);r=d['corrida']
            for H,rr in [(336,d['base_336h']),(672,r)]:
                b=rr['balance_J']
                balances.append(dict(q_m3_h=q,malla_m=h,horizonte_h=H,curva=r['curva'],clima=r['clima'],
                    **{k+'_J':b[k] for k in ['colocacion','hidratacion','aire','suelo','enfriamiento','final','residuo']}))
                filas.append(dict(plan=f'{q}m3h',q_m3_h=q,malla_m=h,paso_max_s=300,horizonte_h=H,
                    curva=r['curva'],clima=r['clima'],peso=r['peso'],M_T_C=rr['Tmax']['valor'],
                    M_Delta_K=rr['DeltaTmax']['valor'],I_T=int(rr['excede_70']),I_Delta=int(rr['excede_20']),
                    I_F=int(rr['excede_70'] or rr['excede_20']),
                    t_Tmax_h=rr['Tmax']['tiempo_h'],fase_Tmax=rr['Tmax']['fase'],xyz_Tmax_m=json.dumps(rr['Tmax']['xyz_Tmax_m']),
                    t_Delta_h=rr['DeltaTmax']['tiempo_h'],fase_Delta=rr['DeltaTmax']['fase'],Tmax_simultanea_C=rr['DeltaTmax']['Tmax_C'],
                    Tmin_S25_simultanea_C=rr['DeltaTmax']['Tmin_S25_C'],
                    xyz_Tmax_en_Delta_m=json.dumps(rr['DeltaTmax']['xyz_Tmax_m']),
                    xyz_S25_en_Delta_m=json.dumps(rr['DeltaTmax']['xyz_S25_m']),archivo=a['ruta']))
    tabla('METRICAS_144_FILAS.csv',filas);tabla('COMPARACION_PLANES.csv',planes)
    tabla('BALANCES_144_FILAS.csv',balances)
    tabla('SENSIBILIDAD_ESPACIAL_24_PARES.csv',resumen['cambios_espaciales'])
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    colores={60:'#166c65',55:'#247bb3'}
    fig,ax=plt.subplots(figsize=(8,4.8),layout='constrained')
    for q in [60,55]:
        m=next(x for x in planes if x['q_m3_h']==q and x['malla_m']==.4)
        ax.scatter(m['D_h'],100*m['P_union'],color=colores[q],s=90,label=f'{q} m³/h · 0,40 m')
        ax.annotate(f"{m['D_h']:.3f} h",(m['D_h'],0),xytext=(0,12),textcoords='offset points',ha='center')
    ax.axhline(5,color='black',ls='--',label='Meta 5 %');ax.axvline(planes[0]['D_h'],color='#166c65',ls=':',label='Cota V/60')
    ax.set(xlabel='Duración de colocación D [h]',ylabel='P de exceder algún límite [%]',ylim=(-.5,6),
        title='Misma protección 504 h + sombra 90 % · 24 pares · 0–672 h')
    ax.legend(loc='center right');ax.grid(alpha=.2)
    fig.savefig(D/'01_D_VS_PROBABILIDAD.png',dpi=180);plt.close(fig)
    esquema=leer(R/'resultados/diseno_circuitos_colocacion/esquema.json')
    fig,ax=plt.subplots(figsize=(11,3.5),layout='constrained')
    for y,q in enumerate([60,55]):
        for c in esquema['capas']:
            inicio=c['inicio_h']*60/q;dur=c['duracion_h']*60/q
            ax.barh(y,dur,left=inicio,color=colores[q],edgecolor='white',height=.45)
            if dur>.35:ax.text(inicio+dur/2,y,str(c['id']),ha='center',va='center',color='white',fontsize=9)
    ax.set(yticks=[0,1],yticklabels=['60 m³/h · propuesta continua','55 m³/h · vecina lenta'],
        xlabel='Horas desde t₀ = 19/11/2026 10:00 UTC−03:00',title='Once capas físicas · sin esperas · mismas capacidades disponibles')
    ax.grid(axis='x',alpha=.2);fig.savefig(D/'02_CRONOGRAMAS.png',dpi=180);plt.close(fig)
    datos={q:leer(S/f'q{q}/malla_0.4_paso300/M4_SS_ERA5-2024.json') for q in [60,55]}
    fig,axs=plt.subplots(3,1,figsize=(12,9),sharex=True,layout='constrained')
    for q,d in datos.items():
        h=d['historia'];t=[r['tiempo_h'] for r in h];e=d['corrida']['DeltaTmax']
        puntos=[(r['tiempo_h'],1,r['Tmax_C'],r['Tmin_S25_C'],r['DeltaT_K']) for r in h]
        puntos.append((e['tiempo_h'],0,e['Tmax_C'],e['Tmin_S25_C'],e['valor']))
        puntos.sort(key=lambda x:(x[0],x[1]));tx=[x[0] for x in puntos]
        caliente=[(x[0],x[1],x[2]) for x in puntos]
        pico=d['corrida']['Tmax'];caliente.append((pico['tiempo_h'],0,pico['valor']));caliente.sort()
        axs[0].plot([x[0] for x in caliente],[x[2] for x in caliente],color=colores[q],label=f'{q} m³/h · Tmax')
        axs[0].plot(tx,[x[3] for x in puntos],color=colores[q],ls='--',label=f'{q} m³/h · Tmin,S25')
        axs[1].plot(t,[np.nan if r['nucleo_C'] is None else r['nucleo_C'] for r in h],color=colores[q],label=f'{q} m³/h · sonda interior')
        axs[2].plot(tx,[x[4] for x in puntos],color=colores[q],label=f'{q} m³/h')
        axs[2].scatter([e['tiempo_h']],[e['valor']],color=colores[q],s=25)
        axs[2].annotate(f"{q}: {e['valor']:.2f} K a {e['tiempo_h']:.2f} h",(e['tiempo_h'],e['valor']),
            xytext=(12,10 if q==55 else -23),textcoords='offset points',fontsize=8,color=colores[q],
            bbox=dict(facecolor='white',edgecolor='none',alpha=.85,pad=1))
    axs[0].axhline(70,color='black',ls='--',label='70 °C');axs[2].axhline(20,color='black',ls='--',label='20 K')
    for a,yl in zip(axs,['Temperatura [°C]','Sonda interior [°C]','ΔT simultáneo [K]']):
        a.axvline(336,color='black',ls=':',lw=1);a.axvline(504,color='#999999',ls=':',lw=1)
        a.set_ylabel(yl);a.grid(alpha=.2);a.legend(fontsize=8,ncol=2)
    axs[-1].set(xlabel='Tiempo desde primera colocación [h]',xlim=(0,672))
    fig.suptitle('M4_SS × ERA5-2024 · 0,40 m / 300 s · sonda (0,0,2 m), Tmax y S25 distintos')
    fig.savefig(D/'03_CURVAS_COMPARABLES.png',dpi=180);plt.close(fig)
    fig,axs=plt.subplots(2,2,figsize=(12,5.4),sharey=True,layout='constrained')
    for fila,evento in enumerate(['diferencial','final']):
        horas=[]
        for ax,q in zip(axs[fila],[60,55]):
            p=np.load(S/f'q{q}/malla_0.4_paso300/M4_SS_ERA5-2024.npz');ids=p['ids'];o=p['origen_m'];h=float(p['lado_m'])
            j=int(np.argmin(abs(o[1]+(np.arange(ids.shape[1])+.5)*h)))
            A=np.where(ids[:,j,:]>0,p[evento+'_T_C'][:,j,:],np.nan);hora=float(p[evento+'_tiempo_h']);horas.append(hora)
            im=ax.pcolormesh(o[0]+h*np.arange(ids.shape[2]+1),o[2]+h*np.arange(ids.shape[0]+1),A,cmap='inferno',vmin=10,vmax=45)
            ax.set(aspect='equal',title=f'{q} m³/h · {hora:g} h',xlabel='x [m]');ax.set_ylim(0,4.5)
        assert abs(horas[0]-horas[1])<1e-9
        axs[fila,0].set_ylabel('z [m]')
    fig.colorbar(im,ax=axs,location='bottom',label='Temperatura de centro [°C] · criterio Tmax incluye también caras',fraction=.1,aspect=50)
    fig.suptitle('M4_SS × ERA5-2024 · 0,40 m / 300 s · corte y≈0 · misma hora y escala por fila')
    fig.savefig(D/'04_CORTES_COMPARABLES_672H.png',dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(11,6.5),layout='constrained')
    cambios=resumen['cambios_espaciales'];x=np.arange(len(cambios))
    ax.barh(x,[r['Delta'] for r in cambios],color='#743e99');ax.axvline(0,color='black',lw=.8)
    ax.set(yticks=x,yticklabels=[f"{r['curva']} / {r['clima'][-4:]}" for r in cambios],
        xlabel='ΔTmax(0,20 m) − ΔTmax(0,40 m) [K]',title='Propuesta con protección nueva · 24 pares completos · 0–672 h')
    ax.tick_params(axis='y',labelsize=8);fig.savefig(D/'05_SENSIBILIDAD_24_PARES.png',dpi=180);plt.close(fig)
    fuentes=leer(R/'datos/hidratacion/manifiesto.json')['curvas']
    raw=np.loadtxt(R/'datos/hidratacion/source_terms.txt');fuentes_tabla=[]
    fig,axs=plt.subplots(1,2,figsize=(12,5),layout='constrained')
    for j,c in enumerate(fuentes,1):
        q=raw[:,j];q=q[np.isfinite(q)];t=np.arange(len(q))/6
        E=float(np.sum((q[:-1]+q[1:])*300))
        csv_original=np.genfromtxt(R/'datos/hidratacion'/c['csv'],delimiter=',',names=True)
        assert abs(E-csv_original['acumulado'][-1])<1e-6
        fuentes_tabla.append(dict(curva=c['id'],peso=c['peso'],fin_h=t[-1],Qmax_W_m3=float(q.max()),calor_total_J_m3=E))
        color=plt.cm.tab10((j-1)%4)
        axs[0].plot(t,q,color=color,ls='-' if c['id'].endswith('_SS') else '--',label=c['id'])
    axs[0].set(xlabel='Edad desde ventana retenida [h]',ylabel='Q [W/m³]',title='Ocho fuentes completas del profesor');axs[0].legend(fontsize=8,ncol=2);axs[0].grid(alpha=.2)
    axs[1].bar(range(8),[x['calor_total_J_m3']/1e6 for x in fuentes_tabla],color=[plt.cm.tab10(i%4) for i in range(8)])
    for j,r in enumerate(fuentes_tabla):axs[1].text(j,r['calor_total_J_m3']/1e6+.8,f"{r['calor_total_J_m3']/1e6:.1f}",ha='center',fontsize=8)
    axs[1].set(xticks=range(8),xticklabels=[x['curva'] for x in fuentes_tabla],ylabel='Calor integrado [MJ/m³]',title='Trapecios de 600 s · cola posterior nula supuesta');axs[1].tick_params(axis='x',rotation=45)
    tabla('OCHO_FUENTES_VERIFICADAS.csv',fuentes_tabla)
    fig.savefig(D/'06_OCHO_FUENTES_Y_CALOR.png',dpi=180);plt.close(fig)
    from datetime import datetime
    cfg=leer(R/'casos/incertidumbre/parametros.json');manifest=leer(R/'datos/clima/radiacion/manifiesto.json')
    fig,axs=plt.subplots(3,1,figsize=(12,7),sharex=True,layout='constrained')
    for c in cfg['historias']:
        hr=leer(R/manifest[c['id']]['snapshot'])['respuesta']['hourly'];i=hr['time'].index(int(datetime.fromisoformat(c['inicio']).timestamp()))
        axs[0].plot(np.arange(673),hr['temperature_2m'][i:i+673],label=c['id'],lw=.8)
        v=np.array(hr['wind_speed_10m'][i:i+673]);axs[1].plot(np.arange(673),5.7+3.8*v*(2/10)**.14,lw=.8)
        axs[2].plot(np.arange(672)+.5,hr['shortwave_radiation'][i+1:i+673],lw=.8)
    for a,y in zip(axs,['Aire [°C]','h [W/(m² K)]','GHI media horaria [W/m²]']):a.set_ylabel(y);a.grid(alpha=.2);a.axvline(336,color='black',ls=':',lw=1)
    axs[0].legend(ncol=3,fontsize=9);axs[-1].set(xlabel='Horas desde inicio de cada bloque histórico',xlim=(0,672))
    fig.suptitle('ERA5 de El Rosal · tres historias completas · mismo período del año')
    fig.savefig(D/'07_CLIMA_672H.png',dpi=180);plt.close(fig)
    sys.path.insert(0,str(R/'desarrollo'))
    from mcplan.difusion_1d import Parametros1D,resolver_1d,solucion_exacta
    par=Parametros1D(**leer(R/'casos/1d/verificacion_seno.json'));sol=resolver_1d(par)
    error=float(np.max(abs(sol.temperatura_C-solucion_exacta(par,sol.x_m[None,:],sol.tiempos_s[:,None]))))
    verificacion=dict(caso='seno1D exacto',error_max_K=error,tests_difusion_1d=24,
        observacion='Verifica el componente difusivo1D; no valida experimentalmente la fundacion3D.',
        balance_max_residuo_J=resumen['max_residuo_J'],balance_max_residuo_relativo=resumen['max_residuo_relativo'])
    (D/'VERIFICACION.json').write_text(json.dumps(verificacion,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (D/'DATOS_CIERRE.json').write_text(json.dumps(dict(resumen=resumen,planes=planes,verificacion=verificacion),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    rutas=set(S.rglob('*.json'))|set(S.rglob('*.npz'))|set(D.glob('*'))
    rutas.update((R/'datos/hidratacion').glob('*'))
    rutas.update([R/'requirements.txt',R/'desarrollo/fundacion/fundacion.ifc',R/'entregas/F02/CIERRE_PUNTOS_RESTANTES.md',
        R/'resultados/diseno_circuitos_colocacion/esquema.json',R/'datos/clima/radiacion/manifiesto.json'])
    for c in cfg['historias']:
        rutas.add(R/c['snapshot']);rutas.add(R/manifest[c['id']]['snapshot'])
    for nombre in ['cierre_f02.py','cierre_f02.json','auditar_cierre_f02.py','documentar_cierre_f02.py','ejecutar_cierre_f02.py',
        'proteccion_postdesmolde.py','proteccion_postdesmolde.json','radiacion_borde.py','radiacion_config.json',
        'sensibilidad_radiacion.py','comparar_circuitos.py','simular_circuitos.py','control_circuitos.py','viento.py','ejecutar.py','cache_geometria_circuitos.py']:
        rutas.add(R/'casos/sensibilidad_h'/nombre)
    archivos=[dict(ruta=str(p.relative_to(R)),bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
        for p in sorted(rutas) if p.is_file() and p.name!='MANIFIESTO_EVIDENCIA.json']
    (D/'MANIFIESTO_EVIDENCIA.json').write_text(json.dumps(dict(
        alcance='Inventario de evidencia principal; no copia de entorno ni SHA final de defensa.',
        solver_base_git='6718163118123c4b05667b91ad5b4d50124dcf2d',archivos=archivos),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Generadas tablas144filas, siete figuras y verificacion. Error seno:',error)


if __name__=='__main__':main()
