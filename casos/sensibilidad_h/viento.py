"""Analiza viento congelado y prepara h; el solver requiere --ejecutar o --verificar."""
import argparse
import csv
from datetime import datetime
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace

import numpy as np

_spec = importlib.util.spec_from_file_location("preparacion_h_viento", Path(__file__).with_name("ejecutar.py"))
_preparacion = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_preparacion)
RAIZ, COPIA, SHA = _preparacion.RAIZ, _preparacion.COPIA, _preparacion.SHA
PLANES = _preparacion.PLANES
FUENTE = "https://energyplus.readthedocs.io/en/stable/guides/engineering-reference/3.5-outside-surface-heat-balance.html"


def leer(ruta):
    return json.loads(ruta.read_text(encoding="utf-8"))


def convertir(v10, altura=2., exponente=.14):
    """Mismo terreno en ambas alturas: cociente del perfil de potencia."""
    v10 = np.asarray(v10, dtype=float)
    if not (0 < altura <= 10 and 0 <= exponente <= 1):
        raise ValueError("Altura entre 0 y 10 m y exponente entre 0 y 1.")
    if not np.isfinite(v10).all() or (v10 < 0).any():
        raise ValueError("Viento faltante, no finito o negativo.")
    local = v10 * (altura / 10.) ** exponente
    return local, 5.7 + 3.8 * local


def estadisticas(valores):
    return dict(minimo=float(np.min(valores)), media=float(np.mean(valores)),
                mediana=float(np.median(valores)), p95=float(np.quantile(valores,.95)),
                maximo=float(np.max(valores)))


def analizar(altura, exponente):
    cfg = leer(COPIA / "casos/incertidumbre/parametros.json")
    series, estad, hashes = {}, [], {}
    for clima in cfg["historias"]:
        ruta = COPIA / clima["snapshot"]
        d = leer(ruta)
        if d["respuesta"]["hourly_units"]["wind_speed_10m"] != "m/s":
            raise ValueError("El viento debe estar en m/s.")
        inicio = int(datetime.fromisoformat(clima["inicio"]).timestamp())
        datos = d["respuesta"]["hourly"]
        marcas = datos["time"]
        i = marcas.index(inicio)
        if marcas[i:i+673] != [inicio + j*3600 for j in range(673)]:
            raise ValueError("Faltan marcas horarias hasta 672 h.")
        v10 = np.array([np.nan if v is None else v for v in datos["wind_speed_10m"][i:i+673]],dtype=float)
        local, h = convertir(v10, altura, exponente)
        series[clima["id"]] = dict(v10_m_s=v10.tolist(), v_local_m_s=local.tolist(), h_W_m2K=h.tolist())
        hashes[clima["id"]] = sha256(ruta.read_bytes()).hexdigest()
        for ventana in (336,600,672):
            fila = dict(clima=clima["id"], ventana_h=ventana)
            for nombre, arr in (("v10",v10),("v_local",local),("h",h)):
                fila.update({nombre+"_"+k:v for k,v in estadisticas(arr[:ventana]).items()})
            estad.append(fila)
    # Ventana común fijada antes de evaluar planes. 600 muestras para [0,600 h).
    media = sum(c["peso"] * np.mean(series[c["id"]]["h_W_m2K"][:600]) for c in cfg["historias"])
    meta = dict(commit_fuentes=SHA, fuente_correlacion=FUENTE, correlacion="h=5.7+3.8*v_local (SI)",
        altura_referencia_viento_m=10, altura_representativa_m=altura, exponente_perfil=exponente,
        terreno="campo abierto supuesto; mismo perfil en ambas alturas",
        h_constante_media_600h_W_m2K=float(media), clima_sha256=hashes,
        discretizacion_h="constante por intervalo horario, valor de su marca inicial",
        hipotesis="Mismo h en caras expuestas; sin apantallamiento, dirección ni rugosidad de superficie.",
        radiacion="No incorporada; h representa convección, con componente natural de la correlación.")
    return meta, series, estad


def csv_guardar(ruta, filas):
    if filas:
        with ruta.open("w",encoding="utf-8",newline="") as archivo:
            escritor=csv.DictWriter(archivo,fieldnames=list(filas[0]))
            escritor.writeheader()
            escritor.writerows(filas)


