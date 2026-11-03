"""Ocupación 3D: sólidos analíticos, frontera, juntas y fundación real."""
from dataclasses import replace
from hashlib import sha256
from pathlib import Path

import numpy as np
import pytest

from mcplan.bim import FundacionIFC, VertidaIFC, analizar_malla, extraer_fundacion_ifc
from mcplan.voxel import (FUERA, FRONTERA, DENTRO, crear_grilla,
                         clasificar_puntos, voxelizar_fundacion)

IFC = Path(__file__).resolve().parents[2]/'desarrollo/fundacion/fundacion.ifc'


def caja():
    v = np.array([[0,0,0],[1,0,0],[1,1,0],[0,1,0],
                  [0,0,1],[1,0,1],[1,1,1],[0,1,1]], dtype=float)
    f = np.array([[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],
                  [1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]])
    return v, f


def tetraedro():
    return (np.array([[0.,0,0],[1,0,0],[0,1,0],[0,0,1]]),
            np.array([[0,2,1],[0,1,3],[0,3,2],[1,2,3]]))


def prisma_concavo():
    poligono = np.array([[0,0],[2,0],[2,1],[1,1],[1,2],[0,2]], dtype=float)
    v = np.vstack([np.column_stack([poligono, np.zeros(6)]),
                   np.column_stack([poligono, np.ones(6)])])
    tapa = np.array([[0,1,3],[1,2,3],[0,3,5],[3,4,5]])
    f = [*tapa[:, ::-1], *(tapa+6)]
    for a in range(6):
        b = (a+1)%6
        f.extend([[a,b,b+6],[a,b+6,a+6]])
    return v, np.array(f)


def modelo(*mallas):
    vertidas = []
    for i, (v, f) in enumerate(mallas, 1):
        calidad = analizar_malla(v, f)
        vertidas.append(VertidaIFC(i, f'sintetico-{i}', f'Vertida_{i:02d}', 'IfcFooting', {}, (),
                                   v, f, v.min(axis=0), v.max(axis=0), calidad))
    return FundacionIFC(Path('sintetico.ifc'), 'sintetico', 'IFC4', 'METRE', 1., 'XYZ [m]', tuple(vertidas), ())


@pytest.fixture(scope='module')
def real():
    return extraer_fundacion_ifc(IFC)


@pytest.fixture(scope='module')
def voxel_real(real):
    return voxelizar_fundacion(real)


@pytest.mark.parametrize('punto,esperado', [
    ([.5,.5,.5],DENTRO), ([1.1,.5,.5],FUERA), ([-.1,.5,.5],FUERA),
    ([.5,.5,0],FRONTERA), ([1,.5,.5],FRONTERA), ([0,0,.5],FRONTERA),
    ([0,0,0],FRONTERA), ([1,1,1],FRONTERA)])
def test_clasificacion_caja_interior_exterior_caras_aristas_vertices(punto, esperado):
    v, f = caja()
    assert clasificar_puntos([punto], v, f)[0] == esperado


def test_tolerancia_por_distancia_euclidea_no_caja_inflada():
    v, f = caja()
    tol = 1e-7
    puntos = [[.5,.5,-.5*tol], [.5,.5,-2*tol], [.5,.5,.5*tol],
              [-.8*tol,-.8*tol,-.8*tol], [-.5*tol,-.5*tol,0]]
    np.testing.assert_array_equal(clasificar_puntos(puntos, v, f, tolerancia_m=tol),
                                  [FRONTERA, FUERA, FRONTERA, FUERA, FRONTERA])


def test_superficie_inclinada_descarta_exterior_dentro_de_bbox():
    v, f = tetraedro()
    p = [[.1,.1,.1],[.4,.4,.4],[.2,.3,.5],[.7,.1,.1]]
    np.testing.assert_array_equal(clasificar_puntos(p, v, f), [DENTRO,FUERA,FRONTERA,DENTRO])


