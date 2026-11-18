"""Familia homogénea de nueve circuitos; enumeración base y confirmación fina.

Sin --ejecutar solo describe. Usa procesos independientes sin modificar
solvers o resultados históricos. Cada par guarda métricas336h y extendidas.
"""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
os.environ['MKL_NUM_THREADS']='1'
import argparse
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from time import perf_counter
import numpy as np
import simular_circuitos as base
from control_circuitos import crear_mapa

RAIZ=base.RAIZ
SALIDA=RAIZ/'resultados/comparacion_circuitos'
ESTADO=None
GEOMETRIAS={}


def iniciar():
    global ESTADO
    ESTADO=base.preparar()


def geometria(h):
    if h in GEOMETRIAS:return GEOMETRIAS[h]
    controles,sol,ids,origen,*_=ESTADO
    if h==.4:
        resultado=(ids,origen,sol.MAPA_CONTROL,sol.CENTROS_CONTROL)
    else:
        insumos=base.viento._preparacion.cargar()[0]
        config=insumos.leer(insumos.RAIZ/insumos.leer(insumos.CONFIG)['base'])
        modelo=controles.extraer_fundacion_ifc(RAIZ/config['archivo_ifc'])
        vox=controles.voxelizar_fundacion(modelo,pasos_m=(h,)*3)
        ocupada=controles.asignar_vertidas(modelo,vox).vertida_id>0
        nuevos=np.zeros_like(ocupada,dtype=int)
        assert np.allclose(vox.grilla.origen_m,origen)
        for z,plano in enumerate(ocupada):
            capa=min(int(((origen[2]+(z+.5)*h)+1e-8)/.4),10)
            nuevos[z][plano]=capa+1
        ijk=np.column_stack(np.unravel_index(np.flatnonzero(nuevos),nuevos.shape))
        centros=np.asarray(origen)+(ijk[:,::-1]+.5)*h
        esquema=base.viento.leer(RAIZ/'resultados/diseno_circuitos_colocacion/esquema.json')
        mapa=crear_mapa(centros,nuevos,h,esquema)
        zona=np.full(ids.shape,-1,int)
        zona.ravel()[np.flatnonzero(ids)]=sol.MAPA_CONTROL[1]
        indices=np.floor((centros-np.asarray(origen))/.4+1e-8).astype(int)[:,::-1]
        dentro=np.all((indices>=0)&(indices<np.array(ids.shape)),axis=1)
        asignacion=np.full(len(indices),-1,int)
        asignacion[dentro]=zona[tuple(indices[dentro].T)]
        mapa=(mapa[0],asignacion,mapa[2],dict(mapa[3],volumen_refrigerable_m3=float((asignacion>=0).sum()*h**3)))
        resultado=(nuevos,origen,mapa,centros)
    assert abs(resultado[2][3]['volumen_refrigerable_m3']-414.016)<1e-6
    GEOMETRIAS[h]=resultado
    return resultado


def campos_guardar(ruta,r,ids,origen,h,comun):
    contenido=dict(ids=ids,origen_m=np.array(origen),lado_m=np.array(h))
    for nombre,campo in r.campos.items():
        contenido[f'{nombre}_T_C']=campo.temperatura_C
        contenido[f'{nombre}_S25_C']=campo.s25_min_C
        contenido[f'{nombre}_tiempo_h']=np.array(campo.tiempo_s/3600)
        contenido[f'{nombre}_fase']=np.array(campo.fase)
    contenido.update(comun)
    np.savez_compressed(ruta,**contenido)


