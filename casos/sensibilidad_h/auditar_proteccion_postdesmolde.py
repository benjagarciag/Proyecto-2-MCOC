"""Audita y agrega las tres alternativas sin recalcular ni editar historicos."""
from pathlib import Path
from hashlib import sha256
import csv
import json
import numpy as np

RAIZ=Path(__file__).resolve().parents[2]
SALIDA=RAIZ/'resultados/proteccion_postdesmolde'
CONFIG=Path(__file__).with_name('proteccion_postdesmolde.json')


def leer(p):return json.loads(p.read_text(encoding='utf8'))
def huella(p):return sha256(Path(p).read_bytes()).hexdigest()


def pieza(path):
    d=leer(path);p=d['procedencia'];r=d['corrida'];cfg=leer(CONFIG)
    assert p['script_sha256']==huella(Path(__file__).with_name('proteccion_postdesmolde.py'))
    assert p['config_sha256']==huella(CONFIG)
    assert p['radiacion_borde_sha256']==huella(Path(__file__).with_name('radiacion_borde.py'))
    assert p['parametros']==cfg['variantes'][p['variante']]
    assert p['horizonte_h']==r['horizonte_h']==672
    ref=p['referencia']
    assert ref['temperatura_colocacion_C']==12 and ref['agua_C']==18
    assert ref['U_W_m3K']==5 and ref['tope_global_W']==15000 and ref['capacidad_m3_h']==60
    assert abs(p['mapa']['volumen_refrigerable_m3']-414.016)<1e-6
    c=p['clima']
    for clave,h in [('snapshot','sha256'),('snapshot_original','original_sha256')]:
        assert huella(RAIZ/c[clave])==c[h]
    assert r['excede_70']==(r['Tmax']['valor']>70)
    assert r['excede_20']==(r['DeltaTmax']['valor']>20)
    dif=r['DeltaTmax']
    assert abs(dif['valor']-dif['Tmax_C']+dif['Tmin_S25_C'])<1e-9
    assert 0<=dif['tiempo_h']<=672 and 0<=r['Tmax']['tiempo_h']<=672
    assert abs(r['balance_J']['residuo'])<.05
    assert r['balance_J']['enfriamiento_pico_W']<=15000.000001
    assert abs(sum(d['control']['energia_extraida_circuito_J'])+r['balance_J']['enfriamiento'])<.1
    rad=d['radiacion'];assert rad['residual_superficie_max_W_m2']<2e-8
    assert abs(sum(rad[k] for k in ['solar_absorbida_exterior_J','conveccion_exterior_J','onda_larga_neta_J'])-r['balance_J']['aire'])<.5
    abiertos=[False]*9;ultimo=-1
    for e in d['control']['eventos_circuitos']:
        j=int(e['circuito'][1:])-1
        assert ultimo<=e['tiempo_h']<=672;ultimo=e['tiempo_h']
        assert abiertos[j]!=e['abierto'];abiertos[j]=e['abierto']
        if e['abierto']:assert e['Tmin_tramos_C']>=19 and e['tiempo_h']>=p['mapa']['cubierto_desde_h'][j]
        else:assert e['Tmin_tramos_C'] is None or e['Tmin_tramos_C']<=18
    assert abiertos==d['control']['circuitos_abiertos_final']
    h=d['historia'];assert abs(h[-1]['tiempo_h']-672)<1e-9
    for x in h:
        assert x['caudal_embebido_L_min']+x['caudal_bypass_L_min']==162
        assert abs(x['Tmax_C']-x['Tmin_S25_C']-x['DeltaT_K'])<1e-9
        assert x['extraccion_W']<=15000.000001
    if d['base_336h'] is not None:
        original=leer(RAIZ/f"resultados/familia_radiacion_336h/q60/malla_0.4_paso300/{r['curva']}_{r['clima']}.json")
        assert d['base_336h']==original['corrida']
        previo=[x for x in h if x['tiempo_h']<=336]
        assert len(previo)==len(original['historia'])
        for a,b in zip(previo,original['historia']):
            for k in ['tiempo_h','Tmax_C','Tmin_S25_C','DeltaT_K']:
                assert abs(a[k]-b[k])<1e-8
    else:
        referencia=RAIZ/f"resultados/familia_radiacion_336h/q60/malla_{p['lado_m']:g}_paso{p['paso_max_s']}/{r['curva']}_{r['clima']}.json"
        if referencia.exists():
            previo=[x for x in h if x['tiempo_h']<=336]
            original=leer(referencia)['historia']
            assert len(previo)==len(original)
            for a,b in zip(previo,original):
                for k in ['tiempo_h','Tmax_C','Tmin_S25_C','DeltaT_K']:
                    assert abs(a[k]-b[k])<1e-8
    return d


