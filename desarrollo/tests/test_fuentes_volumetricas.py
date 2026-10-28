"""Generación W/m³: solución exacta, localización conservativa y regresiones."""
from dataclasses import replace

import numpy as np
import pytest

from mcplan.bordes_termicos import Dirichlet, Neumann, Robin
from mcplan.difusion_2d import Parametros2D
from mcplan.difusion_3d import Parametros3D
from mcplan.difusion_bordes import resolver_2d_bordes, resolver_3d_bordes, paso_maximo_bordes_s
from mcplan.fuentes_volumetricas import fuente_desde_config


def caso(dim, n=8, **cambios):
    valores = dict(celdas_x=n, celdas_y=n, densidad_kg_m3=2., calor_especifico_J_kgK=3.,
                   conductividad_W_mK=1., tiempo_final_s=.08)
    if dim == 2:
        p, solver = Parametros2D(espesor_m=.3, **valores), resolver_2d_bordes
    else:
        p, solver = Parametros3D(celdas_z=n, **valores), resolver_3d_bordes
    return replace(p, **cambios), solver


def caras(dim, borde=None):
    return {f'{e}_{lado}': Neumann() if borde is None else borde
            for e in 'xyz'[:dim] for lado in ('min', 'max')}


def volumen_celda(p, dim):
    return (p.dx_m*p.dy_m*p.espesor_m if dim == 2 else np.prod(p.pasos_espaciales_m))


@pytest.mark.parametrize('dim', [2, 3])
@pytest.mark.parametrize('n', [4, 8, 16])
def test_uniforme_adiabatica_exacta_e_independiente_de_malla(dim, n):
    p, solver = caso(dim, n)
    q = 60.
    r = solver(p, caras(dim), 20., fuente_W_m3=q, n_guardados=10000)
    exacta = 20+q*r.tiempos_s/(p.densidad_kg_m3*p.calor_especifico_J_kgK)
    esperado = np.broadcast_to(exacta.reshape((-1,)+(1,)*dim), r.temperatura_C.shape)
    np.testing.assert_allclose(r.temperatura_C, esperado, atol=1e-12)
    V = p.longitud_x_m*p.longitud_y_m*(p.espesor_m if dim == 2 else p.longitud_z_m)
    assert r.potencia_generada_W == pytest.approx(q*V)
    np.testing.assert_allclose(r.energia_relativa_J-r.energia_relativa_J[0], q*V*r.tiempos_historia_s, atol=1e-11)


@pytest.mark.parametrize('dim', [2, 3])
@pytest.mark.parametrize('espesor_o_largo', [.2, 1.7])
def test_potencia_escala_con_volumen_y_tasa_con_rho_cp(dim, espesor_o_largo):
    cambios = {'espesor_m': espesor_o_largo} if dim == 2 else {'longitud_z_m': espesor_o_largo}
    p, solver = caso(dim, **cambios)
    r = solver(p, caras(dim), 20., fuente_W_m3=120)
    np.testing.assert_allclose(r.temperatura_C[-1], 20+120*p.tiempo_final_s/6, atol=1e-12)
    assert r.potencia_generada_W == pytest.approx(120*espesor_o_largo)


@pytest.mark.parametrize('dim', [2, 3])
@pytest.mark.parametrize('tipo_borde', [Dirichlet(18), Neumann(2), Robin(4, 15)])
def test_balance_con_generacion_y_todos_los_bordes(dim, tipo_borde):
    p, solver = caso(dim)
    r = solver(p, caras(dim, tipo_borde), lambda *xyz: 20+xyz[0],
               fuente_W_m3=lambda *xyz: 10+3*xyz[0], n_guardados=10000)
    # Integral exacta de q=10+3x en [0,1]: 11.5 W por m³ total.
    V = p.espesor_m if dim == 2 else 1.
    assert r.potencia_generada_W == pytest.approx(11.5*V)
    esperado = r.dt_s*(r.potencia_exterior_W[:-1]+11.5*V)
    np.testing.assert_allclose(np.diff(r.energia_relativa_J), esperado, atol=2e-12)


@pytest.mark.parametrize('dim', [2, 3])
def test_fuente_localizada_un_paso_solo_calienta_celdas_activas(dim):
    p, solver = caso(dim, n=4, tiempo_final_s=.001, paso_tiempo_s=.001)
    limites = {e: [0., 1.] for e in 'xyz'[:dim]}
    limites['x'] = [.2, .55]
    q = fuente_desde_config(dict(tipo='caja', valor_W_m3=60, limites_m=limites), p)
    # Solapes en x: .05, .25, .05, 0 m, divididos por dx=.25 m.
    esperado_q = np.broadcast_to(np.array([12., 60., 12., 0.]), q.shape)
    np.testing.assert_allclose(q, esperado_q, atol=1e-13)
    r = solver(p, caras(dim), 20, fuente_W_m3=q)
    np.testing.assert_allclose(r.temperatura_C[-1], 20+.001*esperado_q/6, atol=1e-13)
    q[:] = 999  # El resultado mantiene una copia independiente.
    np.testing.assert_allclose(r.fuente_W_m3, esperado_q, atol=1e-13)


@pytest.mark.parametrize('dim', [2, 3])
@pytest.mark.parametrize('n', [5, 9, 16])
def test_caja_no_alineada_conserva_potencia_al_refinar(dim, n):
    p, solver = caso(dim, n)
    limites = dict(x=[.17, .63], y=[.23, .81])
    if dim == 3:
        limites['z'] = [.11, .72]
    q = fuente_desde_config(dict(tipo='caja', valor_W_m3=90, limites_m=limites), p)
    V_activo = np.prod([b-a for a, b in limites.values()])*(p.espesor_m if dim == 2 else 1.)
    r = solver(p, caras(dim), 20, fuente_W_m3=q)
    assert r.potencia_generada_W == pytest.approx(90*V_activo, rel=2e-14)
    assert r.energia_relativa_J[-1]-r.energia_relativa_J[0] == pytest.approx(90*V_activo*p.tiempo_final_s, rel=2e-11)
    assert r.temperatura_C[-1].max() > r.temperatura_C[-1].min()


