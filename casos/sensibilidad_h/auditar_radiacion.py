"""Audita evidencias radiativas sin ejecutar simulaciones."""
import json
from hashlib import sha256
from pathlib import Path
import numpy as np

RAIZ=Path(__file__).resolve().parents[2]
SALIDA=RAIZ/'resultados/sensibilidad_radiacion'


def leer(p):return json.loads(p.read_text(encoding='utf-8'))


def auditar():
    import radiacion_borde as rb
    manifest=leer(RAIZ/'datos/clima/radiacion/manifiesto.json')
    cfg=leer(RAIZ/'casos/incertidumbre/parametros.json')
    for c in cfg['historias']:
        hr=leer(RAIZ/manifest[c['id']]['snapshot'])['respuesta']['hourly']
        I,_=rb.irradiancias(hr,c['inicio'],0,.2)
        giro,_=rb.irradiancias(hr,c['inicio'],90,.2)
        np.testing.assert_allclose(I[:,:2],giro[:,:2],atol=1e-10)
        np.testing.assert_allclose(I[:,2:].sum(axis=1),giro[:,2:].sum(axis=1),atol=1e-10)
        assert (I>=0).all()
    piezas=[p for p in SALIDA.glob('*/malla*/*.json') if p.name.startswith('M')]+list((SALIDA/'ventana_comun_672').glob('*.json'));eventos=0
    for ruta in piezas:
        d=leer(ruta);p=d['procedencia'];r=d['corrida'];ref=p['referencia']
        if 'ventana_comun' in d:
            assert r['horizonte_h']==672
            assert d['ventana_comun']['script_sha256']==sha256(Path(__file__).with_name('radiacion_ventana_comun.py').read_bytes()).hexdigest()
        for clave,archivo in [('script_sha256','sensibilidad_radiacion.py'),('borde_sha256','radiacion_borde.py'),('configuracion_sha256','radiacion_config.json')]:
            assert p[clave]==sha256(Path(__file__).with_name(archivo).read_bytes()).hexdigest()
        assert ref['temperatura_colocacion_C']==12 and ref['tope_global_W']==15000
        assert ref['capacidad_m3_h']==60 and ref['agua_C']==18 and ref['U_W_m3K']==5
        assert ref['retiros_aislacion_edad_h']==[240,360] and ref['retiro_madera_edad_h']==72
        clima=p['clima_complementario']
        assert sha256((RAIZ/clima['snapshot']).read_bytes()).hexdigest()==clima['sha256']
        assert sha256((RAIZ/clima['snapshot_original']).read_bytes()).hexdigest()==clima['original_sha256']
        assert all(v==0 for v in clima['max_diferencia_variables_comunes'].values())
        assert p['irradiancias']['descomposicion_horizontal_error_max']<.11
        assert abs(ref['volumen_refrigerable_m3']-414.016)<1e-6
        for met,rad in [(r,d['radiacion']),(r['base_336h'],d['radiacion_336'])]:
            assert met['excede_20']==(met['DeltaTmax']['valor']>20)
            assert met['excede_70']==(met['Tmax']['valor']>70)
            delta=met['DeltaTmax']
            assert abs(delta['valor']-delta['Tmax_C']+delta['Tmin_S25_C'])<1e-9
            assert abs(met['balance_J']['residuo'])<.05
            assert met['balance_J']['enfriamiento_pico_W']<=15000.000001
            assert rad['residual_superficie_max_W_m2']<2e-8
            energia=sum(rad[k] for k in ['solar_absorbida_exterior_J','conveccion_exterior_J','onda_larga_neta_J'])
            assert abs(energia-met['balance_J']['aire'])<.5
        abiertos=[False]*9;ultimo=-1
        for e in d['control']['eventos_circuitos']:
            j=int(e['circuito'][1:])-1
            assert e['tiempo_h']>=ultimo;ultimo=e['tiempo_h']
            assert abiertos[j]!=e['abierto'];abiertos[j]=e['abierto']
            if e['abierto']:
                assert e['Tmin_tramos_C']>=19 and e['tiempo_h']>=ref['cubierto_desde_h'][j]
            else:assert e['Tmin_tramos_C'] is None or e['Tmin_tramos_C']<=18
            eventos+=1
        assert abiertos==d['control']['circuitos_abiertos_final']
        assert abs(sum(d['control']['energia_extraida_circuito_J'])+r['balance_J']['enfriamiento'])<.1
        for x in d['historia']:
            assert x['caudal_embebido_L_min']+x['caudal_bypass_L_min']==162
            assert abs(x['Tmax_C']-x['Tmin_S25_C']-x['DeltaT_K'])<1e-9
    matriz=leer(SALIDA/'ambas/malla_0.4_paso300/matriz.json')
    assert matriz['agregador_sha256']==sha256(Path(__file__).with_name('agregar_radiacion.py').read_bytes()).hexdigest()
    filas=matriz['corridas'];assert len(filas)==24
    crit=max(filas,key=lambda r:r['DeltaTmax']['valor'])
    for variante in ['clara','oscura','despejado','giro90']:
        assert (SALIDA/variante/f"malla_0.4_paso300/{crit['curva']}_{crit['clima']}.json").exists()
    for h,dt in [(.2,300),(.4,150)]:
        assert (SALIDA/'ambas'/f'malla_{h:g}_paso{dt}/M4_SS_ERA5-2024.json').exists()
    assert len(list((SALIDA/'ventana_comun_672').glob('*.json')))==4
    for v in ['clara','oscura']:assert (SALIDA/v/'malla_0.4_paso300/M4_SS_ERA5-2024.json').exists()
    assert len({(r['curva'],r['clima']) for r in filas})==24
    assert all(abs(r['peso']-1/24)<1e-14 for r in filas)
    for a in matriz['archivos']:assert sha256((RAIZ/a['ruta']).read_bytes()).hexdigest()==a['sha256']
    control=leer(SALIDA/'sin_radiacion/malla_0.4_paso300/M4_SS_ERA5-2024.json')['corrida']
    anterior=leer(RAIZ/'resultados/circuitos_histeresis/M4_SS_ERA5-2024.json')['corrida']
    for nuevo,viejo in [(control,anterior),(control['base_336h'],anterior['base_336h'])]:
        for k in ['Tmax','DeltaTmax']:assert abs(nuevo[k]['valor']-viejo[k]['valor'])<1e-9
    for campo,fil in [('riesgo_observado',filas),('riesgo_336',[r['base_336h'] for r in filas])]:
        observado=dict(P_T=np.mean([r['excede_70'] for r in fil]),P_delta=np.mean([r['excede_20'] for r in fil]),P_union=np.mean([r['excede_70'] or r['excede_20'] for r in fil]))
        for k,v in observado.items():assert abs(matriz[campo][k]-v)<1e-12
    resumen=dict(piezas=len(piezas),transiciones=eventos,matriz_pares=24,
        piezas_reutilizadas_ventana_comun=sum(bool(leer(p).get('origen_reutilizado')) for p in piezas),
        picos_no_resueltos=matriz['picos_no_resueltos'],estado='APROBADA')
    (SALIDA/'auditoria.json').write_text(json.dumps(resumen,indent=2),encoding='utf-8')
    print(resumen)


if __name__=='__main__':auditar()
