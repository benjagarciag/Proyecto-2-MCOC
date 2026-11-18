"""Sensibilidad separada de espacio/tiempo del control de nueve circuitos.

Mantiene las 11 capas físicas y proyecta la zona refrigerable de referencia
por pertenencia al voxel de 0.4 m. No vuelve a erosionar una celda fina:
eso cambiaría el espesor físico excluido y el modelo de enfriamiento.
"""
import argparse
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
from time import perf_counter
import numpy as np
import simular_circuitos as base
from control_circuitos import crear_mapa


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ejecutar',action='store_true')
    args=p.parse_args()
    if not args.ejecutar:
        print(__doc__);return
    controles,solver,ids,origen,programa,env,fuentes,climas,series,cfg,prov=base.preparar()
    base.verificar(solver)
    esquema=base.viento.leer(base.RAIZ/'resultados/diseno_circuitos_colocacion/esquema.json')
    datos=base.viento._preparacion.cargar()[0]
    config=datos.leer(datos.RAIZ/datos.leer(datos.CONFIG)['base'])
    modelo=controles.extraer_fundacion_ifc(base.RAIZ/config['archivo_ifc'])
    asignacion_base=solver.MAPA_CONTROL[1].copy()
    zona=np.full(ids.shape,-1,int)
    zona.ravel()[np.flatnonzero(ids)]=asignacion_base
    salida=base.RAIZ/'resultados/circuitos_confirmacion'
    salida.mkdir(parents=True,exist_ok=True)
    casos=[('M4_SS','ERA5-2024'),('M4_SS','ERA5-2025'),('M2_SS','ERA5-2024')]
    filas=[]
    for variante,h,dt in [('temporal',.4,150),('espacial',.2,300)]:
        if h==.4:
            actuales=ids
        else:
            vox=controles.voxelizar_fundacion(modelo,pasos_m=(h,)*3)
            ocupada=controles.asignar_vertidas(modelo,vox).vertida_id>0
            actuales=np.zeros_like(ocupada,dtype=int)
            for z,plano in enumerate(ocupada):
                capa=min(int(((vox.grilla.origen_m[2]+(z+.5)*h)+1e-8)/.4),10)
                actuales[z][plano]=capa+1
            origen_fino=np.asarray(vox.grilla.origen_m)
            assert np.allclose(origen_fino,origen)
            ijk=np.column_stack(np.unravel_index(np.flatnonzero(actuales),actuales.shape))
            centros=np.asarray(origen)+(ijk[:,::-1]+.5)*h
            mapa=crear_mapa(centros,actuales,h,esquema)
            indices=np.floor((centros-np.asarray(origen))/.4+1e-8).astype(int)[:,::-1]
            dentro=np.all((indices>=0)&(indices<np.array(ids.shape)),axis=1)
            asignacion=np.full(len(indices),-1,int)
            asignacion[dentro]=zona[tuple(indices[dentro].T)]
            mapa=(mapa[0],asignacion,mapa[2],dict(mapa[3],volumen_refrigerable_m3=float((asignacion>=0).sum()*h**3)))
            solver,_=base.construir_solver(mapa,centros)
        provenance=dict(prov,confirmacion=dict(variante=variante,lado_m=h,paso_max_s=dt,
            script_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
            volumen_voxel_m3=float((actuales>0).sum()*h**3),
            volumen_refrigerable_m3=solver.MAPA_CONTROL[3]['volumen_refrigerable_m3'],
            regla_zona='Pertenencia al voxel refrigerable de referencia 0.4m',
            capas_fisicas='Mismas 11 capas y tiempos IFC; subceldas comparten inicio de su capa'))
        for curva,clima in casos:
            ruta=salida/f'{variante}_{curva}_{clima}.json'
            if ruta.exists():
                d=base.viento.leer(ruta)
                if d['procedencia']!=provenance:raise ValueError('Cambió procedencia; conservar salidas y usar otra carpeta.')
                filas.append(d);continue
            f=next(x for x in fuentes if x['id']==curva)
            aire=climas[clima][1]
            inicio=perf_counter()
            def resolver(horas):
                return solver.simular(actuales,origen,h,programa,f['curva'],replace(env,dt_tope_s=dt),
                    aire[:horas+1],(0,0,2),h_aire_horario_W_m2K=series[clima]['h_W_m2K'][:horas+1])
            r336=resolver(336)
            horas=600;r=resolver(horas)
            while controles.alertas_cola(r,horas,prov['D_h'],168) and horas<672:
                horas+=72;r=resolver(horas)
            assert abs(r.balance_J['residuo'])<.01
            assert r.balance_J['enfriamiento_pico_W']<=15000.000001
            assert abs(sum(r.control_circuitos['energia_extraida_circuito_J'])+r.balance_J['enfriamiento'])<.1
            referencia=base.viento.leer(base.RAIZ/f'resultados/circuitos_histeresis/{curva}_{clima}.json')['corrida']
            metrica=controles.metricas(r,horas)
            d=dict(procedencia=provenance,variante=variante,curva=curva,clima=clima,
                base_336h=controles.metricas(r336,336),**metrica,
                cambio_Tmax_K=metrica['Tmax']['valor']-referencia['Tmax']['valor'],
                cambio_DeltaTmax_K=metrica['DeltaTmax']['valor']-referencia['DeltaTmax']['valor'],
                pico_no_resuelto=controles.alertas_cola(r,horas,prov['D_h'],168),
                historia=r.historia,control=r.control_circuitos,segundos=perf_counter()-inicio)
            base.escribir(ruta,d);filas.append(d)
            print(variante,curva,clima,'Tmax',metrica['Tmax']['valor'],'Delta',metrica['DeltaTmax']['valor'],
                'cambio',d['cambio_DeltaTmax_K'],'alerta',d['pico_no_resuelto'],flush=True)
    resumen=[{k:v for k,v in f.items() if k not in ['historia','control']} for f in filas]
    base.escribir(salida/'resumen.json',dict(casos=resumen,
        alcance='Tres pares decisivos por variante; no matriz completa ni estimación de riesgo fino.'))


if __name__=='__main__':main()
