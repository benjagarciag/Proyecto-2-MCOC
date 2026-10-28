"""Balances independientes, soluciones exactas y regresión 2D/3D."""
from dataclasses import replace
from itertools import product

import numpy as np
import pytest

from mcplan.bordes_termicos import Dirichlet, Neumann, Robin, coeficientes_cara
from mcplan.difusion_bordes import resolver_2d_bordes, resolver_3d_bordes, paso_maximo_bordes_s
from mcplan.difusion_2d import Parametros2D, Dirichlet2D, resolver_2d
from mcplan.difusion_3d import Parametros3D, Dirichlet3D, resolver_3d


def caso(dim, **cambios):
    valores = dict(longitud_x_m=3., longitud_y_m=8., celdas_x=3, celdas_y=4,
                   conductividad_W_mK=2., densidad_kg_m3=3., calor_especifico_J_kgK=4.,
                   tiempo_final_s=.05, paso_tiempo_s=.01)
    if dim == 2:
        p, solver = Parametros2D(espesor_m=.7, **valores), resolver_2d_bordes
    else:
        p, solver = Parametros3D(longitud_z_m=1., celdas_z=2, **valores), resolver_3d_bordes
    return replace(p, **cambios), solver


def caras(dim, valor=None):
    return {f'{e}_{lado}': Neumann() if valor is None else valor
            for e in 'xyz'[:dim] for lado in ('min', 'max')}


def capacidad(p, dim):
    return p.capacidad_celda_J_K if dim == 2 else p.capacidad_voxel_J_K


def area_total_cara(p, dim, eje):
    if dim == 2:
        return (p.longitud_y_m if eje == 'x' else p.longitud_x_m)*p.espesor_m
    return np.prod([getattr(p, f'longitud_{e}_m') for e in 'xyz' if e != eje])


CASOS_CARAS = [(dim, cara, signo) for dim in (2, 3)
               for cara in caras(dim) for signo in (-1, 1)]


@pytest.mark.parametrize('dim,cara,signo', CASOS_CARAS)
def test_neumann_cada_cara_area_signo_y_un_paso(dim, cara, signo):
    p, solver = caso(dim, tiempo_final_s=.01)
    b = caras(dim)
    b[cara] = Neumann(signo*7.)
    r = solver(p, b, 30.)
    eje = 'xyz'.index(cara[0])
    eje_numpy = dim-1-eje
    indice = [slice(None)]*dim
    indice[eje_numpy] = 0 if cara.endswith('min') else -1
    d = getattr(p, f'longitud_{cara[0]}_m')/getattr(p, f'celdas_{cara[0]}')
    # q*A/C = q/(rho*cp*d), también para espesor no unitario.
    esperado = np.full(r.temperatura_C[0].shape, 30.)
    esperado[tuple(indice)] += signo*7*r.dt_s/(p.densidad_kg_m3*p.calor_especifico_J_kgK*d)
    np.testing.assert_allclose(r.temperatura_C[-1], esperado, atol=1e-13)
    potencia = signo*7*area_total_cara(p, dim, cara[0])
    np.testing.assert_allclose(r.potencia_exterior_W, potencia)
    np.testing.assert_allclose(r.energia_relativa_J[-1]-r.energia_relativa_J[0], potencia*r.dt_s)


@pytest.mark.parametrize('dim,cara,signo', CASOS_CARAS)
def test_robin_cada_cara_calienta_o_enfria_y_media_celda(dim, cara, signo):
    p, solver = caso(dim, tiempo_final_s=.01)
    b = caras(dim)
    ambiente, h = 30.+signo*10, 5.
    b[cara] = Robin(h, ambiente)
    r = solver(p, b, 30.)
    d = getattr(p, f'longitud_{cara[0]}_m')/getattr(p, f'celdas_{cara[0]}')
    q = (ambiente-30)/(d/(2*p.conductividad_W_mK)+1/h)
    esperado = np.full(r.temperatura_C[0].shape, 30.)
    indice = [slice(None)]*dim
    indice[dim-1-'xyz'.index(cara[0])] = 0 if cara.endswith('min') else -1
    esperado[tuple(indice)] += q*r.dt_s/(p.densidad_kg_m3*p.calor_especifico_J_kgK*d)
    np.testing.assert_allclose(r.temperatura_C[-1], esperado, atol=1e-13)
    assert r.potencia_exterior_W[0] == pytest.approx(q*area_total_cara(p, dim, cara[0]))


