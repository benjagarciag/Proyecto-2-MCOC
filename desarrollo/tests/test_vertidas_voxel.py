"""Identidad única, conflictos explícitos, ocupación y volúmenes por vertida."""
from dataclasses import replace
from pathlib import Path
from hashlib import sha256

import numpy as np
import pytest

from mcplan.bim import extraer_fundacion_ifc
from mcplan.voxel import voxelizar_fundacion
from mcplan.vertidas_voxel import asignar_vertidas, comparar_volumenes, ConflictoGeometrico
from test_voxel import caja, modelo, tetraedro

IFC = Path(__file__).resolve().parents[2]/'desarrollo/fundacion/fundacion.ifc'


@pytest.fixture(scope='module')
def real():
    return extraer_fundacion_ifc(IFC)


@pytest.fixture(scope='module')
def estudio(real):
    resultados = {}
    for h in (1., .5, .25):
        voxel = voxelizar_fundacion(real, (h,)*3)
        asignacion = asignar_vertidas(real, voxel)
        resultados[h] = (voxel, asignacion, comparar_volumenes(real, asignacion))
    return resultados


def test_dos_cajas_ids_y_volumen_analitico():
    v, f = caja()
    m = modelo((v,f),(v+[1,0,0],f))
    r = voxelizar_fundacion(m, (.5,)*3)
    a = asignar_vertidas(m,r)
    x = r.grilla.centros_xyz_m[0]
    esperado = np.broadcast_to(np.where(x < 1,1,2), r.ocupacion.shape)
    np.testing.assert_array_equal(a.vertida_id,esperado)
    filas = comparar_volumenes(m,a)
    assert [f.numero_voxeles for f in filas] == [8,8]
    assert [f.volumen_voxelizado_m3 for f in filas] == [1,1]
    assert [f.error_relativo_pct for f in filas] == [0,0]


@pytest.mark.parametrize('eje', [0,1,2])
def test_frontera_por_coordenadas_crecientes_en_cada_eje(eje):
    v, f = caja()
    traslado, origen = np.zeros(3), np.zeros(3)
    traslado[eje], origen[eje] = 1., -.5
    m = modelo((v,f),(v+traslado,f))
    r = voxelizar_fundacion(m,(1,)*3,origen_m=origen)
    a = asignar_vertidas(m,r)
    indice = [0,0,0]
    indice[2-eje] = 1
    assert a.vertida_id[tuple(indice)] == 2
    assert a.informe.fronteras_compartidas == 1
    assert a.informe.registros[0].id_asignado == 2
    assert 'sonda' in a.informe.registros[0].criterio


@pytest.mark.parametrize('delta', [-5e-8,0.,5e-8])
def test_juntas_dentro_de_tolerancia_y_orden_no_cambian_id(delta):
    v,f = caja()
    m = modelo((v,f),(v+[1+delta,0,0],f))
    r = voxelizar_fundacion(m,(1,)*3,origen_m=[-.5,0,0])
    a = asignar_vertidas(m,r)
    b = asignar_vertidas(replace(m,vertidas=m.vertidas[::-1]),r)
    np.testing.assert_array_equal(a.vertida_id,b.vertida_id)
    assert a.vertida_id[0,0,1] == 2
    assert a.informe.reclamaciones_multiples == 1
    assert a.informe.interiores_multiples == 0


def test_desempate_no_elige_id_mayor_ni_primero():
    v,f = caja()
    m = modelo((v,f),(v+[1,0,0],f))
    m = replace(m,vertidas=(replace(m.vertidas[0],vertida_id=2),replace(m.vertidas[1],vertida_id=1)))
    r = voxelizar_fundacion(m,(1,)*3,origen_m=[-.5,0,0])
    assert asignar_vertidas(m,r).vertida_id[0,0,1] == 1  # Dueño geométrico derecho.


def test_junta_en_aristas_exteriores_tambien_se_resuelve():
    v,f = caja()
    m = modelo((v,f),(v+[1,0,0],f))
    r = voxelizar_fundacion(m,(1,)*3,origen_m=[-.5,-.5,-.5])
    a = asignar_vertidas(m,r)
    # y,z=0 o 1 son superficies exteriores; el punto x=1 sigue en la junta.
    np.testing.assert_array_equal(a.vertida_id[:2,:2,1],2)
    assert a.informe.fronteras_compartidas == 4


def test_interior_unico_prevalece_sobre_banda_de_frontera_y_se_registra():
    v,f = caja()
    m = modelo((v,f),(v+[.5,0,0],f))
    r = voxelizar_fundacion(m,(.5,)*3,origen_m=[-.25,0,0])
    a = asignar_vertidas(m,r)
    # Los centros x=.5 y x=1 solo son interiores inequívocos a una pieza.
    assert np.all(a.vertida_id[...,1] == 1)
    assert np.all(a.vertida_id[...,2] == 2)
    assert a.informe.interior_y_frontera > 0
    assert any('Interior inequívoco' in d.criterio for d in a.informe.registros)


