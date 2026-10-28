"""Verificaciones 3D sin generar archivos, figuras ni modificar el 2D."""
from dataclasses import replace

import numpy as np
import pytest

from mcplan.balance_cartesiano import potencia_dirichlet_W
from mcplan.difusion_2d import Parametros2D, Dirichlet2D, potencia_neta_W
from mcplan.difusion_3d import Parametros3D, Dirichlet3D, paso_maximo_3d_s, resolver_3d


def normalizados(**cambios):
    # Caso matemático: dx=dy=dz=1, C=1 J/K y G=1 W/K por dirección.
    return replace(Parametros3D(longitud_x_m=3, longitud_y_m=3, longitud_z_m=3,
                               celdas_x=3, celdas_y=3, celdas_z=3,
                               conductividad_W_mK=1, densidad_kg_m3=1,
                               calor_especifico_J_kgK=1, tiempo_final_s=0.1,
                               paso_tiempo_s=0.1), **cambios)


def test_equilibrio_uniforme_con_celdas_y_longitudes_distintas():
    p = Parametros3D(celdas_x=6, celdas_y=4, celdas_z=3,
                    longitud_x_m=2, longitud_y_m=1.2, longitud_z_m=0.8, tiempo_final_s=2000)
    np.testing.assert_array_equal(resolver_3d(p, Dirichlet3D(), 20).temperatura_C, 20)


def test_seis_vecinos_un_paso_manual_y_balance_interno():
    inicial = np.full((3, 3, 3), 20.)
    inicial[1, 1, 1] = 30.
    r = resolver_3d(normalizados(), Dirichlet3D(), lambda X, Y, Z: inicial)
    esperado = inicial.copy()
    esperado[1, 1, 1] = 24.  # Pierde 6*10 W durante 0.1 s con C=1.
    for indice in ((0, 1, 1), (2, 1, 1), (1, 0, 1), (1, 2, 1), (1, 1, 0), (1, 1, 2)):
        esperado[indice] = 21.
    np.testing.assert_allclose(r.temperatura_C[-1], esperado)
    assert r.temperatura_C[-1].sum() == pytest.approx(inicial.sum())
    assert inicial[1, 1, 1] == 30  # No se modifica la entrada del llamador.


@pytest.mark.parametrize('cara,indice', [
    ('x_min_C', (slice(None), slice(None), 0)), ('x_max_C', (slice(None), slice(None), -1)),
    ('y_min_C', (slice(None), 0, slice(None))), ('y_max_C', (slice(None), -1, slice(None))),
    ('z_min_C', (0, slice(None), slice(None))), ('z_max_C', (-1, slice(None), slice(None))),
])
@pytest.mark.parametrize('temperatura_borde', [10., 30.])
def test_seis_caras_signos_y_distancia_media_celda(cara, indice, temperatura_borde):
    p = normalizados()
    r = resolver_3d(p, replace(Dirichlet3D(), **{cara: temperatura_borde}), 20)
    esperado = np.full((3, 3, 3), 20.)
    esperado[indice] += 0.1*2*(temperatura_borde-20)
    np.testing.assert_allclose(r.temperatura_C[-1], esperado)
    assert p.capacidad_voxel_J_K*(r.temperatura_C[-1]-20).sum() == pytest.approx(
        0.1*9*2*(temperatura_borde-20))


def test_energia_global_igual_al_calor_intercambiado_con_bordes_en_varios_pasos():
    p = normalizados(tiempo_final_s=0.5)
    bordes = Dirichlet3D(10, 30, 15, 25, 18, 22)
    r = resolver_3d(p, bordes, lambda X, Y, Z: 20+X+2*Y+3*Z, n_guardados=20)
    calor = 0.
    for T in r.temperatura_C[:-1]:
        # Fórmula de frontera independiente: no utiliza la función de potencia.
        q_borde = 2*((10-T[:, :, 0]).sum() + (30-T[:, :, -1]).sum()
                     + (15-T[:, 0, :]).sum() + (25-T[:, -1, :]).sum()
                     + (18-T[0, :, :]).sum() + (22-T[-1, :, :]).sum())
        calor += q_borde*r.dt_s
    delta_E = p.capacidad_voxel_J_K*(r.temperatura_C[-1]-r.temperatura_C[0]).sum()
    assert delta_E == pytest.approx(calor, abs=1e-11)