def resolver_tarea(tarea):
    q,h,curva,clima,exportar=tarea
    controles,_,_,_,programa,env,fuentes,climas,series,_,prov=ESTADO
    ids,origen,mapa,centros=geometria(h)
    factor=60/q
    programa={k:(t*factor,T) for k,(t,T) in programa.items()}
    mapa=(mapa[0],mapa[1],[t*factor for t in mapa[2]],dict(mapa[3],cubierto_desde_h=[t*factor for t in mapa[2]]))
    sol,hash_solver=base.construir_solver(mapa,centros)
    procedencia=dict(prov,lado_m=h,paso_max_s=300,capacidad_m3_h=q,D_h=prov['D_h']*factor,
        volumen_voxel_m3=float((ids>0).sum()*h**3),**mapa[3])
    procedencia['familia']=dict(script_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        config_sha256=sha256(Path(__file__).with_name('familia_circuitos.json').read_bytes()).hexdigest(),
        solver_adaptado_sha256=hash_solver,zona='Pertenencia a voxeles refrigerables0.40m',
        capas='Mismas11capas físicas; cronograma escalado por60/q',
        cpus='Un hilo BLAS/OMP por proceso; no altera ecuaciones')
    carpeta=SALIDA/f'q{q}/malla_{h:g}'
    carpeta.mkdir(parents=True,exist_ok=True)
    ruta=carpeta/f'{curva}_{clima}.json'
    if ruta.exists():
        d=base.viento.leer(ruta)
        if d['procedencia']!=procedencia:raise ValueError(f'Procedencia distinta:{ruta}')
        if exportar and not ruta.with_suffix('.npz').exists():raise ValueError('Faltan campos; no sustituir resultado.')
        return str(ruta.relative_to(RAIZ))
    aire=climas[clima][1]
    f=next(x for x in fuentes if x['id']==curva)
    inicio=perf_counter();comun={}
    def guardar(t,T):
        if abs(t/3600-428)<1e-7:
            campo=np.full(ids.size,np.nan)
            campo[np.flatnonzero(ids)]=T
            comun['comun_428h_T_C']=campo.reshape(ids.shape)
    def simular(horas):
        return sol.simular(ids,origen,h,programa,f['curva'],replace(env,dt_tope_s=300),
            aire[:horas+1],(0,0,2),h_aire_horario_W_m2K=series[clima]['h_W_m2K'][:horas+1],
            al_guardar=guardar if exportar else None)
    r336=simular(336)
    horas=600;r=simular(horas)
    while controles.alertas_cola(r,horas,procedencia['D_h'],168) and horas<672:
        horas+=72;r=simular(horas)
    assert abs(r.balance_J['residuo'])<.01
    assert r.balance_J['enfriamiento_pico_W']<=15000.000001
    assert abs(sum(r.control_circuitos['energia_extraida_circuito_J'])+r.balance_J['enfriamiento'])<.1
    fila=dict(curva=curva,clima=clima,peso=f['peso']*climas[clima][0]['peso'],
        base_336h=controles.metricas(r336,336),**controles.metricas(r,horas),
        pico_no_resuelto=controles.alertas_cola(r,horas,procedencia['D_h'],168))
    if q==60 and h==.4:
        referencia=base.viento.leer(RAIZ/f'resultados/circuitos_histeresis/{curva}_{clima}.json')['corrida']
        for horizonte in [None,'base_336h']:
            a,b=(fila,referencia) if horizonte is None else (fila[horizonte],referencia[horizonte])
            for k in ['Tmax','DeltaTmax']:
                np.testing.assert_allclose(a[k]['valor'],b[k]['valor'],atol=1e-10,rtol=0)
    if exportar:
        assert 'comun_428h_T_C' in comun
        campos_guardar(ruta.with_suffix('.npz'),r,ids,origen,h,comun)
    base.escribir(ruta,dict(procedencia=procedencia,corrida=fila,historia=r.historia,control=r.control_circuitos,
        control_336=r336.control_circuitos,segundos=perf_counter()-inicio,
        campos_npz=str(ruta.with_suffix('.npz').relative_to(RAIZ)) if exportar else None))
    print(f'q{q} h{h} {curva} {clima}: Tmax={fila["Tmax"]["valor"]:.4f} Delta={fila["DeltaTmax"]["valor"]:.4f} alertas={fila["pico_no_resuelto"]}',flush=True)
    return str(ruta.relative_to(RAIZ))


def leer_resultado(ruta):
    d=base.viento.leer(RAIZ/ruta)
    if 'corrida' in d:return d['corrida']
    claves=['horizonte_h','Tmax','DeltaTmax','excede_70','excede_20','pasos','balance_J','picos_vertidas','pico_no_resuelto','base_336h','curva','clima']
    return dict({k:d[k] for k in claves},peso=1/24)


