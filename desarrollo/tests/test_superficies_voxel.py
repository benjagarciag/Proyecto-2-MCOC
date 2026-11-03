"""Conteos/áreas independientes, orientación y contactos geométricos 3D."""
from dataclasses import replace
from hashlib import sha256
from pathlib import Path

import numpy as np
import pytest

from mcplan.bim import extraer_fundacion_ifc
from mcplan.voxel import crear_grilla,Voxelizacion,voxelizar_fundacion
from mcplan.vertidas_voxel import AsignacionVertidas,InformeAsignacion,asignar_vertidas
from mcplan.superficies_voxel import clasificar_caras,diagnosticar_contactos

IFC = Path(__file__).resolve().parents[2]/'desarrollo/fundacion/fundacion.ifc'


def asignacion(ids,pasos=(1.,1.,1.),origen=(0.,0.,0.)):
    ids = np.asarray(ids)
    g = crear_grilla(origen,np.array(origen)+np.array(ids.shape[::-1])*pasos,pasos)
    ocupacion = ids>0
    r = Voxelizacion(g,ocupacion,np.zeros_like(ocupacion),1e-7,'sintetico',float(ocupacion.sum()*g.volumen_celda_m3))
    return AsignacionVertidas(r,ids,InformeAsignacion(0,0,0,0,()))


def test_celda_aislada_seis_caras_y_areas_anisotropas():
    s = clasificar_caras(asignacion([[[1]]],pasos=(2,3,4)))
    assert s.exteriores.cantidad == 6
    assert s.internas.cantidad == s.interfaces.cantidad == 0
    assert s.exteriores.area_total_m2 == 52
    np.testing.assert_array_equal(s.exteriores.id_b,0)
    assert s.exteriores.vecino_fuera_dominio.all()
    for normal,area in zip(s.exteriores.normal_xyz,s.exteriores.area_m2):
        assert area == [12,8,6][np.argmax(abs(normal))]
    assert len(np.unique(s.exteriores.normal_xyz,axis=0)) == 6


@pytest.mark.parametrize('diferentes',[False,True])
def test_dos_celdas_misma_o_distinta_vertida(diferentes):
    s = clasificar_caras(asignacion([[[1,2 if diferentes else 1]]],pasos=(2,3,4)))
    assert s.exteriores.cantidad == 10 and s.exteriores.area_total_m2 == 80
    assert s.internas.cantidad == (0 if diferentes else 1)
    assert s.interfaces.cantidad == (1 if diferentes else 0)
    contacto = s.interfaces if diferentes else s.internas
    assert contacto.area_total_m2 == 12
    np.testing.assert_array_equal(contacto.normal_xyz,[[1,0,0]])
    assert not contacto.vecino_fuera_dominio.any()


@pytest.mark.parametrize('eje',[0,1,2])
def test_contacto_unico_por_eje_y_normal_no_depende_del_id(eje):
    forma = [1,1,1]
    forma[2-eje] = 2
    ids = np.array([5,2]).reshape(forma)
    pasos = np.array([.2,.3,.4])
    s = clasificar_caras(asignacion(ids,pasos))
    assert s.interfaces.cantidad == 1
    normal = np.zeros(3,dtype=int);normal[eje]=1
    np.testing.assert_array_equal(s.interfaces.normal_xyz,[normal])
    assert s.interfaces.id_a[0] == 5 and s.interfaces.id_b[0] == 2
    c = s.contactos_por_par[0]
    assert c.par == (2,5) and c.cantidad_caras == 1
    assert c.area_m2 == pytest.approx(np.prod(pasos)/pasos[eje])


def test_caja_solida_con_area_analitica_y_balance_de_incidencias():
    s = clasificar_caras(asignacion(np.ones((4,2,3),dtype=int),pasos=(.5,1.5,.25)))
    assert s.exteriores.cantidad == 52
    assert s.internas.cantidad == 46
    assert s.interfaces.cantidad == 0
    assert s.exteriores.area_total_m2 == pytest.approx(2*(1.5*3+1.5*1+3*1))
    assert s.internas.area_total_m2 == pytest.approx(21)
    assert 6*24 == 52+2*46


