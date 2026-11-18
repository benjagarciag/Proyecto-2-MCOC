"""Balance no lineal en superficie exterior de las capas, sin doble conteo."""
from datetime import datetime,timezone
import calendar
import numpy as np

SIGMA=5.670374419e-8


def vector_solar(timestamp,lat=-37.277929,lon=-72.368271):
    """NOAA: vector ENU en el punto medio de cada horaUTC."""
    d=datetime.fromtimestamp(float(timestamp),timezone.utc)
    hora=d.hour+d.minute/60+d.second/3600
    gamma=2*np.pi/(366 if calendar.isleap(d.year) else 365)*(d.timetuple().tm_yday-1+(hora-12)/24)
    eot=229.18*(.000075+.001868*np.cos(gamma)-.032077*np.sin(gamma)-.014615*np.cos(2*gamma)-.040849*np.sin(2*gamma))
    dec=.006918-.399912*np.cos(gamma)+.070257*np.sin(gamma)-.006758*np.cos(2*gamma)+.000907*np.sin(2*gamma)-.002697*np.cos(3*gamma)+.00148*np.sin(3*gamma)
    w=np.deg2rad((hora*60+eot+4*lon)/4-180)
    phi=np.deg2rad(lat)
    return np.array([-np.cos(dec)*np.sin(w),np.cos(phi)*np.sin(dec)-np.sin(phi)*np.cos(dec)*np.cos(w),
        np.sin(phi)*np.sin(dec)+np.cos(phi)*np.cos(dec)*np.cos(w)])


def irradiancias(hr,inicio,yaw=0,albedo=.2):
    indices=hr['time'].index(int(datetime.fromisoformat(inicio).timestamp()))
    # Irradiancias de la marca j+1: promedio de la hora[j,j+1].
    ghi=np.array(hr['shortwave_radiation'][indices+1:indices+674])
    dhi=np.array(hr['diffuse_radiation'][indices+1:indices+674])
    dni=np.array(hr['direct_normal_irradiance'][indices+1:indices+674])
    assert len(ghi)==673
    sol=np.array([vector_solar(hr['time'][indices+j]+1800) for j in range(673)])
    theta=np.deg2rad(yaw)
    E,N=sol[:,0].copy(),sol[:,1].copy()
    # +x del modelo se gira desdeEste haciaNorte.
    sol[:,0]=np.cos(theta)*E+np.sin(theta)*N
    sol[:,1]=-np.sin(theta)*E+np.cos(theta)*N
    directo=np.where(sol[:,2]>0,dni,0)
    I=np.empty((673,6))
    I[:,0]=albedo*ghi;I[:,1]=ghi
    for j,coseno in [(2,-sol[:,1]),(3,sol[:,1]),(4,-sol[:,0]),(5,sol[:,0])]:
        I[:,j]=directo*np.maximum(coseno,0)+.5*dhi+.5*albedo*ghi
    return I,dict(GHI_max_W_m2=float(ghi.max()),I_vertical_max_W_m2=float(I[:,2:].max()),
        descomposicion_horizontal_error_max=float(np.max(abs(np.array(hr['direct_radiation'][indices+1:indices+674])+dhi-ghi))))


def superficie(Tc,R,h,Ta,I,alpha,eps,Tenv4):
    """Ts[°C],q[W/m²] entrante y flujos exteriores: balance exacto gris."""
    Tc,R,I,Tenv4=np.broadcast_arrays(np.asarray(Tc,float),np.asarray(R,float),np.asarray(I,float),np.asarray(Tenv4,float))
    assert (R>0).all() and h>=0 and 0<=alpha<=1 and 0<=eps<=1
    if eps==0:
        Ts=(Tc/R+h*Ta+alpha*I)/(1/R+h)
    else:
        hr=4*eps*SIGMA*(Ta+273.15)**3
        Te=np.maximum(Tenv4,0)**.25-273.15
        Ts=(Tc/R+h*Ta+hr*Te+alpha*I)/(1/R+h+hr)
        for _ in range(9):
            K=Ts+273.15
            f=(Ts-Tc)/R-h*(Ta-Ts)-alpha*I-eps*SIGMA*(Tenv4-K**4)
            paso=f/(1/R+h+4*eps*SIGMA*K**3)
            Ts-=paso
            if np.max(abs(paso))<1e-10:break
        else:raise RuntimeError('No convergió balance superficial.')
    solar=alpha*I
    conv=h*(Ta-Ts)
    lw=eps*SIGMA*(Tenv4-(Ts+273.15)**4)
    q=(Ts-Tc)/R
    resid=q-conv-solar-lw
    if np.max(abs(resid))>2e-8:raise RuntimeError('Residual de superficie excesivo.')
    return Ts,q,solar,conv,lw