@pytest.mark.parametrize('dim', [2, 3])
def test_adiabatico_no_uniforme_conserva_energia_y_acota_temperaturas(dim):
    p, solver = caso(dim, tiempo_final_s=10.)
    r = solver(p, caras(dim), lambda *xyz: 30+5*np.cos(xyz[0])+2*np.sin(xyz[1]))
    np.testing.assert_allclose(r.energia_relativa_J, r.energia_relativa_J[0], rtol=3e-15)
    np.testing.assert_array_equal(r.potencia_exterior_W, 0.)
    assert r.temperatura_C[-1].min() >= r.temperatura_C[0].min()-1e-12
    assert r.temperatura_C[-1].max() <= r.temperatura_C[0].max()+1e-12
    assert np.ptp(r.temperatura_C[-1]) < np.ptp(r.temperatura_C[0])


@pytest.mark.parametrize('dim', [2, 3])
def test_balance_mixto_paso_a_paso_con_energia_exterior_independiente(dim):
    p, solver = caso(dim, tiempo_final_s=.1)
    b = caras(dim)
    b.update(x_min=Neumann(13), x_max=Robin(7, 12), y_min=Dirichlet(41))
    r = solver(p, b, lambda *xyz: 25+xyz[0]+2*xyz[1], n_guardados=100)
    energias = capacidad(p, dim)*r.temperatura_C.reshape(len(r.tiempos_s), -1).sum(axis=1)
    # Cada cara se calcula por separado, sin llamar al operador del solver.
    potencia = []
    e = p.espesor_m if dim == 2 else p.longitud_z_m/p.celdas_z
    dx, dy = p.longitud_x_m/p.celdas_x, p.longitud_y_m/p.celdas_y
    for T in r.temperatura_C[:-1]:
        pxmin = 13*area_total_cara(p, dim, 'x')
        pxmax = np.sum((12-T[..., -1])*dy*e/(dx/(2*p.conductividad_W_mK)+1/7))
        pymin = np.sum((41-T[..., 0, :])*dx*e/(dy/(2*p.conductividad_W_mK)))
        potencia.append(pxmin+pxmax+pymin)
    np.testing.assert_allclose(np.diff(energias), r.dt_s*np.array(potencia), rtol=2e-11, atol=2e-11)
    np.testing.assert_allclose(r.potencia_exterior_W[:-1], potencia)


@pytest.mark.parametrize('dim', [2, 3])
def test_robin_estacionario_exacto_resistencias_en_serie(dim):
    p, solver = caso(dim, tiempo_final_s=2.)
    b = caras(dim)
    b.update(x_min=Dirichlet(100), x_max=Robin(5, 20))
    q = 80/(p.longitud_x_m/p.conductividad_W_mK+1/5)
    r = solver(p, b, lambda *xyz: 100-q*xyz[0]/p.conductividad_W_mK)
    np.testing.assert_allclose(r.temperatura_C[-1], r.temperatura_C[0], atol=2e-12)
    np.testing.assert_allclose(r.potencia_exterior_W, 0., atol=2e-12)


@pytest.mark.parametrize('dim', [2, 3])
def test_neumann_estacionario_exacto_con_flujos_opuestos(dim):
    p, solver = caso(dim, tiempo_final_s=2.)
    b = caras(dim)
    b.update(x_min=Neumann(8), x_max=Neumann(-8))
    r = solver(p, b, lambda *xyz: 50-8*xyz[0]/p.conductividad_W_mK)
    np.testing.assert_allclose(r.temperatura_C[-1], r.temperatura_C[0], atol=2e-12)


