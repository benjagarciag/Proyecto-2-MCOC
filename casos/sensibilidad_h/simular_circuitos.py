"""24 escenarios con circuitos19/18°C, capas0.4m y sumidero equivalente global15kW."""
import argparse
from dataclasses import replace
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import sys
from time import perf_counter
from types import ModuleType

import numpy as np
import viento
import conductividad as comun
from control_circuitos import ControlCircuitos,crear_mapa,adaptar

RAIZ = viento.RAIZ


def escribir(ruta,d):
    temporal = ruta.with_suffix('.tmp')
    temporal.write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    temporal.replace(ruta)


def construir_solver(mapa,centros):
    ruta = viento.COPIA/'desarrollo/mcplan/termica_fundacion.py'
    codigo = ruta.read_text(encoding='utf-8')
    codigo = viento.cambiar(codigo,'intervalo_salida_s=3600., enfriamiento=None):',
        'intervalo_salida_s=3600., enfriamiento=None, h_aire_horario_W_m2K=None):')
    codigo = viento.cambiar(codigo,'    def preparar(t):', '''    serie_h = np.asarray(h_aire_horario_W_m2K,dtype=float)
    if serie_h.shape!=aire.shape or not np.isfinite(serie_h).all() or (serie_h<0).any():
        raise ValueError('h horario incompatible.')
    def h_en(t):
        return float(serie_h[min(int(t//3600),len(serie_h)-1)])
    def preparar(t):''')
    assert codigo.count('h_W_m2K=entorno.h_aire_W_m2K')==2
    codigo = codigo.replace('h_W_m2K=entorno.h_aire_W_m2K','h_W_m2K=h_en(t)')
    codigo = adaptar(codigo,viento.cambiar)
    nombre = 'mcplan.termica_circuitos_control'
    m = ModuleType(nombre)
    m.__package__,m.__file__ = 'mcplan',str(ruta)
    m.ControlCircuitos,m.MAPA_CONTROL,m.CENTROS_CONTROL = ControlCircuitos,mapa,centros
    sys.modules[nombre] = m
    exec(compile(codigo,str(ruta),'exec'),m.__dict__)
    return m,sha256(codigo.encode()).hexdigest()


def preparar():
    viento._preparacion.preparar()
    insumos,_,_ = viento._preparacion.cargar()
    controles,_,Entorno,_,cargar_era5,serie_aire = insumos.importar_solver('ifc')
    esquema = viento.leer(RAIZ/'resultados/diseno_circuitos_colocacion/esquema.json')
    datos = insumos.leer(insumos.RAIZ/insumos.leer(insumos.CONFIG)['base'])
    modelo = controles.extraer_fundacion_ifc(RAIZ/datos['archivo_ifc'])
    assert modelo.sha256_ifc==esquema['ifc_sha256']
    vox = controles.voxelizar_fundacion(modelo,pasos_m=(.4,)*3)
    asignada = controles.asignar_vertidas(modelo,vox)
    ids = np.zeros_like(asignada.vertida_id)
    programa = {}
    for z,plano in enumerate(asignada.vertida_id):
        if (plano>0).any():
            capa = esquema['capas'][z]
            ids[z][plano>0] = z+1
            programa[z+1] = (capa['inicio_h']*3600,12.)
    ocupados = np.flatnonzero(ids)
    coords = np.column_stack(np.unravel_index(ocupados,ids.shape))
    origen = vox.grilla.origen_m
    centros = origen+(coords[:,::-1]+.5)*.4
    mapa = crear_mapa(centros,ids,.4,esquema)
    solver,huella = construir_solver(mapa,centros)
    entorno = dict(datos['entorno'])
    entorno['capas_laterales'] = (controles.Capa(.018,.158,72),controles.Capa(.04,.042,240),controles.Capa(.04,.042,360))
    entorno['capas_superiores'] = entorno['capas_laterales'][1:]
    entorno['dt_tope_s'] = 300
    env = Entorno(**entorno)
    fuentes = controles.materiales(datos,insumos.HIDRATACION/'manifiesto.json')
    cfg = insumos.leer(insumos.CONFIG)
    meta,series,_ = viento.analizar(2.,.14)
    climas = {}
    for c in cfg['historias']:
        _,tiempo = cargar_era5(insumos.RAIZ/c['snapshot'])
        climas[c['id']] = (c,serie_aire(tiempo,datetime.fromisoformat(c['inicio']),672))
    origen_archivos = {str(Path(__file__).relative_to(RAIZ)):sha256(Path(__file__).read_bytes()).hexdigest(),
        'casos/sensibilidad_h/control_circuitos.py':sha256(Path(__file__).with_name('control_circuitos.py').read_bytes()).hexdigest(),
        'esquema_circuitos':sha256((RAIZ/'resultados/diseno_circuitos_colocacion/esquema.json').read_bytes()).hexdigest(),
        'config_base':sha256((insumos.RAIZ/cfg['base']).read_bytes()).hexdigest(),
        'manifiesto_fuentes':sha256((insumos.HIDRATACION/'manifiesto.json').read_bytes()).hexdigest()}
    procedencia = dict(commit_congelado=viento.SHA,ifc_sha256=modelo.sha256_ifc,solver_adaptado_sha256=huella,
        archivos_sha256=origen_archivos,modelo_viento=meta,agua_C=18,apertura_C=19,cierre_C=18,
        caudal_ramal_L_min=18,caudal_total_con_bypass_L_min=162,U_W_m3K=5,tope_global_W=15000,
        lado_m=.4,paso_max_s=300,regla='histeresis por circuito, cubierto antes de abrir; sin apagado global fijo',
        temperatura_colocacion_C=12,capacidad_m3_h=60,retiros_aislacion_edad_h=[240,360],
        retiro_madera_edad_h=72,D_h=esquema['duracion_total_h'],
        volumen_ifc_m3=modelo.volumen_total_mallas_m3,volumen_voxel_m3=len(ocupados)*.4**3,**mapa[3])
    return controles,solver,ids,origen,programa,env,fuentes,climas,series,cfg,procedencia


