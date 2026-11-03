"""IFC real de solo lectura y variantes temporales dentro de la copia E07."""
from hashlib import sha256
from pathlib import Path
import subprocess
import sys

import ifcopenshell
import ifcopenshell.guid
import ifcopenshell.util.element
import ifcopenshell.util.unit
import numpy as np
import pytest

from mcplan.bim import extraer_fundacion_ifc, analizar_malla

RAIZ = Path(__file__).resolve().parents[2]
IFC = RAIZ/'desarrollo/fundacion/fundacion.ifc'
# Referencias de auditoría redondeadas a 0.001 m³. Se tolera medio último
# decimal (0.0005 m³), más 1e-8 m³ de margen numérico. No es tolerancia voxel.
VOLUMENES = [147.626, 147.626, 214.224, 88.925, 38.375]
TOL_VOLUMEN_M3 = .00050001
# Las coordenadas IFC proceden de precisión float32 de Blender: desviaciones
# de ~1.7e-6 m en el ancho 18 m. Margen de comparación: 3 micrómetros.
TOL_DIMENSION_M = 3e-6


@pytest.fixture(scope='module')
def fundacion():
    return extraer_fundacion_ifc(IFC)


def test_cinco_objetos_ids_guids_y_orden(fundacion):
    assert [v.vertida_id for v in fundacion.vertidas] == [1, 2, 3, 4, 5]
    assert [v.nombre for v in fundacion.vertidas] == [f'Vertida_{i:02d}' for i in range(1, 6)]
    assert len({v.guid for v in fundacion.vertidas}) == 5
    assert all(v.clase_ifc == 'IfcFooting' for v in fundacion.vertidas)


def test_propiedades_constructivas_sin_inventar_materiales(fundacion):
    assert [v.inicio_h for v in fundacion.vertidas] == [0, 6, 12, 18, 24]
    assert [v.inicio_s for v in fundacion.vertidas] == [0, 21600, 43200, 64800, 86400]
    assert [v.temperatura_colocacion_C for v in fundacion.vertidas] == [19, 18, 18, 18, 18]
    for v in fundacion.vertidas:
        assert v.tipo_hormigon == 'M1'
        assert v.propiedades['Moldaje'] == 'TBD'
        assert v.propiedades['Aislacion'] == 'TBD'
        assert v.propiedades['RetiroMoldaje_h'] == 72
        assert v.materiales_asociados == ()
    assert any('sin asociación IfcMaterial' in aviso for aviso in fundacion.advertencias)


@pytest.mark.parametrize('indice', range(5))
def test_volumen_y_dimensiones_por_vertida(fundacion, indice):
    v = fundacion.vertidas[indice]
    assert v.volumen_m3 == pytest.approx(VOLUMENES[indice], abs=TOL_VOLUMEN_M3, rel=0)
    dimensiones = [(18, 18, .55), (18, 18, .55), (18, 18, 1.1), (12.5, 12.5, 1.1), (7, 7, 1)]
    np.testing.assert_allclose(v.dimensiones_m, dimensiones[indice], atol=TOL_DIMENSION_M, rtol=0)
    assert v.calidad.numero_triangulos == [28, 28, 28, 28, 188][indice]
    assert v.calidad.cerrada and v.calidad.orientacion_consistente
    assert v.calidad.componentes_conexas == 1
    assert v.calidad.area_superficial_m2 > 0
    assert np.isfinite(v.vertices_m).all()
    assert v.triangulos.min() >= 0 and v.triangulos.max() < len(v.vertices_m)


def test_global_unidades_y_coordenadas(fundacion):
    assert fundacion.schema == 'IFC4'
    assert fundacion.unidad_longitud_ifc == 'METRE'
    assert fundacion.escala_longitud_ifc_a_m == 1
    np.testing.assert_allclose(fundacion.bbox_min_m, [-9, -9, 0], atol=TOL_DIMENSION_M, rtol=0)
    np.testing.assert_allclose(fundacion.bbox_max_m, [9, 9, 4.3], atol=TOL_DIMENSION_M, rtol=0)
    assert fundacion.volumen_total_mallas_m3 == pytest.approx(636.775, abs=TOL_VOLUMEN_M3, rel=0)


