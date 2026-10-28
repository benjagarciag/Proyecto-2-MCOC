"""Verificaciones independientes del balance 2D; no crean gráficos ni archivos."""
from dataclasses import replace

import numpy as np
import pytest

from mcplan.difusion_2d import Dirichlet2D, Parametros2D, paso_maximo_s, resolver_2d


def normalizados(**cambios):
    # Caso matemático sintético: alpha=1, dx=dy=1, capacidad=1 J/K, G=1 W/K.
    return replace(Parametros2D(longitud_x_m=3, longitud_y_m=3, celdas_x=3, celdas_y=3,
                               conductividad_W_mK=1, densidad_kg_m3=1,
                               calor_especifico_J_kgK=1, tiempo_final_s=0.1,
                               paso_tiempo_s=0.1), **cambios)


def test_equilibrio_uniforme_en_malla_rectangular():
    p = Parametros2D(longitud_x_m=2, longitud_y_m=0.7, celdas_x=7, celdas_y=4,
                    tiempo_final_s=2000)
    r = resolver_2d(p, Dirichlet2D(), 20)
    np.testing.assert_array_equal(r.temperatura_C, 20)


def test_un_paso_manual_y_conservacion_de_intercambios_interiores():
    p = normalizados()
    inicial = np.full((3, 3), 20.)
    inicial[1, 1] = 28.
    r = resolver_2d(p, Dirichlet2D(), lambda X, Y: inicial)
    esperado = np.array([[20, 20.8, 20], [20.8, 24.8, 20.8], [20, 20.8, 20]])
    np.testing.assert_allclose(r.temperatura_C[-1], esperado)
    assert r.temperatura_C[-1].sum() == pytest.approx(inicial.sum())
    assert inicial[1, 1] == 28  # No se modifica el arreglo del llamador.


@pytest.mark.parametrize('cara,indice', [
    ('izquierda_C', (slice(None), 0)), ('derecha_C', (slice(None), -1)),
    ('inferior_C', (0, slice(None))), ('superior_C', (-1, slice(None))),
])
def test_cada_cara_dirichlet_usa_media_celda_y_signo_correcto(cara, indice):
    p = normalizados()
    r = resolver_2d(p, replace(Dirichlet2D(), **{cara: 10}), 20)
    esperado = np.full((3, 3), 20.)
    esperado[indice] = 18.  # dt*(T_b-20)/(dx/2) = -2 K; no impone 10 al centro.
    np.testing.assert_allclose(r.temperatura_C[-1], esperado)
    delta_energia = p.capacidad_celda_J_K * (r.temperatura_C[-1] - 20).sum()
    assert delta_energia == pytest.approx(-60 * 0.1)  # Q_borde=-60 W, dt=0.1 s.


def error_seno(nx, ny, lx=1., ly=1.7):
    p = Parametros2D(longitud_x_m=lx, longitud_y_m=ly, celdas_x=nx, celdas_y=ny,
                    conductividad_W_mK=1, densidad_kg_m3=2, calor_especifico_J_kgK=5,
                    tiempo_final_s=0.2)
    inicial = lambda X, Y: 20 + 10*np.sin(np.pi*X/lx)*np.sin(np.pi*Y/ly)
    r = resolver_2d(p, Dirichlet2D(), inicial)
    X, Y = np.meshgrid(r.x_m, r.y_m)
    exacta = 20 + 10*np.sin(np.pi*X/lx)*np.sin(np.pi*Y/ly)*np.exp(
        -0.1*np.pi**2*(1/lx**2 + 1/ly**2)*p.tiempo_final_s)
    return np.max(np.abs(r.temperatura_C[-1] - exacta)), r


def test_seno_exacto_con_dx_distinto_de_dy():
    error, r = error_seno(24, 16)
    assert error < 0.015
    assert r.temperatura_C.min() >= 20
    assert r.temperatura_C.max() <= 30


def test_refinamiento_conjunto_espacial_y_temporal():
    # dt automático escala con dx²/dy²: no demuestra órdenes independientes.
    errores = [error_seno(n, n)[0] for n in (8, 16, 32)]
    assert 3 < errores[0]/errores[1] < 5
    assert 3 < errores[1]/errores[2] < 5


def test_estabilidad_incluye_esquinas_no_solo_celdas_interiores():
    p = normalizados()
    assert paso_maximo_s(p) == pytest.approx(1/6)  # 2G+G por cada dirección.
    with pytest.raises(ValueError, match='inestable'):
        resolver_2d(replace(p, paso_tiempo_s=0.2), Dirichlet2D(), 20)
    r = resolver_2d(replace(p, paso_tiempo_s=1/6, tiempo_final_s=1/6), Dirichlet2D(), 25)
    assert r.temperatura_C.min() >= 20
    assert r.temperatura_C.max() <= 25


def test_ajuste_uniforme_y_tiempo_cero():
    r = resolver_2d(normalizados(tiempo_final_s=0.25), Dirichlet2D(), 20)
    assert r.dt_s == pytest.approx(0.25/3)
    assert r.tiempos_s[-1] == 0.25
    r0 = resolver_2d(normalizados(tiempo_final_s=0), Dirichlet2D(), 23)
    assert r0.temperatura_C.shape == (1, 3, 3)
    np.testing.assert_array_equal(r0.temperatura_C, 23)


@pytest.mark.parametrize('cambio', [
    {'conductividad_W_mK': 0}, {'densidad_kg_m3': -1}, {'calor_especifico_J_kgK': float('nan')},
    {'celdas_y': 2.5}, {'celdas_x': True}, {'longitud_x_m': 0}, {'espesor_m': 0},
    {'tiempo_final_s': -1}, {'paso_tiempo_s': 0}, {'seguridad': 1.1},
])
def test_rechaza_parametros_invalidos(cambio):
    with pytest.raises(ValueError):
        normalizados(**cambio)


def test_rechaza_borde_y_condicion_inicial_invalidos():
    with pytest.raises(ValueError):
        Dirichlet2D(superior_C=float('inf'))
    for inicial in (float('nan'), lambda X, Y: np.zeros((2, 2))):
        with pytest.raises(ValueError):
            resolver_2d(normalizados(), Dirichlet2D(), inicial)


def test_espesor_uniforme_no_cambia_la_temperatura():
    p = normalizados()
    r1 = resolver_2d(p, Dirichlet2D(), 25)
    r2 = resolver_2d(replace(p, espesor_m=0.25), Dirichlet2D(), 25)
    np.testing.assert_allclose(r1.temperatura_C, r2.temperatura_C)
