"""Ilustra hidratación por edades independientes, sin conducción de la fundación.

Papel en el proyecto: ejemplo ejecutable de la etapa correspondiente.
Recibe hidratacion.json: rho/cp/theta/tau didácticos y calendario IFC.
Entrega curvas K y W/m³, energía J, tres PNG y resumen_hidratacion.json.
Reutiliza mcplan.construccion y mcplan.hidratacion; no altera sus módulos ni el BIM.
Las salidas se guardan bajo resultados/e07; --solo-datos omite gráficos.
--solo-datos conserva la escritura del JSON del caso.
"""
import argparse
from dataclasses import asdict
import json
import os
from pathlib import Path
import sys

RAIZ=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(RAIZ/'desarrollo'))
os.environ.setdefault('MPLCONFIGDIR',str(RAIZ/'.venv/cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from mcplan.bim import extraer_fundacion_ifc
from mcplan.voxel import voxelizar_fundacion
from mcplan.vertidas_voxel import asignar_vertidas
from mcplan.construccion import preparar_construccion,iniciar_construccion,avanzar_construccion
from mcplan.hidratacion import CurvaAdiabatica,HidratacionVertidas
from extraer_ifc import COLORES

SALIDA=RAIZ/'resultados/e07/hidratacion'


def guardar(fig,nombre):
    """Recibe una figura Matplotlib y su nombre PNG; guarda en la carpeta fija de esta etapa.
    Solo cambia la salida gráfica del caso, no datos, geometría ni parámetros.
    """
    fig.savefig(SALIDA/nombre,dpi=140,bbox_inches='tight')
    plt.close(fig)
    print('Figura:',SALIDA/nombre)


def graficar(h,config,volumenes,intervalos):
    """Recibe modelo, configuración, volúmenes por ID [m³] y energías de intervalos [J].
    Dibuja edad/elevación [h/K], fuente [W/m³] y energía [GJ]; no calcula temperaturas espaciales.
    Se incluyen ambos lados de los eventos para no dibujar generación antes de colocar.
    """
    horizonte=config['horizonte_h']
    edades=np.linspace(0,horizonte*3600,1201)
    fig,axes=plt.subplots(1,2,figsize=(14,5),layout='constrained')
    for material,curva in h.curvas_por_material.items():
        axes[0].plot(edades/3600,curva.elevacion_K(edades),label=material)
        axes[1].plot(edades/3600,curva.valor(edades),label=material)
    axes[0].set(xlabel='Edad desde colocación [h]',ylabel='Elevación adiabática acumulada [K]',
                title='Curva ideal; no es la temperatura de la fundación')
    axes[1].set(xlabel='Edad desde colocación [h]',ylabel="Generación volumétrica q''' [W/m³]",
                title='Fuente instantánea: derivada de la curva adiabática')
    for ax in axes:ax.grid(alpha=.25);ax.legend()
    parametros='; '.join(f'{m}: ρ={c.densidad_kg_m3:g} kg/m³ · cp={c.calor_especifico_J_kgK:g} J/(kg·K) · '
                         f'θ∞={c.theta_infinito_K:g} K · τ={c.tau_s/3600:g} h'
                         for m,c in h.curvas_por_material.items())
    fig.suptitle('E07 — Modelo exponencial didáctico, sin calibración de M1 · guía §§23–25\n'+parametros)
    guardar(fig,'curva_adiabatica_y_fuente.png')

    t=np.arange(0,horizonte*3600,config['paso_muestreo_h']*3600)
    # Incluye lados de los saltos: no dibujar una rampa de generación antes de colocar.
    eventos=[c.inicio_s for c in h.programa.colocaciones if c.inicio_s<=horizonte*3600]
    t=np.unique(np.concatenate([t,[-1,horizonte*3600],eventos,
                               [np.nextafter(s,-np.inf) for s in eventos]]))
    fig,axes=plt.subplots(1,2,figsize=(15,5),layout='constrained')
    figE,axE=plt.subplots(1,2,figsize=(15,5),layout='constrained')
    for c in h.programa.colocaciones:
        curva=h.curvas_por_material[c.material]
        color=COLORES[c.vertida_id-1]
        edad=t-c.inicio_s
        etiqueta=f'Vertida {c.vertida_id:02d} · inicio {c.inicio_s/3600:g} h'
        axes[0].plot(t/3600,curva.elevacion_K(edad),color=color,label=etiqueta)
        axes[1].plot(t/3600,curva.valor(edad),color=color,label=etiqueta)
        energia=curva.acumulada_J_m3(edad)*volumenes[c.vertida_id]
        axE[0].plot(t/3600,energia/1e9,color=color,label=f'Vertida {c.vertida_id:02d}')
    axes[0].set(xlabel='Tiempo desde primera colocación [h]',ylabel='Elevación adiabática ideal [K]',
                title='Misma curva M1, cinco edades independientes')
    axes[1].set(xlabel='Tiempo desde primera colocación [h]',ylabel="q''' por vertida [W/m³]",
                title='Cero antes de colocar; no se reinicia la edad anterior')
    for ax in axes:
        ax.set_xlim(-2,horizonte)
        ax.grid(alpha=.25);ax.legend(fontsize=9)
    fig.suptitle('Cinco vertidas — Hidratación didáctica desplazada según el IFC\n'
                 'Elevación adiabática y fuente; no se calcula conducción ni pérdidas al ambiente')
    guardar(fig,'hidratacion_por_vertida.png')

    axE[0].set(xlabel='Tiempo desde primera colocación [h]',ylabel='Energía acumulada [GJ]',
               title='Generación integrada, ponderada por volumen voxelizado')
    axE[0].legend(fontsize=9)
    posiciones=np.arange(len(intervalos));base=np.zeros(len(intervalos))
    for c in h.programa.colocaciones:
        valores=np.array([i['energia_por_vertida_J'][str(c.vertida_id)] for i in intervalos])/1e9
        axE[1].bar(posiciones,valores,bottom=base,color=COLORES[c.vertida_id-1],label=f'{c.vertida_id:02d}')
        base+=valores
    axE[1].set_xticks(posiciones,[f'{i["inicio_h"]:g}–{i["fin_h"]:g}' for i in intervalos],rotation=35)
    axE[1].set(xlabel='Intervalo de tiempo [h] · duraciones distintas',ylabel='Energía del intervalo [GJ]',
               title='Integral exacta; no se aproxima por q(t_inicio)·Δt')
    for ax in axE:ax.grid(alpha=.2)
    figE.suptitle('Energía de hidratación didáctica · 1 GJ = 10⁹ J\n'
                  'No incluye energía sensible de colocación, conducción ni intercambio exterior')
    guardar(figE,'energia_hidratacion.png')


def main():
    """Lee los argumentos/configuración y ejecuta el caso con las unidades anteriores.
    No devuelve un resultado de API: imprime el resumen y guarda las salidas indicadas.
    Para reutilizar datos desde otro código, importar los módulos mcplan en vez de este main.
    """
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--parametros',type=Path,default=Path(__file__).with_name('hidratacion.json'))
    parser.add_argument('--solo-datos',action='store_true')
    args=parser.parse_args()
    config=json.loads(args.parametros.read_text(encoding='utf-8'))
    horizonte,paso=config['horizonte_h'],config['paso_muestreo_h']
    limites=np.asarray(config['limites_intervalos_h'])
    if (isinstance(horizonte,bool) or isinstance(paso,bool) or not np.isfinite([horizonte,paso]).all()
        or horizonte<=0 or paso<=0 or horizonte/paso>20000 or limites.dtype.kind not in 'fiu'
        or limites.ndim!=1 or len(limites)<2 or not np.isfinite(limites).all()
        or limites[0]!=0 or limites[-1]!=horizonte or not (np.diff(limites)>0).all()):
        raise ValueError('Horizonte/paso positivos; intervalos crecientes desde 0 hasta el horizonte; máximo 20000 muestras.')
    f=extraer_fundacion_ifc(RAIZ/config['archivo_ifc'])
    a=asignar_vertidas(f,voxelizar_fundacion(f,config['pasos_m'],origen_m=config['origen_m'],
                         tolerancia_m=config['tolerancia_m'],max_celdas=config['max_celdas']))
    p=preparar_construccion(f,a)
    curvas={m:CurvaAdiabatica(**c) for m,c in config['curvas_por_material'].items()}
    h=HidratacionVertidas(p,curvas)
    V=a.voxelizacion.grilla.volumen_celda_m3
    volumenes={c.vertida_id:float(np.count_nonzero(a.vertida_id==c.vertida_id)*V) for c in p.colocaciones}
    print(config['caracter_parametros'])
    if p.ids_sin_voxeles:print('ADVERTENCIA: vertidas sin voxeles:',p.ids_sin_voxeles)
    e=iniciar_construccion(p)
    reportes=[]
    for hora in limites:
        e=avanzar_construccion(e,float(hora)*3600)
        campo=h.fuente_W_m3(e)
        total_E=h.energia_intervalo_J(0,float(hora)*3600)
        filas=[]
        for c in p.colocaciones:
            mascara=a.vertida_id==c.vertida_id
            edad=e.tiempo_s-c.inicio_s
            filas.append({'vertida_id':c.vertida_id,'edad_h':edad/3600 if edad>=0 else None,
                          'q_W_m3':float(curvas[c.material].valor(edad)),
                          'elevacion_adiabatica_K':float(curvas[c.material].elevacion_K(edad)),
                          'potencia_W':float(campo[mascara].sum()*V),
                          'energia_acumulada_J':float(total_E[mascara].sum())})
        reportes.append({'tiempo_h':float(hora),'potencia_total_W':float(campo.sum()*V),
                         'energia_total_J':float(total_E.sum()),'vertidas':filas})
        print(f't={hora:g} h | potencia={campo.sum()*V/1000:.6f} kW | energía={total_E.sum()/1e9:.6f} GJ')
    intervalos=[]
    for inicio,fin in zip(limites,limites[1:]):
        E=h.energia_intervalo_J(float(inicio)*3600,float(fin)*3600)
        intervalos.append({'inicio_h':float(inicio),'fin_h':float(fin),'energia_total_J':float(E.sum()),
                           'energia_por_vertida_J':{str(c.vertida_id):float(E[a.vertida_id==c.vertida_id].sum())
                                                    for c in p.colocaciones}})
    suma_intervalos=sum(i['energia_total_J'] for i in intervalos)
    final=reportes[-1]['energia_total_J']
    if not np.isclose(suma_intervalos,final,rtol=1e-13,atol=1e-6):
        raise RuntimeError('No cierra la suma de energía de los intervalos.')
    informe={'caracter_parametros':config['caracter_parametros'],'sha256_ifc':f.sha256_ifc,
             'pasos_m':config['pasos_m'],'volumenes_voxelizados_m3':volumenes,
             'ids_sin_voxeles':p.ids_sin_voxeles,'calendario':[asdict(c) for c in p.colocaciones],
             'curvas_por_material':config['curvas_por_material'],
             'energia_asintotica_total_J':sum(curvas[c.material].energia_final_J_m3*volumenes[c.vertida_id] for c in p.colocaciones),
             'residuo_suma_intervalos_J':suma_intervalos-final,'reportes':reportes,'intervalos':intervalos,
             'alcance':'Solo curva adiabática y generación. No son temperaturas simuladas de la fundación ni resultados calibrados de M1.'}
    SALIDA.mkdir(parents=True,exist_ok=True)
    (SALIDA/'resumen_hidratacion.json').write_text(json.dumps(informe,ensure_ascii=False,allow_nan=False,indent=2)+'\n',encoding='utf-8')
    if not args.solo_datos:graficar(h,config,volumenes,intervalos)


if __name__=='__main__':main()