def rutas_plan(q,h):
    matriz=base.viento.leer(RAIZ/'resultados/circuitos_histeresis/matriz.json')
    rutas=[]
    for f in matriz['corridas']:
        nombre=f'{f["curva"]}_{f["clima"]}.json'
        nueva=SALIDA/f'q{q}/malla_{h:g}'/nombre
        if nueva.exists():rutas.append(str(nueva.relative_to(RAIZ)));continue
        if q==60 and h==.4:rutas.append(f'resultados/circuitos_histeresis/{nombre}');continue
        confirm=RAIZ/'resultados/circuitos_confirmacion'/f'espacial_{nombre}'
        if q==60 and h==.2 and confirm.exists():rutas.append(str(confirm.relative_to(RAIZ)));continue
        return None
    return rutas


def agregar():
    controles=ESTADO[0]
    cfg=base.viento.leer(Path(__file__).with_name('familia_circuitos.json'))
    for q in cfg['planes_m3_h']:
        for h in [.4,.2]:
            rutas=rutas_plan(q,h)
            if rutas is None:continue
            filas=[leer_resultado(r) for r in rutas]
            base.comun.validar_filas(filas)
            indice=[dict(ruta=r,sha256=sha256((RAIZ/r).read_bytes()).hexdigest()) for r in rutas]
            d=dict(plan=f'q{q}',capacidad_m3_h=q,lado_m=h,paso_max_s=300,
                D_h=ESTADO[-1]['D_h']*60/q,corridas=filas,archivos=indice,
                riesgo=controles.riesgo(filas),
                riesgo_336=controles.riesgo([dict(f['base_336h'],peso=f['peso'],clima=f['clima']) for f in filas]),
                sensibilidades_pesos={c:controles.riesgo(filas,c) for c in ESTADO[7]},
                picos_no_resueltos=sum(f['pico_no_resuelto'] for f in filas),
                config_sha256=sha256(Path(__file__).with_name('familia_circuitos.json').read_bytes()).hexdigest())
            carpeta=SALIDA/f'q{q}/malla_{h:g}';carpeta.mkdir(parents=True,exist_ok=True)
            base.escribir(carpeta/'matriz.json',d)
            print('MATRIZ',q,h,d['riesgo'],'alertas',d['picos_no_resueltos'],flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ejecutar',action='store_true')
    p.add_argument('--fase',choices=['base','fina','marginales','agregar'],default='base')
    p.add_argument('--lote',type=int,choices=[0,1,2],help='Tercio de tareas, para tres procesos independientes sin IPC')
    args=p.parse_args()
    if not args.ejecutar:print(__doc__);return
    iniciar();base.verificar(ESTADO[1])
    cfg=base.viento.leer(Path(__file__).with_name('familia_circuitos.json'))
    esquema=base.viento.leer(RAIZ/'resultados/diseno_circuitos_colocacion/esquema.json')
    Vmax=max(c['volumen_m3'] for c in esquema['capas'])
    assert all(Vmax/q*60<=cfg['ventana_union_condicion_min'] for q in cfg['planes_m3_h'])
    tareas=[]
    for q in cfg['planes_m3_h']:
        for f in base.viento.leer(RAIZ/'resultados/circuitos_histeresis/matriz.json')['corridas']:
            c,a=f['curva'],f['clima']
            exportar=(c,a)==('M4_SS','ERA5-2024')
            if args.fase=='base' and (q!=60 or exportar):tareas.append((q,.4,c,a,exportar))
            if args.fase=='fina' and q==60:
                anterior=RAIZ/f'resultados/circuitos_confirmacion/espacial_{c}_{a}.json'
                if not anterior.exists():tareas.append((q,.2,c,a,False))
            if args.fase=='marginales' and q!=60:
                r=SALIDA/f'q{q}/malla_0.4/{c}_{a}.json'
                if r.exists() and base.viento.leer(r)['corrida']['DeltaTmax']['valor']>=19:
                    tareas.append((q,.2,c,a,False))
    if args.lote is not None:tareas=tareas[args.lote::3]
    print('Tareas',len(tareas),'fase',args.fase,'lote',args.lote,flush=True)
    for i,tarea in enumerate(tareas,1):
        resolver_tarea(tarea);print('Completadas',i,'/',len(tareas),flush=True)
    if args.lote is None:agregar()


if __name__=='__main__':main()
