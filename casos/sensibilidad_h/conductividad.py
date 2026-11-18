"""Sensibilidad independiente a k con rho/cp fijos y viento horario; sin solver por defecto."""
import argparse
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace

import viento


RAIZ = viento.RAIZ
PLAN = "publicada_unica"
VALORES = (1.6, 2., 8/3.6, 2.4)


def etiqueta(k):
    return f"{k:.10g}"


def ruta_base(lado, paso):
    return RAIZ / f"resultados/sensibilidad_h/viento/horario/malla_{lado:g}_paso{paso}/{PLAN}.json"


def revisar_base(ruta, meta, hashes, lado, paso):
    d = viento.leer(ruta)
    origen = d["modelo_viento"]
    for clave in ("altura_representativa_m", "exponente_perfil", "clima_sha256"):
        if origen[clave] != meta[clave]:
            raise ValueError("La referencia k=2 usa otra exposición o clima.")
    for clave in hashes:
        if origen[clave] != hashes[clave]:
            raise ValueError("La referencia usa otra adaptación del solver/ejecutor.")
    if origen["modo"] != "horario" or d["experimento"] != PLAN or (d["lado_m"], d["paso_max_s"]) != (lado, paso):
        raise ValueError("Referencia distinta del estudio previsto.")
    validar_filas(d["corridas"])
    return d


def validar_filas(filas):
    if len(filas) != 24 or len({(f["curva"],f["clima"]) for f in filas}) != 24:
        raise ValueError("Se requieren 24 pares únicos.")
    if abs(sum(f["peso"] for f in filas) - 1) > 1e-10:
        raise ValueError("Los pesos no suman uno.")


