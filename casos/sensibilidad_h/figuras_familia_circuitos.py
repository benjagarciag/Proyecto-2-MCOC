"""Tablas y figuras de la familia homogénea; lee resultados, no simula."""
import argparse
import csv
from hashlib import sha256
import json
import os
from pathlib import Path
import numpy as np

RAIZ=Path(__file__).resolve().parents[2]
os.environ.setdefault('MPLCONFIGDIR',str(RAIZ/'.venv/cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

SALIDA=RAIZ/'entregas/F02/evidencia_circuitos'
FIG=SALIDA/'figuras'
COLORES={60:'#166c65',55:'#2f74b5',50:'#ac6e16',45:'#a54369'}


def leer(p):return json.loads(Path(p).read_text(encoding='utf-8'))


def guardar(fig,nombre):
    fig.savefig(FIG/f'{nombre}.png',dpi=170,bbox_inches='tight',facecolor='white')
    plt.close(fig)


def csv_guardar(nombre,filas):
    with (SALIDA/nombre).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(filas[0]));w.writeheader();w.writerows(filas)


def datos():
    raw=np.loadtxt(RAIZ/'datos/hidratacion/source_terms.txt')
    ids=[f'M{i}_{camp}' for camp in ['SS','22A'] for i in range(1,5)]
    fig,axs=plt.subplots(1,2,figsize=(11,4.3),sharey=True,layout='constrained')
    controles=[]
    for j,nombre in enumerate(ids):
        q=raw[:,j+1];q=q[np.isfinite(q)];t=np.arange(len(q))/6
        a=np.r_[0,np.cumsum(300*(q[:-1]+q[1:]))]
        tabla=np.genfromtxt(RAIZ/f'datos/hidratacion/{nombre}.csv',delimiter=',',names=True)
        np.testing.assert_allclose(a,tabla['acumulado'],rtol=0,atol=1e-5)
        np.testing.assert_allclose(t,tabla['edad_h'],rtol=0,atol=1e-10)
        axs[j//4].plot(t,q,label=nombre,lw=1.5)
        controles.append(dict(curva=nombre,energia_MJ_m3=a[-1]/1e6,Qmax_W_m3=q.max(),duracion_h=t[-1]))
    for ax,camp in zip(axs,['SS','22A']):
        ax.set(xlabel='Edad térmica [h]',title=f'Campaña {camp}',xlim=(0,250),ylim=(0,700));ax.legend();ax.grid(alpha=.2)
    axs[0].set_ylabel('Fuente volumétrica Q [W/m³]')
    fig.suptitle('Ocho fuentes completas del profesor · escenarios de modelo')
    guardar(fig,'01_fuentes');csv_guardar('fuentes_verificadas.csv',controles)
    cfg=leer(RAIZ/'casos/incertidumbre/parametros.json')
    fig,axs=plt.subplots(2,1,figsize=(11,6),sharex=True,layout='constrained')
    metadata=[]
    for clima in cfg['historias']:
        p=RAIZ/clima['snapshot'];d=leer(p);hr=d['respuesta']['hourly'];md=d['metadata']
        assert len(hr['time'])==696 and all(np.diff(hr['time'])==3600)
        assert md['coordenadas_solicitadas']==dict(latitud=-37.277929,longitud=-72.368271)
        aire=np.array(hr['temperature_2m'][13:13+673]);v=np.array(hr['wind_speed_10m'][13:13+673])
        assert len(aire)==673 and np.isfinite(aire).all() and np.isfinite(v).all()
        h=5.7+3.8*v*(2/10)**.14
        axs[0].plot(np.arange(601)/24,aire[:601],label=clima['id'])
        axs[1].step(np.arange(601)/24,h[:601],where='post',label=clima['id'])
        metadata.append(dict(clima=clima['id'],snapshot=clima['snapshot'],sha256=sha256(p.read_bytes()).hexdigest(),
            descarga_utc=md['descargado_utc'],inicio_historico=clima['inicio'],inicio_modelo=cfg['inicio'],
            lat_solicitada=-37.277929,lon_solicitada=-72.368271,lat_devuelta=d['respuesta']['latitude'],
            lon_devuelta=d['respuesta']['longitude'],marcas=696,horas_disponibles_desde_t0=682))
    axs[0].set(ylabel='Aire [°C]',title='Tres bloques históricos ERA5 · El Rosal · t₀ 19/11/2026 10:00 UTC−03')
    axs[1].set(ylabel='h horario [W/(m² K)]',xlabel='Días desde primera colocación',xlim=(0,25))
    for ax in axs:ax.axvline(14,color='gray',ls='--');ax.legend(ncol=3);ax.grid(alpha=.2)
    guardar(fig,'02_clima');csv_guardar('clima_metadatos.csv',metadata)
    fuente=(RAIZ/'datos/hidratacion/source_terms.txt').read_bytes()
    assert sha256(fuente.replace(b'\r\n',b'\n')).hexdigest()=='182b4a500dd02060b89dc452f007a379c7ab6cdc569e67de59a04c00d3497956'
    (SALIDA/'huellas_datos.json').write_text(json.dumps(dict(source_raw_sha256=sha256(fuente).hexdigest(),
        source_LF_sha256=sha256(fuente.replace(b'\r\n',b'\n')).hexdigest(),nota='Diferencia CRLF/LF respecto de copia de Matías; series e integrales verificadas'),indent=2)+'\n',encoding='utf-8')
    esquema=leer(RAIZ/'resultados/diseno_circuitos_colocacion/esquema.json')
    fig,ax=plt.subplots(figsize=(11,4.4),layout='constrained');filas=[]
    cmap=plt.get_cmap('viridis',11)
    for j,q in enumerate(COLORES):
        for c in esquema['capas']:
            t=c['inicio_h']*60/q;dur=c['duracion_h']*60/q
            ax.broken_barh([(t,dur)],(j-.3,.6),facecolors=cmap(c['id']-1),edgecolors='white')
            if dur>.15:ax.text(t+dur/2,j,str(c['id']),ha='center',va='center',fontsize=7.5 if dur<.4 else 8,color='black' if c['id']>=9 else 'white')
            filas.append(dict(plan=f'q{q}',capa=c['id'],z_inf_m=c['z_inferior_m'],z_sup_m=c['z_superior_m'],
                volumen_m3=c['volumen_m3'],inicio_h=t,fin_h=t+dur))
    ax.set_yticks(range(4),[f'{q} m³/h' for q in COLORES]);ax.invert_yaxis()
    ax.set(xlabel='Horas desde inicio común',title='Colocación continua · 11 capas físicas · dos frentes coordinados',xlim=(0,15))
    ax.grid(axis='x',alpha=.2);guardar(fig,'03_cronogramas');csv_guardar('cronogramas.csv',filas)


def matrices():
    return {q:leer(RAIZ/f'resultados/comparacion_circuitos/q{q}/malla_0.4/matriz.json') for q in COLORES}


def tablas(ms):
    comparacion=[];escenarios=[];sensibilidad=[]
    fina=RAIZ/'resultados/comparacion_circuitos/q60/malla_0.2/matriz.json'
    todos=list(ms.values())+([leer(fina)] if fina.exists() else [])
    for m in todos:
        for horas in [336,600]:
            fs=[dict(f['base_336h'],curva=f['curva'],clima=f['clima'],peso=f['peso']) if horas==336 else f for f in m['corridas']]
            riesgos=m['riesgo_336'] if horas==336 else m['riesgo']
            comparacion.append(dict(plan=m['plan'],caudal_m3_h=m['capacidad_m3_h'],D_h=m['D_h'],lado_m=m['lado_m'],
                horizonte_h=horas,Tmax_C=max(f['Tmax']['valor'] for f in fs),DeltaTmax_K=max(f['DeltaTmax']['valor'] for f in fs),
                **{k:100*v for k,v in riesgos.items()},cumple=riesgos['P_union']<=.05,alertas=m['picos_no_resueltos']))
            for f in fs:
                escenarios.append(dict(plan=m['plan'],lado_m=m['lado_m'],horizonte_h=horas,curva=f['curva'],clima=f['clima'],peso=f['peso'],
                    Tmax_C=f['Tmax']['valor'],Tmax_h=f['Tmax']['tiempo_h'],fase_Tmax=f['Tmax']['fase'],xyz_Tmax_m=str(f['Tmax']['xyz_Tmax_m']),
                    DeltaTmax_K=f['DeltaTmax']['valor'],DeltaT_h=f['DeltaTmax']['tiempo_h'],fase_Delta=f['DeltaTmax']['fase'],
                    xyz_caliente_en_Delta_m=str(f['DeltaTmax']['xyz_Tmax_m']),
                    T_caliente_simultanea_C=f['DeltaTmax']['Tmax_C'],T_S25_simultanea_C=f['DeltaTmax']['Tmin_S25_C'],
                    xyz_S25_m=str(f['DeltaTmax']['xyz_S25_m']),I_T=int(f['excede_70']),I_delta=int(f['excede_20']),
                    I_union=int(f['excede_70'] or f['excede_20']),balance_residuo_J=f['balance_J']['residuo']))
            for nombre in ['publicados','solo_SS','doble_2023','doble_2024','doble_2025']:
                w=[f['peso']*(int(f['curva'].endswith('_SS')) if nombre=='solo_SS' else
                    (2 if nombre.startswith('doble_') and f['clima'].endswith(nombre[-4:]) else 1)) for f in fs]
                total=sum(w)
                sensibilidad.append(dict(plan=m['plan'],lado_m=m['lado_m'],horizonte_h=horas,sensibilidad=nombre,
                    P_union_porcentaje=100*sum(ww*(f['excede_70'] or f['excede_20']) for f,ww in zip(fs,w))/total))
    csv_guardar('comparacion_planes.csv',comparacion);csv_guardar('escenarios.csv',escenarios);csv_guardar('sensibilidad_pesos.csv',sensibilidad)


def resultados(ms):
    orden=sorted(ms,key=lambda q:ms[q]['D_h']);D=[ms[q]['D_h'] for q in orden]
    fig,axs=plt.subplots(1,2,figsize=(11,4.5),layout='constrained')
    for horizonte,key in [('14 días','riesgo_336'),('Extensión','riesgo')]:
        axs[0].plot(D,[100*ms[q][key]['P_union'] for q in orden],marker='o',label=horizonte)
    axs[0].plot(D[0],100*ms[60]['riesgo']['P_union'],marker='*',markersize=14,color=COLORES[60],ls='none',label='Propuesta 60 m³/h')
    axs[0].axhline(5,ls='--',color='#a93232',label='Límite 5 %');axs[0].set(ylabel='Probabilidad conjunta [%]',ylim=(-.5,10))
    for b,label in [(True,'14 días'),(False,'Extensión')]:
        axs[1].plot(D,[max((f['base_336h'] if b else f)['DeltaTmax']['valor'] for f in ms[q]['corridas']) for q in orden],marker='o',label=label)
    axs[1].axhline(20,color='#a93232',ls='--',label='Límite 20 K');axs[1].set_ylabel('Mayor diferencial del catálogo [K]')
    for ax in axs:
        ax.axvline(D[0],color='gray',ls=':',lw=1)
        ax.set_xlabel('Duración total de colocación D [h]');ax.grid(alpha=.2);ax.legend()
        ax.set_xticks(D,[f'{d:.2f}\n{q} m³/h' for d,q in zip(D,orden)])
    fig.suptitle('Misma geometría, fuentes, climas y controles · malla 0,40 m / paso máximo 300 s')
    guardar(fig,'04_duracion_riesgo')
    fig,axs=plt.subplots(2,1,figsize=(12,8),sharex=True)
    ids=sorted({f['curva'] for f in ms[60]['corridas']});col=plt.get_cmap('tab10')
    for j,curva in enumerate(ids):
        for clima,ls in zip(['ERA5-2023','ERA5-2024','ERA5-2025'],['-',':','--']):
            fs=[next(f for f in ms[q]['corridas'] if f['curva']==curva and f['clima']==clima) for q in orden]
            for ax,k in zip(axs,['Tmax','DeltaTmax']):ax.plot(D,[f[k]['valor'] for f in fs],ls=ls,color=col(j),marker='.',lw=1)
    axs[0].axhline(70,ls='--',color='black');axs[1].axhline(20,ls='--',color='black')
    axs[0].set(ylabel='Tmax [°C]',ylim=(30,72));axs[1].set(ylabel='ΔTmax [K]',xlabel='Duración de colocación D [h]')
    for ax in axs:ax.grid(alpha=.2)
    handles=[Line2D([0],[0],color=col(j),label=curva) for j,curva in enumerate(ids)]
    handles += [Line2D([0],[0],color='gray',ls=ls,label=a) for a,ls in zip(['2023','2024','2025'],['-',':','--'])]
    fig.legend(handles=handles,ncol=6,loc='lower center',fontsize=9)
    fig.subplots_adjust(bottom=.16,hspace=.13);fig.suptitle('24 escenarios por plan · se unen solo los cuatro puntos calculados · horizonte extendido')
    guardar(fig,'05_curvas_por_escenario')
    piezas={q:leer(RAIZ/f'resultados/comparacion_circuitos/q{q}/malla_0.4/M4_SS_ERA5-2024.json') for q in orden}
    fig,axs=plt.subplots(3,1,figsize=(11,8),sharex=True,layout='constrained')
    for q,d in piezas.items():
        hist=d['historia'];dias=[x['tiempo_h']/24 for x in hist]
        for ax,k in zip(axs,['Tmax_C','Tmin_S25_C','DeltaT_K']):
            ax.plot(dias,[x[k] for x in hist],label=f'{q} m³/h',color=COLORES[q],lw=1.2)
        axs[0].plot(dias,[x['nucleo_C'] for x in hist],color=COLORES[q],ls=':',lw=.8)
    for ax,label in zip(axs,['Tmax y sonda interior [°C]','Tmin,S25 [°C]','ΔT [K]']):
        ax.set_ylabel(label);ax.grid(alpha=.2);ax.axvline(14,color='gray',ls='--')
    axs[0].legend(ncol=4);axs[2].axhline(20,color='black',ls='--')
    axs[2].set(xlabel='Días desde inicio común',xlim=(0,25));axs[0].set_title('M4_SS × ERA5-2024 · sólida: Tmax; punteada: sonda interior (0,0,2) m')
    guardar(fig,'06_historias_comunes')
    fig,axs=plt.subplots(2,4,figsize=(13,3.6),sharex=True,sharey=True,layout='constrained')
    for j,q in enumerate(orden):
        p=RAIZ/piezas[q]['campos_npz']
        with np.load(p) as a:
            T=a['comun_428h_T_C'];h=float(a['lado_m']);o=a['origen_m']
            ys=o[1]+(np.arange(T.shape[1])+.5)*h
            for i,y in enumerate([0,-8.8]):
                iy=int(np.argmin(abs(ys-y)))
                im=axs[i,j].imshow(np.ma.masked_invalid(T[:,iy,:]),origin='lower',
                    extent=(o[0],o[0]+T.shape[2]*h,o[2],o[2]+T.shape[0]*h),
                    vmin=8,vmax=35,cmap='inferno',aspect='equal',interpolation='nearest')
                mostrar_y=0 if abs(ys[iy])<.01 else ys[iy]
                axs[i,j].set_title(f'{q} m³/h · y={mostrar_y:.1f} m',fontsize=10)
                axs[i,j].set_xlabel('x [m]')
    axs[0,0].set_ylabel('z [m]');axs[1,0].set_ylabel('z [m]')
    fig.colorbar(im,ax=axs,label='Temperatura de centro [°C]',shrink=.8)
    fig.suptitle('Cortes a la misma hora: 428 h · M4_SS × ERA5-2024 · escala común 8–35 °C')
    guardar(fig,'07_cortes_comunes')
    ruta_fina=RAIZ/'resultados/comparacion_circuitos/q60/malla_0.2/matriz.json'
    if not ruta_fina.exists():return
    fina=leer(ruta_fina)
    fb={(f['curva'],f['clima']):f for f in ms[60]['corridas']}
    ff={(f['curva'],f['clima']):f for f in fina['corridas']}
    claves=sorted(fb);filas=[]
    fig,ax=plt.subplots(figsize=(12,5.5),layout='constrained')
    for fs,label,marker in [(fb,'0,40 m / 300 s','o'),(ff,'0,20 m / 300 s','x')]:
        ax.plot(range(24),[fs[k]['DeltaTmax']['valor'] for k in claves],marker=marker,lw=1,label=label)
    for k in claves:
        filas.append(dict(curva=k[0],clima=k[1],cambio_Tmax_K=ff[k]['Tmax']['valor']-fb[k]['Tmax']['valor'],
            cambio_DeltaTmax_K=ff[k]['DeltaTmax']['valor']-fb[k]['DeltaTmax']['valor']))
    ax.axhline(20,color='black',ls='--');ax.set_xticks(range(24),[f'{c}\n{a[-4:]}' for c,a in claves],rotation=90,fontsize=8)
    ax.set(ylabel='ΔTmax extendido [K]',title='Candidata 60 m³/h · catálogo completo en ambas mallas');ax.legend();ax.grid(alpha=.2)
    guardar(fig,'08_sensibilidad_espacial');csv_guardar('sensibilidad_espacial.csv',filas)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--datos',action='store_true');a=p.parse_args()
    FIG.mkdir(parents=True,exist_ok=True);datos()
    if not a.datos:
        ms=matrices();tablas(ms);resultados(ms)
    print('Figuras y tablas generadas en',SALIDA)


if __name__=='__main__':main()