def test_lectura_no_altera_bytes_y_resultados_independientes():
    antes = IFC.read_bytes()
    a, b = extraer_fundacion_ifc(IFC), extraer_fundacion_ifc(IFC)
    assert IFC.read_bytes() == antes
    assert a.sha256_ifc == sha256(antes).hexdigest()
    np.testing.assert_array_equal(a.vertidas[0].vertices_m, b.vertidas[0].vertices_m)
    assert not np.shares_memory(a.vertidas[0].vertices_m, b.vertidas[0].vertices_m)
    with pytest.raises(ValueError):
        a.vertidas[0].vertices_m[0, 0] = 999


def test_verificador_anterior_delega_y_no_modifica_ifc():
    antes = IFC.read_bytes()
    r = subprocess.run([sys.executable, '-B', str(RAIZ/'desarrollo/fundacion/verificar_ifc.py'), str(IFC)],
                       capture_output=True, text=True, check=True)
    assert 'VERIFICACI' in r.stdout and 'OK:' in r.stdout and '636.775' in r.stdout
    assert IFC.read_bytes() == antes


def guardar_variante(modelo, tmp_path):
    destino = tmp_path/'variante.ifc'
    modelo.write(str(destino))
    return destino


@pytest.mark.parametrize('numero', [4, 6])
def test_rechaza_numero_incorrecto_de_vertidas(tmp_path, numero):
    modelo = ifcopenshell.open(str(IFC))
    if numero == 4:
        modelo.remove(modelo.by_type('IfcFooting')[-1])
    else:
        modelo.create_entity('IfcFooting', GlobalId=ifcopenshell.guid.new(), Name='Extra')
    with pytest.raises(ValueError, match='cinco IfcFooting'):
        extraer_fundacion_ifc(guardar_variante(modelo, tmp_path))


@pytest.mark.parametrize('defecto', ['id_duplicado', 'guid_duplicado', 'nombre', 'propiedad_ausente', 'horario_negativo'])
def test_rechaza_identidad_o_propiedades_invalidas(tmp_path, defecto):
    modelo = ifcopenshell.open(str(IFC))
    primero, segundo = sorted(modelo.by_type('IfcFooting'), key=lambda p: p.Name)[:2]
    pset = ifcopenshell.util.element.get_pset(segundo, 'UANDES_HormigonMasivo')
    propiedades = modelo.by_id(pset['id']).HasProperties
    if defecto == 'id_duplicado':
        next(p for p in propiedades if p.Name == 'VertidaID').NominalValue.wrappedValue = 1
    elif defecto == 'guid_duplicado':
        segundo.GlobalId = primero.GlobalId
    elif defecto == 'nombre':
        segundo.Name = 'Vertida_otra'
    elif defecto == 'propiedad_ausente':
        modelo.by_id(pset['id']).HasProperties = tuple(p for p in propiedades if p.Name != 'Inicio_h')
    else:
        next(p for p in propiedades if p.Name == 'Inicio_h').NominalValue.wrappedValue = -1.
    with pytest.raises(ValueError):
        extraer_fundacion_ifc(guardar_variante(modelo, tmp_path))


def test_lee_material_asociado_cuando_existe(tmp_path):
    modelo = ifcopenshell.open(str(IFC))
    producto = next(p for p in modelo.by_type('IfcFooting') if p.Name == 'Vertida_01')
    material = modelo.create_entity('IfcMaterial', Name='Material_prueba', Category='concrete')
    modelo.create_entity('IfcRelAssociatesMaterial', GlobalId=ifcopenshell.guid.new(),
                         RelatedObjects=[producto], RelatingMaterial=material)
    v = extraer_fundacion_ifc(guardar_variante(modelo, tmp_path)).vertidas[0]
    assert len(v.materiales_asociados) == 1
    assert v.materiales_asociados[0].nombre == 'Material_prueba'
    assert v.materiales_asociados[0].clase_ifc == 'IfcMaterial'
    assert v.materiales_asociados[0].categoria == 'concrete'