@pytest.mark.parametrize('dim', [2, 3])
def test_refinamiento_transiente_exacto_con_generacion_y_conduccion(dim):
    errores = []
    for n in (8, 16, 32):
        p, solver = caso(dim, n, tiempo_final_s=.1)
        def inicial(*xyz):
            return 20+5*np.prod([np.cos(np.pi*x) for x in xyz], axis=0)
        r = solver(p, caras(dim), inicial, fuente_W_m3=12)
        exacta = 20+12*.1/6+(r.temperatura_C[0]-20)*np.exp(-p.alpha_m2_s*dim*np.pi**2*.1)
        errores.append(np.max(np.abs(r.temperatura_C[-1]-exacta)))
    assert errores[0]/errores[1] > 3.0
    assert errores[1]/errores[2] > 3.0
    assert errores[-1] < .003


@pytest.mark.parametrize('dim', [2, 3])
def test_fuente_y_robin_equilibrio_parabolico_convergente(dim):
    errores = []
    for n in (8, 16):
        p, solver = caso(dim, n, celdas_y=3, tiempo_final_s=12.)
        if dim == 3:
            p = replace(p, celdas_z=2)
        h, q, ambiente = 4., 12., 20.
        b = caras(dim)
        b.update(x_min=Robin(h, ambiente), x_max=Robin(h, ambiente))
        # Solución estacionaria exacta de una placa de L=1 con generación uniforme.
        def exacta(*xyz):
            x = xyz[0]
            return ambiente+q/(2*h)+q*x*(1-x)/(2*p.conductividad_W_mK)
        r = solver(p, b, exacta, fuente_W_m3=q)
        error = np.max(np.abs(r.temperatura_C[-1]-r.temperatura_C[0]))
        errores.append(error)
        # El perfil exacto continuo no es exactamente estacionario discreto;
        # su discrepancia de borde es O(dx²), y disminuye al refinar.
        assert abs(r.potencia_exterior_W[-1]+r.potencia_generada_W) < .01
    assert errores[0]/errores[1] > 3.5
    assert errores[-1] < .01


@pytest.mark.parametrize('dim', [2, 3])
def test_robin_con_fuente_puede_perder_calor_y_seguir_calentando(dim):
    p, solver = caso(dim)
    r = solver(p, caras(dim, Robin(1., 20)), 21, fuente_W_m3=600)
    assert r.potencia_exterior_W[0] < 0
    assert r.potencia_generada_W > abs(r.potencia_exterior_W[0])
    assert r.temperatura_C[-1].mean() > 21


@pytest.mark.parametrize('dim', [2, 3])
def test_default_y_fuente_cero_iguales_y_mismo_limite_estable(dim):
    p, solver = caso(dim)
    b = caras(dim, Robin(3, 15))
    r0 = solver(p, b, 25)
    r1 = solver(p, b, 25, fuente_W_m3=0.)
    np.testing.assert_array_equal(r0.temperatura_C, r1.temperatura_C)
    r2 = solver(p, b, 25, fuente_W_m3=1e5)
    assert r2.dt_max_s == r0.dt_max_s == paso_maximo_bordes_s(p, b)
    with pytest.raises(ValueError, match='inestable'):
        solver(replace(p, paso_tiempo_s=r0.dt_max_s*1.01), b, fuente_W_m3=0)


@pytest.mark.parametrize('dim', [2, 3])
def test_tiempo_cero_no_integra_fuente(dim):
    p, solver = caso(dim, tiempo_final_s=0)
    r = solver(p, caras(dim), 20, fuente_W_m3=60)
    np.testing.assert_array_equal(r.temperatura_C, 20)
    assert r.n_pasos == 0 and r.potencia_generada_W > 0


@pytest.mark.parametrize('fuente', [-1, True, '10', float('nan'), float('inf'), [1, 2],
                                   lambda *xyz: xyz[0]*np.nan, lambda *xyz: -np.ones_like(xyz[0])])
def test_validacion_fuente(fuente):
    p, solver = caso(2)
    with pytest.raises(ValueError):
        solver(p, caras(2), fuente_W_m3=fuente)


@pytest.mark.parametrize('config', [
    {}, {'tipo': 'otro', 'valor_W_m3': 10}, {'tipo': 'uniforme', 'valor_W_m3': -1},
    {'tipo': 'uniforme', 'valor_W_m3': 10, 'extra': 1},
    {'tipo': 'caja', 'valor_W_m3': 10, 'limites_m': {'x': [0, 1]}},
    {'tipo': 'caja', 'valor_W_m3': 10, 'limites_m': {'x': [0, 2], 'y': [0, 1]}},
    {'tipo': 'caja', 'valor_W_m3': 10, 'limites_m': {'x': [.5, .5], 'y': [0, 1]}},
    {'tipo': 'caja', 'valor_W_m3': 10, 'limites_m': {'x': ['0', 1], 'y': [0, 1]}}
])
def test_validacion_configuracion(config):
    p, _ = caso(2)
    with pytest.raises(ValueError):
        fuente_desde_config(config, p)


def test_config_uniforme():
    p, _ = caso(3)
    assert fuente_desde_config({'tipo': 'uniforme', 'valor_W_m3': 27}, p) == 27
