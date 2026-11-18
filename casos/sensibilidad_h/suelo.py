"""Sensibilidad de temperatura y resistencia de suelo por separado; sin solver por defecto."""
import argparse
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace

import conductividad as comun
import viento


RAIZ, PLAN = comun.RAIZ, comun.PLAN
# La longitud representa resistencia equivalente, no una cota geotécnica.
VARIANTES = {
    'base': dict(suelo_C=15., k_suelo_W_mK=1.2, profundidad_suelo_m=.5),
    'temperatura_12': dict(suelo_C=12., k_suelo_W_mK=1.2, profundidad_suelo_m=.5),
    'temperatura_18': dict(suelo_C=18., k_suelo_W_mK=1.2, profundidad_suelo_m=.5),
    'temperatura_22': dict(suelo_C=22., k_suelo_W_mK=1.2, profundidad_suelo_m=.5),
    'resistencia_mitad': dict(suelo_C=15., k_suelo_W_mK=1.2, profundidad_suelo_m=.25),
    'resistencia_doble': dict(suelo_C=15., k_suelo_W_mK=1.2, profundidad_suelo_m=1.),
}


def resumir(salida, referencia, lado, paso):
    original=viento.leer(referencia)
    comun.validar_filas(original['corridas'])
    base={(f['curva'],f['clima']):f for f in original['corridas']}
    matrices=[('base',original)]
    for ruta in sorted(salida.glob(f'*/malla_{lado:g}_paso{paso}/{PLAN}.json')):
        d=viento.leer(ruta)
        matrices.append((d['estudio_suelo']['variante'],d))
    tabla,pares=[],[]
    for nombre,d in matrices:
        filas=d['corridas'];comun.validar_filas(filas)
        if {(f['curva'],f['clima']) for f in filas}!=set(base):
            raise ValueError('Catálogo distinto de la referencia.')
        valores=VARIANTES[nombre]
        pt=sum(f['peso'] for f in filas if f['Tmax']['valor']>70)
        pd=sum(f['peso'] for f in filas if f['DeltaTmax']['valor']>20)
        pf=sum(f['peso'] for f in filas if f['Tmax']['valor']>70 or f['DeltaTmax']['valor']>20)
        alertas=sum(f['pico_no_resuelto'] for f in filas)
        tabla.append(dict(variante=nombre,**valores,
            R_suelo_m2K_W=valores['profundidad_suelo_m']/valores['k_suelo_W_mK'],
            lado_m=lado,paso_max_s=paso,Tmax_C=max(f['Tmax']['valor'] for f in filas),
            DeltaTmax_K=max(f['DeltaTmax']['valor'] for f in filas),
            P_T=pt,P_delta=pd,P_f=pf,alertas_cola=alertas,
            estado='indeterminado: cola pendiente' if alertas else ('cumple en esta resolución' if pf<=.05 else 'excede')))
        for f in filas:
            b=base[(f['curva'],f['clima'])]
            pares.append(dict(variante=nombre,curva=f['curva'],clima=f['clima'],
                Tmax_C=f['Tmax']['valor'],DeltaTmax_K=f['DeltaTmax']['valor'],
                cambio_Tmax_K=f['Tmax']['valor']-b['Tmax']['valor'],
                cambio_DeltaTmax_K=f['DeltaTmax']['valor']-b['DeltaTmax']['valor'],
                excede_70=f['Tmax']['valor']>70,excede_20=f['DeltaTmax']['valor']>20,
                hora_DeltaTmax=f['DeltaTmax']['tiempo_h'],horizonte_h=f['horizonte_h'],
                alerta_cola=f['pico_no_resuelto'],energia_suelo_J=f['balance_J']['suelo'],
                residuo_J=f['balance_J']['residuo']))
    viento.csv_guardar(salida/f'comparacion_malla_{lado:g}_paso{paso}.csv',tabla)
    viento.csv_guardar(salida/f'escenarios_malla_{lado:g}_paso{paso}.csv',pares)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ejecutar',action='store_true')
    p.add_argument('--comprobar-insumos',action='store_true')
    p.add_argument('--resumir',action='store_true')
    p.add_argument('--variantes',nargs='+',choices=VARIANTES,default=list(VARIANTES))
    p.add_argument('--lado',type=float,choices=(.5,.25),default=.5)
    p.add_argument('--paso-max',type=int,choices=(900,450),default=900)
    p.add_argument('--salida',type=Path,default=RAIZ/'resultados/sensibilidad_suelo')
    args=p.parse_args()
    referencia=comun.ruta_base(args.lado,args.paso_max)
    print('Única, h horario, k hormigón=2, rho=2476 y cp=1023. Protecciones y extracción sin cambios.')
    for nombre in dict.fromkeys(args.variantes):
        v=VARIANTES[nombre]
        print(nombre, 'T=',v['suelo_C'],'°C; R_suelo=',v['profundidad_suelo_m']/v['k_suelo_W_mK'],'m2 K/W')
    print('Pares nuevos:',24*len(set(args.variantes)-{'base'}),'(cada par evalúa varias ventanas).')
    if not (args.ejecutar or args.comprobar_insumos or args.resumir):
        print('Sin simulaciones. Añadir --comprobar-insumos o --ejecutar.')
        return
    if args.resumir:
        resumir(args.salida,referencia,args.lado,args.paso_max)
        return
    viento._preparacion.preparar()
    meta,series,_=viento.analizar(2.,.14)
    insumos,motor,solver,hashes=viento.cargar_motor({c:s['h_W_m2K'] for c,s in series.items()})
    base=comun.revisar_base(referencia,meta,hashes,args.lado,args.paso_max)
    original_importar=insumos.importar_solver
    estado={'variante':'base'}

    def importar(origen):
        partes=list(original_importar(origen));clase=partes[2]
        def entorno(*posicionales,**nombrados):
            return replace(clase(*posicionales,**nombrados),**VARIANTES[estado['variante']])
        partes[2]=entorno
        return tuple(partes)

    insumos.importar_solver=importar
    configuracion=insumos.leer(insumos.CONFIG)
    datos_base=insumos.leer(insumos.RAIZ/configuracion['base'])
    if datos_base['entorno']['k_W_mK']!=2 or any(datos_base['entorno'][k]!=v for k,v in VARIANTES['base'].items()):
        raise ValueError('La configuración base del suelo u hormigón cambió.')
    controles,*_=insumos.importar_solver('exportada')
    materiales=controles.materiales(datos_base,insumos.HIDRATACION/'manifiesto.json')
    if not all(f['rho_kg_m3']==2476 and f['cp_J_kgK']==1023 for f in materiales):
        raise ValueError('Las propiedades del hormigón cambiaron.')
    if args.comprobar_insumos:
        _,_,entorno,*_=insumos.importar_solver('exportada')
        datos=dict(datos_base['entorno'])
        datos['capas_laterales']=tuple(controles.Capa(**c) for c in datos['capas_laterales'])
        for nombre in args.variantes:
            estado['variante']=nombre
            e=entorno(**datos)
            assert all(getattr(e,k)==v for k,v in VARIANTES[nombre].items())
            assert e.k_W_mK==2
        ids,_=insumos.leer_malla(controles,datos_base,args.lado,'exportada')
        print('Lectura, catálogo, propiedades y sustitución del suelo correctas; máscara',ids.shape,'. Sin simulaciones.')
        return
    viento.verificar(solver)
    args.salida.mkdir(parents=True,exist_ok=True)
    cfg=insumos.leer(insumos.CONFIGURACIONES)
    for nombre in dict.fromkeys(args.variantes):
        if nombre=='base':
            print('Base: reutilizada sin recalcular.')
            continue
        estado['variante']=nombre
        destino=args.salida/nombre/f'malla_{args.lado:g}_paso{args.paso_max}'
        destino.mkdir(parents=True,exist_ok=True)
        ruta=destino/f'{PLAN}.json'
        procedencia=dict(variante=nombre,**VARIANTES[nombre],k_hormigon_W_mK=2,rho_kg_m3=2476,cp_J_kgK=1023,
            modelo_viento=meta,**hashes,lado_m=args.lado,paso_max_s=args.paso_max,
            referencia_sha256=sha256(referencia.read_bytes()).hexdigest(),
            script_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
        if ruta.exists():
            if viento.leer(ruta).get('estudio_suelo')!=procedencia:
                raise ValueError('Procedencia distinta; elegir otra salida.')
            print('Conservado:',ruta)
            continue
        piezas=[]
        for curva,clima in sorted((f['curva'],f['clima']) for f in base['corridas']):
            individual=destino/f'{PLAN}_{curva}_{clima}.json'
            if not individual.exists():
                motor.ejecutar(SimpleNamespace(experimento=PLAN,salida=destino,modo='completo',
                    escenario=[curva,clima],geometria='exportada',lado=args.lado,paso_max=args.paso_max,traza=False),cfg)
                d=viento.leer(individual);d['estudio_suelo']=procedencia
                individual.write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
            d=viento.leer(individual)
            if d.get('estudio_suelo')!=procedencia:
                raise ValueError('Procedencia inconsistente: '+str(individual))
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