def test_unidad_milimetro_no_se_aplica_dos_veces(tmp_path, fundacion):
    modelo = ifcopenshell.open(str(IFC))
    unidad = ifcopenshell.util.unit.get_project_unit(modelo, 'LENGTHUNIT')
    unidad.Prefix = 'MILLI'
    # No se escalan las coordenadas numéricas: esta variante representa un
    # modelo físicamente 1000 veces menor. Solo se escribe la copia temporal.
    r = extraer_fundacion_ifc(guardar_variante(modelo, tmp_path))
    assert r.escala_longitud_ifc_a_m == .001
    np.testing.assert_allclose(r.dimensiones_m, fundacion.dimensiones_m*.001, atol=1e-10)
    assert r.volumen_total_mallas_m3 == pytest.approx(fundacion.volumen_total_mallas_m3*1e-9, rel=1e-8)


def test_placements_globales_aplicados_y_volumen_invariante(tmp_path, fundacion):
    import ifcopenshell.api.geometry
    import ifcopenshell.util.placement
    modelo = ifcopenshell.open(str(IFC))
    producto = next(p for p in modelo.by_type('IfcFooting') if p.Name == 'Vertida_01')
    matriz = ifcopenshell.util.placement.get_local_placement(producto.ObjectPlacement)
    desplazamiento = np.array([100., 200., 50.])
    matriz[:3, 3] += desplazamiento
    ifcopenshell.api.geometry.edit_object_placement(modelo, product=producto, matrix=matriz, is_si=True)
    v = extraer_fundacion_ifc(guardar_variante(modelo, tmp_path)).vertidas[0]
    np.testing.assert_allclose(v.bbox_min_m, fundacion.vertidas[0].bbox_min_m+desplazamiento, atol=1e-9)
    np.testing.assert_allclose(v.bbox_max_m, fundacion.vertidas[0].bbox_max_m+desplazamiento, atol=1e-9)
    assert v.volumen_m3 == pytest.approx(fundacion.vertidas[0].volumen_m3, rel=1e-12)


def tetraedro():
    return (np.array([[0., 0., 0.], [1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]),
            np.array([[0, 2, 1], [0, 1, 3], [0, 3, 2], [1, 2, 3]]))


@pytest.mark.parametrize('escala,traslacion', [(1., 0.), (2., 1e6)])
def test_volumen_analitico_tetraedro_y_traslacion(escala, traslacion):
    v, f = tetraedro()
    resultado = analizar_malla(v*escala+traslacion, f)
    assert resultado.volumen_m3 == pytest.approx(escala**3/6, rel=1e-13)


def test_orientacion_global_invertida_conserva_volumen_absoluto():
    v, f = tetraedro()
    a, b = analizar_malla(v, f), analizar_malla(v, f[:, ::-1])
    assert a.volumen_m3 == b.volumen_m3
    assert a.volumen_firmado_m3 == -b.volumen_firmado_m3


@pytest.mark.parametrize('defecto', ['abierta', 'orientacion', 'duplicada', 'indice', 'nan', 'degenerada', 'desconexa', 'contacto_puntual', 'sin_usar', 'indices_float'])
def test_rechaza_mallas_no_utilizables(fundacion, defecto):
    v, f = tetraedro()
    if defecto == 'abierta':
        v, f = fundacion.vertidas[0].vertices_m, fundacion.vertidas[0].triangulos[:-1]
    elif defecto == 'orientacion':
        f[0] = f[0, ::-1]
    elif defecto == 'duplicada':
        f = np.vstack([f, f[0]])
    elif defecto == 'indice':
        f[0, 0] = 99
    elif defecto == 'nan':
        v[0, 0] = np.nan
    elif defecto == 'degenerada':
        v[3] = v[2]
    elif defecto == 'desconexa':
        v, f = np.vstack([v, v+3]), np.vstack([f, f+4])
    elif defecto == 'contacto_puntual':
        # Segundo tetraedro en el octante negativo, comparte solo el índice 0.
        v = np.vstack([v, -v[1:]])
        mapa = np.array([0, 4, 5, 6])
        f = np.vstack([f, mapa[f][:, ::-1]])
    elif defecto == 'sin_usar':
        v = np.vstack([v, [2, 2, 2]])
    else:
        f = f.astype(float)
    with pytest.raises(ValueError):
        analizar_malla(v, f)