@pytest.mark.parametrize('mixto',[False,True])
def test_escalon_con_celda_vacia_no_es_solo_bbox(mixto):
    ids = np.array([[[1,1],[2 if mixto else 1,0]]])
    s = clasificar_caras(asignacion(ids))
    assert s.exteriores.cantidad == 14 and s.exteriores.area_total_m2 == 14
    assert s.internas.cantidad == (1 if mixto else 2)
    assert s.interfaces.cantidad == (1 if mixto else 0)
    assert 6*3 == s.exteriores.cantidad+2*(s.internas.cantidad+s.interfaces.cantidad)


def test_cavidad_interior_es_hormigon_vacio_y_no_fuera_de_dominio():
    ids = np.ones((3,3,3),dtype=int)
    ids[1,1,1] = 0
    s = clasificar_caras(asignacion(ids))
    assert s.exteriores.cantidad == 60  # 54 caras de caja + seis de cavidad.
    assert s.internas.cantidad == 48
    assert np.count_nonzero(~s.exteriores.vecino_fuera_dominio) == 6
    np.testing.assert_array_equal(s.exteriores.celda_b_zyx[~s.exteriores.vecino_fuera_dominio],np.tile([1,1,1],(6,1)))


def test_no_hay_contacto_periodico_entre_extremos():
    s = clasificar_caras(asignacion([[[1,0,2]]]))
    assert s.exteriores.cantidad == 12
    assert not s.interfaces.cantidad and not s.internas.cantidad


def test_cuadrilateros_orientados_areas_y_coordenadas_trasladadas():
    a = asignacion([[[1,2]]],pasos=(2,3,4),origen=(-10,20,50))
    s = clasificar_caras(a)
    for caras in (s.exteriores,s.interfaces):
        vertices = caras.vertices_m(a.voxelizacion.grilla)
        cruz = np.cross(vertices[:,1]-vertices[:,0],vertices[:,2]-vertices[:,0])
        np.testing.assert_allclose(np.linalg.norm(cruz,axis=1),caras.area_m2)
        np.testing.assert_allclose(cruz,caras.normal_xyz*caras.area_m2[:,None])
        np.testing.assert_allclose(vertices.mean(axis=1),caras.centros_m(a.voxelizacion.grilla))
    np.testing.assert_allclose(s.interfaces.centros_m(a.voxelizacion.grilla),[[-8,21.5,52]])
    # Área vectorial exterior de la unión cerrada debe anularse.
    np.testing.assert_allclose((s.exteriores.normal_xyz*s.exteriores.area_m2[:,None]).sum(axis=0),0)


@pytest.fixture(scope='module')
def estudio():
    m = extraer_fundacion_ifc(IFC)
    salida = {}
    for h in (1.,.5,.25):
        a = asignar_vertidas(m,voxelizar_fundacion(m,(h,)*3))
        salida[h] = clasificar_caras(a)
    return salida


