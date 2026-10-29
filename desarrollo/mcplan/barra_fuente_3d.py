"""Preparación de la barra docente, fuente móvil y observación espacial."""
import numpy as np
from .difusion_3d import Parametros3D
from .bordes_termicos import Dirichlet, Neumann
from .fuentes_volumetricas import fuente_desde_config
from .fuente_temporal_2d import PulsoTermico
from .fuente_temporal_3d import resolver_fuente_temporal_3d


CASOS_BARRA = {'barra_d20':'Barra 3D · Dirichlet 20 °C',
               'barra_d30':'Barra 3D · Dirichlet 30 °C',
               'barra_n0':'Barra 3D · Neumann cero',
               'barra_beta':'Barra 3D · Robin beta editable'}


def interpolar_campos(campos, coords, punto):
    """Interpolación trilineal interior; fuera de centros se aproxima por el centro extremo."""
    resultado = campos
    for valores, x in zip(reversed(coords),reversed(punto)):
        superior = int(np.searchsorted(valores,x))
        inferior = max(0,min(superior-1,len(valores)-1))
        superior = max(0,min(superior,len(valores)-1))
        peso = (x-valores[inferior])/(valores[superior]-valores[inferior]) if superior != inferior else 0.
        resultado = (1-peso)*np.take(resultado,inferior,axis=1)+peso*np.take(resultado,superior,axis=1)
    return resultado


def calcular_barra(caso,c):
    if c['dimension'] != 3 or c['tf_s'] <= 0:
        raise ValueError('Este caso requiere dimensión 3 y tiempo final positivo.')
    p = Parametros3D(longitud_x_m=c['Lx'],longitud_y_m=c['Ly'],longitud_z_m=c['Lz'],
                     celdas_x=c['nx'],celdas_y=c['ny'],celdas_z=c['nz'],
                     conductividad_W_mK=c['k'],densidad_kg_m3=c['rho'],calor_especifico_J_kgK=c['cp'],
                     tiempo_final_s=c['tf_s'],paso_tiempo_s=c['dt_s'])
    largos = np.array([c['Lx'],c['Ly'],c['Lz']])
    centro = np.array([c['fuente_x'],c['fuente_y'],c['fuente_z']])
    tam = np.array([c['tam_x'],c['tam_y'],c['tam_z']])
    punto = np.array([c['punto_x'],c['punto_y'],c['punto_z']])
    if not np.isfinite(np.r_[centro,tam,punto]).all() or (tam<=0).any():
        raise ValueError('Posiciones y tamaños deben ser finitos; tamaños positivos.')
    inferior,superior = centro-tam/2,centro+tam/2
    if (inferior < -largos/2-1e-12).any() or (superior > largos/2+1e-12).any():
        raise ValueError('La zona fuente debe quedar completamente dentro de la barra.')
    if (abs(punto)>largos/2+1e-12).any():
        raise ValueError('El punto de observación debe pertenecer a la barra.')
    limites = {e:[float(max(0,lo+L/2)),float(min(L,hi+L/2))]
               for e,lo,hi,L in zip('xyz',inferior,superior,largos)}
    mascara = fuente_desde_config(dict(tipo='caja',valor_W_m3=1.,limites_m=limites),p)
    bordes = {f'{e}_{lado}':Neumann(0) for e in 'xyz' for lado in ('min','max')}
    if caso in ('barra_d20','barra_d30'):
        Tb = 20 if caso == 'barra_d20' else 30
        bordes = {cara:Dirichlet(Tb) for cara in bordes}
    pulso = PulsoTermico(c['Qmax'],c['duracion_h']*3600)
    r = resolver_fuente_temporal_3d(p,bordes,pulso,mascara,c['T0'],
                                   beta_exterior=c['beta'] if caso == 'barra_beta' else None,
                                   ambiente_C=20.)
    coords = tuple(x-L/2 for x,L in zip(r.coordenadas_m,largos))
    temperatura_punto = interpolar_campos(r.temperatura_C,coords,punto)
    if caso in ('barra_d20','barra_d30') and np.isclose(abs(punto),largos/2).any():
        # Cara física prescrita, no confundir con su centro de celda vecino.
        temperatura_punto = np.full_like(r.tiempos_s,20. if caso == 'barra_d20' else 30.)
    dentro = bool(((punto >= inferior)&(punto <= superior)).all())
    indices = tuple(int(np.argmin(abs(x-v))) for x,v in zip(coords,punto))
    notas = ['Origen en el centro; z representa la altura.',
             'Qmax en W/m³ dentro de una caja; cero fuera. Integral por intersección de celdas.',
             'Los cortes pasan por los centros de celda más cercanos al punto elegido.']
    if any(v<x[0] or v>x[-1] for x,v in zip(coords,punto)) and caso not in ('barra_d20','barra_d30'):
        notas.append('Punto junto a la cara: T se aproxima por los centros extremos; no es T exacta de superficie.')
    if caso == 'barra_beta':
        notas.append(f'Normal exterior: dT/dn=beta*(T-20); beta={c["beta"]:g} 1/m.')
        notas.append('beta<0 enfría; beta=0 aísla; beta>0 amplifica al superar 20 °C. La cota de dt no elimina ese crecimiento físico de la ley.')
    if caso == 'barra_d30':
        notas.append('El contorno salta a 30 °C desde el inicio; el interior parte a T0. Es un cambio impuesto en la superficie.')
    extras = dict(q_t=r.tiempos_historia_s,
                   criterios=r.criterios,
                   q_fuente=pulso.valor(r.tiempos_historia_s),
                   q_punto=pulso.valor(r.tiempos_historia_s)*(1. if dentro else 0.),
                   T_punto=temperatura_punto,punto=punto,indices=indices,notas=notas,
                   caja=(inferior,superior),
                   energia_generada=r.calor_generado_J,
                   volumen_fuente=float(np.prod(tam)),
                   adiabatico=caso=='barra_n0' or (caso=='barra_beta' and c['beta']==0))
    return dict(caso=caso,config=dict(c),tiempos=r.tiempos_s,campos=r.temperatura_C,
                coordenadas=coords,dt=r.dt_s,dt_limite=r.dt_max_s,media_exacta=None,campo_exacto=None,
                energia=r.energia_relativa_J-r.energia_relativa_J[0],
                balance=r.calor_exterior_J+r.calor_generado_J,potencia_inicial=None,
                potencia_esperada=None,extras=extras)
