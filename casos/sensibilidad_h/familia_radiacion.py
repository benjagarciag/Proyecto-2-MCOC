"""Comparación y confirmación F02 con radiación, ventana común336h.

Sin --ejecutar no simula. Conserva fuentes y resultados históricos con hash.
"""
import argparse
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from time import perf_counter
import numpy as np
import sensibilidad_radiacion as radiacion

f=radiacion.f
RAIZ=f.RAIZ
SALIDA=RAIZ/'resultados/familia_radiacion_336h'
CONFIG=Path(__file__).with_suffix('.json')


def leer(p):return f.base.viento.leer(p)
def huella(p):return sha256(Path(p).read_bytes()).hexdigest()


def resolver(q,h,curva,clima,dt=300):
    cfg=leer(CONFIG)
    controles,_,_,_,programa,env,fuentes,climas,series,_,ref=f.ESTADO
    if h==.2:
        import cache_geometria_circuitos as cache
        if .2 not in f.GEOMETRIAS and cache.RUTA.exists():f.GEOMETRIAS[.2]=cache.cargar()
    ids,origen,mapa,centros=f.geometria(h)
    factor=60/q
    programa={vid:(t*factor,T) for vid,(t,T) in programa.items()}
    mapa=(mapa[0],mapa[1],[t*factor for t in mapa[2]],dict(mapa[3],cubierto_desde_h=[t*factor for t in mapa[2]]))
    cfg_rad=leer(Path(radiacion.__file__).with_name('radiacion_config.json'))
    rad,estad,fuente_clima=radiacion.modelo(clima,cfg_rad['variantes']['ambas'],cfg_rad)
    sol,hash_sol=radiacion.motor(mapa,centros,rad)
    fuente=next(x for x in fuentes if x['id']==curva)
    p=dict(referencia=ref,capacidad_m3_h=q,D_h=ref['D_h']*factor,lado_m=h,paso_max_s=dt,horizonte_h=336,
        temperatura_colocacion_C=12,agua_C=18,U_W_m3K=5,tope_global_W=15000,
        volumen_voxel_m3=float((ids>0).sum()*h**3),**mapa[3],
        radiacion=cfg_rad['variantes']['ambas'],albedo=.2,irradiancias=estad,clima_complementario=fuente_clima,
        script_sha256=huella(__file__),config_sha256=huella(CONFIG),
        radiacion_borde_sha256=huella(Path(radiacion.__file__).with_name('radiacion_borde.py')),
        configuracion_radiacion_sha256=huella(Path(radiacion.__file__).with_name('radiacion_config.json')),
        motor_radiacion_sha256=huella(radiacion.__file__),solver_adaptado_sha256=hash_sol,
        ecuacion_frio='U*V*max(T-18,0), circuito abierto, limitado globalmente a15kW',
        ventana='0–336h desde primera colocacion; no exige pico resuelto despues de336h')
    carpeta=SALIDA/f'q{q}'/f'malla_{h:g}_paso{dt}';carpeta.mkdir(parents=True,exist_ok=True)
    ruta=carpeta/f'{curva}_{clima}.json'
    if ruta.exists():
        if leer(ruta)['procedencia']!=p:raise ValueError(f'Cambió procedencia: {ruta}')
        print('Conservado',q,h,dt,curva,clima,flush=True)
        return ruta
    inicio=perf_counter()
    exportar=(h==.4 and dt==300 and (curva,clima)==('M4_SS','ERA5-2024'))
    anterior=radiacion.SALIDA/'ambas'/f'malla_{h:g}_paso{dt}'/f'{curva}_{clima}.json'
    if q==60 and anterior.exists() and not exportar:
        d=leer(anterior);a=d['procedencia']
        assert a['referencia']==ref and a['mapa']==mapa[3]
        assert a['solver_adaptado_sha256']==hash_sol
        assert a['parametros']==p['radiacion']
        assert a['borde_sha256']==p['radiacion_borde_sha256']
        assert a['configuracion_sha256']==p['configuracion_radiacion_sha256']
        assert a['script_sha256']==p['motor_radiacion_sha256']
        assert a['lado_m']==h and a['paso_max_s']==dt
        r=dict(d['corrida']['base_336h'],curva=curva,clima=clima,peso=fuente['peso']*climas[clima][0]['peso'])
        eventos=[e for e in d['control']['eventos_circuitos'] if e['tiempo_h']<=336]
        contenido=dict(procedencia=p,corrida=r,historia=[x for x in d['historia'] if x['tiempo_h']<=336],
            eventos_control_336=eventos,control_336=None,radiacion=d['radiacion_336'],campos_npz=None,
            reutilizado=dict(ruta=str(anterior.relative_to(RAIZ)),sha256=huella(anterior),
                alcance='Metricas336 exactas y eventos filtrados; sin inventar energia por ramal336 no guardada'))
    else:
        r=sol.simular(ids,origen,h,programa,fuente['curva'],replace(env,dt_tope_s=dt),climas[clima][1][:337],
            (0,0,2),h_aire_horario_W_m2K=series[clima]['h_W_m2K'][:337])
        contenido=dict(procedencia=p,corrida=dict(controles.metricas(r,336),curva=curva,clima=clima,
            peso=fuente['peso']*climas[clima][0]['peso']),historia=r.historia,
            eventos_control_336=r.control_circuitos['eventos_circuitos'],control_336=r.control_circuitos,
            radiacion=r.radiacion,campos_npz=None)
        if exportar:
            f.campos_guardar(ruta.with_suffix('.npz'),r,ids,origen,h,{})
            contenido['campos_npz']=str(ruta.with_suffix('.npz').relative_to(RAIZ))
    met=contenido['corrida'];energ=contenido['radiacion']
    assert abs(met['balance_J']['residuo'])<.05
    assert met['balance_J']['enfriamiento_pico_W']<=15000.000001
    assert abs(sum(energ[k] for k in ['solar_absorbida_exterior_J','conveccion_exterior_J','onda_larga_neta_J'])-met['balance_J']['aire'])<.5
    if contenido['control_336'] is not None:
        assert abs(sum(contenido['control_336']['energia_extraida_circuito_J'])+met['balance_J']['enfriamiento'])<.1
    contenido['segundos']=perf_counter()-inicio
    f.base.escribir(ruta,contenido)
    print('TERMINADO',q,h,dt,curva,clima,'Tmax',round(met['Tmax']['valor'],4),'Delta',round(met['DeltaTmax']['valor'],4),'reutilizado','reutilizado' in contenido,flush=True)
    return ruta


