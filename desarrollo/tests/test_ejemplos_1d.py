"""Comprobaciones de los bordes y del aporte térmico de los ejemplos de clase."""
import numpy as np
import pytest
from mcplan.ejemplos_1d import resolver_ejemplo


def test_neumann_calienta_sin_superar_contacto_y_tiende_a_uniformidad():
    r = resolver_ejemplo("neumann")
    np.testing.assert_array_equal(r.perfiles_C[0], 20.)
    np.testing.assert_array_equal(r.perfiles_C[1:, 0], 60.)
    assert r.perfiles_C.min() >= 20
    assert r.perfiles_C.max() <= 60
    assert 59 < r.perfiles_C[-1, -1] < 60
    assert r.tiempos_historia_s[-1] == 18000


def test_robin_primeros_dos_pasos_con_balance_superficial():
    r = resolver_ejemplo("robin", tiempo_final_s=135.)
    assert r.dt_s == pytest.approx(67.5)
    aire = 20 + 10*np.sin(2*np.pi*67.5/(12*3600))
    esperado = 20 + 67.5*2*12/(2400*900*0.0125)*(aire-20)
    assert r.historia_C[-1, 0] == pytest.approx(esperado)
    assert r.historia_C[-1, 1] == 20
    assert r.historia_C[-1, 2] == 20


def test_robin_registra_perfiles_10_h_y_historia_48_h():
    r = resolver_ejemplo("robin")
    assert r.tiempos_perfiles_s[-1] == pytest.approx(10*3600, abs=r.dt_s/2)
    assert r.tiempos_historia_s[-1] == 48*3600
    assert r.perfiles_C.min() >= 10
    assert r.perfiles_C.max() <= 30


def test_calor_interno_un_paso_suma_r_por_q0_y_mantiene_extremos():
    r = resolver_ejemplo("calor_interno", tiempo_final_s=0.45)
    np.testing.assert_allclose(r.perfiles_C[-1, 1:-1], 0.45*(5./6000))
    np.testing.assert_array_equal(r.perfiles_C[:, [0, -1]], 0)
    np.testing.assert_allclose(r.perfiles_C[-1], r.perfiles_C[-1, ::-1])


@pytest.mark.parametrize("nombre,dt", [("neumann", 0.6), ("calor_interno", 0.6), ("robin", 80)])
def test_paso_inestable_se_rechaza(nombre, dt):
    with pytest.raises(ValueError, match="inestable"):
        resolver_ejemplo(nombre, paso_tiempo_s=dt)