@pytest.mark.parametrize('h',[1.,.5,.25])
def test_fundacion_real_conteos_areas_y_contactos_sin_duplicacion(estudio,h):
    s = estudio[h]
    esperado = {1.:(728,1100,336),.5:(3040,11200,2700),.25:(11976,104732,10888)}[h]
    assert tuple(c.cantidad for c in (s.exteriores,s.internas,s.interfaces)) == esperado
    for caras in (s.exteriores,s.internas,s.interfaces):
        assert caras.area_total_m2 == pytest.approx(caras.cantidad*h*h)
    for caras in (s.internas,s.interfaces):
        claves = np.column_stack([caras.celda_a_zyx,caras.celda_b_zyx])
        assert len(np.unique(claves,axis=0)) == len(claves)
        assert (caras.normal_xyz >= 0).all()
        assert (caras.id_b > 0).all()
    assert (s.internas.id_a == s.internas.id_b).all()
    assert (s.interfaces.id_a != s.interfaces.id_b).all()
    assert sum(c.cantidad_caras for c in s.contactos_por_par) == s.interfaces.cantidad
    assert sum(c.area_m2 for c in s.contactos_por_par) == pytest.approx(s.interfaces.area_total_m2)
    assert sum(n for n,area in s.exterior_por_direccion.values()) == s.exteriores.cantidad
    np.testing.assert_allclose((s.exteriores.normal_xyz*s.exteriores.area_m2[:,None]).sum(axis=0),0)


def test_interfaces_perdidas_y_contacto_artificial_por_capa_no_resuelta(estudio):
    esperados = [(1,2),(2,3),(3,4),(4,5)]
    d = diagnosticar_contactos(estudio[1.],[1,2,3,4,5],esperados)
    assert d.ids_sin_voxeles == (2,)
    assert d.contactos_esperados_ausentes == ((1,2),(2,3))
    assert d.contactos_no_esperados == ((1,3),)
    for h in (.5,.25):
        d = diagnosticar_contactos(estudio[h],[1,2,3,4,5],esperados)
        assert d.ids_sin_voxeles == d.contactos_esperados_ausentes == d.contactos_no_esperados == ()


def test_areas_por_par_de_fundacion(estudio):
    assert {c.par:c.area_m2 for c in estudio[.5].contactos_por_par} == {(1,2):269.,(2,3):244.,(3,4):123.,(4,5):39.}
    assert {c.par:c.area_m2 for c in estudio[.25].contactos_por_par} == {(1,2):266.25,(2,3):266.25,(3,4):109.5,(4,5):38.5}


def test_conserva_ids_ocupacion_e_ifc(estudio):
    antes = IFC.read_bytes()
    a = estudio[.5].asignacion
    ids,ocupacion = a.vertida_id.copy(),a.voxelizacion.ocupacion.copy()
    s = clasificar_caras(a)
    assert s.asignacion is a
    np.testing.assert_array_equal(a.vertida_id,ids)
    np.testing.assert_array_equal(a.voxelizacion.ocupacion,ocupacion)
    assert sha256(IFC.read_bytes()).hexdigest() == sha256(antes).hexdigest()
    assert not s.exteriores.normal_xyz.flags.writeable


@pytest.mark.parametrize('defecto',['dtype','id_negativo','id_grande','ocupacion'])
def test_rechaza_datos_incompatibles(defecto):
    a = asignacion([[[1]]])
    if defecto=='dtype':
        a = replace(a,vertida_id=a.vertida_id.astype(float))
    elif defecto=='id_negativo':
        a = replace(a,vertida_id=np.array([[[-1]]]))
    elif defecto=='id_grande':
        a = replace(a,vertida_id=np.array([[[6]]]))
    else:
        a = replace(a,vertida_id=np.zeros((1,1,1),dtype=int))
    with pytest.raises(ValueError):
        clasificar_caras(a)


def test_grilla_vacia_no_inventa_caras():
    s = clasificar_caras(asignacion(np.zeros((2,2,2),dtype=int)))
    assert s.exteriores.cantidad == s.internas.cantidad == s.interfaces.cantidad == 0
    assert s.interfaces.vertices_m(s.asignacion.voxelizacion.grilla).shape == (0,4,3)
    assert s.contactos_por_par == ()


def test_referencia_de_contactos_invalida():
    s = clasificar_caras(asignacion([[[1]]]))
    with pytest.raises(ValueError):
        diagnosticar_contactos(s,[1,2],[(1,1)])
    with pytest.raises(ValueError):
        diagnosticar_contactos(s,[1,2],[(1,3)])
