"""Auditoría de comparación F02 con solar+LW en la ventana común336h."""
from pathlib import Path
import numpy as np
import familia_radiacion as motor

R=motor.RAIZ
S=motor.SALIDA


def pieza(q,h,curva,clima,dt=300):
    path=S/f'q{q}'/f'malla_{h:g}_paso{dt}'/f'{curva}_{clima}.json'
    d=motor.leer(path);p=d['procedencia'];r=d['corrida']
    assert p['script_sha256']==motor.huella(motor.__file__)
    assert p['config_sha256']==motor.huella(motor.CONFIG)
    assert p['radiacion_borde_sha256']==motor.huella(Path(motor.__file__).with_name('radiacion_borde.py'))
    assert p['configuracion_radiacion_sha256']==motor.huella(Path(motor.__file__).with_name('radiacion_config.json'))
    assert p['motor_radiacion_sha256']==motor.huella(Path(motor.__file__).with_name('sensibilidad_radiacion.py'))
    assert p['capacidad_m3_h']==q and p['lado_m']==h and p['paso_max_s']==dt
    assert r['horizonte_h']==p['horizonte_h']==336
    assert p['temperatura_colocacion_C']==12 and p['agua_C']==18 and p['U_W_m3K']==5 and p['tope_global_W']==15000
    assert abs(p['volumen_refrigerable_m3']-414.016)<1e-6
    assert p['radiacion']==dict(alpha=.6,eps=.9,cielo='nubes',yaw=0)
    esquema=motor.leer(R/'resultados/diseno_circuitos_colocacion/esquema.json')
    vcapas=sum(c['volumen_m3'] for c in esquema['capas'])
    assert abs(p['D_h']-vcapas/q)<1e-10
    assert abs(vcapas-p['referencia']['volumen_ifc_m3'])<1e-3
    np.testing.assert_allclose(p['cubierto_desde_h'],np.array(p['referencia']['cubierto_desde_h'])*60/q,atol=1e-12)
    for k in ['snapshot','snapshot_original']:
        c=p['clima_complementario'];hashkey='sha256' if k=='snapshot' else 'original_sha256'
        assert motor.huella(R/c[k])==c[hashkey]
    assert r['excede_70']==(r['Tmax']['valor']>70)
    assert r['excede_20']==(r['DeltaTmax']['valor']>20)
    diff=r['DeltaTmax'];assert abs(diff['valor']-diff['Tmax_C']+diff['Tmin_S25_C'])<1e-9
    assert 0<=diff['tiempo_h']<=336 and 0<=r['Tmax']['tiempo_h']<=336
    assert abs(r['balance_J']['residuo'])<.05
    assert r['balance_J']['enfriamiento_pico_W']<=15000.000001
    rad=d['radiacion'];assert rad['residual_superficie_max_W_m2']<2e-8
    assert abs(sum(rad[k] for k in ['solar_absorbida_exterior_J','conveccion_exterior_J','onda_larga_neta_J'])-r['balance_J']['aire'])<.5
    abiertos=[False]*9;ultimo=-1
    for e in d['eventos_control_336']:
        assert ultimo<=e['tiempo_h']<=336;ultimo=e['tiempo_h']
        j=int(e['circuito'][1:])-1
        assert abiertos[j]!=e['abierto'];abiertos[j]=e['abierto']
        if e['abierto']:assert e['Tmin_tramos_C']>=19 and e['tiempo_h']>=p['cubierto_desde_h'][j]
        else:assert e['Tmin_tramos_C'] is None or e['Tmin_tramos_C']<=18
    if d['control_336'] is not None:
        assert abiertos==d['control_336']['circuitos_abiertos_final']
        assert abs(sum(d['control_336']['energia_extraida_circuito_J'])+r['balance_J']['enfriamiento'])<.1
    else:
        o=d['reutilizado'];assert motor.huella(R/o['ruta'])==o['sha256']
        original=motor.leer(R/o['ruta'])
        for k,v in original['corrida']['base_336h'].items():assert r[k]==v
        assert d['radiacion']==original['radiacion_336']
    for hi in d['historia']:
        assert hi['tiempo_h']<=336
        assert hi['caudal_embebido_L_min']+hi['caudal_bypass_L_min']==162
        assert abs(hi['Tmax_C']-hi['Tmin_S25_C']-hi['DeltaT_K'])<1e-9
    return d,path


def probabilidades(filas,weights=None):
    w=np.array(weights if weights is not None else [r['peso'] for r in filas]);w=w/w.sum()
    return dict(P_T=float(sum(wi*r['excede_70'] for wi,r in zip(w,filas))),
        P_delta=float(sum(wi*r['excede_20'] for wi,r in zip(w,filas))),
        P_union=float(sum(wi*(r['excede_70'] or r['excede_20']) for wi,r in zip(w,filas))))


