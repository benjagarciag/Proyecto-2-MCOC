"""Interfaz, capacidades locales, conservación y referencias matemáticas."""
from dataclasses import asdict, replace

import numpy as np
import pytest

from mcplan.bordes_termicos import Dirichlet, Neumann, Robin
from mcplan.difusion_2d import Parametros2D
from mcplan.difusion_3d import Parametros3D
from mcplan.difusion_bordes import resolver_2d_bordes, resolver_3d_bordes, paso_maximo_bordes_s, _preparar_balance
from mcplan.materiales_termicos import MaterialTermico, DosMateriales, materiales_desde_config
from mcplan.balance_cartesiano import _caras


M0 = MaterialTermico(1., 1., 2.)
M1 = MaterialTermico(4., 2., 4.)


def caso(dim, n=8, **cambios):
    valores = dict(celdas_x=n, celdas_y=3, longitud_x_m=1., longitud_y_m=.6,
                   conductividad_W_mK=1, densidad_kg_m3=1, calor_especifico_J_kgK=2,
                   tiempo_final_s=.05)
    if dim == 2:
        p, solver = Parametros2D(espesor_m=.7, **valores), resolver_2d_bordes
    else:
        p, solver = Parametros3D(celdas_z=2, longitud_z_m=.4, **valores), resolver_3d_bordes
    return replace(p, **cambios), solver


def caras(dim, borde=None):
    return {f'{e}_{lado}': Neumann() if borde is None else borde
            for e in 'xyz'[:dim] for lado in ('min', 'max')}


def bloques(p, eje='x', m0=M0, m1=M1):
    return materiales_desde_config(dict(eje=eje, interfaz_m=getattr(p, f'longitud_{eje}_m')/2,
                                       materiales=[asdict(m0), asdict(m1)]), p)


CASOS_EJE = [(dim, eje) for dim in (2, 3) for eje in 'xyz'[:dim]]


@pytest.mark.parametrize('dim,eje', CASOS_EJE)
def test_un_paso_manual_conservativo_en_cada_direccion(dim, eje):
    cambios = dict(longitud_x_m=2., longitud_y_m=2., celdas_y=2,
                   tiempo_final_s=.1, paso_tiempo_s=.1)
    if dim == 3:
        cambios.update(longitud_z_m=2.)
    p, solver = caso(dim, 2, **cambios)
    m = bloques(p, eje)
    inicial = lambda *xyz: np.where(xyz['xyz'.index(eje)] < 1, 80., 20.)
    r = solver(p, caras(dim), inicial, materiales=m)
    # k_h=1.6 W/mK; P/V=1.6*(80-20)=96 W/m³; C/V=2 u 8 J/(m³K).
    esperado = np.where(r.materiales.ids == 0, 80-.1*96/2, 20+.1*96/8)
    np.testing.assert_allclose(r.temperatura_C[-1], esperado, atol=1e-13)
    np.testing.assert_allclose(r.energia_relativa_J, r.energia_relativa_J[0], rtol=2e-15)


@pytest.mark.parametrize('dim', [2, 3])
def test_conservacion_adiabatica_y_equilibrio_ponderado_por_capacidad(dim):
    p, solver = caso(dim, tiempo_final_s=4.)
    r = solver(p, caras(dim), lambda *xyz: np.where(xyz[0] < .5, 80., 20.), materiales=bloques(p))
    np.testing.assert_allclose(r.energia_relativa_J, r.energia_relativa_J[0], rtol=4e-15)
    # C_0 por volumen=2, C_1=8 y volúmenes iguales: equilibrio 32°C, no 50°C.
    media_energetica = (r.temperatura_C*r.capacidad_J_K).reshape(len(r.tiempos_s), -1).sum(axis=1)/r.capacidad_J_K.sum()
    np.testing.assert_allclose(media_energetica, 32., atol=1e-12)
    np.testing.assert_allclose(r.temperatura_C[-1], 32., atol=.02)


