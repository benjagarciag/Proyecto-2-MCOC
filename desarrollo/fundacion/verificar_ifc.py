"""Punto 25: verificar el IFC mediante el lector reutilizable, sin modificarlo."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mcplan.bim import extraer_fundacion_ifc


def verificar(ruta: Path) -> None:
    """Conserva el comando anterior; extracción y validación viven en mcplan.bim."""
    modelo = extraer_fundacion_ifc(ruta)
    print('Archivo:', modelo.ruta)
    print('Schema:', modelo.schema)
    print('Unidad IFC:', modelo.unidad_longitud_ifc)
    print('Escala de longitud IFC a metros:', modelo.escala_longitud_ifc_a_m)
    print('Coordenadas:', modelo.sistema_coordenadas)
    for v in modelo.vertidas:
        print('\n'+'='*60)
        print('Nombre:', v.nombre)
        print('Clase:', v.clase_ifc)
        print('GUID:', v.guid)
        print('Propiedades:', v.propiedades)
        print('Materiales IFC:', v.materiales_asociados)
        print('BBox min [m]:', v.bbox_min_m.round(4))
        print('BBox max [m]:', v.bbox_max_m.round(4))
        print('Dimensiones X/Y/Z [m]:', v.dimensiones_m.round(4))
        print('Triángulos:', v.calidad.numero_triangulos)
        print('Volumen de malla [m3]:', round(v.volumen_m3, 9))
    print('\nGLOBAL')
    print('BBox min [m]:', modelo.bbox_min_m.round(4))
    print('BBox max [m]:', modelo.bbox_max_m.round(4))
    print('Dimensiones X/Y/Z [m]:', modelo.dimensiones_m.round(4))
    print('Número de vertidas:', len(modelo.vertidas))
    print('Suma de volúmenes de malla [m3]:', round(modelo.volumen_total_mallas_m3, 9))
    print('SHA256 IFC:', modelo.sha256_ifc)
    print('VERIFICACIÓN OK: identidad, propiedades y mallas cerradas/orientadas de cinco vertidas.')
    for aviso in modelo.advertencias:
        print('AVISO:', aviso)
    print('No se certifican autointersecciones, solapes entre sólidos ni todas las cotas docentes.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archivo', nargs='?', type=Path, default=Path(__file__).resolve().parent/'fundacion.ifc')
    verificar(parser.parse_args().archivo)