def riesgo(filas,prioridad=None,solo_ss=False):
    w=np.array([r['peso']*(2 if r['clima']==prioridad else 1)*(not solo_ss or r['curva'].endswith('_SS')) for r in filas])
    w=w/w.sum()
    return dict(P_T=float(sum(wi*r['excede_70'] for wi,r in zip(w,filas))),
        P_delta=float(sum(wi*r['excede_20'] for wi,r in zip(w,filas))),
        P_union=float(sum(wi*(r['excede_70'] or r['excede_20']) for wi,r in zip(w,filas))))


def comprobar_sombra_independiente():
    import proteccion_postdesmolde as m
    rb=m.estudio.rb
    original=rb.Radiacion(np.full((673,6),800.),np.full(673,10.),np.full(673,20.))
    rad=m.RadiacionSombra(original,360,.1)
    Tc=np.array([30.,25.]);R=np.array([.2,1.]);d=np.array([1,3])
    calculada=rad.flujo(Tc,R,15,20,d,500*3600,500,.16,np.array([400.,100.]))
    N=2.;emis=(.787+.764*np.log(283.15/273))*(1+.0224*N-.0035*N*N+.00028*N**3)
    emis=np.clip(emis,0,1)
    for j,(vista,tau) in enumerate([(1.,.1),(.5,1.)]):
        env4=(vista*emis+1-vista)*293.15**4
        lo,hi=-100.,150.
        for _ in range(90):
            Ts=(lo+hi)/2
            residual=(Ts-Tc[j])/R[j]-15*(20-Ts)-.6*800*tau-.9*rb.SIGMA*(env4-(Ts+273.15)**4)
            if residual>0:hi=Ts
            else:lo=Ts
        independiente=.16*((lo+hi)/2-Tc[j])/R[j]
        np.testing.assert_allclose(calculada[j],independiente,atol=1e-10,rtol=0)
    np.testing.assert_allclose(rad.ultima[0],.16*.6*800*(.1+1),atol=1e-10)


def main():
    comprobar_sombra_independiente()
    cfg=leer(CONFIG);piezas=[];matrices=[];selectivos=[]
    for path in sorted(SALIDA.glob('*/malla*/*.json')):
        if not path.name.startswith('M'):continue
        piezas.append((path,pieza(path)))
    for variante in cfg['variantes']:
        pares=[(p,d) for p,d in piezas if d['procedencia']['variante']==variante and d['procedencia']['lado_m']==.4 and d['procedencia']['paso_max_s']==300]
        if len(pares)!=24:
            print('MATRIZ PENDIENTE',variante,len(pares),'/24');continue
        filas=[d['corrida'] for _,d in pares]
        assert len({(r['curva'],r['clima']) for r in filas})==24
        assert all(abs(r['peso']-1/24)<1e-14 for r in filas)
        m=dict(variante=variante,pares=24,horizonte_h=672,lado_m=.4,paso_max_s=300,
            Tmax=max(r['Tmax']['valor'] for r in filas),Delta=max(r['DeltaTmax']['valor'] for r in filas),
            critico_Delta=max(filas,key=lambda r:r['DeltaTmax']['valor']),
            riesgo=riesgo(filas),alertas=sum(r['pico_no_resuelto'] for r in filas),
            pesos_solo_SS=riesgo(filas,solo_ss=True),
            pesos_doble_anio={c:riesgo(filas,c) for c in ['ERA5-2023','ERA5-2024','ERA5-2025']},
            corridas=filas,archivos=[dict(ruta=str(p.relative_to(RAIZ)),sha256=huella(p)) for p,_ in pares])
        (SALIDA/variante/'matriz.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        matrices.append({k:v for k,v in m.items() if k not in ['corridas','archivos']})
    for p,d in piezas:
        pp=d['procedencia'];r=d['corrida']
        if pp['lado_m']==.4 and pp['paso_max_s']==300:continue
        b=leer(SALIDA/pp['variante']/f"malla_0.4_paso300/{r['curva']}_{r['clima']}.json")['corrida']
        selectivos.append(dict(variante=pp['variante'],curva=r['curva'],clima=r['clima'],
            lado_m=pp['lado_m'],paso_max_s=pp['paso_max_s'],Tmax=r['Tmax']['valor'],
            Delta=r['DeltaTmax']['valor'],cambio_Tmax=r['Tmax']['valor']-b['Tmax']['valor'],
            cambio_Delta=r['DeltaTmax']['valor']-b['DeltaTmax']['valor'],alerta=r['pico_no_resuelto']))
    resumen=dict(estado_auditoria='APROBADA',matrices_completas=len(matrices),piezas=len(piezas),
        transiciones=sum(len(d['control']['eventos_circuitos']) for _,d in piezas),
        matrices=matrices,confirmaciones_selectivas=selectivos,script_sha256=huella(__file__))
    (SALIDA/'resumen.json').write_text(json.dumps(resumen,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('AUDITORIA APROBADA',len(piezas),'piezas;',len(matrices),'matrices completas')
    for m in matrices:print(m['variante'],'Tmax',m['Tmax'],'Delta',m['Delta'],'riesgo',m['riesgo'],'alertas',m['alertas'])
    for r in selectivos:print('SELECTIVO',r)


if __name__=='__main__':main()
