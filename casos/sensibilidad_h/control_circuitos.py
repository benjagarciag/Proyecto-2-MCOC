"""Control idealizado19/18 °C por circuito y extracción volumétrica equivalente."""
import numpy as np


def estados_nuevos(anteriores, minimas, cubiertos):
    anteriores = np.asarray(anteriores,bool)
    minimas = np.asarray(minimas,float)
    cubiertos = np.asarray(cubiertos,bool)
    validos = cubiertos & np.isfinite(minimas)
    return validos & np.where(anteriores,minimas>18,minimas>=19)


def distancias_segmentos(centros, xy, z):
    distancia = np.full(len(centros),np.inf)
    for a,b in zip(xy,xy[1:]):
        a,b = np.r_[a,z],np.r_[b,z]
        vector = b-a
        s = np.clip((centros-a)@vector/np.dot(vector,vector),0,1)
        distancia = np.minimum(distancia,np.linalg.norm(centros-a-s[:,None]*vector,axis=1))
    return distancia


class ControlCircuitos:
    def __init__(self, monitores, asignacion, cubiertos_h, agua=18, U=5, tope=15000):
        self.monitores = monitores
        self.asignacion = np.asarray(asignacion,int)
        self.cubiertos_s = np.asarray(cubiertos_h)*3600
        self.agua,self.U,self.tope = agua,U,tope
        self.abiertos = np.zeros(len(monitores),bool)
        self.eventos = []
        self.energia = np.zeros(len(monitores))
        self.horas_abierto = np.zeros(len(monitores))
        self.ultima_potencia = 0.

    def extraer(self,t,dt,T,C,V):
        minimas = np.array([np.min(T[idx]) for idx in self.monitores])
        nuevos = estados_nuevos(self.abiertos,minimas,t>=self.cubiertos_s)
        for j in np.flatnonzero(nuevos!=self.abiertos):
            self.eventos.append(dict(tiempo_h=t/3600,circuito=f'C{j+1:02}',
                abierto=bool(nuevos[j]),Tmin_tramos_C=float(minimas[j]) if np.isfinite(minimas[j]) else None))
        self.abiertos = nuevos
        indices = np.flatnonzero(self.asignacion>=0)
        indices = indices[self.abiertos[self.asignacion[indices]] & np.isfinite(T[indices])]
        potencia = np.zeros(len(T))
        potencia[indices] = self.U*V*np.maximum(T[indices]-self.agua,0)
        # La extracción por sí sola no puede cruzar18 °C en un paso.
        potencia[indices] = np.minimum(potencia[indices],C*np.maximum(T[indices]-self.agua,0)/dt)
        suma = float(potencia.sum())
        if suma>self.tope:
            potencia *= self.tope/suma
        self.ultima_potencia = float(potencia.sum())
        self.energia += dt*np.bincount(self.asignacion[indices],weights=potencia[indices],minlength=len(self.abiertos))
        self.horas_abierto += self.abiertos*dt/3600
        return potencia

    def resumen(self):
        return dict(eventos_circuitos=self.eventos,energia_extraida_circuito_J=self.energia.tolist(),
            horas_abierto_circuito=self.horas_abierto.tolist(),circuitos_abiertos_final=self.abiertos.tolist())