def test_superficie_concava_no_se_sustituye_por_caja_o_envolvente_convexa():
    v, f = prisma_concavo()
    assert analizar_malla(v, f).volumen_m3 == pytest.approx(3)
    p = [[.5,1.5,.5],[1.5,.5,.5],[1.5,1.5,.5],[1,1.5,.5]]
    np.testing.assert_array_equal(clasificar_puntos(p, v, f), [DENTRO,DENTRO,FUERA,FRONTERA])
    r = voxelizar_fundacion(modelo((v,f)), (.5,.5,.5))
    assert r.numero_ocupados == 24 and r.grilla.numero_celdas == 32
    assert r.volumen_ocupado_m3 == 3


@pytest.mark.parametrize('pasos', [(.5,.25,.2),(.25,.5,.1)])
def test_grilla_anisotropa_centros_origen_dimensiones_y_volumen(pasos):
    origen = np.array([-3.,2.,10.])
    grilla = crear_grilla(origen, origen+[1,1,1], pasos)
    assert grilla.forma_xyz == tuple(int(round(1/d)) for d in pasos)
    np.testing.assert_array_equal(grilla.origen_m, origen)
    np.testing.assert_allclose(grilla.dimensiones_m, 1)
    for centros, o, d, n in zip(grilla.centros_xyz_m, origen, pasos, grilla.forma_xyz):
        np.testing.assert_allclose(centros, o+(np.arange(n)+.5)*d)
    assert grilla.numero_celdas*grilla.volumen_celda_m3 == pytest.approx(1)


def test_ultima_celda_entera_cubre_bbox_sin_ajustar_paso():
    g = crear_grilla([0,0,0], [1.01,1,1], [.5,.5,.5])
    assert g.forma_xyz == (3,2,2)
    np.testing.assert_allclose(g.dimensiones_m, [1.5,1,1])
    np.testing.assert_allclose(g.centros_xyz_m[0], [.25,.75,1.25])


def test_volumen_caja_conocido_y_refinamiento():
    m = modelo(caja())
    for d in (.5,.25):
        r = voxelizar_fundacion(m, (d,d,d))
        assert r.ocupacion.all()
        assert r.volumen_ocupado_m3 == 1
        assert r.numero_ocupados == round(1/d)**3


def test_refinamiento_sintetico_inclinado_mejora_volumen():
    m = modelo(tetraedro())
    errores = []
    for n in (4,8):
        r = voxelizar_fundacion(m, (1/n,)*3)
        centros = r.grilla.centros_xyz_m
        Z,Y,X = np.meshgrid(*centros[::-1], indexing='ij')
        np.testing.assert_array_equal(r.ocupacion, X+Y+Z <= 1)
        errores.append(abs(r.volumen_ocupado_m3-1/6))
    assert errores[1] < errores[0]


def test_traslacion_preserva_ocupacion_y_coordenadas_fisicas():
    v, f = tetraedro()
    desplazamiento = np.array([1000.,-2000.,50.])
    a = voxelizar_fundacion(modelo((v,f)), (.25,)*3)
    b = voxelizar_fundacion(modelo((v+desplazamiento,f)), (.25,)*3)
    np.testing.assert_array_equal(a.ocupacion,b.ocupacion)
    np.testing.assert_array_equal(b.grilla.origen_m,a.grilla.origen_m+desplazamiento)
    for i in range(3):
        np.testing.assert_allclose(b.grilla.centros_xyz_m[i],a.grilla.centros_xyz_m[i]+desplazamiento[i])


def test_orientacion_global_orden_triangulos_y_lotes_no_cambian_clasificacion():
    v, f = tetraedro()
    p = np.random.default_rng(42).uniform(-.1,1.1,(101,3))
    referencia = clasificar_puntos(p,v,f,tamano_lote=7)
    np.testing.assert_array_equal(referencia, clasificar_puntos(p,v,f[::-1,::-1],tamano_lote=64))
    np.testing.assert_array_equal(referencia >= FRONTERA, ((p >= 0).all(axis=1) & (p.sum(axis=1) <= 1)))


