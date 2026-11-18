"""Auditoría de matrices homogéneas, fuentes e indicadores; sin simulación."""
from hashlib import sha256
import argparse
from pathlib import Path
import json
import math
import comparar_circuitos as familia


def revisar_pieza(ruta,q,h):
    d=familia.base.viento.leer(familia.RAIZ/ruta)
    r=familia.leer_resultado(ruta)
    p=d['procedencia'];cf=p.get('confirmacion',{})
    assert cf.get('lado_m',p['lado_m'])==h
    assert cf.get('paso_max_s',p['paso_max_s'])==300
    assert p['capacidad_m3_h']==q
    assert p['agua_C']==18 and p['U_W_m3K']==5 and p['tope_global_W']==15000
    assert p['caudal_ramal_L_min']==18 and p['caudal_total_con_bypass_L_min']==162
    assert p['retiros_aislacion_edad_h']==[240,360] and p['temperatura_colocacion_C']==12
    assert p['regla']=='histeresis por circuito, cubierto antes de abrir; sin apagado global fijo'
    assert abs(cf.get('volumen_refrigerable_m3',p['volumen_refrigerable_m3'])-414.016)<1e-6
    if 'familia' in p:
        assert p['familia']['script_sha256']==sha256(Path(familia.__file__).read_bytes()).hexdigest()
        assert p['familia']['config_sha256']==sha256(Path(familia.__file__).with_name('familia_circuitos.json').read_bytes()).hexdigest()
    assert not r['pico_no_resuelto'] and r['horizonte_h']>=600
    for s in [r,r['base_336h']]:
        assert s['excede_70']==(s['Tmax']['valor']>70)
        assert s['excede_20']==(s['DeltaTmax']['valor']>20)
        assert abs(s['DeltaTmax']['valor']-s['DeltaTmax']['Tmax_C']+s['DeltaTmax']['Tmin_S25_C'])<1e-10
        assert abs(s['balance_J']['residuo'])<.01
        assert s['balance_J']['enfriamiento_pico_W']<=15000.000001
    assert abs(sum(d['control']['energia_extraida_circuito_J'])+r['balance_J']['enfriamiento'])<.1
    abiertos=[False]*9;ultimo=-1;n=0
    for e in d['control']['eventos_circuitos']:
        j=int(e['circuito'][1:])-1
        assert e['tiempo_h']>=ultimo;ultimo=e['tiempo_h']
        assert abiertos[j]!=e['abierto'];abiertos[j]=e['abierto']
        if e['abierto']:
            assert e['Tmin_tramos_C']>=19
            assert e['tiempo_h']>=p['cubierto_desde_h'][j]
        else:assert e['Tmin_tramos_C'] is None or e['Tmin_tramos_C']<=18
        n+=1
    assert abiertos==d['control']['circuitos_abiertos_final']
    for x in d['historia']:
        assert x['caudal_embebido_L_min']+x['caudal_bypass_L_min']==162
        assert x['caudal_embebido_L_min']==x['circuitos_abiertos']*18
    return n,p['modelo_viento'],p['archivos_sha256']


