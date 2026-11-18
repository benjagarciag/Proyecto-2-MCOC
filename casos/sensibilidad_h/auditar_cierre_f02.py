"""Audita familia homogénea final y propuesta fina completa; sin solver."""
from pathlib import Path
from hashlib import sha256
import json
import numpy as np

R=Path(__file__).resolve().parents[2];S=R/'resultados/cierre_f02'


def leer(p):return json.loads(p.read_text(encoding='utf8'))
def huella(p):return sha256(Path(p).read_bytes()).hexdigest()


def pieza(path):
    d=leer(path);p=d['procedencia'];r=d['corrida'];q=p['q_m3_h'];h=p['lado_m']
    for k,n in [('script_sha256','cierre_f02.py'),('config_sha256','cierre_f02.json'),
        ('motor_proteccion_sha256','proteccion_postdesmolde.py'),('config_proteccion_sha256','proteccion_postdesmolde.json'),
        ('radiacion_borde_sha256','radiacion_borde.py')]:assert p[k]==huella(Path(__file__).with_name(n))
    assert p['horizonte_h']==r['horizonte_h']==672
    assert p['proteccion']==dict(retiro_ultima_manta_edad_h=504,transmitancia_solar_postretiro=.1)
    assert p['paso_max_s']==300 and abs(p['mapa']['volumen_refrigerable_m3']-414.016)<1e-6
    assert abs(p['D_h']-p['referencia']['D_h']*60/q)<1e-12
    np.testing.assert_allclose(p['mapa']['cubierto_desde_h'],np.array(p['referencia']['cubierto_desde_h'])*60/q,atol=1e-12)
    for k,a in [('snapshot','sha256'),('snapshot_original','original_sha256')]:assert huella(R/p['clima'][k])==p['clima'][a]
    assert r['excede_70']==(r['Tmax']['valor']>70) and r['excede_20']==(r['DeltaTmax']['valor']>20)
    dif=r['DeltaTmax'];assert abs(dif['valor']-dif['Tmax_C']+dif['Tmin_S25_C'])<1e-9
    assert abs(r['balance_J']['residuo'])<.05 and r['balance_J']['enfriamiento_pico_W']<=15000.000001
    assert abs(sum(d['control']['energia_extraida_circuito_J'])+r['balance_J']['enfriamiento'])<.1
    rad=d['radiacion'];assert rad['residual_superficie_max_W_m2']<2e-8
    assert abs(sum(rad[k] for k in ['solar_absorbida_exterior_J','conveccion_exterior_J','onda_larga_neta_J'])-r['balance_J']['aire'])<.5
    estados=[False]*9;ultimo=-1
    for e in d['control']['eventos_circuitos']:
        j=int(e['circuito'][1:])-1
        assert ultimo<=e['tiempo_h']<=672;ultimo=e['tiempo_h']
        assert estados[j]!=e['abierto'];estados[j]=e['abierto']
        if e['abierto']:assert e['Tmin_tramos_C']>=19 and e['tiempo_h']>=p['mapa']['cubierto_desde_h'][j]
        else:assert e['Tmin_tramos_C'] is None or e['Tmin_tramos_C']<=18
    assert estados==d['control']['circuitos_abiertos_final']
    for x in d['historia']:
        assert x['caudal_embebido_L_min']+x['caudal_bypass_L_min']==162
        assert abs(x['Tmax_C']-x['Tmin_S25_C']-x['DeltaT_K'])<1e-9
    assert d['historia'][-1]['tiempo_h']==672
    anterior=leer(R/f"resultados/familia_radiacion_336h/q{q}/malla_{h:g}_paso300/{r['curva']}_{r['clima']}.json")
    assert d['base_336h']==anterior['corrida']
    hh=[x for x in d['historia'] if x['tiempo_h']<=336]
    assert len(hh)==len(anterior['historia'])
    for a,b in zip(hh,anterior['historia']):
        for k in ['tiempo_h','Tmax_C','Tmin_S25_C','DeltaT_K']:assert abs(a[k]-b[k])<1e-8
    if 'reutilizado' in d:
        o=d['reutilizado'];assert huella(R/o['ruta'])==o['sha256']
        original=leer(R/o['ruta'])
        for k in ['corrida','historia','control','radiacion']:assert d[k]==original[k]
    if 'campos_npz' in d:assert (R/d['campos_npz']).is_file()
    return d