@pytest.mark.parametrize('dim,eje', CASOS_EJE)
def test_estacionario_exacto_flujo_continuo_y_temperatura_de_contacto(dim, eje):
    cambios = dict(celdas_y=4)
    p, solver = caso(dim, **cambios)
    b = caras(dim)
    b.update({f'{eje}_min': Dirichlet(80), f'{eje}_max': Dirichlet(20)})
    L = getattr(p, f'longitud_{eje}_m')
    q = 60/(L/2/M0.conductividad_W_mK+L/2/M1.conductividad_W_mK)
    Tcontacto = 80-q*L/(2*M0.conductividad_W_mK)
    def exacta(*xyz):
        x = xyz['xyz'.index(eje)]
        return np.where(x < L/2, 80-q*x/M0.conductividad_W_mK,
                        Tcontacto-q*(x-L/2)/M1.conductividad_W_mK)
    m = bloques(p, eje)
    r = solver(p, b, exacta, materiales=m)
    np.testing.assert_allclose(r.temperatura_C[-1], r.temperatura_C[0], atol=2e-12)
    forma, pasos, _, _, G, _, _, campos = _preparar_balance(p, b, m)
    eje_numpy = dim-1-'xyz'.index(eje)
    a, c, _, _ = _caras(eje_numpy, dim)
    A = (np.prod(pasos)*(p.espesor_m if dim == 2 else 1))/pasos[eje_numpy]
    flujo = G[eje_numpy]*(r.temperatura_C[-1][a]-r.temperatura_C[-1][c])/A
    np.testing.assert_allclose(flujo, q, atol=2e-12)  # Todas las caras, no solo la interfaz.
    interfaz = [slice(None)]*dim
    interfaz[eje_numpy] = forma[eje_numpy]//2-1
    i = tuple(interfaz)
    interfaz[eje_numpy] += 1
    j = tuple(interfaz)
    Ti, Tj = r.temperatura_C[-1][i], r.temperatura_C[-1][j]
    desde_i = Ti-q*(pasos[eje_numpy]/2)/campos.k_W_mK[i]
    desde_j = Tj+q*(pasos[eje_numpy]/2)/campos.k_W_mK[j]
    np.testing.assert_allclose(desde_i, Tcontacto, atol=1e-12)
    np.testing.assert_allclose(desde_j, Tcontacto, atol=1e-12)