def riesgo(filas,pesos=None):
    pesos=pesos or [r['peso'] for r in filas]
    total=sum(pesos)
    assert total>0
    return dict(P_T=sum(w*r['excede_70'] for w,r in zip(pesos,filas))/total,
        P_delta=sum(w*r['excede_20'] for w,r in zip(pesos,filas))/total,
        P_union=sum(w*(r['excede_70'] or r['excede_20']) for w,r in zip(pesos,filas))/total)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--solo-base',action='store_true');args=ap.parse_args()
    config=familia.base.viento.leer(Path(familia.__file__).with_name('familia_circuitos.json'))
    incertidumbre=familia.base.viento.leer(familia.RAIZ/'casos/incertidumbre/parametros.json')
    assert incertidumbre['inicio']=='2026-11-19T10:00:00-03:00'
    assert len(incertidumbre['historias'])==3
    assert all(abs(c['peso']-1/3)<1e-14 for c in incertidumbre['historias'])
    metadatos=[];n_eventos=0;comunes=None
    for q,h in [(q,.4) for q in config['planes_m3_h']]+([] if args.solo_base else [(60,.2)]):
        ruta=familia.SALIDA/f'q{q}/malla_{h:g}/matriz.json'
        d=familia.base.viento.leer(ruta)
        filas=d['corridas'];familia.base.comun.validar_filas(filas)
        assert all(abs(r['peso']-1/24)<1e-14 for r in filas)
        assert len(d['archivos'])==24 and d['picos_no_resueltos']==0
        for archivo,r in zip(d['archivos'],filas):
            assert archivo['sha256']==sha256((familia.RAIZ/archivo['ruta']).read_bytes()).hexdigest()
            assert familia.leer_resultado(archivo['ruta'])==r
            n,viento,fuentes=revisar_pieza(archivo['ruta'],q,h)
            actual=(viento,fuentes)
            if comunes is None:comunes=actual
            assert actual==comunes
            n_eventos+=n
        assert riesgo(filas)==d['riesgo']
        assert riesgo([dict(r['base_336h'],peso=r['peso']) for r in filas])==d['riesgo_336']
        pesos={a:riesgo(filas,[r['peso']*(2 if r['clima']==a else 1) for r in filas]) for a in d['sensibilidades_pesos']}
        assert pesos==d['sensibilidades_pesos']
        soloSS=riesgo(filas,[r['peso'] if r['curva'].endswith('_SS') else 0 for r in filas])
        metadatos.append(dict(plan=f'q{q}',lado_m=h,riesgo=d['riesgo'],riesgo_336=d['riesgo_336'],solo_SS=soloSS,
            archivo=str(ruta.relative_to(familia.RAIZ)),matriz_sha256=sha256(ruta.read_bytes()).hexdigest()))
    esquema=familia.base.viento.leer(familia.RAIZ/'resultados/diseno_circuitos_colocacion/esquema.json')
    capa=max(c['volumen_m3'] for c in esquema['capas'])
    assert all(capa/q*60<=150 for q in config['planes_m3_h'])
    assert all(q<=60 for q in config['planes_m3_h'])
    refinos=[]
    if not args.solo_base:
        for q in [55,50,45]:
            for clima in ['ERA5-2024','ERA5-2025']:
                ruta=f'resultados/comparacion_circuitos/q{q}/malla_0.2/M4_SS_{clima}.json'
                n,viento,fuentes=revisar_pieza(ruta,q,.2)
                assert (viento,fuentes)==comunes
                n_eventos+=n
                r=familia.leer_resultado(ruta)
                refinos.append(dict(plan=f'q{q}',clima=clima,DeltaTmax_K=r['DeltaTmax']['valor'],
                    Tmax_C=r['Tmax']['valor'],excede_20=r['excede_20'],ruta=ruta,
                    sha256=sha256((familia.RAIZ/ruta).read_bytes()).hexdigest()))
    rutas=['casos/incertidumbre/parametros.json','casos/sensibilidad_h/familia_circuitos.json',
        'datos/hidratacion/manifiesto.json','resultados/diseno_circuitos_colocacion/esquema.json',
        'entregas/F02/insumos_equipo.json']
    texto=dict(matrices=metadatos,refinos_alternativas=refinos,transiciones_auditadas=n_eventos,
        insumos_comparacion_sha256={r:sha256((familia.RAIZ/r).read_bytes()).hexdigest() for r in rutas},
        inicio_comun=incertidumbre['inicio'],historias=incertidumbre['historias'],familia=config,
        comprobaciones='Pesos, pares, fuentes/clima comunes, coberturas, histéresis, energía, límites y probabilidades independientes',
        alcance='Cuatro matrices base completas y candidata fina completa; refinamientos alternativos son selectivos')
    familia.base.escribir(familia.SALIDA/('auditoria_base.json' if args.solo_base else 'auditoria.json'),texto)
    print('APROBADO:',len(metadatos),'matrices completas;',n_eventos,'transiciones; configuración y fuentes comunes.')


if __name__=='__main__':main()
