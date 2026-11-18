"""Sensibilidad de solar/LW sobre propuesta9circuitos; sin solver por defecto."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
os.environ['MKL_NUM_THREADS']='1'
import argparse
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from time import perf_counter
import numpy as np
import comparar_circuitos as f
import radiacion_borde as rb

RAIZ=f.RAIZ
SALIDA=RAIZ/'resultados/sensibilidad_radiacion'


def motor(mapa,centros,modelo):
    viejo=f.base.adaptar
    def transformar(codigo,cambiar):return rb.adaptar(viejo(codigo,cambiar),cambiar)
    f.base.adaptar=transformar
    try:m,huella=f.base.construir_solver(mapa,centros)
    finally:f.base.adaptar=viejo
    m.MODELO_RADIACION=modelo
    return m,huella


def modelo(clima,opciones,config):
    manifest=f.base.viento.leer(RAIZ/'datos/clima/radiacion/manifiesto.json')
    hr=f.base.viento.leer(RAIZ/manifest[clima]['snapshot'])['respuesta']['hourly']
    c=f.ESTADO[7][clima][0]
    I,meta=rb.irradiancias(hr,c['inicio'],opciones['yaw'],config['albedo_suelo'])
    inicio=hr['time'].index(int(__import__('datetime').datetime.fromisoformat(c['inicio']).timestamp()))
    rad=rb.Radiacion(I,hr['dew_point_2m'][inicio:inicio+673],hr['cloud_cover'][inicio:inicio+673],
        opciones['alpha'],opciones['eps'],opciones['cielo'])
    assert all(v==0 for v in manifest[clima]['max_diferencia_variables_comunes'].values())
    return rad,meta,manifest[clima]


def verificar():
    # Sol-aire analítica, efecto deR, equilibrio radiativo y raíces independientes.
    R=np.array([.1,2.]);Tc=np.array([30.,30.]);Ta=20.;h=15.;I=np.array([800.,800.])
    Ts,q,*_=rb.superficie(Tc,R,h,Ta,I,.6,0,np.full(2,(Ta+273.15)**4))
    esperada=(h*(Ta-Tc)+.6*I)/(1+h*R)
    np.testing.assert_allclose(q,esperada,atol=1e-11,rtol=0)
    assert abs(q[1])<abs(q[0])
    Ts,q,*_=rb.superficie(np.array([20.]),np.array([.1]),15,20,np.array([0.]),0,.9,np.array([293.15**4]))
    np.testing.assert_allclose(q,0,atol=1e-10)
    Ts,q,*_=rb.superficie(np.array([30.]),np.array([.1]),15,20,np.array([800.]),.6,.9,np.array([270.**4]))
    lo,hi=-100.,150.
    for _ in range(100):
        mid=(lo+hi)/2
        resid=(mid-30)/.1-15*(20-mid)-.6*800-.9*rb.SIGMA*(270**4-(mid+273.15)**4)
        if resid>0:hi=mid
        else:lo=mid
    np.testing.assert_allclose(Ts,(lo+hi)/2,atol=1e-10)
    # El sol nocturno no produce directa; vector unitario y rotaciónsin creación de energía.
    for stamp in [1700409600,1700467200]:np.testing.assert_allclose(np.linalg.norm(rb.vector_solar(stamp)),1,atol=1e-12)
    cfg=f.base.viento.leer(Path(__file__).with_name('radiacion_config.json'))
    rad,_,_=modelo('ERA5-2024',cfg['variantes']['sin_radiacion'],cfg)
    sol,_=motor(f.ESTADO[1].MAPA_CONTROL,f.ESTADO[1].CENTROS_CONTROL,rad)
    f.base.verificar(sol)
    print('Aprobados: sol-aire analítica, aislación exterior, equilibrioLW, Newton contra bisección, vector solar y balance de celda.',flush=True)


def resolver(variante,curva,clima,h=.4,dt=300):
    config=f.base.viento.leer(Path(__file__).with_name('radiacion_config.json'))
    controles,_,_,_,programa,env,fuentes,climas,series,_,prov=f.ESTADO
    if h==.2:
        import cache_geometria_circuitos as cache
        if .2 not in f.GEOMETRIAS and cache.RUTA.exists():f.GEOMETRIAS[.2]=cache.cargar()
    ids,origen,mapa,centros=f.geometria(h)
    rad,estad,climafuente=modelo(clima,config['variantes'][variante],config)
    sol,huella=motor(mapa,centros,rad)
    fuente=next(x for x in fuentes if x['id']==curva)
    pp=dict(referencia=prov,estudio='solar+onda larga en frontera exterior',variante=variante,
        parametros=config['variantes'][variante],lado_m=h,paso_max_s=dt,mapa=mapa[3],
        script_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        borde_sha256=sha256(Path(rb.__file__).read_bytes()).hexdigest(),
        configuracion_sha256=sha256(Path(__file__).with_name('radiacion_config.json').read_bytes()).hexdigest(),
        solver_adaptado_sha256=huella,clima_complementario=climafuente,irradiancias=estad,
        hipotesis=config['hipotesis'],albedo=config['albedo_suelo'])
    carpeta=SALIDA/variante/f'malla_{h:g}_paso{dt}';carpeta.mkdir(parents=True,exist_ok=True)
    ruta=carpeta/f'{curva}_{clima}.json'
    if ruta.exists():
        d=f.base.viento.leer(ruta)
        if d['procedencia']!=pp:raise ValueError('Cambió procedencia; preservar salidas y usar nueva carpeta.')
        return ruta
    inicio=perf_counter();aire=climas[clima][1]
    def simular(horas):
        return sol.simular(ids,origen,h,programa,fuente['curva'],replace(env,dt_tope_s=dt),aire[:horas+1],
            (0,0,2),h_aire_horario_W_m2K=series[clima]['h_W_m2K'][:horas+1])
    r336=simular(336)
    horas=600;r=simular(horas)
    while controles.alertas_cola(r,horas,prov['D_h'],168) and horas<672:
        horas+=72;r=simular(horas)
    assert abs(r.balance_J['residuo'])<.05
    assert r.balance_J['enfriamiento_pico_W']<=15000.000001
    assert abs(sum(r.control_circuitos['energia_extraida_circuito_J'])+r.balance_J['enfriamiento'])<.1
    for rr in [r336,r]:
        em=rr.radiacion
        assert abs(sum(em[k] for k in ['solar_absorbida_exterior_J','conveccion_exterior_J','onda_larga_neta_J'])-rr.balance_J['aire'])<.5
    met=controles.metricas(r,horas)
    row=dict(curva=curva,clima=clima,peso=fuente['peso']*climas[clima][0]['peso'],
        base_336h=controles.metricas(r336,336),**met,pico_no_resuelto=controles.alertas_cola(r,horas,prov['D_h'],168))
    if variante=='sin_radiacion' and h==.4 and dt==300:
        anterior=f.base.viento.leer(RAIZ/f'resultados/circuitos_histeresis/{curva}_{clima}.json')['corrida']
        for key in ['Tmax','DeltaTmax']:
            np.testing.assert_allclose(row[key]['valor'],anterior[key]['valor'],rtol=0,atol=1e-9)
        print('Control sin radiación reproduce máximos del estudio original.',flush=True)
    f.base.escribir(ruta,dict(procedencia=pp,corrida=row,historia=r.historia,control=r.control_circuitos,
        radiacion=r.radiacion,radiacion_336=r336.radiacion,segundos=perf_counter()-inicio))
    print(variante,curva,clima,h,dt,'Tmax',round(row['Tmax']['valor'],4),'Delta14',round(row['base_336h']['DeltaTmax']['valor'],4),
        'DeltaExt',round(row['DeltaTmax']['valor'],4),horas,'alerta',row['pico_no_resuelto'],flush=True)
    return ruta


def agregar():
    rutas=sorted((SALIDA/'ambas/malla_0.4_paso300').glob('M*.json'))
    if len(rutas)!=24:return
    filas=[f.base.viento.leer(p)['corrida'] for p in rutas]
    f.base.comun.validar_filas(filas)
    controles=f.ESTADO[0]
    f.base.escribir(SALIDA/'ambas/malla_0.4_paso300/matriz.json',dict(corridas=filas,
        riesgo_observado=controles.riesgo(filas),
        riesgo_336=controles.riesgo([dict(r['base_336h'],peso=r['peso']) for r in filas]),
        picos_no_resueltos=sum(r['pico_no_resuelto'] for r in filas),
        archivos=[dict(ruta=str(p.relative_to(RAIZ)),sha256=sha256(p.read_bytes()).hexdigest()) for p in rutas]))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ejecutar',action='store_true');p.add_argument('--fase',choices=['verificar','control','piloto','matriz','cotas','fina','agregar'],default='verificar')
    p.add_argument('--lote',type=int,choices=[0,1,2])
    a=p.parse_args()
    if not a.ejecutar:print(__doc__);return
    f.iniciar()
    if a.fase=='verificar':verificar();return
    tareas=[]
    if a.fase=='control':tareas=[('sin_radiacion','M4_SS','ERA5-2024',.4,300)]
    if a.fase=='piloto':tareas=[(v,'M4_SS',c,.4,300) for v in ['solar','larga','ambas'] for c in f.ESTADO[7]]
    if a.fase=='matriz':tareas=[('ambas',fu['id'],c,.4,300) for fu in f.ESTADO[6] for c in f.ESTADO[7]]
    if a.fase in ['cotas','fina']:
        m=f.base.viento.leer(SALIDA/'ambas/malla_0.4_paso300/matriz.json')
        crit=max(m['corridas'],key=lambda r:r['DeltaTmax']['valor'])
        if a.fase=='cotas':tareas=[(v,crit['curva'],crit['clima'],.4,300) for v in ['clara','oscura','despejado','giro90']]
        else:tareas=[('ambas',crit['curva'],crit['clima'],.2,300),('ambas',crit['curva'],crit['clima'],.4,150)]
    if a.lote is not None:tareas=tareas[a.lote::3]
    print('FASE',a.fase,'tareas',len(tareas),'lote',a.lote,flush=True)
    for tarea in tareas:resolver(*tarea)
    if a.lote is None:agregar()


if __name__=='__main__':main()