@pytest.mark.parametrize('dim', [2, 3])
def test_neumann_transitorio_exacto_coseno(dim):
    cambios = dict(longitud_x_m=1., longitud_y_m=1., celdas_x=18, celdas_y=18,
                   tiempo_final_s=.04, paso_tiempo_s=None)
    if dim == 3:
        cambios.update(longitud_z_m=1., celdas_z=18)
    p, solver = caso(dim, **cambios)
    def inicial(*xyz):
        return 30+5*np.prod([np.cos(np.pi*x) for x in xyz], axis=0)
    r = solver(p, caras(dim), inicial)
    grillas = np.meshgrid(*reversed(r.coordenadas_m), indexing='ij')
    exacta = 30+(inicial(*reversed(grillas))-30)*np.exp(-p.alpha_m2_s*np.pi**2*dim*p.tiempo_final_s)
    assert np.max(np.abs(r.temperatura_C[-1]-exacta)) < .01


@pytest.mark.parametrize('dim,amplitud', list(product((2, 3), (-30., 30.))))
def test_robin_transitorio_exacto_modo_plano(dim, amplitud):
    p, solver = caso(dim, longitud_x_m=1., celdas_x=32, tiempo_final_s=.2, paso_tiempo_s=None)
    h, Lmedio = 5., .5
    Bi = h*Lmedio/p.conductividad_W_mK
    lo, hi = 0., np.pi/2-1e-12
    for _ in range(60):
        mu = (lo+hi)/2
        if mu*np.tan(mu) < Bi:
            lo = mu
        else:
            hi = mu
    mu = (lo+hi)/2
    b = caras(dim)
    b.update(x_min=Robin(h, 20), x_max=Robin(h, 20))
    def inicial(*xyz):
        return 20+amplitud*np.cos(mu*(xyz[0]-.5)/Lmedio)
    r = solver(p, b, inicial)
    exacta = 20+(r.temperatura_C[0]-20)*np.exp(-p.alpha_m2_s*(mu/Lmedio)**2*p.tiempo_final_s)
    assert np.max(np.abs(r.temperatura_C[-1]-exacta)) < .01


@pytest.mark.parametrize('dim', [2, 3])
def test_limites_h_cero_infinito_y_estabilidad(dim):
    p, solver = caso(dim, paso_tiempo_s=None)
    dta = paso_maximo_bordes_s(p, caras(dim))
    dtr = paso_maximo_bordes_s(p, caras(dim, Robin(100, 20)))
    dtd = paso_maximo_bordes_s(p, caras(dim, Dirichlet(20)))
    assert dtd <= dtr <= dta
    assert paso_maximo_bordes_s(p, caras(dim, Robin(0, 999))) == dta
    assert paso_maximo_bordes_s(p, caras(dim, Robin(1e15, 20))) == pytest.approx(dtd)
    # Cálculo independiente por eje: máximo entre interior (2G) y borde (G+H).
    # Con solo dos celdas en un eje no existe celda interior en esa dirección.
    volumen = capacidad(p, dim)/(p.densidad_kg_m3*p.calor_especifico_J_kgK)
    suma_max = 0.
    for eje in 'xyz'[:dim]:
        n = getattr(p, f'celdas_{eje}')
        d = getattr(p, f'longitud_{eje}_m')/n
        A = volumen/d
        G = p.conductividad_W_mK*A/d
        H = A/(d/(2*p.conductividad_W_mK)+1/100)
        suma_max += max(G+H, 2*G if n > 2 else 0.)
    assert dtr == pytest.approx(capacidad(p, dim)/suma_max)
    with pytest.raises(ValueError, match='inestable'):
        solver(replace(p, paso_tiempo_s=dtr*1.01, tiempo_final_s=.001), caras(dim, Robin(100, 20)), 30)
    a = solver(p, caras(dim), lambda *xyz: 25+xyz[0])
    z = solver(p, caras(dim, Robin(0, 999)), lambda *xyz: 25+xyz[0])
    np.testing.assert_array_equal(a.temperatura_C, z.temperatura_C)
    # Límite manual: C=12*volumen, G=2*area; esquinas Dirichlet 3 sum(G).
    limites = p.capacidad_celda_J_K/(3*(p.Gx_W_K+p.Gy_W_K)) if dim == 2 else p.capacidad_voxel_J_K/(3*sum(p.conductancias_zyx_W_K))
    assert dtd == pytest.approx(limites)
    # Paso permitido en adiabático pero rechazado si se agregan caras Dirichlet.
    with pytest.raises(ValueError, match='inestable'):
        solver(replace(p, paso_tiempo_s=(dtd+dta)/2, tiempo_final_s=.001), caras(dim, Dirichlet(20)), 30)


