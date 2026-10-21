"""Reproducción del video y verificación analítica independiente (guía §7)."""
from dataclasses import replace
import json
from pathlib import Path
import numpy as np
import pytest
from mcplan.difusion_1d import (
    Parametros1D, perfil_estacionario, perfil_inicial, resolver_1d, solucion_exacta,
)

RAIZ = Path(__file__).resolve().parents[2]


def cargar(nombre):
    return Parametros1D(**json.loads((RAIZ / "casos/1d" / nombre).read_text(encoding="utf-8")))


def test_reproduce_los_20_perfiles_del_codigo_original_del_profesor():
    original = RAIZ / "casos/1d/codigos/01_1d_dirichlet_verification.py"
    texto = original.read_text(encoding="utf-8")
    # Solo el bloque numérico inspeccionado, sin imports, gráficos ni IO.
    bloque = texto[texto.index("L = 1.0"):texto.index("# Texact")]
    referencia = {"np": np}
    exec(compile(bloque, str(original), "exec"), referencia)
    p = cargar("parametros.json")
    r = resolver_1d(p)
    assert p.n_pasos == referencia["nsteps"]
    assert p.dt_s == pytest.approx(referencia["dt"], abs=1e-15)
    for paso, perfil in referencia["snapshots"].items():
        np.testing.assert_allclose(r.temperatura_C[paso], perfil, rtol=0, atol=1e-12)


def test_perfil_uniforme_bordes_distintos_y_rango():
    r = resolver_1d(Parametros1D(tiempo_final_s=10))
    np.testing.assert_array_equal(r.temperatura_C[0, 1:-1], 20)
    np.testing.assert_array_equal(r.temperatura_C[:, 0], 0)
    np.testing.assert_array_equal(r.temperatura_C[:, -1], 10)
    assert r.temperatura_C.min() >= 0
    assert r.temperatura_C.max() <= 20
    assert not np.allclose(r.temperatura_C[-1], r.temperatura_C[-1, ::-1])


def test_seno_guia_coincide_con_solucion_exacta():
    p = cargar("verificacion_seno.json")
    r = resolver_1d(p)
    exacta = solucion_exacta(p, r.x_m[None, :], r.tiempos_s[:, None])
    assert np.max(np.abs(r.temperatura_C - exacta)) < 0.003
    np.testing.assert_allclose(r.temperatura_C, r.temperatura_C[:, ::-1], atol=1e-12)


def test_no_aplicar_solucion_sinusoidal_al_caso_uniforme():
    with pytest.raises(ValueError, match="no corresponde"):
        solucion_exacta(Parametros1D(), 0.5, 100)


def test_equilibrio_lineal_con_bordes_distintos():
    p = Parametros1D(n_intervalos=10, tiempo_final_s=20)
    r = resolver_1d(p, lambda x: perfil_estacionario(p, x))
    np.testing.assert_allclose(r.temperatura_C, np.broadcast_to(r.temperatura_C[0], r.temperatura_C.shape), atol=1e-13)


def test_uniforme_en_equilibrio_con_bordes_iguales():
    p = Parametros1D(temperatura_izquierda_C=20, temperatura_derecha_C=20, tiempo_final_s=10)
    np.testing.assert_array_equal(resolver_1d(p).temperatura_C, 20)


def test_actualizacion_simultanea_comprobada_a_mano():
    p = Parametros1D(n_intervalos=4, difusividad_m2_s=1e-6,
                     paso_tiempo_s=15625, tiempo_final_s=15625,
                     temperatura_izquierda_C=20, temperatura_derecha_C=20)
    inicial = np.array([20., 24., 28., 24., 20.])
    r = resolver_1d(p, lambda x: inicial)
    np.testing.assert_allclose(r.temperatura_C[-1], [20, 24, 26, 24, 20])
    np.testing.assert_array_equal(inicial, [20, 24, 28, 24, 20])


def test_refinamiento_seno_con_r_constante():
    errores = []
    for n in (10, 20, 40):
        p = replace(cargar("verificacion_seno.json"), n_intervalos=n)
        r = resolver_1d(p)
        errores.append(np.max(np.abs(r.temperatura_C[-1] - solucion_exacta(p, r.x_m, p.tiempo_final_s))))
    assert 3.7 < errores[0] / errores[1] < 4.3
    assert 3.7 < errores[1] / errores[2] < 4.3


def test_paso_inestable_se_rechaza_antes_de_ajustar():
    with pytest.raises(ValueError, match="inestable"):
        resolver_1d(Parametros1D(paso_tiempo_s=0.6, tiempo_final_s=0.1))


def test_limite_estable_y_ajuste_uniforme_del_tiempo():
    p = Parametros1D(paso_tiempo_s=0.5, tiempo_final_s=1.1)
    r = resolver_1d(p)
    assert p.dt_s == pytest.approx(1.1 / 3)
    np.testing.assert_allclose(r.tiempos_s, [0, 1.1/3, 2.2/3, 1.1])
    assert p.fourier <= 0.5


def test_tiempo_cero_devuelve_estado_inicial_con_bordes():
    p = Parametros1D(tiempo_final_s=0)
    r = resolver_1d(p)
    assert r.temperatura_C.shape == (1, 101)
    np.testing.assert_array_equal(r.temperatura_C[0], perfil_inicial(p, r.x_m))
    np.testing.assert_array_equal(r.tiempos_s, [0])


@pytest.mark.parametrize("cambio", [
    {"longitud_m": 0}, {"difusividad_m2_s": -1}, {"paso_tiempo_s": 0},
    {"fourier_objetivo": 0}, {"n_intervalos": 1}, {"n_intervalos": 20.5},
    {"n_intervalos": True}, {"tiempo_final_s": -1},
    {"amplitud_inicial_K": float("nan")}, {"temperatura_derecha_C": float("inf")},
    {"perfil_inicial": "otro"},
])
def test_parametros_invalidos(cambio):
    with pytest.raises(ValueError):
        replace(Parametros1D(), **cambio)


@pytest.mark.parametrize("perfil", [lambda x: np.zeros(3), lambda x: x * np.nan])
def test_perfil_personalizado_invalido(perfil):
    with pytest.raises(ValueError):
        resolver_1d(Parametros1D(), perfil)
