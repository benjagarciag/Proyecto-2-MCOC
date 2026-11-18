"""Comparación de cuatro mecanismos en una ventana común672h, sin alterar piezas."""
import argparse,json
from hashlib import sha256
from pathlib import Path
from dataclasses import replace
import sensibilidad_radiacion as estudio


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ejecutar',action='store_true');a=p.parse_args()
    if not a.ejecutar:print(__doc__);return
    estudio.f.iniciar();f=estudio.f
    controles,_,_,_,programa,env,fuentes,climas,series,_,prov=f.ESTADO
    ids,origen,mapa,centros=f.geometria(.4)
    cfg=f.base.viento.leer(Path(estudio.__file__).with_name('radiacion_config.json'))
    fuente=next(x for x in fuentes if x['id']=='M4_SS')
    destino=estudio.SALIDA/'ventana_comun_672';destino.mkdir(parents=True,exist_ok=True)
    for variante in ['sin_radiacion','solar','larga','ambas']:
        ruta=destino/f'{variante}.json'
        if ruta.exists():continue
        anterior=f.base.viento.leer(estudio.SALIDA/variante/'malla_0.4_paso300/M4_SS_ERA5-2024.json')
        if anterior['corrida']['horizonte_h']==672:
            resultado=dict(anterior,origen_reutilizado=True)
        else:
            rad,_,_=estudio.modelo('ERA5-2024',cfg['variantes'][variante],cfg)
            sol,huella=estudio.motor(mapa,centros,rad)
            assert huella==anterior['procedencia']['solver_adaptado_sha256']
            r=sol.simular(ids,origen,.4,programa,fuente['curva'],replace(env,dt_tope_s=300),climas['ERA5-2024'][1][:673],(0,0,2),h_aire_horario_W_m2K=series['ERA5-2024']['h_W_m2K'][:673])
            assert abs(r.balance_J['residuo'])<.05
            met=controles.metricas(r,672)
            resultado=dict(procedencia=anterior['procedencia'],corrida=dict(curva='M4_SS',clima='ERA5-2024',peso=1/24,base_336h=anterior['corrida']['base_336h'],**met,pico_no_resuelto=controles.alertas_cola(r,672,prov['D_h'],168)),historia=r.historia,control=r.control_circuitos,radiacion=r.radiacion,radiacion_336=anterior['radiacion_336'])
        resultado['ventana_comun']=dict(horas=672,script_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
        f.base.escribir(ruta,resultado)
        print('Ventana común',variante,'Tmax',resultado['corrida']['Tmax']['valor'],'Delta',resultado['corrida']['DeltaTmax']['valor'],flush=True)


if __name__=='__main__':main()