def graficar(salida, series, media):
    os.environ.setdefault("MPLCONFIGDIR",str(RAIZ / ".venv/cache/matplotlib"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(3,1,figsize=(11,8),sharex=True,layout="constrained")
    for ax,(clima,s) in zip(axes,series.items()):
        ax.plot(np.arange(601)/24,s["h_W_m2K"][:601],lw=1,color="#237b83",label="h horario derivado del viento")
        ax.axhline(media,color="#c57929",ls="--",label=f"Media común 600 h: {media:.2f}")
        ax.axhline(5,color="#777",ls=":",label="Referencia anterior: 5")
        ax.set(title=clima,ylabel="h [W/(m²·K)]",ylim=(0,40))
        ax.grid(alpha=.18)
    axes[0].legend(loc="upper left",fontsize=8,ncol=3)
    axes[-1].set_xlabel("Días desde el inicio de construcción")
    fig.suptitle("Coeficiente convectivo derivado del viento histórico\nAltura y terreno son hipótesis de exposición; no una calibración de la fundación",fontsize=13)
    fig.savefig(salida / "h_derivado_del_viento.png",dpi=160)
    plt.close(fig)


def cambiar(fuente, antes, despues):
    if fuente.count(antes) != 1:
        raise ValueError("Cambió el código congelado; revisar adaptación: " + antes[:50])
    return fuente.replace(antes,despues)


def cargar_motor(series_h):
    # Importa dependencias congeladas. Los archivos originales no se editan.
    insumos, _, _ = _preparacion.cargar()
    original_importar = insumos.importar_solver
    original_importar("exportada")
    ruta_solver = COPIA / "desarrollo/mcplan/termica_fundacion.py"
    codigo = ruta_solver.read_text(encoding="utf-8")
    codigo = cambiar(codigo,"intervalo_salida_s=3600., enfriamiento=None):",
        "intervalo_salida_s=3600., enfriamiento=None, h_aire_horario_W_m2K=None):")
    codigo = cambiar(codigo,"    def preparar(t):", '''    if h_aire_horario_W_m2K is None:
        serie_h = np.full(len(aire), entorno.h_aire_W_m2K)
    else:
        serie_h = np.asarray(h_aire_horario_W_m2K, dtype=float)
    if serie_h.shape != aire.shape or not np.isfinite(serie_h).all() or (serie_h < 0).any():
        raise ValueError("Se requiere h horario finito y no negativo, con una marca por temperatura de aire.")

    def h_en(t):
        return float(serie_h[min(int(t//3600), len(serie_h)-1)])

    def preparar(t):''')
    if codigo.count("h_W_m2K=entorno.h_aire_W_m2K") != 2:
        raise ValueError("No se identificaron ambos bordes de aire.")
    codigo = codigo.replace("h_W_m2K=entorno.h_aire_W_m2K","h_W_m2K=h_en(t)")
    nombre="mcplan.termica_fundacion_viento"
    modulo=ModuleType(nombre)
    modulo.__file__=str(ruta_solver)
    modulo.__package__="mcplan"
    sys.modules[nombre]=modulo
    exec(compile(codigo,str(ruta_solver),"exec"),modulo.__dict__)

    def importar(origen):
        elementos=list(original_importar(origen))
        elementos[3]=modulo.simular
        return tuple(elementos)
    insumos.importar_solver=importar
    ruta= COPIA / "casos/f02_verificaciones/ejecutar.py"
    fuente=ruta.read_text(encoding="utf-8")
    fuente=cambiar(fuente,'air[:hours+1], base["nucleo_xyz_m"], enfriamiento=cooling)',
        'air[:hours+1], base["nucleo_xyz_m"], enfriamiento=cooling, h_aire_horario_W_m2K=SERIES_H[weather["id"]][:hours+1])')
    fuente=cambiar(fuente,"        final = solve(horizon)",'''        final = solve(horizon)
        while (controls.alertas_cola(final, horizon, duration, cfg['inicio_tardio_edad_min_h'])
               and horizon < cfg['extension_max_h']):
            horizon = min(horizon + 72, cfg['extension_max_h'])
            final = solve(horizon)''')
    motor=ModuleType("f02_viento")
    motor.__file__=str(ruta)
    motor.SERIES_H=series_h
    exec(compile(fuente,str(ruta),"exec"),motor.__dict__)
    return insumos,motor,modulo,dict(solver_adaptado_sha256=sha256(codigo.encode()).hexdigest(),
                                   ejecutor_adaptado_sha256=sha256(fuente.encode()).hexdigest())


def verificar(solver):
    from mcplan.termica_fundacion import simular, EntornoFundacion
    from mcplan.hidratacion import CurvaAdiabatica
    entorno=EntornoFundacion(2,5,15,.5,1.2,(),-10,900)
    curva=CurvaAdiabatica(0,3600,2400,900)
    args=(np.ones((1,1,1),dtype=int),(0,0,0),1,{1:(0,20)},curva,entorno,[10,10,10],(.5,.5,.5))
    base=simular(*args)
    constante=solver.simular(*args,h_aire_horario_W_m2K=[5,5,5])
    assert base.pico==constante.pico and base.diferencial==constante.diferencial
    assert base.balance_J==constante.balance_J
    np.testing.assert_array_equal(base.campos['final'].temperatura_C,constante.campos['final'].temperatura_C)
    variable=solver.simular(*args,h_aire_horario_W_m2K=[5,20,20])
    temperatura=20.
    for h in (5,20):
        H=1/(.5/2+1/h)
        for _ in range(4):
            temperatura += 900*6*H*(10-temperatura)/(2400*900)
    np.testing.assert_allclose(variable.campos['final'].temperatura_C,temperatura,atol=1e-12,rtol=0)
    assert abs(variable.balance_J['residuo']) < 1e-6
    print("Verificaciones sintéticas aprobadas: h constante idéntico al solver congelado y cambio horario con balance independiente.")


def resumir(salida):
    tabla=[]
    for ruta in sorted(salida.glob("*/malla_*/*.json")):
        if ruta.stem not in PLANES+("publicada_tras_colocacion",):
            continue
        d=leer(ruta)
        if "corridas" not in d:
            continue
        filas=d["corridas"]
        if len(filas)!=24 or len({(f['curva'],f['clima']) for f in filas})!=24:
            raise ValueError("Matriz incompleta: "+str(ruta))
        pf=sum(f['peso'] for f in filas if f['Tmax']['valor']>70 or f['DeltaTmax']['valor']>20)
        tabla.append(dict(modelo=d['modelo_viento']['modo'],plan=d['experimento'],lado_m=d['lado_m'],
            paso_max_s=d['paso_max_s'],D_h=d['D_h'],Tmax_C=max(f['Tmax']['valor'] for f in filas),
            DeltaTmax_K=max(f['DeltaTmax']['valor'] for f in filas),
            P_T=sum(f['peso'] for f in filas if f['Tmax']['valor']>70),
            P_delta=sum(f['peso'] for f in filas if f['DeltaTmax']['valor']>20),P_f=pf,
            alertas_cola=sum(f['pico_no_resuelto'] for f in filas),
            cumple_sin_alertas=pf<=.05 and not any(f['pico_no_resuelto'] for f in filas)))
    csv_guardar(salida / "comparacion.csv",tabla)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ejecutar",action="store_true")
    p.add_argument("--verificar",action="store_true",help="Ejecuta solo dos comprobaciones sintéticas del adaptador.")
    p.add_argument("--comprobar-insumos",action="store_true")
    p.add_argument("--resumir",action="store_true")
    p.add_argument("--altura",type=float,default=2.)
    p.add_argument("--exponente",type=float,default=.14)
    p.add_argument("--modo",nargs="+",choices=("horario","constante_media"),default=["horario","constante_media"])
    p.add_argument("--planes",nargs="+",choices=PLANES+("publicada_tras_colocacion",),default=list(PLANES))
    p.add_argument("--lado",type=float,choices=(.5,.25),default=.5)
    p.add_argument("--paso-max",type=int,choices=(900,450),default=900)
    p.add_argument("--salida",type=Path,default=RAIZ / "resultados/sensibilidad_h/viento")
    args=p.parse_args()
    if args.resumir:
        resumir(args.salida)
        return
    _preparacion.preparar()
    meta,series,estad=analizar(args.altura,args.exponente)
    print('h constante común derivado de 600 h:',meta['h_constante_media_600h_W_m2K'])
    for f in estad:
        if f['ventana_h']==600:
            print(f['clima'],'v10 media:',f['v10_media'],'h media:',f['h_media'],'h rango:',f['h_minimo'],f['h_maximo'])
    if args.verificar or args.comprobar_insumos:
        insumos,motor,solver,_=cargar_motor({k:s['h_W_m2K'] for k,s in series.items()})
        if args.verificar:
            verificar(solver)
        else:
            controles,*_=insumos.importar_solver('exportada')
            cfg=insumos.leer(insumos.CONFIG)
            ids,_=insumos.leer_malla(controles,insumos.leer(insumos.RAIZ / cfg['base']),args.lado,'exportada')
            assert len(series)==3 and all(len(s['h_W_m2K'])==673 for s in series.values())
            print('Importación y lectura correctas; máscara',ids.shape,'. Sin simulaciones.')
        return
    args.salida.mkdir(parents=True,exist_ok=True)
    ruta_meta=args.salida / 'modelo_viento.json'
    if ruta_meta.exists() and leer(ruta_meta)!=meta:
        raise ValueError('Cambió la configuración del viento; elegir otra --salida.')
    ruta_meta.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (args.salida / 'series_h.json').write_text(json.dumps(series,indent=2)+'\n',encoding='utf-8')
    csv_guardar(args.salida / 'estadisticas_viento_h.csv',estad)
    graficar(args.salida,series,meta['h_constante_media_600h_W_m2K'])
    if not args.ejecutar:
        print('Se prepararon estadísticas y gráfico. No se ejecutaron simulaciones.')
        return
    # Un módulo por proceso: las series se sustituyen entre modos, sin redefinir importadores.
    insumos,motor,solver,hashes=cargar_motor({k:s['h_W_m2K'] for k,s in series.items()})
    verificar(solver)
    cfg=insumos.leer(insumos.CONFIGURACIONES)
    for modo in dict.fromkeys(args.modo):
        motor.SERIES_H={k:(s['h_W_m2K'] if modo=='horario' else [meta['h_constante_media_600h_W_m2K']]*673)
                        for k,s in series.items()}
        destino=args.salida / modo / f'malla_{args.lado:g}_paso{args.paso_max}'
        destino.mkdir(parents=True,exist_ok=True)
        procedencia=dict(**meta,**hashes,modo=modo,lado_m=args.lado,paso_max_s=args.paso_max,
                         script_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
        for plan in dict.fromkeys(args.planes):
            ruta=destino / f'{plan}.json'
            if ruta.exists():
                if leer(ruta).get('modelo_viento')!=procedencia:
                    raise ValueError('Cambió la procedencia; usar otra salida.')
                print('Conservado:',ruta)
                continue
            # El motor exige un par explícito si se cambia malla o paso. Ejecutar
            # sus 24 pares por separado y agregar sin renormalizar los pesos.
            if args.lado!=.5 or args.paso_max!=900:
                piezas=[]
                for curva in [c['id'] for c in insumos.leer(insumos.HIDRATACION / 'manifiesto.json')['curvas']]:
                    for clima in series:
                        nombre=destino / f'{plan}_{curva}_{clima}.json'
                        if not nombre.exists():
                            motor.ejecutar(SimpleNamespace(experimento=plan,salida=destino,modo='completo',
                                escenario=[curva,clima],geometria='exportada',lado=args.lado,paso_max=args.paso_max,traza=False),cfg)
                            pieza=leer(nombre);pieza['modelo_viento']=procedencia
                            nombre.write_text(json.dumps(pieza,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
                        pieza=leer(nombre)
                        if pieza.get('modelo_viento')!=procedencia:
                            raise ValueError('Procedencia diferente en '+str(nombre))
                        piezas.append(pieza)
                resultado=dict(piezas[0])
                resultado['corridas']=[f for pieza in piezas for f in pieza['corridas']]
                resultado['duracion_auditoria_s']=sum(x['duracion_auditoria_s'] for x in piezas)
                resultado['riesgo']=motor.insumos.importar_solver('exportada')[0].riesgo(resultado['corridas'])
                resultado['horizontes_h']=sorted({f['horizonte_h'] for f in resultado['corridas']})
                resultado['picos_no_resueltos']=sum(f['pico_no_resuelto'] for f in resultado['corridas'])
                resultado['riesgo_336']=None
                resultado['sensibilidades_pesos']=None
                with ruta.open('x',encoding='utf-8') as archivo:
                    json.dump(resultado,archivo,ensure_ascii=False,indent=2,allow_nan=False)
            else:
                motor.ejecutar(SimpleNamespace(experimento=plan,salida=destino,modo='completo',
                    escenario=None,geometria='exportada',lado=None,paso_max=None,traza=False),cfg)
                resultado=leer(ruta)
            resultado['modelo_viento']=procedencia
            ruta.write_text(json.dumps(resultado,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
            resumir(args.salida)


if __name__=='__main__':
    main()