def riesgo(rs,prioridad=None,solo_ss=False):
    assert len(rs)==24 and len({(r['curva'],r['clima']) for r in rs})==24
    assert all(abs(r['peso']-1/24)<1e-14 for r in rs)
    w=np.array([r['peso']*(2 if r['clima']==prioridad else 1)*(not solo_ss or r['curva'].endswith('_SS')) for r in rs])
    w=w/w.sum()
    return dict(P_T=float(sum(x*r['excede_70'] for x,r in zip(w,rs))),
        P_delta=float(sum(x*r['excede_20'] for x,r in zip(w,rs))),
        P_union=float(sum(x*(r['excede_70'] or r['excede_20']) for x,r in zip(w,rs))))


def main():
    matrices=[];piezas=[];porgrupo={}
    for q,h in [(60,.4),(55,.4),(60,.2)]:
        carpeta=S/f'q{q}/malla_{h:g}_paso300';rutas=sorted(carpeta.glob('M*.json'))
        assert len(rutas)==24,(q,h,len(rutas))
        ds=[pieza(p) for p in rutas];piezas+=ds
        rs=[d['corrida'] for d in ds];porgrupo[(q,h)]=ds
        m=dict(q=q,h=h,paso_max_s=300,D_h=ds[0]['procedencia']['D_h'],horizonte_h=672,
            Tmax=max(r['Tmax']['valor'] for r in rs),Delta=max(r['DeltaTmax']['valor'] for r in rs),
            riesgo=riesgo(rs),riesgo_336=riesgo([dict(d['base_336h'],curva=d['corrida']['curva'],clima=d['corrida']['clima'],peso=d['corrida']['peso']) for d in ds]),
            pesos_solo_SS=riesgo(rs,solo_ss=True),pesos_doble_anio={c:riesgo(rs,c) for c in ['ERA5-2023','ERA5-2024','ERA5-2025']},
            alertas=sum(r['pico_no_resuelto'] for r in rs),corridas=rs,
            archivos=[dict(ruta=str(p.relative_to(R)),sha256=huella(p)) for p in rutas])
        (carpeta/'matriz.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        matrices.append({k:v for k,v in m.items() if k not in ['corridas','archivos']})
    base={(d['corrida']['curva'],d['corrida']['clima']):d['corrida'] for d in porgrupo[(60,.4)]}
    cambios=[]
    for d in porgrupo[(60,.2)]:
        r=d['corrida'];b=base[(r['curva'],r['clima'])]
        cambios.append(dict(curva=r['curva'],clima=r['clima'],Tmax=r['Tmax']['valor']-b['Tmax']['valor'],Delta=r['DeltaTmax']['valor']-b['DeltaTmax']['valor']))
    resumen=dict(estado='APROBADA',matrices=matrices,piezas=len(piezas),
        reutilizadas=sum('reutilizado' in d for d in piezas),
        transiciones=sum(len(d['control']['eventos_circuitos']) for d in piezas),cambios_espaciales=cambios,
        max_cambio_espacial_Tmax=max(abs(x['Tmax']) for x in cambios),
        max_cambio_espacial_Delta=max(abs(x['Delta']) for x in cambios),
        max_residuo_J=max(abs(d['corrida']['balance_J']['residuo']) for d in piezas),
        max_residuo_relativo=max(abs(d['corrida']['balance_J']['residuo'])/max(1,sum(abs(d['corrida']['balance_J'][k]) for k in ['colocacion','hidratacion','aire','suelo','enfriamiento'])) for d in piezas),
        auditor_sha256=huella(__file__))
    (S/'resumen.json').write_text(json.dumps(resumen,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('AUDITORIA APROBADA',resumen['piezas'],'piezas;',resumen['transiciones'],'transiciones')
    for m in matrices:print(m)
    print('CAMBIO ESPACIAL MAXIMO',resumen['max_cambio_espacial_Delta'])


if __name__=='__main__':main()
