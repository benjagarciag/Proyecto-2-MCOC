"""Comprobaciones sintéticas independientes: conservación, signo y solución estacionaria."""
import numpy as np
from suelo_columnas import Columnas


def verificar(solver):
    c = Columnas(2,.25,.25,4,1.2,1.8e6,15,.5,2)
    inicial = c.T.copy()
    c.avanzar(100,np.array([0]),np.array([20.]))
    assert c.T[0,0] < 15 and c.T[1,0] == 15
    np.testing.assert_allclose((c.T-inicial).sum()*c.C,-2000,atol=1e-7)
    assert abs(c.balance()['suelo_residuo_J']) < 1e-7
    # Perfil lineal estacionario: flujo prescrito en cima, T15 al fondo.
    c = Columnas(1,1,.25,4,1.2,1.8e6,15,.5,2)
    z = (np.arange(16)+.5)*.25
    c.T[0] = 15+2*(4-z)
    previa = c.T.copy()
    c.avanzar(900,np.array([0]),np.array([-2.4]))
    np.testing.assert_allclose(c.T,previa,atol=1e-13)
    # Comparador independiente: matriz Euler de un cubo de hormigón + suelo.
    from mcplan.hidratacion import CurvaAdiabatica
    entorno = solver.EntornoFundacion(2,0,15,.5,1.2,(),0,900)
    curva = CurvaAdiabatica(0,3600,2476,1023)
    cfg = solver.SUELO_CONFIG
    area, dz = .25,cfg['dz_m']
    n = round(cfg['profundidad_m']/dz)
    capacidades = np.r_[2476*1023*.5**3,np.full(n,cfg['capacidad_J_m3K']*area*dz)]
    enlaces = np.r_[area/(.25/2+dz/2/1.2),np.full(n-1,1.2*area/dz)]
    fondo = 2*1.2*area/dz
    sums = np.zeros(n+1)
    sums[:-1] += enlaces
    sums[1:] += enlaces
    sums[-1] += fondo
    paso = min(900,.8*np.min(capacidades/sums))
    # El adaptador usa una cota global de suelo algo más conservadora.
    prueba_col = Columnas(1,area,dz,cfg['profundidad_m'],1.2,cfg['capacidad_J_m3K'],15,.5,2)
    paso = min(900,prueba_col.dt_max)
    T = np.r_[20.,np.full(n,15.)]
    t = 0.
    while t < 3600:
        dt = min(paso,3600-t)
        potencia = np.zeros(n+1)
        flujo = enlaces*(T[1:]-T[:-1])
        potencia[:-1] += flujo
        potencia[1:] -= flujo
        potencia[-1] += fondo*(15-T[-1])
        T += dt*potencia/capacidades
        t += dt
    r = solver.simular(np.ones((1,1,1),int),(0,0,0),.5,{1:(0,20)},curva,
        entorno,[15,15],(.25,.25,.25),h_aire_horario_W_m2K=[0,0])
    np.testing.assert_allclose(r.campos['final'].temperatura_C, T[0],atol=1e-11,rtol=0)
    assert abs(r.balance_J['residuo']) < 1e-7
    assert abs(r.balance_J['suelo_residuo_J']) < 1e-7
    assert abs(r.balance_J['conjunto_residuo_J']) < 1e-7
    print('Aprobado: signo, conservación por columna, perfil lineal estacionario y acoplamiento contra matriz independiente.')
