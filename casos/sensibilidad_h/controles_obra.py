"""Compara potencia y temperatura de colocación con h horario; solver solo bajo --ejecutar."""
import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace

import conductividad as comun
import viento

RAIZ, PLAN = comun.RAIZ, comun.PLAN
CASOS = {
    'potencia_15kw': dict(plan='unica', edad_inicio_h=6, tope_W=15000.),
    'colocacion_10c': dict(plan='unica', edad_inicio_h=6, temperatura_C=10.),
    'combinada_15kw_10c': dict(plan='unica', edad_inicio_h=6, tope_W=15000., temperatura_C=10.),
}


def resumir(salida, referencia, lado, paso):
    base=viento.leer(referencia)
    comun.validar_filas(base['corridas'])
    original={(f['curva'],f['clima']):f for f in base['corridas']}
    matrices=[('base',base)]
    for ruta in sorted(salida.glob(f'*/malla_{lado:g}_paso{paso}/*.json')):
        if ruta.stem not in CASOS:
            continue
        d=viento.leer(ruta)
        matrices.append((d['estudio_controles']['caso'],d))
    tabla, pares=[],[]
    for nombre,d in matrices:
        filas=d['corridas'];comun.validar_filas(filas)
        if {(f['curva'],f['clima']) for f in filas}!=set(original):
            raise ValueError('Catálogo distinto de la referencia.')
        pt=sum(f['peso'] for f in filas if f['Tmax']['valor']>70)
        pd=sum(f['peso'] for f in filas if f['DeltaTmax']['valor']>20)
        pf=sum(f['peso'] for f in filas if f['Tmax']['valor']>70 or f['DeltaTmax']['valor']>20)
        alertas=sum(f['pico_no_resuelto'] for f in filas)
        tabla.append(dict(caso=nombre,colocacion_C=d['plan'][0]['colocacion_C'],
            tope_kW=d['enfriamiento']['tope_W']/1000,U_W_m3K=d['enfriamiento']['U_W_m3K'],
            D_h=d['D_h'],lado_m=lado,paso_max_s=paso,Tmax_C=max(f['Tmax']['valor'] for f in filas),
            DeltaTmax_K=max(f['DeltaTmax']['valor'] for f in filas),P_T=pt,P_delta=pd,P_f=pf,
            alertas_cola=alertas,
            extraccion_max_MWh=max(-f['balance_J']['enfriamiento']/3.6e9 for f in filas),
            estado='indeterminado: cola pendiente' if alertas else ('cumple en esta resolución' if pf<=.05 else 'excede')))
        for f in filas:
            b=original[(f['curva'],f['clima'])]
            pares.append(dict(caso=nombre,curva=f['curva'],clima=f['clima'],
                Tmax_C=f['Tmax']['valor'],DeltaTmax_K=f['DeltaTmax']['valor'],
                cambio_Tmax_K=f['Tmax']['valor']-b['Tmax']['valor'],
                cambio_DeltaTmax_K=f['DeltaTmax']['valor']-b['DeltaTmax']['valor'],
                excede_70=f['Tmax']['valor']>70,excede_20=f['DeltaTmax']['valor']>20,
                hora_DeltaTmax=f['DeltaTmax']['tiempo_h'],horizonte_h=f['horizonte_h'],
                alerta_cola=f['pico_no_resuelto'],residuo_J=f['balance_J']['residuo']))
    viento.csv_guardar(salida/f'comparacion_malla_{lado:g}_paso{paso}.csv',tabla)
    viento.csv_guardar(salida/f'escenarios_malla_{lado:g}_paso{paso}.csv',pares)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ejecutar',action='store_true')
    p.add_argument('--comprobar-insumos',action='store_true')
    p.add_argument('--resumir',action='store_true')
    p.add_argument('--casos',nargs='+',choices=CASOS,default=list(CASOS))
    p.add_argument('--lado',type=float,choices=(.5,.25),default=.5)
    p.add_argument('--paso-max',type=int,choices=(900,450),default=900)
    p.add_argument('--salida',type=Path,default=RAIZ/'resultados/controles_obra')
    args=p.parse_args()
    referencia=comun.ruta_base(args.lado,args.paso_max)
    print('Única con h horario, suelo 15 °C/R0 y k hormigón=2. Mantas/retiros sin cambios.')
    print('Base: 12 kW / colocación 12,231833… °C; U=5, encendido 6 h y apagado 432 h.')
    for nombre in dict.fromkeys(args.casos):
        print(nombre,CASOS[nombre])
    print('Pares nuevos:',24*len(set(args.casos)))
    if not (args.ejecutar or args.comprobar_insumos or args.resumir):
        print('Sin simulaciones. Usar --comprobar-insumos o --ejecutar.')
        return
    if args.resumir:
        resumir(args.salida,referencia,args.lado,args.paso_max)
        return
    viento._preparacion.preparar()
    meta,series,_=viento.analizar(2.,.14)
    insumos,motor,solver,hashes=viento.cargar_motor({c:s['h_W_m2K'] for c,s in series.items()})
    base=comun.revisar_base(referencia,meta,hashes,args.lado,args.paso_max)
    frio=base['enfriamiento']
    if (frio['U_W_m3K'],frio['tope_W'],frio['referencia_C'],frio['comienzo_edad_h'],frio['apagado_h'])!=(5,12000,18,6,432):
        raise ValueError('Los controles de referencia cambiaron.')
    controles,*_=insumos.importar_solver('exportada')
    datos=insumos.leer(insumos.RAIZ/insumos.leer(insumos.CONFIG)['base'])
    entorno=datos['entorno']
    if (entorno['k_W_mK'],entorno['suelo_C'],entorno['k_suelo_W_mK'],entorno['profundidad_suelo_m'])!=(2,15,1.2,.5):
        raise ValueError('La referencia física cambió.')
    fuentes=controles.materiales(datos,insumos.HIDRATACION/'manifiesto.json')
    if not all(f['rho_kg_m3']==2476 and f['cp_J_kgK']==1023 for f in fuentes):
        raise ValueError('Las propiedades del hormigón cambiaron.')
    cfg=deepcopy(insumos.leer(insumos.CONFIGURACIONES))
    cfg['experimentos'].update(deepcopy(CASOS))
    if args.comprobar_insumos:
        ids,_=insumos.leer_malla(controles,datos,args.lado,'exportada')
        for nombre in args.casos:
            elegido=cfg['experimentos'][nombre]
            assert elegido['plan']=='unica' and elegido['edad_inicio_h']==6
            assert elegido.get('tope_W',12000) in (12000,15000)
            assert elegido.get('temperatura_C',base['plan'][0]['colocacion_C'])>0
        print('Referencias, propiedades, geometría y configuración comprobadas; máscara',ids.shape,'. Sin simulaciones.')
        return
    viento.verificar(solver)
    args.salida.mkdir(parents=True,exist_ok=True)
    for nombre in dict.fromkeys(args.casos):
        destino=args.salida/nombre/f'malla_{args.lado:g}_paso{args.paso_max}'
        destino.mkdir(parents=True,exist_ok=True)
        ruta=destino/f'{nombre}.json'
        procedencia=dict(caso=nombre,parametros=CASOS[nombre],modelo_viento=meta,**hashes,
            U_W_m3K=5,k_hormigon_W_mK=2,rho_kg_m3=2476,cp_J_kgK=1023,
            lado_m=args.lado,paso_max_s=args.paso_max,
            referencia_sha256=sha256(referencia.read_bytes()).hexdigest(),
            script_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
        if ruta.exists():
            if viento.leer(ruta).get('estudio_controles')!=procedencia:
                raise ValueError('Procedencia distinta; elegir otra salida.')
            print('Conservado:',ruta)
            continue
        piezas=[]
        for curva,clima in sorted((f['curva'],f['clima']) for f in base['corridas']):
            individual=destino/f'{nombre}_{curva}_{clima}.json'
            if not individual.exists():
                motor.ejecutar(SimpleNamespace(experimento=nombre,salida=destino,modo='completo',
                    escenario=[curva,clima],geometria='exportada',lado=args.lado,paso_max=args.paso_max,traza=False),cfg)
                d=viento.leer(individual);d['estudio_controles']=procedencia
                individual.write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
            d=viento.leer(individual)
            if d.get('estudio_controles')!=procedencia:
                raise ValueError('Procedencia inconsistente: '+str(individual))
            esperado_T=CASOS[nombre].get('temperatura_C',base['plan'][0]['colocacion_C'])
            assert d['plan'][0]['colocacion_C']==esperado_T
            assert d['enfriamiento']['tope_W']==CASOS[nombre].get('tope_W',12000)
            assert d['enfriamiento']['U_W_m3K']==5
            piezas.append(d)
        resultado=dict(piezas[0]);filas=[f for d in piezas for f in d['corridas']]
        comun.validar_filas(filas)
        resultado.update(corridas=filas,horizontes_h=sorted({f['horizonte_h'] for f in filas}),
            picos_no_resueltos=sum(f['pico_no_resuelto'] for f in filas),
            duracion_auditoria_s=sum(d['duracion_auditoria_s'] for d in piezas),riesgo=controles.riesgo(filas),
            riesgo_336=controles.riesgo([dict(f['base_336h'],peso=f['peso'],clima=f['clima']) for f in filas]),
            sensibilidades_pesos={c:controles.riesgo(filas,c) for c in series})
        with ruta.open('x',encoding='utf-8') as archivo:
            json.dump(resultado,archivo,ensure_ascii=False,indent=2,allow_nan=False)
        resumir(args.salida,referencia,args.lado,args.paso_max)
        print('Matriz completa guardada:',ruta)
    resumir(args.salida,referencia,args.lado,args.paso_max)


if __name__=='__main__':
    main()