def agregar():
    for q in leer(CONFIG)['planes_m3_h']:
        for h in [.4,.2]:
            carpeta=SALIDA/f'q{q}'/f'malla_{h:g}_paso300'
            rutas=sorted(p for p in carpeta.glob('*.json') if p.name.startswith('M'))
            if len(rutas)!=24:continue
            filas=[leer(p)['corrida'] for p in rutas];f.base.comun.validar_filas(filas)
            m=dict(capacidad_m3_h=q,lado_m=h,paso_max_s=300,horizonte_h=336,D_h=f.ESTADO[-1]['D_h']*60/q,
                corridas=filas,riesgo=f.ESTADO[0].riesgo(filas),
                sensibilidades_pesos={c:f.ESTADO[0].riesgo(filas,c) for c in f.ESTADO[7]},
                archivos=[dict(ruta=str(p.relative_to(RAIZ)),sha256=huella(p)) for p in rutas],
                script_sha256=huella(__file__),config_sha256=huella(CONFIG))
            f.base.escribir(carpeta/'matriz.json',m)
            print('MATRIZ',q,h,m['riesgo'],flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ejecutar',action='store_true')
    p.add_argument('--fase',choices=['base','fina','temporal','alternativas','agregar'],default='base')
    p.add_argument('--lote',type=int,choices=[0,1,2])
    a=p.parse_args()
    if not a.ejecutar:print(__doc__);return
    f.iniciar();cfg=leer(CONFIG)
    pares=[(x['id'],c) for x in f.ESTADO[6] for c in f.ESTADO[7]]
    tareas=[]
    if a.fase=='base':tareas=[(q,.4,x,c,300) for q in cfg['planes_m3_h'] for x,c in pares]
    if a.fase=='fina':tareas=[(60,.2,x,c,300) for x,c in pares]
    if a.fase=='temporal':tareas=[(60,.4,x,c,150) for x,c in cfg['pares_temporales']]
    if a.fase=='alternativas':tareas=[(q,.2,x,c,300) for q in [55,50,45] for x,c in cfg['pares_alternativas_finas']]
    if a.lote is not None:tareas=tareas[a.lote::3]
    print('FASE',a.fase,'LOTE',a.lote,'TAREAS',len(tareas),flush=True)
    for t in tareas:resolver(*t)
    if a.lote is None:agregar()


if __name__=='__main__':main()