def test_solape_interior_se_detecta_antes_de_asignar():
    v,f = caja()
    m = modelo((v,f),(v,f))
    r = voxelizar_fundacion(m,(.5,)*3)
    antes = r.ocupacion.copy()
    with pytest.raises(ConflictoGeometrico) as error:
        asignar_vertidas(m,r)
    assert error.value.informe.interiores_multiples == 8
    assert error.value.informe.reclamaciones_multiples == 8
    assert all(d.id_asignado is None for d in error.value.informe.registros)
    np.testing.assert_array_equal(r.ocupacion,antes)


def test_coincidencia_de_superficies_sin_dueño_unico_se_rechaza():
    v,f = caja()
    m = modelo((v,f),(v,f))
    r = voxelizar_fundacion(m,(1,)*3,origen_m=[-.5,-.5,-.5])
    with pytest.raises(ConflictoGeometrico) as error:
        asignar_vertidas(m,r)
    assert 'Sonda dentro de varios' in error.value.informe.registros[-1].criterio


def test_frontera_inclinada_entre_dos_tetraedros():
    v,f = tetraedro()
    otro = v.copy()
    otro[0] = [1,1,1]
    m = modelo((v,f),(otro,f))
    r = voxelizar_fundacion(m,(1,)*3,origen_m=[-1/6]*3)
    a = asignar_vertidas(m,r)
    # El centro (1/3,1/3,1/3) está en x+y+z=1. Hacia +Z/Y/X entra al segundo.
    assert a.vertida_id[0,0,0] == 2
    assert a.informe.fronteras_compartidas == 1


def test_volumen_con_voxeles_anisotropos():
    v,f = caja()
    m = modelo((v,f),(v+[1,0,0],f))
    r = voxelizar_fundacion(m,(.25,.5,.2))
    filas = comparar_volumenes(m,asignar_vertidas(m,r))
    assert [f.numero_voxeles for f in filas] == [40,40]
    np.testing.assert_allclose([f.volumen_voxelizado_m3 for f in filas],[1,1])


@pytest.mark.parametrize('h', [1.,.5,.25])
def test_fundacion_ocupacion_validez_ids_y_balance_por_vertida(estudio,h):
    r,a,filas = estudio[h]
    np.testing.assert_array_equal(a.vertida_id > 0,r.ocupacion)
    assert set(np.unique(a.vertida_id)).issubset({0,1,2,3,4,5})
    assert sum(f.numero_voxeles for f in filas) == r.numero_ocupados
    assert sum(f.volumen_voxelizado_m3 for f in filas) == pytest.approx(r.volumen_ocupado_m3)
    assert a.informe.reclamaciones_multiples == 0
    for f in filas:
        assert f.volumen_voxelizado_m3 == f.numero_voxeles*h**3
        assert f.diferencia_absoluta_m3 == abs(f.volumen_voxelizado_m3-f.volumen_ifc_m3)
        assert f.error_relativo_pct == pytest.approx(100*f.diferencia_absoluta_m3/f.volumen_ifc_m3)


def test_resoluciones_muestran_perdida_de_capa_y_errores_no_monotonos(estudio):
    assert [f.numero_voxeles for f in estudio[.5][2]] == [1076,1076,1696,980,312]
    assert estudio[1.][2][1].numero_voxeles == 0  # Capa fina sin centros, no IDs perdidos.
    assert estudio[1.][2][1].error_relativo_pct == 100
    assert estudio[.25][2][0].error_relativo_pct > estudio[.5][2][0].error_relativo_pct
    assert estudio[.25][2][2].error_relativo_pct > estudio[.5][2][2].error_relativo_pct
    assert estudio[.25][0].volumen_ocupado_m3 == 633.375


def test_orden_real_independiente_y_mascaras_sin_modificar(real,estudio):
    r,a,_ = estudio[.5]
    b = asignar_vertidas(replace(real,vertidas=real.vertidas[::-1]),r)
    np.testing.assert_array_equal(a.vertida_id,b.vertida_id)
    assert a.voxelizacion is r
    assert not a.vertida_id.flags.writeable


def test_lectura_y_asignacion_no_alteran_ifc(real,estudio):
    antes = IFC.read_bytes()
    r = estudio[.5][0]
    asignar_vertidas(real,r)
    assert IFC.read_bytes() == antes
    assert sha256(antes).hexdigest() == real.sha256_ifc


def test_datos_incompatibles_o_ids_duplicados_se_rechazan():
    v,f = caja()
    m = modelo((v,f),(v+[1,0,0],f))
    r = voxelizar_fundacion(m,(.5,)*3)
    with pytest.raises(ValueError,match='otra versión'):
        asignar_vertidas(m,replace(r,sha256_ifc='otro'))
    with pytest.raises(ValueError,match='IDs únicos'):
        asignar_vertidas(replace(m,vertidas=(m.vertidas[0],m.vertidas[0])),r)
    alterada = r.ocupacion.copy()
    alterada[0,0,0] = False
    with pytest.raises(ValueError,match='no reproduce'):
        asignar_vertidas(m,replace(r,ocupacion=alterada))
