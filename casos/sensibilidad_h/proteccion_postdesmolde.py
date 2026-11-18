"""Tres medidas de proteccion tras desmolde; nuevas salidas, sin alterar estudios previos."""
import argparse
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from time import perf_counter
import numpy as np
import sensibilidad_radiacion as estudio

f=estudio.f
RAIZ=f.RAIZ
CONFIG=Path(__file__).with_suffix('.json')
SALIDA=RAIZ/'resultados/proteccion_postdesmolde'


def leer(p):return f.base.viento.leer(p)
def huella(p):return sha256(Path(p).read_bytes()).hexdigest()


class RadiacionSombra(estudio.rb.Radiacion):
    def __init__(self, original, retiro, tau):
        super().__init__(original.I,original.dew,original.nubes,original.alpha,original.eps,original.cielo)
        self.retiro,self.tau=retiro,tau

    def nueva(self):return RadiacionSombra(self,self.retiro,self.tau)

    def flujo(self,Tc,R,h,Ta,d,t,j_solar,A,edades):
        # Se conserva exactamente el balance superficial ya verificado.
        # La transmitancia modifica solo solar incidente por cara y edad local.
        original=self.I
        factores=np.where(np.asarray(edades)>=self.retiro,self.tau,1.)
        # Evitar mutar arrays meteorologicos compartidos: irradiancia local por
        # orientacion no basta si existen caras de distinta edad en una direccion.
        if np.all(factores==1):
            return super().flujo(Tc,R,h,Ta,d,t,j_solar,A)
        hora=min(t/3600,len(self.dew)-1)
        td=np.interp(hora,np.arange(len(self.dew)),self.dew)+273.15
        N=np.interp(hora,np.arange(len(self.nubes)),self.nubes)/10
        emis=float(np.clip((.787+.764*np.log(td/273))*(1+.0224*N-.0035*N*N+.00028*N**3),0,1))
        F=np.where(d==1,1.,np.where(d==0,0.,.5))
        env4=(F*emis+1-F)*(Ta+273.15)**4
        I=original[min(j_solar,len(original)-1),d]*factores
        Ts,q,solar,conv,lw=estudio.rb.superficie(Tc,R,h,Ta,I,self.alpha,self.eps,env4)
        self.ultima=A*np.array([solar.sum(),conv.sum(),lw.sum()])
        self.ts_min=min(self.ts_min,float(Ts.min()));self.ts_max=max(self.ts_max,float(Ts.max()))
        self.residual_max=max(self.residual_max,float(np.max(abs(q-solar-conv-lw))))
        return A*q


def motor(mapa,centros,rad):
    viejo=f.base.adaptar
    def transformar(codigo,cambiar):
        codigo=estudio.rb.adaptar(viejo(codigo,cambiar),cambiar)
        return cambiar(codigo,
            'radiacion.flujo(T[i[air]],Rrad[air],hconv,aire_en(t),d[air],t,jsolar,A)',
            'radiacion.flujo(T[i[air]],Rrad[air],hconv,aire_en(t),d[air],t,jsolar,A,edades=(t-comienzos[i[air]])/3600)')
    f.base.adaptar=transformar
    try:m,sha=f.base.construir_solver(mapa,centros)
    finally:f.base.adaptar=viejo
    m.MODELO_RADIACION=rad
    return m,sha


