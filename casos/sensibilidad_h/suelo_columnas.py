"""Columnas FV 1D de suelo, acopladas conservativamente al hormigón explícito."""
import numpy as np


class Columnas:
    def __init__(self, n, area, dz, profundidad, k, capacidad, inicial, h_concreto, k_concreto):
        valores = np.array([area,dz,profundidad,k,capacidad,h_concreto,k_concreto],float)
        if n < 1 or not np.isfinite(valores).all() or (valores <= 0).any() or not np.isfinite(inicial):
            raise ValueError('Propiedades/dominio de suelo inválidos.')
        nz = round(profundidad/dz)
        if nz < 2 or not np.isclose(nz*dz,profundidad):
            raise ValueError('La profundidad debe contener al menos dos celdas completas.')
        self.T = np.full((n,nz),float(inicial))
        self.inicial = float(inicial)
        self.C = capacidad*area*dz
        self.G = k*area/dz
        self.H = area/(h_concreto/2/k_concreto+dz/2/k)
        self.dt_max = .8*self.C/max(3*self.G,self.G+self.H,2*self.G)
        self.energia_fondo = 0.
        self.energia_hormigon = 0.

    def avanzar(self, dt, columnas, potencia_hormigon):
        if not 0 < dt <= self.dt_max*(1+1e-10):
            raise ValueError('Paso de suelo fuera de estabilidad.')
        q = self.G*(self.T[:,1:]-self.T[:,:-1])
        p = np.zeros_like(self.T)
        p[:,:-1] += q
        p[:,1:] -= q
        # La misma potencia que recibe hormigón sale del suelo.
        np.add.at(p[:,0],columnas,-potencia_hormigon)
        fondo = 2*self.G*(self.inicial-self.T[:,-1])
        p[:,-1] += fondo
        self.T += dt*p/self.C
        self.energia_fondo += dt*float(fondo.sum())
        self.energia_hormigon += dt*float(np.sum(potencia_hormigon))

    def balance(self):
        almacenada = self.C*float((self.T-self.inicial).sum())
        return dict(suelo_almacenado_J=almacenada, suelo_fondo_J=self.energia_fondo,
            suelo_residuo_J=almacenada-self.energia_fondo+self.energia_hormigon,
            suelo_superior_min_C=float(self.T[:,0].min()),
            suelo_superior_max_C=float(self.T[:,0].max()))


def adaptar(fuente, cambiar):
    """Adapta la fuente congelada; no escribe el solver original."""
    fuente = cambiar(fuente,'    def preparar(t):', '''    basal = np.flatnonzero(np.isclose(centros[:,2]-distancia,
        entorno.plano_suelo_z_m, atol=1e-7, rtol=0) & (vecinos[:,0] < 0))
    mapa_suelo = np.full(len(T), -1, dtype=int)
    mapa_suelo[basal] = np.arange(len(basal))
    columnas = Columnas(len(basal), A, SUELO_CONFIG['dz_m'], SUELO_CONFIG['profundidad_m'],
        entorno.k_suelo_W_mK, SUELO_CONFIG['capacidad_J_m3K'], entorno.suelo_C, h_m, k)
    if enfriamiento is not None:
        raise ValueError('Este contraste está verificado solo sin extracción interna.')

    def preparar(t):''')
    fuente = cambiar(fuente,'        H[es_suelo] = suelo.H_W_K','        H[es_suelo] = columnas.H')
    fuente = cambiar(fuente,'        return ia, pares, i, d, es_suelo, H, dt, enfriados',
        '        return ia, pares, i, d, es_suelo, H, min(dt,columnas.dt_max), enfriados')
    fuente = cambiar(fuente,'        return H*(np.where(suelo_mask, entorno.suelo_C, aire_en(t))-T[i])',
        '''        temperatura_exterior = np.full(len(i), aire_en(t))
        indices = mapa_suelo[i[suelo_mask]]
        assert (indices >= 0).all()
        temperatura_exterior[suelo_mask] = columnas.T[indices,0]
        return H*(temperatura_exterior-T[i])''')
    fuente = cambiar(fuente,'            T[ia] += (dt*potencia[ia] + energia)/C',
        '''            columnas.avanzar(dt, mapa_suelo[i[suelo_mask]], P_borde[suelo_mask])
            T[ia] += (dt*potencia[ia] + energia)/C''')
    fuente = cambiar(fuente,'    if enfriamiento is not None:\n        balance.update(enfriamiento=',
        '''    balance.update(columnas.balance())
    balance['conjunto_residuo_J'] = balance['residuo'] + balance['suelo_residuo_J']
    if enfriamiento is not None:
        balance.update(enfriamiento=''')
    return fuente
