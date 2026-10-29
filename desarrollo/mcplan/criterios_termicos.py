"""Criterios docentes: Tmax<=70 y max_t(Tmax_Omega-Tmin_S25)<=20.

S25 se aproxima en seis planos a 25 mm de las caras de una caja. Se incluyen
las aristas del cubo interior. La reconstrucción es lineal entre centros y
caras físicas; no sustituye un estudio de refinamiento de la capa superficial.
"""
import numpy as np


def preparar_s25(p,bordes,beta_exterior=None,ambiente_C=20.,profundidad_m=.025):
    from .bordes_termicos import Dirichlet,Neumann,Robin
    largos = np.array([p.longitud_z_m,p.longitud_y_m,p.longitud_x_m])
    numeros = np.array([p.celdas_z,p.celdas_y,p.celdas_x])
    pasos = largos/numeros
    if (largos <= 2*profundidad_m).any():
        raise ValueError('El dominio debe permitir una capa S25 interior a 25 mm.')
    leyes = []
    for eje,L,d in zip('zyx',largos,pasos):
        par=[]
        for lado in ('min','max'):
            b=bordes[eje+'_'+lado]
            if beta_exterior is not None:
                a=1/(1-beta_exterior*d/2)
                par.append((a,(1-a)*ambiente_C))
            elif isinstance(b,Dirichlet):
                par.append((0.,b.temperatura_C))
            elif isinstance(b,Neumann):
                par.append((1.,b.flujo_entrante_W_m2*d/(2*p.conductividad_W_mK)))
            elif isinstance(b,Robin):
                a=1/(1+b.h_W_m2K*d/(2*p.conductividad_W_mK))
                par.append((a,(1-a)*b.ambiente_C))
        leyes.append(par)
    # Interpoladores sobre el cubo interior: extremos S25 y centros interiores.
    tablas=[]
    for L,n,d in zip(largos,numeros,pasos):
        centros=(np.arange(n)+.5)*d
        origen=np.r_[0,centros,L]
        destino=np.unique(np.r_[profundidad_m,centros[(centros>profundidad_m)&(centros<L-profundidad_m)],L-profundidad_m])
        hi=np.searchsorted(origen,destino)
        lo=hi-1
        w=(destino-origen[lo])/(origen[hi]-origen[lo])
        tablas.append((lo,hi,w))
    return leyes,tablas,bool(np.all(pasos/2<=profundidad_m+1e-12))


def minimo_s25(T,preparacion,incluir_maximo=False):
    leyes,tablas,_=preparacion
    extendido=T
    for eje,par in enumerate(leyes):
        inferior=par[0][0]*np.take(extendido,[0],axis=eje)+par[0][1]
        superior=par[1][0]*np.take(extendido,[-1],axis=eje)+par[1][1]
        extendido=np.concatenate((inferior,extendido,superior),axis=eje)
    # Solo seis superficies, sin construir un historial o volumen refinado.
    minimo=np.inf
    for normal in range(3):
        for extremo in (0,-1):
            lo,hi,w=tablas[normal]
            cara=(1-w[extremo])*np.take(extendido,lo[extremo],axis=normal)+w[extremo]*np.take(extendido,hi[extremo],axis=normal)
            tangentes=[e for e in range(3) if e!=normal]
            for eje_local,eje_global in enumerate(tangentes):
                lo,hi,w=tablas[eje_global]
                forma=[1]*cara.ndim; forma[eje_local]=len(w)
                pesos=w.reshape(forma)
                cara=(1-pesos)*np.take(cara,lo,axis=eje_local)+pesos*np.take(cara,hi,axis=eje_local)
            minimo=min(minimo,float(cara.min()))
    return (minimo,float(extendido.max())) if incluir_maximo else minimo


def resumir_criterios(tiempos,tmax,tmin_s25,resuelve_s25):
    delta=tmax-tmin_s25
    i,j=int(np.argmax(tmax)),int(np.argmax(delta))
    return dict(Tmax_C=float(tmax[i]),tiempo_Tmax_h=float(tiempos[i]/3600),
                DeltaTmax_K=float(delta[j]),tiempo_DeltaTmax_h=float(tiempos[j]/3600),
                Tmin_S25_al_Delta_C=float(tmin_s25[j]),
                cumple_Tmax=bool(tmax[i]<=70.),cumple_Delta=bool(delta[j]<=20.),
                resuelve_s25=resuelve_s25,horizonte_h=float(tiempos[-1]/3600),
                horizonte_14dias=bool(tiempos[-1]>=14*86400),profundidad_m=.025)