class Radiacion:
    def __init__(self,I,dew,nubes,alpha=.6,eps=.9,cielo='nubes'):
        self.I=np.asarray(I,float);self.dew=np.asarray(dew,float);self.nubes=np.asarray(nubes,float)
        self.alpha,self.eps,self.cielo=alpha,eps,cielo
        self.reset()

    def reset(self):
        self.energia=np.zeros(3);self.ultima=np.zeros(3)
        self.ts_min=np.inf;self.ts_max=-np.inf;self.clips=0
        self.residual_max=0.

    def nueva(self):return Radiacion(self.I,self.dew,self.nubes,self.alpha,self.eps,self.cielo)

    def flujo(self,Tc,R,h,Ta,d,t,j_solar,A):
        hora=min(t/3600,len(self.dew)-1)
        td=np.interp(hora,np.arange(len(self.dew)),self.dew)+273.15
        N=np.interp(hora,np.arange(len(self.nubes)),self.nubes)/10
        if self.cielo=='despejado':N=0
        if self.cielo=='cubierto':N=10
        emis=(.787+.764*np.log(td/273))*(1+.0224*N-.0035*N*N+.00028*N**3)
        emis=float(np.clip(emis,0,1))
        # Totalcloud se usa como proxy de nubosidad opaca; no mediciónIR.
        F=np.where(d==1,1.,np.where(d==0,0.,.5))
        env4=(F*emis+1-F)*(Ta+273.15)**4
        Ts,q,solar,conv,lw=superficie(Tc,R,h,Ta,self.I[min(j_solar,len(self.I)-1),d],self.alpha,self.eps,env4)
        self.ultima=A*np.array([solar.sum(),conv.sum(),lw.sum()])
        self.ts_min=min(self.ts_min,float(Ts.min()));self.ts_max=max(self.ts_max,float(Ts.max()))
        self.residual_max=max(self.residual_max,float(np.max(abs(q-solar-conv-lw))))
        return A*q

    def acumular(self,dt):self.energia+=dt*self.ultima

    def resumen(self):
        return dict(solar_absorbida_exterior_J=float(self.energia[0]),conveccion_exterior_J=float(self.energia[1]),
            onda_larga_neta_J=float(self.energia[2]),Ts_externa_min_C=self.ts_min,Ts_externa_max_C=self.ts_max,
            residual_superficie_max_W_m2=self.residual_max)


def adaptar(codigo,cambiar):
    codigo=cambiar(codigo,'    historia, campos = [], {}','    radiacion = MODELO_RADIACION.nueva()\n    historia, campos = [], {}')
    codigo=cambiar(codigo,'        enfriados = np.empty(0, dtype=np.intp)', '''        Rrad = np.full(len(i),distancia/k)
        for vid,(inicio,_) in programa.items():
            for cs,orientacion in ((entorno.capas_laterales,d>=2),(entorno.capas_superiores,d==1)):
                mascara = (propietarios[i]==vid) & orientacion & ~es_suelo
                if cs and mascara.any():
                    Rrad[mascara] += sum(c.resistencia_m2K_W((t-inicio)/3600) for c in cs)
        Hlim = np.where(es_suelo,H,A/Rrad)
        suma += np.bincount(i,weights=Hlim-H,minlength=len(T))
        enfriados = np.empty(0, dtype=np.intp)''')
    codigo=cambiar(codigo,'        return ia, pares, i, d, es_suelo, H, dt, enfriados',
        '        return ia, pares, i, d, es_suelo, H, dt, enfriados, Rrad, h_en(t), int(t//3600)')
    codigo=cambiar(codigo,'''        _, _, i, _, suelo_mask, H, _, _ = op
        return H*(np.where(suelo_mask, entorno.suelo_C, aire_en(t))-T[i])''', '''        _, _, i, d, suelo_mask, H, _, _, Rrad, hconv, jsolar = op
        P = np.zeros(len(i))
        P[suelo_mask] = H[suelo_mask]*(entorno.suelo_C-T[i[suelo_mask]])
        air = ~suelo_mask
        if air.any():
            P[air] = radiacion.flujo(T[i[air]],Rrad[air],hconv,aire_en(t),d[air],t,jsolar,A)
        return P''')
    codigo=cambiar(codigo,'        ia, _, i, d, _, _, _, _ = op','        ia, _, i, d, _, _, _, _, _, _, _ = op')
    codigo=cambiar(codigo,'        ia, pares, i, _, suelo_mask, _, dt_max, enfriados = op',
        '        ia, pares, i, _, suelo_mask, _, dt_max, enfriados, _, _, _ = op')
    codigo=cambiar(codigo,'            e_aire += dt*float(P_borde[~suelo_mask].sum())',
        '            e_aire += dt*float(P_borde[~suelo_mask].sum())\n            radiacion.acumular(dt)')
    codigo=cambiar(codigo,'    resultado.control_circuitos = control.resumen()',
        '    resultado.control_circuitos = control.resumen()\n    resultado.radiacion = radiacion.resumen()')
    return codigo