@pytest.mark.parametrize('dim', [2, 3])
def test_regresion_dirichlet_contra_solver_preexistente(dim):
    p, solver = caso(dim)
    b = caras(dim)
    valores = dict(x_min=11, x_max=23, y_min=34, y_max=45, z_min=56, z_max=67)
    b = {cara: Dirichlet(valores[cara]) for cara in b}
    inicial = lambda *xyz: 30+xyz[0]-2*xyz[1]
    nuevo = solver(p, b, inicial, n_guardados=100)
    if dim == 2:
        viejo = resolver_2d(p, Dirichlet2D(11, 23, 34, 45), inicial)
    else:
        viejo = resolver_3d(p, Dirichlet3D(11, 23, 34, 45, 56, 67), inicial, n_guardados=100)
    np.testing.assert_allclose(nuevo.temperatura_C, viejo.temperatura_C, atol=1e-13)
    assert nuevo.dt_max_s == viejo.dt_max_s


@pytest.mark.parametrize('dim', [2, 3])
def test_equilibrio_robin_y_limite_no_sobrepasa_ambiente(dim):
    p, solver = caso(dim, paso_tiempo_s=None, tiempo_final_s=10.)
    b = caras(dim, Robin(12, 20))
    np.testing.assert_allclose(solver(p, b, 20).temperatura_C, 20.)
    p = replace(p, paso_tiempo_s=paso_maximo_bordes_s(p, b))
    r = solver(p, b, 70)
    assert np.min(r.temperatura_C) >= 20-1e-12
    assert np.max(r.temperatura_C) <= 70+1e-12
    assert np.all(np.diff(r.energia_relativa_J) <= 1e-10)


@pytest.mark.parametrize('dim', [2, 3])
def test_memoria_tiempo_cero_y_no_modificar_inicial(dim):
    p, solver = caso(dim, tiempo_final_s=0.)
    b = caras(dim)
    forma = (p.celdas_y, p.celdas_x) if dim == 2 else p.forma_zyx
    inicial = np.full(forma, 31.)
    r = solver(p, b, lambda *xyz: inicial)
    assert r.n_pasos == 0 and len(r.tiempos_s) == 1 and r.dt_s == 0
    p = replace(p, tiempo_final_s=.123)
    r = solver(p, b, lambda *xyz: inicial, n_guardados=3)
    assert len(r.tiempos_s) == 3 and r.tiempos_s[-1] == .123
    np.testing.assert_array_equal(inicial, 31)


@pytest.mark.parametrize('constructor,args', [
    (Robin, (-1, 20)), (Robin, (float('inf'), 20)), (Robin, (5, float('nan'))),
    (Robin, (True, 20)), (Neumann, (float('inf'),)), (Neumann, (True,)),
    (Dirichlet, (float('nan'),)), (Dirichlet, ('20',))])
def test_validacion_datos_borde(constructor, args):
    with pytest.raises(ValueError):
        constructor(*args)


@pytest.mark.parametrize('dim', [2, 3])
def test_validacion_caras_inicial_y_guardados(dim):
    p, solver = caso(dim)
    b = caras(dim)
    for invalido in ({}, dict(b, inexistente=Neumann()), dict(b, x_min=123)):
        with pytest.raises(ValueError):
            solver(p, invalido)
    for inicial in (float('nan'), lambda *xyz: np.zeros((2,)), lambda *xyz: xyz[0]*np.nan):
        with pytest.raises(ValueError):
            solver(p, b, inicial)
    for n in (1, True, 2.5):
        with pytest.raises(ValueError):
            solver(p, b, 20, n_guardados=n)


def test_coeficiente_robin_independiente():
    H, B = coeficientes_cara(Robin(10, 50), 3., .2, 2.)
    assert H == pytest.approx(15.)  # 3/(0.2/2+1/10)
    assert B == pytest.approx(750.)