def verificar(solver):
    from control_circuitos import estados_nuevos
    np.testing.assert_array_equal(estados_nuevos([False,True,True,False,True],[18.5,18.5,18,19,22],[True,True,True,True,False]),[False,True,False,True,False])
    c = ControlCircuitos([np.array([0,1]),np.array([2])],[0,0,1],[0,1],tope=10)
    p = c.extraer(0,10,np.array([20.,19.,30.]),1000,1)
    assert c.abiertos.tolist()==[True,False] and p.sum()<=10 and p[2]==0
    c.extraer(10,10,np.array([20.,18.,30.]),1000,1)
    assert not c.abiertos.any()
    c.extraer(20,10,np.array([20.,18.5,30.]),1000,1)
    assert not c.abiertos.any()
    c.extraer(30,10,np.array([20.,19.,30.]),1000,1)
    assert c.abiertos[0] and len(c.eventos)==3
    viejo_mapa,viejos_centros = solver.MAPA_CONTROL,solver.CENTROS_CONTROL
    solver.MAPA_CONTROL = ([np.array([0])]*9,np.array([0]),[0]*9,{})
    solver.CENTROS_CONTROL = np.array([[.2,.2,.2]])
    from mcplan.hidratacion import CurvaAdiabatica
    env = solver.EntornoFundacion(2,0,20,.5,1.2,(),0,300)
    curva = CurvaAdiabatica(0,3600,2476,1023)
    r = solver.simular(np.ones((1,1,1),int),(0,0,0),.4,{1:(0,20)},curva,env,[20,20],(.2,.2,.2),h_aire_horario_W_m2K=[0,0])
    C = 2476*1023*.4**3
    H = .4**2/(.2/2+.5/1.2)
    T = 20.
    extraida = 0.
    for _ in range(12):
        q = 5*.4**3*(T-18)
        T += 300*(H*(20-T)-q)/C
        extraida += q*300
    np.testing.assert_allclose(r.campos['final'].temperatura_C,T,atol=1e-12,rtol=0)
    np.testing.assert_allclose(-r.balance_J['enfriamiento'],extraida,atol=1e-8)
    assert abs(r.balance_J['residuo'])<1e-7
    solver.MAPA_CONTROL,solver.CENTROS_CONTROL = viejo_mapa,viejos_centros
    print('Aprobadas: histéresis, cierre por cualquier tramo, cobertura, reapertura, tope global y balance contra Euler independiente.')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ejecutar',action='store_true')
    p.add_argument('--verificar',action='store_true')
    p.add_argument('--comprobar-insumos',action='store_true')
    p.add_argument('--escenario',nargs=2,metavar=('CURVA','CLIMA'))
    p.add_argument('--salida',type=Path,default=RAIZ/'resultados/circuitos_histeresis')
    args = p.parse_args()
    if not (args.ejecutar or args.verificar or args.comprobar_insumos):
        print(__doc__);return
    controles,solver,ids,origen,programa,env,fuentes,climas,series,cfg,procedencia = preparar()
    print('Geometría IFC:',ids.shape,'capas:',len(programa), 'volumen voxel:',procedencia['volumen_voxel_m3'])
    print('Mapa de control:',{k:procedencia[k] for k in ['volumen_refrigerable_m3','celdas_monitor_por_circuito','cubierto_desde_h']})
    if args.verificar or args.ejecutar: verificar(solver)
    if not args.ejecutar: return
    args.salida.mkdir(parents=True,exist_ok=True)
    filas = []
    for f in fuentes:
        for clima,(c,aire) in climas.items():
            if args.escenario and [f['id'],clima]!=args.escenario: continue
            ruta = args.salida/f'{f["id"]}_{clima}.json'
            if ruta.exists():
                d = viento.leer(ruta)
                if d['procedencia']!=procedencia:raise ValueError('Procedencia distinta; elegir otra salida.')
                filas.append(d['corrida']);print('Conservado:',ruta.name,flush=True);continue
            inicio = perf_counter()
            def resolver(horas):
                return solver.simular(ids,origen,.4,programa,f['curva'],env,aire[:horas+1],(0,0,2),h_aire_horario_W_m2K=series[clima]['h_W_m2K'][:horas+1])
            primero = resolver(336)
            horas = 600
            final = resolver(horas)
            while controles.alertas_cola(final,horas,procedencia['D_h'],168) and horas<672:
                horas += 72;final = resolver(horas)
            assert abs(final.balance_J['residuo'])<.005
            assert 0<=final.balance_J['enfriamiento_pico_W']<=15000.000001
            assert abs(sum(final.control_circuitos['energia_extraida_circuito_J'])+final.balance_J['enfriamiento'])<.05
            fila = dict(curva=f['id'],clima=clima,peso=f['peso']*c['peso'],base_336h=controles.metricas(primero,336),
                **controles.metricas(final,horas),pico_no_resuelto=controles.alertas_cola(final,horas,procedencia['D_h'],168))
            escribir(ruta,dict(procedencia=procedencia,corrida=fila,historia=final.historia,control=final.control_circuitos,
                control_336=primero.control_circuitos,segundos=perf_counter()-inicio))
            filas.append(fila)
            print(f'{f["id"]} {clima}: Tmax={fila["Tmax"]["valor"]:.3f}; Delta={fila["DeltaTmax"]["valor"]:.3f}; {horas}h; alerta={fila["pico_no_resuelto"]}',flush=True)
    if not args.escenario:
        comun.validar_filas(filas)
        d = dict(procedencia=procedencia,corridas=filas,riesgo=controles.riesgo(filas),
            riesgo_336=controles.riesgo([dict(f['base_336h'],peso=f['peso'],clima=f['clima']) for f in filas]),
            sensibilidades_pesos={c:controles.riesgo(filas,c) for c in climas},
            picos_no_resueltos=sum(f['pico_no_resuelto'] for f in filas))
        escribir(args.salida/'matriz.json',d)
        viento.csv_guardar(args.salida/'resumen.csv',[dict(Tmax_C=max(f['Tmax']['valor'] for f in filas),
            DeltaTmax_K=max(f['DeltaTmax']['valor'] for f in filas),**d['riesgo'],alertas=d['picos_no_resueltos'])])
        print('MATRIZ COMPLETA:',d['riesgo'],'alertas',d['picos_no_resueltos'],flush=True)


if __name__ == '__main__':main()
