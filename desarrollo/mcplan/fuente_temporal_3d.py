"""Fuente temporal 3D separable: Q(x,y,z,t)=mascara(x,y,z)*pulso(t).

Reutiliza los balances y bordes existentes. No realiza E/S ni ejecuta casos
al importar. La integral de la fuente por paso se evalúa analíticamente.
"""
from dataclasses import dataclass
from math import ceil

import numpy as np

from .bordes_termicos import preparar_operador, potencia_con_bordes_W
from .difusion_bordes import geometria_y_bordes
from .difusion_3d import Parametros3D
from .difusion_2d import _real_finito
from .balance_cartesiano import _caras
from .criterios_termicos import preparar_s25,minimo_s25,resumir_criterios


@dataclass
class ResultadoTemporal3D:
    parametros: Parametros3D
    coordenadas_m: tuple
    tiempos_s: np.ndarray
    temperatura_C: np.ndarray
    tiempos_historia_s: np.ndarray
    energia_relativa_J: np.ndarray
    calor_exterior_J: np.ndarray
    calor_generado_J: np.ndarray
    mascara: np.ndarray
    dt_s: float
    dt_max_s: float
    criterios: dict


def resolver_fuente_temporal_3d(p, bordes, pulso, mascara=1., temperatura_inicial_C=20., n_guardados=81,
                              *, beta_exterior=None, ambiente_C=20.):
    if not isinstance(p, Parametros3D):
        raise ValueError('Se requiere Parametros3D.')
    _real_finito('temperatura_inicial_C', temperatura_inicial_C)
    if isinstance(n_guardados, bool) or not isinstance(n_guardados, int) or n_guardados < 2:
        raise ValueError('n_guardados debe ser entero >=2.')
    forma, pasos, areas, capacidad, pares = geometria_y_bordes(p, bordes)
    G, caras, suma = preparar_operador(forma, pasos, areas, p.conductividad_W_mK, pares)
    if beta_exterior is not None:
        # Gradiente con normal EXTERIOR: dT/dn=beta*(T_superficie-Tamb).
        # T_superficie=T_centro+(d/2)*beta*(T_superficie-Tamb).
        # Flujo entrante=k*beta*(T_centro-Tamb)/(1-beta*d/2).
        _real_finito('beta_exterior', beta_exterior)
        _real_finito('ambiente_C', ambiente_C)
        nuevas_caras = []
        # Para este modo todos los bordes de entrada deben ser adiabáticos;
        # se sustituye su ley, sin tocar el operador de los otros solvers.
        from .bordes_termicos import Neumann
        if not all(isinstance(b,Neumann) and b.flujo_entrante_W_m2 == 0 for b in bordes.values()):
            raise ValueError('El modo beta requiere caras base Neumann cero.')
        for eje,(d,A) in enumerate(zip(pasos,areas)):
            if beta_exterior*d/2 >= 1-1e-12:
                raise ValueError('beta*distancia_centro_cara debe ser <1. Reducir beta o refinar la malla.')
            H = -p.conductividad_W_mK*A*beta_exterior/(1-beta_exterior*d/2)
            _,_,minimo,maximo = _caras(eje,3)
            for indice in (minimo,maximo):
                nuevas_caras.append((indice,H,H*ambiente_C))
                suma[indice] += abs(H)  # Cota conservadora del avance, también si beta>0.
        caras = tuple(nuevas_caras)
    limite = float(np.min(capacidad/suma))
    propuesto = p.paso_tiempo_s if p.paso_tiempo_s is not None else p.seguridad*limite
    if propuesto > limite*(1+1e-14):
        raise ValueError(f'Paso inestable: {propuesto:g} s > {limite:g} s.')
    n = ceil(p.tiempo_final_s/propuesto)
    if n > 200000 or np.prod(forma)*n > 250000000 or np.prod(forma)*min(n+1,n_guardados) > 15000000:
        raise ValueError('Caso demasiado grande para la ventana; reducir malla o duración.')
    dt = p.tiempo_final_s/n if n else 0.
    tiempos = np.linspace(0,p.tiempo_final_s,n+1)
    datos = np.asarray(mascara)
    if datos.dtype.kind not in 'iuf' or not np.isfinite(datos).all() or (datos < 0).any() or (datos > 1).any():
        raise ValueError('La máscara debe tener valores reales entre 0 y 1.')
    mascara = np.array(np.broadcast_to(datos,forma),copy=True,dtype=float)
    ids = np.unique(np.rint(np.linspace(0,n,min(n+1,n_guardados))).astype(int))
    posiciones = {int(paso):i for i,paso in enumerate(ids)}
    campos = np.empty((len(ids),*forma))
    energias, exterior = np.empty(n+1), np.zeros(n+1)
    s25=preparar_s25(p,bordes,beta_exterior,ambiente_C)
    maximos,minimos_s25=np.empty(n+1),np.empty(n+1)
    T = np.full(forma,temperatura_inicial_C,dtype=float)
    volumen = np.prod(pasos)
    acumulada = pulso.acumulada_J_m3(tiempos)
    incrementos = np.diff(acumulada)/(p.densidad_kg_m3*p.calor_especifico_J_kgK)
    for paso in range(n+1):
        energias[paso] = capacidad*T.sum()
        minimos_s25[paso],maximos[paso]=minimo_s25(T,s25,incluir_maximo=True)
        if paso in posiciones: campos[posiciones[paso]] = T
        if paso < n:
            potencia, neta = potencia_con_bordes_W(T,G,caras)
            exterior[paso+1] = exterior[paso]+dt*neta
            T = T+dt*potencia/capacidad+incrementos[paso]*mascara
            if not np.isfinite(T).all():
                raise ValueError('El campo dejó de ser finito. Con beta>0 la ley exterior puede amplificar el calentamiento.')
    coords = tuple((np.arange(nc)+.5)*d for nc,d in zip(forma,pasos))
    generada = (acumulada-acumulada[0])*volumen*mascara.sum()
    return ResultadoTemporal3D(p,tuple(reversed(coords)),tiempos[ids],campos,
                              tiempos,energias,exterior,generada,mascara,dt,limite,
                              resumir_criterios(tiempos,maximos,minimos_s25,s25[2]))