def resolver(variante,curva,clima,h=.4,dt=300):
    cfg=leer(CONFIG);op=cfg['variantes'][variante]
    controles,_,_,_,programa,env,fuentes,climas,series,_,ref=f.ESTADO
    if h==.2:
        import cache_geometria_circuitos as cache
        if .2 not in f.GEOMETRIAS and cache.RUTA.exists():f.GEOMETRIAS[.2]=cache.cargar()
    ids,origen,mapa,centros=f.geometria(h)
    capas=tuple(replace(c,retiro_edad_h=op['retiro_ultima_manta_edad_h']) if c.retiro_edad_h==360 else c for c in env.capas_laterales)
    superiores=tuple(replace(c,retiro_edad_h=op['retiro_ultima_manta_edad_h']) if c.retiro_edad_h==360 else c for c in env.capas_superiores)
    env=replace(env,capas_laterales=capas,capas_superiores=superiores,dt_tope_s=dt)
    cfg_rad=leer(Path(estudio.__file__).with_name('radiacion_config.json'))
    rad,estad,metaclima=estudio.modelo(clima,cfg_rad['variantes']['ambas'],cfg_rad)
    rad=RadiacionSombra(rad,op['retiro_ultima_manta_edad_h'],op['transmitancia_solar_postretiro'])
    sol,hash_sol=motor(mapa,centros,rad)
    fuente=next(x for x in fuentes if x['id']==curva)
    p=dict(variante=variante,parametros=op,horizonte_h=672,lado_m=h,paso_max_s=dt,
        referencia=ref,script_sha256=huella(__file__),config_sha256=huella(CONFIG),
        radiacion_borde_sha256=huella(Path(estudio.rb.__file__)),solver_adaptado_sha256=hash_sol,
        clima=metaclima,irradiancias=estad,hipotesis=cfg['hipotesis'],mapa=mapa[3])
    carpeta=SALIDA/variante/f'malla_{h:g}_paso{dt}'
    carpeta.mkdir(parents=True,exist_ok=True)
    ruta=carpeta/f'{curva}_{clima}.json'
    if ruta.exists():
        assert leer(ruta)['procedencia']==p,'Procedencia distinta; conservar salida previa.'
        print('CONSERVADO',variante,curva,clima,h,dt,flush=True);return ruta
    inicio=perf_counter()
    r=sol.simular(ids,origen,h,programa,fuente['curva'],env,climas[clima][1][:673],(0,0,2),
        h_aire_horario_W_m2K=series[clima]['h_W_m2K'][:673])
    met=controles.metricas(r,672)
    referencia=leer(RAIZ/f'resultados/familia_radiacion_336h/q60/malla_0.4_paso300/{curva}_{clima}.json')['corrida']
    assert abs(r.balance_J['residuo'])<.05
    assert r.balance_J['enfriamiento_pico_W']<=15000.000001
    assert abs(sum(r.control_circuitos['energia_extraida_circuito_J'])+r.balance_J['enfriamiento'])<.1
    assert abs(sum(r.radiacion[k] for k in ['solar_absorbida_exterior_J','conveccion_exterior_J','onda_larga_neta_J'])-r.balance_J['aire'])<.5
    historia336=[x for x in r.historia if x['tiempo_h']<=336]
    # Las medidas comienzan despues de336h. Se guardan metricas exactas de la
    # corrida existente a336h; la coincidencia completa de historia se audita.
    original=leer(RAIZ/f'resultados/familia_radiacion_336h/q60/malla_0.4_paso300/{curva}_{clima}.json')
    if h==.4 and dt==300:
        # Distinto horizonte añade solo eventos posteriores: historia previa igual.
        assert len(historia336)==len(original['historia'])
        for a,b in zip(historia336,original['historia']):
            for k in ['tiempo_h','Tmax_C','Tmin_S25_C','DeltaT_K']:
                assert abs(a[k]-b[k])<1e-8,(k,a[k],b[k])
        base336=referencia
    else:
        base336=None
    contenido=dict(procedencia=p,corrida=dict(met,curva=curva,clima=clima,
        peso=fuente['peso']*climas[clima][0]['peso'],
        pico_no_resuelto=controles.alertas_cola(r,672,ref['D_h'],168)),
        base_336h=base336,historia=r.historia,control=r.control_circuitos,
        radiacion=r.radiacion,segundos=perf_counter()-inicio)
    f.base.escribir(ruta,contenido)
    print('TERMINADO',variante,curva,clima,h,dt,'Tmax',round(met['Tmax']['valor'],4),
        'Delta',round(met['DeltaTmax']['valor'],4),'alerta',contenido['corrida']['pico_no_resuelto'],
        's',round(contenido['segundos'],1),flush=True)
    return ruta


def verificar():
    cfg=leer(Path(estudio.__file__).with_name('radiacion_config.json'))
    rad,_,_=estudio.modelo('ERA5-2024',cfg['variantes']['ambas'],cfg)
    Tc=np.array([30.,25.]);R=np.array([.1,1.]);d=np.array([1,3])
    for tau,edad in [(1.,600.),(.1,100.)]:
        a=rad.nueva();b=RadiacionSombra(rad,360,tau)
        np.testing.assert_allclose(a.flujo(Tc,R,15,20,d,43200,12,.16),
            b.flujo(Tc,R,15,20,d,43200,12,.16,np.array([edad,edad])),atol=1e-12)
    b=RadiacionSombra(rad,360,0.)
    b.flujo(Tc,R,15,20,d,43200,12,.16,np.array([400.,100.]))
    # Solo la primera cara esta sombreada; segunda conserva solar original.
    esperado=.16*.6*rad.I[12,d[1]]
    np.testing.assert_allclose(b.ultima[0],esperado,atol=1e-12)
    print('Verificado: equivalencia sin sombra, activacion local y balance superficial.',flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ejecutar',action='store_true');p.add_argument('--verificar',action='store_true')
    p.add_argument('--variante',choices=list(leer(CONFIG)['variantes']))
    p.add_argument('--escenario',nargs=2);p.add_argument('--pilotos',action='store_true')
    p.add_argument('--lote',type=int);p.add_argument('--lotes',type=int,default=3)
    p.add_argument('--malla',type=float,default=.4,choices=[.4,.2]);p.add_argument('--paso',type=int,default=300,choices=[300,150])
    a=p.parse_args()
    if not(a.ejecutar or a.verificar):print(__doc__);return
    f.iniciar()
    if a.verificar:verificar()
    if not a.ejecutar:return
    cfg=leer(CONFIG);variantes=[a.variante] if a.variante else list(cfg['variantes'])
    pares=[a.escenario] if a.escenario else cfg['pilotos'] if a.pilotos else [(x['id'],c) for x in f.ESTADO[6] for c in f.ESTADO[7]]
    tareas=[(v,*par) for v in variantes for par in pares]
    if a.lote is not None:tareas=tareas[a.lote::a.lotes]
    for v,curva,clima in tareas:resolver(v,curva,clima,a.malla,a.paso)


if __name__=='__main__':main()