def error_seno(nx, ny, nz):
    p = Parametros3D(longitud_x_m=1, longitud_y_m=1.3, longitud_z_m=0.7,
                    celdas_x=nx, celdas_y=ny, celdas_z=nz,
                    conductividad_W_mK=1, densidad_kg_m3=2, calor_especifico_J_kgK=5,
                    tiempo_final_s=0.1)
    inicial = lambda X, Y, Z: 20+10*np.sin(np.pi*X)*np.sin(np.pi*Y/1.3)*np.sin(np.pi*Z/0.7)
    r = resolver_3d(p, Dirichlet3D(), inicial)
    Z, Y, X = np.meshgrid(r.z_m, r.y_m, r.x_m, indexing='ij')
    exacta = 20+10*np.sin(np.pi*X)*np.sin(np.pi*Y/1.3)*np.sin(np.pi*Z/0.7)*np.exp(
        -0.1*np.pi**2*(1+1/1.3**2+1/0.7**2)*0.1)
    return np.max(np.abs(r.temperatura_C[-1]-exacta)), r


def test_solucion_exacta_con_tres_pasos_espaciales_diferentes():
    error, r = error_seno(16, 12, 10)
    assert error < 0.03
    assert r.temperatura_C.min() >= 20
    assert r.temperatura_C.max() <= 30


def test_refinamiento_conjunto_no_ordenes_independientes():
    # Mallas en el rango asintótico; con 6 celdas el ajuste usa solo cinco pasos.
    errores = [error_seno(n, n, n)[0] for n in (12, 24, 48)]
    assert 3 < errores[0]/errores[1] < 5
    assert 3 < errores[1]/errores[2] < 5


def test_estabilidad_de_esquina_y_rechazo_antes_del_ajuste_temporal():
    p = normalizados()
    assert paso_maximo_3d_s(p) == pytest.approx(1/9)  # Tres ejes, 2G+G por eje.
    with pytest.raises(ValueError, match='inestable'):
        resolver_3d(replace(p, paso_tiempo_s=0.12, tiempo_final_s=0.01), Dirichlet3D())
    r = resolver_3d(replace(p, paso_tiempo_s=1/9, tiempo_final_s=1/9), Dirichlet3D(), 30)
    assert r.temperatura_C.min() >= 20
    assert r.temperatura_C.max() <= 30


def test_instantaneas_limitadas_y_ajuste_del_tiempo_final():
    r = resolver_3d(normalizados(tiempo_final_s=1.05), Dirichlet3D(), 25, n_guardados=3)
    assert r.n_pasos == 11
    assert r.dt_s == pytest.approx(1.05/11)
    assert len(r.tiempos_s) == 3
    assert len(r.tiempos_historia_s) == 12
    assert r.tiempos_s[-1] == r.tiempos_historia_s[-1] == 1.05
    r0 = resolver_3d(normalizados(tiempo_final_s=0), Dirichlet3D(), 23)
    assert r0.temperatura_C.shape == (1, 3, 3, 3)
    np.testing.assert_array_equal(r0.temperatura_C, 23)


@pytest.mark.parametrize('cambio', [
    {'longitud_z_m': 0}, {'celdas_z': 2.5}, {'celdas_x': True},
    {'conductividad_W_mK': -1}, {'densidad_kg_m3': 0},
    {'calor_especifico_J_kgK': float('nan')}, {'tiempo_final_s': -1},
    {'paso_tiempo_s': 0}, {'seguridad': 1.1},
])
def test_rechaza_parametros_invalidos(cambio):
    with pytest.raises(ValueError):
        normalizados(**cambio)


def test_rechaza_borde_inicial_o_guardados_invalidos():
    with pytest.raises(ValueError):
        Dirichlet3D(z_min_C=float('inf'))
    for inicial in (float('nan'), lambda X, Y, Z: np.zeros((2, 2))):
        with pytest.raises(ValueError):
            resolver_3d(normalizados(), Dirichlet3D(), inicial)
    with pytest.raises(ValueError):
        resolver_3d(normalizados(), Dirichlet3D(), n_guardados=1)


def test_balance_por_ejes_reproduce_el_balance_2d_existente():
    p = Parametros2D(celdas_x=5, celdas_y=3, longitud_x_m=2, longitud_y_m=0.8)
    b = Dirichlet2D(10, 30, 15, 25)
    T = np.arange(15, dtype=float).reshape(3, 5)+20
    generic = potencia_dirichlet_W(T, (p.Gy_W_K, p.Gx_W_K), ((15, 25), (10, 30)))
    np.testing.assert_allclose(generic, potencia_neta_W(p, b, T))
