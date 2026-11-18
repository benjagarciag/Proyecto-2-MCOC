"""Familia final55/60 con proteccion504h+sombra; matrices672h y propuesta fina completa."""
import argparse
from dataclasses import replace
from pathlib import Path
from time import perf_counter
import proteccion_postdesmolde as p
import numpy as np

R=p.RAIZ;S=R/'resultados/cierre_f02';CONFIG=Path(__file__).with_suffix('.json')


def resolver(q,h,curva,clima):
    controles,_,_,_,programa,env,fuentes,climas,series,_,ref=p.f.ESTADO
    if h==.2:
        import cache_geometria_circuitos as cache
        if .2 not in p.f.GEOMETRIAS and cache.RUTA.exists():p.f.GEOMETRIAS[.2]=cache.cargar()
    ids,origen,mapa,centros=p.f.geometria(h)
    factor=60/q
    programa={j:(t*factor,T) for j,(t,T) in programa.items()}
    mapa=(mapa[0],mapa[1],[t*factor for t in mapa[2]],dict(mapa[3],cubierto_desde_h=[t*factor for t in mapa[2]]))
    cfg=p.leer(Path(p.__file__).with_suffix('.json'))
    op=cfg['variantes']['combinada_504_sombra_90']
    def capas(cs):return tuple(replace(c,retiro_edad_h=504) if c.retiro_edad_h==360 else c for c in cs)
    env=replace(env,capas_laterales=capas(env.capas_laterales),capas_superiores=capas(env.capas_superiores),dt_tope_s=300)
    rc=p.leer(Path(p.__file__).with_name('radiacion_config.json'))
    rad,estad,climafuente=p.estudio.modelo(clima,rc['variantes']['ambas'],rc)
    rad=p.RadiacionSombra(rad,504,.1)
    sol,hashsol=p.motor(mapa,centros,rad)
    fuente=next(x for x in fuentes if x['id']==curva)
    procedencia=dict(q_m3_h=q,lado_m=h,paso_max_s=300,horizonte_h=672,D_h=ref['D_h']*factor,
        referencia=ref,mapa=mapa[3],proteccion=op,clima=climafuente,
        script_sha256=p.huella(__file__),config_sha256=p.huella(CONFIG),
        motor_proteccion_sha256=p.huella(p.__file__),config_proteccion_sha256=p.huella(p.CONFIG),
        radiacion_borde_sha256=p.huella(p.estudio.rb.__file__),solver_adaptado_sha256=hashsol)
    carpeta=S/f'q{q}/malla_{h:g}_paso300';carpeta.mkdir(parents=True,exist_ok=True)
    ruta=carpeta/f'{curva}_{clima}.json'
    if ruta.exists():
        assert p.leer(ruta)['procedencia']==procedencia
        print('CONSERVADO',q,h,curva,clima,flush=True);return
    inicio=perf_counter()
    antigua=p.SALIDA/'combinada_504_sombra_90'/f'malla_{h:g}_paso300/{curva}_{clima}.json'
    campos=(h==.4 and curva=='M4_SS' and clima=='ERA5-2024')
    if q==60 and antigua.exists() and not campos:
        a=p.leer(antigua)
        assert a['procedencia']['solver_adaptado_sha256']==hashsol
        assert a['procedencia']['script_sha256']==procedencia['motor_proteccion_sha256']
        assert a['procedencia']['parametros']==op and a['procedencia']['mapa']==mapa[3]
        contenido={k:a[k] for k in ['corrida','base_336h','historia','control','radiacion']}
        contenido['reutilizado']=dict(ruta=str(antigua.relative_to(R)),sha256=p.huella(antigua))
    else:
        r=sol.simular(ids,origen,h,programa,fuente['curva'],env,climas[clima][1][:673],(0,0,2),h_aire_horario_W_m2K=series[clima]['h_W_m2K'][:673])
        met=controles.metricas(r,672)
        assert abs(r.balance_J['residuo'])<.05
        assert r.balance_J['enfriamiento_pico_W']<=15000.000001
        assert abs(sum(r.control_circuitos['energia_extraida_circuito_J'])+r.balance_J['enfriamiento'])<.1
        contenido=dict(corrida=dict(met,curva=curva,clima=clima,peso=fuente['peso']*climas[clima][0]['peso'],
            pico_no_resuelto=controles.alertas_cola(r,672,ref['D_h']*factor,168)),
            base_336h=None,historia=r.historia,control=r.control_circuitos,radiacion=r.radiacion)
        if campos:
            p.f.campos_guardar(ruta.with_suffix('.npz'),r,ids,origen,h,{})
            contenido['campos_npz']=str(ruta.with_suffix('.npz').relative_to(R))
    if h==.4:
        original=p.leer(R/f'resultados/familia_radiacion_336h/q{q}/malla_0.4_paso300/{curva}_{clima}.json')
        anterior=[x for x in contenido['historia'] if x['tiempo_h']<=336]
        assert len(anterior)==len(original['historia'])
        for a,b in zip(anterior,original['historia']):
            for k in ['tiempo_h','Tmax_C','Tmin_S25_C','DeltaT_K']:assert abs(a[k]-b[k])<1e-8
        contenido['base_336h']=original['corrida']
    else:
        original=p.leer(R/f'resultados/familia_radiacion_336h/q60/malla_0.2_paso300/{curva}_{clima}.json')
        anterior=[x for x in contenido['historia'] if x['tiempo_h']<=336]
        assert len(anterior)==len(original['historia'])
        for a,b in zip(anterior,original['historia']):
            for k in ['tiempo_h','Tmax_C','Tmin_S25_C','DeltaT_K']:assert abs(a[k]-b[k])<1e-8
        contenido['base_336h']=original['corrida']
    p.f.base.escribir(ruta,dict(procedencia=procedencia,**contenido,segundos=perf_counter()-inicio))
    print('TERMINADO',q,h,curva,clima,'Delta',round(contenido['corrida']['DeltaTmax']['valor'],4),
        'alerta',contenido['corrida']['pico_no_resuelto'],'s',round(perf_counter()-inicio,1),flush=True)


def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--ejecutar',action='store_true');a.add_argument('--fase',choices=['base','fina'],default='base')
    a.add_argument('--lote',type=int,default=0);a.add_argument('--lotes',type=int,default=3)
    z=a.parse_args()
    if not z.ejecutar:print(__doc__);return
    p.f.iniciar()
    pares=[(x['id'],c) for x in p.f.ESTADO[6] for c in p.f.ESTADO[7]]
    tareas=[(q,.4,*par) for q in [60,55] for par in pares] if z.fase=='base' else [(60,.2,*par) for par in pares]
    for t in tareas[z.lote::z.lotes]:resolver(*t)


if __name__=='__main__':main()