@pytest.mark.parametrize('delta', [0.,-5e-8,5e-8])
def test_union_juntas_cercanas_y_orden_de_vertidas(delta):
    v,f = caja()
    m = modelo((v,f),(v+[1+delta,0,0],f))
    # Con origen -.5, x=1 es centro de una celda, justo en la junta.
    r = voxelizar_fundacion(m,(1,1,1),origen_m=[-.5,0,0])
    s = voxelizar_fundacion(replace(m,vertidas=m.vertidas[::-1]),(1,1,1),origen_m=[-.5,0,0])
    np.testing.assert_array_equal(r.ocupacion,s.ocupacion)
    assert r.ocupacion[0,0,1] and r.centros_sobre_malla[0,0,1]


def test_solidos_superpuestos_se_ocupan_una_sola_vez():
    v,f = caja()
    r = voxelizar_fundacion(modelo((v,f),(v,f)),(.5,)*3)
    assert r.numero_ocupados == 8 and r.volumen_ocupado_m3 == 1
    assert r.volumen_referencia_mallas_m3 == 2  # Suma de cuerpos, no unión booleana.


def test_fundacion_real_forma_coordenadas_mascara_y_volumen(real,voxel_real):
    r = voxel_real
    assert r.grilla.forma_xyz == (37,37,9)
    np.testing.assert_array_equal(r.grilla.origen_m,real.bbox_min_m)
    assert np.all(r.grilla.limites_superiores_m >= real.bbox_max_m)
    assert r.ocupacion.shape == r.grilla.forma_zyx and r.ocupacion.dtype == bool
    assert r.numero_ocupados == 5140
    assert r.grilla.numero_celdas == 12321
    assert r.volumen_ocupado_m3 == 642.5
    assert abs(r.diferencia_volumen_m3)/r.volumen_referencia_mallas_m3 < .02
    x,y,z = r.grilla.centros_xyz_m
    indice = lambda px,py,pz: (np.argmin(abs(z-pz)),np.argmin(abs(y-py)),np.argmin(abs(x-px)))
    assert r.ocupacion[indice(.25,.25,.25)]
    assert r.ocupacion[indice(.25,.25,3.75)]
    assert not r.ocupacion[indice(8.75,8.75,.25)]  # Esquina vacía dentro del bbox.
    assert not r.ocupacion[..., -1].any()


def test_ifc_y_mallas_no_se_modifican(real):
    antes = IFC.read_bytes()
    vertices = [v.vertices_m.copy() for v in real.vertidas]
    r = voxelizar_fundacion(real)
    assert IFC.read_bytes() == antes
    assert r.sha256_ifc == sha256(antes).hexdigest()
    for v, referencia in zip(real.vertidas,vertices):
        np.testing.assert_array_equal(v.vertices_m,referencia)


@pytest.mark.parametrize('pasos', [(0,1,1),(-1,1,1),(1,2),(1,np.nan,1),(True,False,True)])
def test_rechaza_resolucion_invalida(pasos):
    with pytest.raises(ValueError):
        crear_grilla([0,0,0],[1,1,1],pasos)


@pytest.mark.parametrize('tol', [0,-1,np.nan,True,'texto'])
def test_rechaza_tolerancia_invalida(tol):
    with pytest.raises(ValueError):
        clasificar_puntos([[.5,.5,.5]],*caja(),tolerancia_m=tol)


def test_limites_entradas_y_proteccion_memoria():
    with pytest.raises(ValueError):
        crear_grilla([0,0,0],[1,1,1],(.001,)*3)
    with pytest.raises(ValueError):
        crear_grilla([0,0,0],[1,1,1],(.5,)*3,origen_m=[.1,0,0])
    with pytest.raises(ValueError):
        clasificar_puntos([[np.nan,0,0]],*caja())
    with pytest.raises(ValueError):
        clasificar_puntos([[0,0,0]],*caja(),tamano_lote=False)
    with pytest.raises(ValueError):
        voxelizar_fundacion(modelo(caja()), tolerancia_m=.1)


def test_lista_de_puntos_vacia():
    assert clasificar_puntos(np.empty((0,3)),*caja()).shape == (0,)
