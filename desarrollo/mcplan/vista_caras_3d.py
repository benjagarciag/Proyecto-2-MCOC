"""Geometría y colores de seis caras; no ejecuta el solver."""
import numpy as np


def geometria_caras(c):
    """Un cuadrilátero por cara exterior de celda; orden igual a temperaturas."""
    bordes = [np.linspace(-c[L]/2,c[L]/2,c[n]+1)
              for L,n in (('Lx','nx'),('Ly','ny'),('Lz','nz'))]
    caras = {}
    for eje,nombre in enumerate('xyz'):
        # Orden de filas y columnas consistente con T[z,y,x].
        otros = sorted(set(range(3))-{eje},reverse=True)
        fila,columna = otros
        F,C = np.meshgrid(bordes[fila],bordes[columna],indexing='ij')
        for lado,valor in (('min',bordes[eje][0]),('max',bordes[eje][-1])):
            vertices = []
            for df,dc in ((0,0),(0,1),(1,1),(1,0)):
                v = np.empty((*F[:-1,:-1].shape,3))
                v[...,eje] = valor
                v[...,fila] = F[df:F.shape[0]-1+df,dc:F.shape[1]-1+dc]
                v[...,columna] = C[df:C.shape[0]-1+df,dc:C.shape[1]-1+dc]
                vertices.append(v)
            caras[nombre+'_'+lado] = np.stack(vertices,axis=-2).reshape(-1,4,3)
    return caras


def temperaturas_caras(T,c,caso,fisicas=True):
    """Caras físicas o centros exteriores proyectados, sin confundir ambos."""
    caras = dict(x_min=T[...,0],x_max=T[...,-1],
                 y_min=T[:,0,:],y_max=T[:,-1,:],z_min=T[0],z_max=T[-1])
    if not fisicas:
        return caras
    if caso in ('barra_d20','barra_d30'):
        Tb = 20. if caso == 'barra_d20' else 30.
        return {k:np.full_like(v,Tb) for k,v in caras.items()}
    if caso == 'barra_beta':
        for nombre,valor in caras.items():
            eje = nombre[0]
            d = c['L'+eje]/c['n'+eje]
            caras[nombre] = 20.+(valor-20.)/(1-c['beta']*d/2)
    # Neumann cero: valor extrapolado en cara igual al centro vecino.
    return caras