@pytest.mark.parametrize('dim', [2, 3])
@pytest.mark.parametrize('k1', [.1, 1., 10.])
def test_conductividad_armonica_y_contraste_de_k(dim, k1):
    p, _ = caso(dim)
    m = bloques(p, m1=MaterialTermico(k1, 2, 4))
    forma, pasos, _, volumen, G, _, _, _ = _preparar_balance(p, caras(dim), m)
    d, A = pasos[-1], volumen/pasos[-1]
    esperado = A/(d/2/1.+d/2/k1)
    np.testing.assert_allclose(G[-1][..., forma[-1]//2-1], esperado)


@pytest.mark.parametrize('dim', [2, 3])
@pytest.mark.parametrize('borde', [Dirichlet(15), Neumann(4), Robin(10, 15)])
def test_recupera_homogeneo_con_fuente_y_todos_los_bordes(dim, borde):
    p, solver = caso(dim)
    m = bloques(p, m1=M0)
    b = caras(dim, borde)
    inicial = lambda *xyz: 25+2*xyz[0]+xyz[1]
    viejo = solver(p, b, inicial, fuente_W_m3=10)
    nuevo = solver(p, b, inicial, fuente_W_m3=10, materiales=m)
    np.testing.assert_allclose(nuevo.temperatura_C, viejo.temperatura_C, atol=2e-13)
    np.testing.assert_allclose(nuevo.energia_relativa_J, viejo.energia_relativa_J, atol=2e-13)
    assert nuevo.dt_max_s == pytest.approx(viejo.dt_max_s)


@pytest.mark.parametrize('dim', [2, 3])
@pytest.mark.parametrize('tipo', ['dirichlet', 'robin'])
def test_bordes_exteriores_usan_k_local_y_capacidad_local(dim, tipo):
    p, solver = caso(dim, tiempo_final_s=.0001, paso_tiempo_s=.0001)
    borde = Dirichlet(20) if tipo == 'dirichlet' else Robin(3, 20)
    b, m = caras(dim, borde), bloques(p)
    r = solver(p, b, 30, materiales=m)
    forma, pasos, _, volumen, _, _, _, campos = _preparar_balance(p, b, m)
    P = np.zeros(forma)
    for eje, d in enumerate(pasos):
        A = volumen/d
        _, _, minimo, maximo = _caras(eje, dim)
        for cara in (minimo, maximo):
            R = d/(2*campos.k_W_mK[cara])+(0 if tipo == 'dirichlet' else 1/3)
            P[cara] += A/R*(20-30)
    np.testing.assert_allclose(r.temperatura_C[-1], 30+r.dt_s*P/r.capacidad_J_K, atol=1e-13)


@pytest.mark.parametrize('dim', [2, 3])
def test_fuente_con_capacidades_distintas_y_balance_abierto(dim):
    p, solver = caso(dim)
    b = caras(dim, Robin(2, 10))
    r = solver(p, b, lambda *xyz: 25+xyz[0], materiales=bloques(p), fuente_W_m3=100)
    Ptotal = 100*(p.espesor_m if dim == 2 else p.longitud_z_m)*p.longitud_y_m
    np.testing.assert_allclose(np.diff(r.energia_relativa_J),
                               r.dt_s*(r.potencia_exterior_W[:-1]+Ptotal), atol=1e-12)
    assert r.potencia_generada_W == pytest.approx(Ptotal)
    # Un paso desde T uniforme y adiabático: solo fuente, tasa q/(rho*cp).
    p = replace(p, tiempo_final_s=.001, paso_tiempo_s=.001)
    s = solver(p, caras(dim), 20, materiales=bloques(p), fuente_W_m3=100)
    np.testing.assert_allclose(s.temperatura_C[-1], 20+.001*100/(s.materiales.rho_kg_m3*s.materiales.cp_J_kgK))


@pytest.mark.parametrize('dim', [2, 3])
def test_limite_estable_independiente_y_rechazo_de_paso(dim):
    p, solver = caso(dim)
    m, b = bloques(p), caras(dim, Robin(8, 20))
    forma, pasos, C, V, _, _, _, campos = _preparar_balance(p, b, m)
    # Recorre cada celda/vecino para obtener sumG, sin usar el operador vectorizado.
    limites = []
    for indice in np.ndindex(forma):
        suma = 0.
        ki = campos.k_W_mK[indice]
        for eje, d in enumerate(pasos):
            A = V/d
            for direccion in (-1, 1):
                vecino = list(indice)
                vecino[eje] += direccion
                if 0 <= vecino[eje] < forma[eje]:
                    kj = campos.k_W_mK[tuple(vecino)]
                    suma += A/(d/2/ki+d/2/kj)
                else:
                    suma += A/(d/2/ki+1/8)
        limites.append(C[indice]/suma)
    dt_max = paso_maximo_bordes_s(p, b, materiales=m)
    assert dt_max == pytest.approx(min(limites))
    with pytest.raises(ValueError, match='inestable'):
        solver(replace(p, tiempo_final_s=.0001, paso_tiempo_s=dt_max*1.001), b, 30, materiales=m)
    r = solver(replace(p, paso_tiempo_s=dt_max), b, 70, materiales=m)
    assert r.temperatura_C.min() >= 20-1e-12
    assert r.temperatura_C.max() <= 70+1e-12


@pytest.mark.parametrize('dim', [2, 3])
def test_refinamiento_transiente_exacto_con_flujo_no_nulo_en_interfaz(dim):
    errores = []
    for n in (8, 16, 32):
        # Mantener dt/dx²=0.05 evita que los otros ejes cambien la relación
        # temporal durante el refinamiento de esta solución que solo varía en x.
        p, solver = caso(dim, n, tiempo_final_s=.03, paso_tiempo_s=.05/n**2)
        # Alpha=1 en ambos, pero k y rho*cp distintos. El modo continuo es
        # cos(pi*x) en la izquierda y 1/4*cos(pi*x) en la derecha.
        m = bloques(p, m0=MaterialTermico(1, 1, 1), m1=MaterialTermico(4, 2, 2))
        def inicial(*xyz):
            x = xyz[0]
            return 30+10*np.where(x < .5, 1., .25)*np.cos(np.pi*x)
        r = solver(p, caras(dim), inicial, materiales=m)
        exacta = 30+(r.temperatura_C[0]-30)*np.exp(-np.pi**2*p.tiempo_final_s)
        errores.append(np.max(np.abs(r.temperatura_C[-1]-exacta)))
    assert errores[0]/errores[1] > 3.
    assert errores[1]/errores[2] > 3.
    assert errores[-1] < .004


@pytest.mark.parametrize('dim', [2, 3])
def test_mapa_heterogeneo_con_intercambio_en_todos_los_ejes(dim):
    p, solver = caso(dim, tiempo_final_s=.2)
    forma = (p.celdas_y, p.celdas_x) if dim == 2 else p.forma_zyx
    ids = np.indices(forma).sum(axis=0) % 2
    inicial = np.random.default_rng(1906).uniform(20, 60, forma)
    r = solver(p, caras(dim), lambda *xyz: inicial, materiales=DosMateriales(M0, M1, ids))
    np.testing.assert_allclose(r.energia_relativa_J, r.energia_relativa_J[0], rtol=4e-15)
    assert r.temperatura_C[-1].min() >= inicial.min()-1e-12
    assert r.temperatura_C[-1].max() <= inicial.max()+1e-12
    assert np.ptp(r.temperatura_C[-1]) < np.ptp(inicial)


@pytest.mark.parametrize('dim', [2, 3])
def test_datos_copiados_y_tiempo_cero(dim):
    p, solver = caso(dim, tiempo_final_s=0)
    m = bloques(p)
    r = solver(p, caras(dim), 20, materiales=m)
    m.ids[:] = 0
    assert (r.materiales.ids == 1).any()
    np.testing.assert_array_equal(r.temperatura_C, 20)
    np.testing.assert_allclose(r.materiales.alpha_m2_s, .5)


@pytest.mark.parametrize('campo,valor', [('conductividad_W_mK', 0), ('densidad_kg_m3', -1),
                                       ('calor_especifico_J_kgK', float('inf')),
                                       ('conductividad_W_mK', True)])
def test_validacion_propiedades(campo, valor):
    entrada = asdict(M0)
    entrada[campo] = valor
    with pytest.raises(ValueError):
        MaterialTermico(**entrada)


@pytest.mark.parametrize('dim', [2, 3])
def test_validacion_mapa_y_plano(dim):
    p, solver = caso(dim)
    forma = (p.celdas_y, p.celdas_x) if dim == 2 else p.forma_zyx
    for ids in (np.zeros((2,)), np.full(forma, 2), np.zeros(forma, dtype=float), np.zeros(forma, dtype=bool)):
        with pytest.raises(ValueError):
            solver(p, caras(dim), materiales=DosMateriales(M0, M1, ids))
    for posicion in (0., 1., .51):
        with pytest.raises(ValueError, match='interfaz'):
            materiales_desde_config(dict(eje='x', interfaz_m=posicion, materiales=[asdict(M0), asdict(M1)]), p)
    with pytest.raises(ValueError):
        solver(p, caras(dim), materiales='dos')