def resumir(salida, referencia, lado, paso):
    original = viento.leer(referencia)
    validar_filas(original["corridas"])
    matrices = [(2.,original)]
    for ruta in sorted(salida.glob(f"k_*/malla_{lado:g}_paso{paso}/{PLAN}.json")):
        d=viento.leer(ruta)
        k=d["estudio_k"]["k_W_mK"]
        if k==2:
            continue
        matrices.append((k,d))
    tabla, comparacion = [], []
    base={(f['curva'],f['clima']):f for f in original['corridas']}
    for k,d in sorted(matrices):
        filas=d['corridas']
        validar_filas(filas)
        pt=sum(f['peso'] for f in filas if f['Tmax']['valor']>70)
        pd=sum(f['peso'] for f in filas if f['DeltaTmax']['valor']>20)
        pf=sum(f['peso'] for f in filas if f['Tmax']['valor']>70 or f['DeltaTmax']['valor']>20)
        tabla.append(dict(k_W_mK=k,rho_kg_m3=2476,cp_J_kgK=1023,lado_m=lado,paso_max_s=paso,
            Tmax_C=max(f['Tmax']['valor'] for f in filas),DeltaTmax_K=max(f['DeltaTmax']['valor'] for f in filas),
            P_T=pt,P_delta=pd,P_f=pf,alertas_cola=sum(f['pico_no_resuelto'] for f in filas),
            cumple_sin_alertas=pf<=.05 and not any(f['pico_no_resuelto'] for f in filas)))
        for f in filas:
            b=base[(f['curva'],f['clima'])]
            comparacion.append(dict(k_W_mK=k,curva=f['curva'],clima=f['clima'],
                Tmax_C=f['Tmax']['valor'],DeltaTmax_K=f['DeltaTmax']['valor'],
                cambio_Tmax_K=f['Tmax']['valor']-b['Tmax']['valor'],
                cambio_DeltaTmax_K=f['DeltaTmax']['valor']-b['DeltaTmax']['valor'],
                excede_70=f['Tmax']['valor']>70,excede_20=f['DeltaTmax']['valor']>20,
                hora_DeltaTmax=f['DeltaTmax']['tiempo_h'],horizonte_h=f['horizonte_h'],
                alerta_cola=f['pico_no_resuelto'],residuo_J=f['balance_J']['residuo']))
    viento.csv_guardar(salida / f'comparacion_malla_{lado:g}_paso{paso}.csv',tabla)
    viento.csv_guardar(salida / f'escenarios_malla_{lado:g}_paso{paso}.csv',comparacion)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ejecutar',action='store_true')
    p.add_argument('--comprobar-insumos',action='store_true')
    p.add_argument('--resumir',action='store_true')
    p.add_argument('--k',nargs='+',type=float,default=list(VALORES))
    p.add_argument('--lado',type=float,choices=(.5,.25),default=.5)
    p.add_argument('--paso-max',type=int,choices=(900,450),default=900)
    p.add_argument('--salida',type=Path,default=RAIZ / 'resultados/sensibilidad_k')
    args=p.parse_args()
    if not all(0<k<10 for k in args.k) or len({etiqueta(k) for k in args.k})!=len(args.k):
        p.error('Indicar k positivos <10, sin duplicados.')
    referencia=ruta_base(args.lado,args.paso_max)
    print('Plan: única, h horario. rho=2476 kg/m3, cp=1023 J/(kg K).')
    print('k [W/(m K)]:',args.k,'malla:',args.lado,'paso máximo:',args.paso_max)
    print('Se reutiliza k=2 de',referencia)
    if not (args.ejecutar or args.comprobar_insumos or args.resumir):
        print('Sin simulaciones. Usar --comprobar-insumos o --ejecutar.')
        return
    if args.resumir:
        resumir(args.salida,referencia,args.lado,args.paso_max)
        return
    viento._preparacion.preparar()
    meta,series,_=viento.analizar(2.,.14)
    insumos,motor,solver,hashes=viento.cargar_motor({c:s['h_W_m2K'] for c,s in series.items()})
    base=revisar_base(referencia,meta,hashes,args.lado,args.paso_max)
    original_importar=insumos.importar_solver
    estado={'k':2.}

    def importar(origen):
        elementos=list(original_importar(origen))
        clase=elementos[2]
        def entorno(*posicionales,**nombrados):
            return replace(clase(*posicionales,**nombrados),k_W_mK=estado['k'])
        elementos[2]=entorno
        return tuple(elementos)

    insumos.importar_solver=importar
    configuracion=insumos.leer(insumos.CONFIG)
    parametros_base=insumos.leer(insumos.RAIZ / configuracion['base'])
    controles,*_=insumos.importar_solver('exportada')
    materiales=controles.materiales(parametros_base,insumos.HIDRATACION / 'manifiesto.json')
    if not all(f['rho_kg_m3']==2476 and f['cp_J_kgK']==1023 for f in materiales):
        raise ValueError('Las propiedades del manifiesto no coinciden con las fijadas.')
    if args.comprobar_insumos:
        controles,_,entorno,*_=insumos.importar_solver('exportada')
        datos=dict(parametros_base['entorno'])
        datos['capas_laterales']=tuple(controles.Capa(**c) for c in datos['capas_laterales'])
        for k in args.k:
            estado['k']=k
            assert entorno(**datos).k_W_mK==k
        ids,_=insumos.leer_malla(controles,parametros_base,args.lado,'exportada')
        print('Lectura, propiedades y sustitución de k correctas. Máscara:',ids.shape,'. Sin simulaciones.')
        return
    viento.verificar(solver)
    args.salida.mkdir(parents=True,exist_ok=True)
    cfg=insumos.leer(insumos.CONFIGURACIONES)
    origenes={(f['curva'],f['clima']):f for f in base['corridas']}
    for k in args.k:
        if k==2.:
            print('k=2: se conserva la matriz existente, sin repetirla.')
            continue
        estado['k']=k
        destino=args.salida / f'k_{etiqueta(k)}' / f'malla_{args.lado:g}_paso{args.paso_max}'
        destino.mkdir(parents=True,exist_ok=True)
        ruta=destino / f'{PLAN}.json'
        procedencia=dict(k_W_mK=k,rho_kg_m3=2476,cp_J_kgK=1023,modelo_viento=meta,
            **hashes,lado_m=args.lado,paso_max_s=args.paso_max,
            referencia_sha256=sha256(referencia.read_bytes()).hexdigest(),
            script_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
        if ruta.exists():
            if viento.leer(ruta).get('estudio_k')!=procedencia:
                raise ValueError('Cambió la procedencia; usar otra salida.')
            print('Conservado:',ruta)
            continue
        piezas=[]
        for curva,clima in sorted(origenes):
            individual=destino / f'{PLAN}_{curva}_{clima}.json'
            if not individual.exists():
                motor.ejecutar(SimpleNamespace(experimento=PLAN,salida=destino,modo='completo',
                    escenario=[curva,clima],geometria='exportada',lado=args.lado,paso_max=args.paso_max,traza=False),cfg)
                d=viento.leer(individual);d['estudio_k']=procedencia
                individual.write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
            d=viento.leer(individual)
            if d.get('estudio_k')!=procedencia:
                raise ValueError('Procedencia inconsistente: '+str(individual))
            piezas.append(d)
        resultado=dict(piezas[0])
        filas=[f for d in piezas for f in d['corridas']]
        validar_filas(filas)
        resultado.update(corridas=filas,horizontes_h=sorted({f['horizonte_h'] for f in filas}),
            picos_no_resueltos=sum(f['pico_no_resuelto'] for f in filas),
            duracion_auditoria_s=sum(d['duracion_auditoria_s'] for d in piezas),
            riesgo=controles.riesgo(filas),
            riesgo_336=controles.riesgo([dict(f['base_336h'],peso=f['peso'],clima=f['clima']) for f in filas]),
            sensibilidades_pesos={c:controles.riesgo(filas,c) for c in series})
        with ruta.open('x',encoding='utf-8') as archivo:
            json.dump(resultado,archivo,ensure_ascii=False,indent=2,allow_nan=False)
        resumir(args.salida,referencia,args.lado,args.paso_max)
        print('Matriz completa guardada:',ruta)
    resumir(args.salida,referencia,args.lado,args.paso_max)


if __name__=='__main__':
    main()