def main():
    cfg=motor.leer(motor.CONFIG)
    matrices={};piezas=[];planes=[]
    for q,h in [(q,.4) for q in cfg['planes_m3_h']]+[(60,.2)]:
        path=S/f'q{q}'/f'malla_{h:g}_paso300/matriz.json';m=motor.leer(path)
        filas=m['corridas'];motor.f.base.comun.validar_filas(filas)
        assert len({(r['curva'],r['clima']) for r in filas})==24 and len(m['archivos'])==24
        assert all(abs(r['peso']-1/24)<1e-14 for r in filas)
        for r,a in zip(filas,m['archivos']):
            d,p=pieza(q,h,r['curva'],r['clima']);assert r==d['corrida']
            assert motor.huella(R/a['ruta'])==a['sha256'] and p==R/a['ruta']
            piezas.append(d)
        for k,v in probabilidades(filas).items():assert abs(m['riesgo'][k]-v)<1e-12
        solo=probabilidades(filas,[r['peso'] if r['curva'].endswith('_SS') else 0 for r in filas])
        for c,riesgo in m['sensibilidades_pesos'].items():
            calculo=probabilidades(filas,[r['peso']*(2 if r['clima']==c else 1) for r in filas])
            for k,v in calculo.items():assert abs(riesgo[k]-v)<1e-12
        matrices[(q,h)]=m
        planes.append(dict(q=q,h=h,D_h=m['D_h'],Tmax=max(r['Tmax']['valor'] for r in filas),
            Delta=max(r['DeltaTmax']['valor'] for r in filas),riesgo=m['riesgo'],solo_SS=solo))
    base={(r['curva'],r['clima']):r for r in matrices[(60,.4)]['corridas']}
    fina={(r['curva'],r['clima']):r for r in matrices[(60,.2)]['corridas']}
    cambios=[dict(curva=c,clima=a,Tmax=fina[(c,a)]['Tmax']['valor']-b['Tmax']['valor'],
        Delta=fina[(c,a)]['DeltaTmax']['valor']-b['DeltaTmax']['valor']) for (c,a),b in base.items()]
    temporal=[]
    for c,a in cfg['pares_temporales']:
        d,_=pieza(60,.4,c,a,150);piezas.append(d);r=d['corrida'];b=base[(c,a)]
        temporal.append(dict(curva=c,clima=a,Tmax=r['Tmax']['valor']-b['Tmax']['valor'],Delta=r['DeltaTmax']['valor']-b['DeltaTmax']['valor']))
    alternativas=[]
    for q in [55,50,45]:
        for c,a in cfg['pares_alternativas_finas']:
            d,_=pieza(q,.2,c,a);piezas.append(d);alternativas.append(dict(q=q,curva=c,clima=a,Tmax=d['corrida']['Tmax']['valor'],Delta=d['corrida']['DeltaTmax']['valor']))
    assert len(piezas)==129
    # La factibilidad de unión se evalúa con el volumen físico, no el voxelizado.
    esquema=motor.leer(R/'resultados/diseno_circuitos_colocacion/esquema.json')
    vmax=max(c['volumen_m3'] for c in esquema['capas'])
    union={str(q):vmax/q*60 for q in cfg['planes_m3_h']}
    assert all(x<=150 for x in union.values())
    resumen=dict(estado='APROBADA',horizonte_h=336,matrices_completas=5,piezas=len(piezas),
        transiciones=sum(len(d['eventos_control_336']) for d in piezas),
        reutilizadas=sum('reutilizado' in d for d in piezas),planes=planes,
        cambios_espaciales=cambios,cambios_temporales=temporal,alternativas_finas=alternativas,
        max_cambio_espacial_Tmax=max(abs(r['Tmax']) for r in cambios),
        max_cambio_espacial_Delta=max(abs(r['Delta']) for r in cambios),
        max_cambio_temporal_Tmax=max(abs(r['Tmax']) for r in temporal),
        max_cambio_temporal_Delta=max(abs(r['Delta']) for r in temporal),
        minutos_capa_mayor=union,script_sha256=motor.huella(__file__))
    motor.f.base.escribir(S/'resumen.json',resumen)
    print('AUDITORIA APROBADA:',len(piezas),'piezas,5 matrices;',resumen['transiciones'],'transiciones')
    print('Planes',planes)
    print('Cambios maximosDelta espacio/tiempo',resumen['max_cambio_espacial_Delta'],resumen['max_cambio_temporal_Delta'])


if __name__=='__main__':main()
