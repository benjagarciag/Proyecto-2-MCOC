"""Unidades, energía, linealidad y estabilidad de la fuente temporal."""
from dataclasses import replace

import numpy as np
import pytest

from mcplan.difusion_2d import Parametros2D, potencia_neta_W, resolver_2d, Dirichlet2D
from mcplan.fuente_temporal_2d import PulsoTermico, resolver_fuente_temporal_2d


@pytest.mark.parametrize('forma', ['coseno', 'triangular', 'rectangular'])
def test_energia_total_y_fuente_fuera_del_intervalo(forma):
    pulso = PulsoTermico(100, 7200, forma)
    assert pulso.acumulada_J_m3(20000) == pytest.approx(100*7200/2)
    np.testing.assert_array_equal(pulso.valor(np.array([-1, 7200, 8000])), 0)
    t = np.linspace(0, 7200, 20001)
    assert np.trapezoid(pulso.valor(t), t) == pytest.approx(360000, rel=1e-4)
    assert np.all(pulso.valor(t) >= 0)


def parametros():
    return Parametros2D(longitud_x_m=4, longitud_y_m=2, celdas_x=6, celdas_y=4,
                        tiempo_final_s=7200, paso_tiempo_s=300)


def test_balance_energia_por_paso_y_linealidad():
    p = parametros()
    fuente = PulsoTermico(1000, 3600)
    r = resolver_fuente_temporal_2d(p, fuente)
    r2 = resolver_fuente_temporal_2d(p, PulsoTermico(2000, 3600))
    np.testing.assert_allclose(r2.temperatura_C-20, 2*(r.temperatura_C-20), atol=1e-12)
    volumen_total = p.longitud_x_m*p.longitud_y_m*p.espesor_m
    for n in range(len(r.tiempos_s)-1):
        energia = p.capacidad_celda_J_K*np.sum(r.temperatura_C[n+1]-r.temperatura_C[n])
        exterior = r.dt_s*potencia_neta_W(p, r.bordes, r.temperatura_C[n]).sum()
        generada = volumen_total*(fuente.acumulada_J_m3(r.tiempos_s[n+1])
                                  - fuente.acumulada_J_m3(r.tiempos_s[n]))
        assert energia == pytest.approx(exterior+generada, abs=1e-5)
    adiabatico = 20+fuente.acumulada_J_m3(r.tiempos_s)/(p.densidad_kg_m3*p.calor_especifico_J_kgK)
    assert r.temperatura_C.min() >= 20-1e-12
    assert np.all(r.temperatura_C.max(axis=(1, 2)) <= adiabatico+1e-12)


def test_fuente_cero_equivale_a_solver_original():
    p = parametros()
    r = resolver_fuente_temporal_2d(p, PulsoTermico(0, 3600))
    original = resolver_2d(p, Dirichlet2D(), 20)
    np.testing.assert_array_equal(r.temperatura_C, original.temperatura_C)


def test_rechaza_paso_inestable():
    p = replace(parametros(), celdas_x=40, celdas_y=20, paso_tiempo_s=3600)
    with pytest.raises(ValueError, match='inestable'):
        resolver_fuente_temporal_2d(p, PulsoTermico(100, 3600))


@pytest.mark.parametrize('args', [(-1, 100), (1, 0), (float('nan'), 100), (1, 100, 'otra')])
def test_rechaza_pulso_invalido(args):
    with pytest.raises(ValueError):
        PulsoTermico(*args)
