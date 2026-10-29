"""Comprobaciones para ejecutar personalmente al estudiar la barra 3D."""
from dataclasses import replace
import numpy as np
import pytest

from mcplan.difusion_3d import Parametros3D
from mcplan.bordes_termicos import Neumann, Robin
from mcplan.fuente_temporal_2d import PulsoTermico
from mcplan.fuente_temporal_3d import resolver_fuente_temporal_3d
from mcplan.difusion_bordes import resolver_3d_bordes
from mcplan.visualizador_termico import predeterminados, calcular, verificar


def parametros():
    return Parametros3D(longitud_x_m=3,longitud_y_m=3,longitud_z_m=6,
                        celdas_x=3,celdas_y=3,celdas_z=6,tiempo_final_s=.1,paso_tiempo_s=.1,
                        conductividad_W_mK=2,densidad_kg_m3=3,calor_especifico_J_kgK=4)


def caras():
    return {f'{e}_{lado}':Neumann(0) for e in 'xyz' for lado in ('min','max')}


@pytest.mark.parametrize('beta',[-1.,0.,.1])
def test_beta_exterior_un_paso_manual_y_balance(beta):
    p = parametros()
    r = resolver_fuente_temporal_3d(p,caras(),PulsoTermico(0,1),temperatura_inicial_C=30,
                                   beta_exterior=beta,n_guardados=2)
    # Celda de esquina: tres caras de 1 m², distancia centro-cara 0,5 m.
    potencia_cara = p.conductividad_W_mK*beta*(30-20)/(1-beta*.5)
    esperado = 30+p.paso_tiempo_s*3*potencia_cara/p.capacidad_voxel_J_K
    assert r.temperatura_C[-1,0,0,0] == pytest.approx(esperado)
    delta = r.energia_relativa_J[-1]-r.energia_relativa_J[0]
    assert delta == pytest.approx(r.calor_exterior_J[-1],abs=1e-9)
    if beta:
        assert np.sign(delta) == np.sign(beta)


def test_beta_negativo_equivale_robin_pasivo():
    p = replace(parametros(),tiempo_final_s=1)
    beta = -1.
    r = resolver_fuente_temporal_3d(p,caras(),PulsoTermico(0,1),temperatura_inicial_C=30,
                                   beta_exterior=beta,n_guardados=20)
    b = {cara:Robin(-p.conductividad_W_mK*beta,20) for cara in caras()}
    referencia = resolver_3d_bordes(p,b,30,n_guardados=20)
    np.testing.assert_allclose(r.temperatura_C,referencia.temperatura_C,atol=1e-12)


def test_energia_fuente_uniforme_temporal_adiabatica_exacta():
    p = replace(parametros(),tiempo_final_s=2)
    pulso = PulsoTermico(100,1)
    r = resolver_fuente_temporal_3d(p,caras(),pulso)
    exacta = 20+pulso.acumulada_J_m3(r.tiempos_s)/(p.densidad_kg_m3*p.calor_especifico_J_kgK)
    np.testing.assert_allclose(r.temperatura_C, np.broadcast_to(exacta[:,None,None,None],r.temperatura_C.shape),atol=1e-12)
    delta = r.energia_relativa_J-r.energia_relativa_J[0]
    np.testing.assert_allclose(delta,r.calor_generado_J,atol=1e-8)


@pytest.mark.parametrize('caso',['barra_d20','barra_d30','barra_n0','barra_beta'])
def test_barra_movil_y_punto_fuera_de_la_fuente(caso):
    c = predeterminados(caso)
    c.update(nx=6,ny=6,nz=12,tf_s=600,dt_s=100,fuente_x=.5,punto_x=-1.,beta=-1.)
    v = calcular(caso,c)
    assert v.extras['volumen_fuente'] == pytest.approx(1)
    np.testing.assert_array_equal(v.extras['q_punto'],0)
    assert verificar(v)[0]


def test_beta_singular_requiere_refinamiento():
    with pytest.raises(ValueError,match='refinar'):
        resolver_fuente_temporal_3d(parametros(),caras(),PulsoTermico(0,1),beta_exterior=2)