def crear_mapa(centros, ids, h, esquema):
    distancias = np.column_stack([distancias_segmentos(centros,np.array(c['xy_m']),c['z_m']) for c in esquema['circuitos']])
    # Una capa de voxeles exteriores excluida: centro de celda interior≥0,6 m
    # de una cara plana exterior para h0,4. La geometría sigue siendo voxelizada.
    ocupada = ids>0
    interior = ocupada.copy()
    p = np.pad(ocupada,1)
    for eje in range(3):
        for s in (0,2):
            corte = [slice(1,-1)]*3
            corte[eje] = slice(s,s+ids.shape[eje])
            interior &= p[tuple(corte)]
    asignacion = np.argmin(distancias,axis=1)
    asignacion[~interior.ravel()[np.flatnonzero(ids)]] = -1
    monitores = []
    coberturas = []
    error_max = 0.
    for j,c in enumerate(esquema['circuitos']):
        elegidos = set(np.flatnonzero(distancias[:,j]<=np.sqrt(3)*h/2+.0125).tolist())
        # Asegura muestreo de todos los segmentos aunque la línea quede entre celdas.
        for a,b in zip(c['xy_m'],c['xy_m'][1:]):
            a,b = np.r_[a,c['z_m']],np.r_[b,c['z_m']]
            for s in np.linspace(0,1,max(2,int(np.linalg.norm(b-a)/(h/2))+1)):
                d = np.linalg.norm(centros-(a+s*(b-a)),axis=1)
                i = int(np.argmin(d));elegidos.add(i);error_max=max(error_max,float(d[i]))
        monitores.append(np.array(sorted(elegidos),int))
        capa = next(x for x in esquema['capas'] if x['z_superior_m']>=c['z_m']+.0125)
        coberturas.append(capa['fin_h'])
    assert all(len(x)>0 for x in monitores)
    assert set(asignacion[asignacion>=0])==set(range(9))
    return monitores,asignacion,coberturas,dict(error_muestreo_max_m=error_max,
        volumen_refrigerable_m3=float((asignacion>=0).sum()*h**3),
        celdas_monitor_por_circuito=[len(x) for x in monitores],cubierto_desde_h=coberturas)


def adaptar(fuente,cambiar):
    fuente = cambiar(fuente,'    k, distancia = entorno.k_W_mK, h_m/2',
        '''    control = ControlCircuitos(*MAPA_CONTROL[:3])
    if not np.allclose(centros,CENTROS_CONTROL):
        raise ValueError('El mapa de circuitos no corresponde a los centros del solver.')
    k, distancia = entorno.k_W_mK, h_m/2''')
    fuente = cambiar(fuente,'    def preparar(t):',
        '''    eventos = sorted(set(eventos) | {float(s) for s in control.cubiertos_s if 0<s<tf})

    def preparar(t):''')
    fuente = cambiar(fuente,'        dt = min(entorno.dt_tope_s, .8*C/suma.max()) if suma.max() > 0 else entorno.dt_tope_s',
        '''        suma[control.asignacion>=0] += control.U*V
        dt = min(entorno.dt_tope_s, .8*C/suma.max()) if suma.max() > 0 else entorno.dt_tope_s''')
    fuente = cambiar(fuente,'            energia = V*curva.energia_intervalo_J_m3(t-comienzos[ia], siguiente-comienzos[ia])',
        '''            enfriamiento_control = control.extraer(t,dt,T,C,V)
            potencia -= enfriamiento_control
            e_extraida += dt*control.ultima_potencia
            potencia_frio_max = max(potencia_frio_max,control.ultima_potencia)
            energia = V*curva.energia_intervalo_J_m3(t-comienzos[ia], siguiente-comienzos[ia])''')
    fuente = cambiar(fuente,'    if enfriamiento is not None:\n        balance.update(enfriamiento=',
        '    if True:\n        balance.update(enfriamiento=')
    fuente = cambiar(fuente,'    return Corrida(historia, pico, diferencial, campos, balance, pasos, tuple(centros[i_nucleo]),\n                   minimo, list(picos_vertidas.values()))',
        '''    resultado = Corrida(historia, pico, diferencial, campos, balance, pasos, tuple(centros[i_nucleo]),
                   minimo, list(picos_vertidas.values()))
    resultado.control_circuitos = control.resumen()
    return resultado''')
    fuente = cambiar(fuente,'                                 suelo_W=float(P[op[4]].sum()), voxeles_activos=len(ia)))',
        '''                                 suelo_W=float(P[op[4]].sum()), voxeles_activos=len(ia),
                                 circuitos_abiertos=int(control.abiertos.sum()),
                                 caudal_embebido_L_min=int(control.abiertos.sum())*18,
                                 caudal_bypass_L_min=(9-int(control.abiertos.sum()))*18,
                                 extraccion_W=control.ultima_potencia))''')
    return fuente
