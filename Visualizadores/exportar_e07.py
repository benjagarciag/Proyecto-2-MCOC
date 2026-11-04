"""Exporta el IFC real y los módulos E07 a un HTML autónomo con un laboratorio térmico bajo botón.

Desde la raíz: .venv/Scripts/python.exe -B Visualizadores/exportar_e07.py
Solo escribe Visualizadores/E07.html. No modifica IFC, parámetros ni resultados.
"""
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
from itertools import groupby
import json
from pathlib import Path
import subprocess
import sys


def exportar(raiz, plantilla, salida):
    sys.path.insert(0, str(raiz / 'desarrollo'))
    from mcplan.bim import extraer_fundacion_ifc
    from mcplan.voxel import voxelizar_fundacion
    from mcplan.vertidas_voxel import asignar_vertidas, comparar_volumenes
    from mcplan.superficies_voxel import clasificar_caras, diagnosticar_contactos
    from mcplan.construccion import preparar_construccion, iniciar_construccion, avanzar_construccion, superficies_construidas

    fundacion = extraer_fundacion_ifc(raiz / 'desarrollo/fundacion/fundacion.ifc')
    referencia_contactos = json.loads((raiz / 'casos/e07/superficies.json').read_text(encoding='utf-8-sig'))['contactos_ifc_esperados']
    commit = subprocess.check_output(['git', '-C', str(raiz), 'rev-parse', 'HEAD'], text=True).strip()
    datos = dict(fecha=datetime.now(timezone.utc).isoformat(), commit=commit,
                 sha256_ifc=fundacion.sha256_ifc, coordenadas=fundacion.sistema_coordenadas,
                 volumen_ifc=fundacion.volumen_total_mallas_m3,
                 bbox=[fundacion.bbox_min_m.tolist(), fundacion.bbox_max_m.tolist()],
                 advertencias=list(fundacion.advertencias),
                 contactos_esperados=referencia_contactos, vertidas=[], grillas=[])
    for v in fundacion.vertidas:
        datos['vertidas'].append(dict(id=v.vertida_id, nombre=v.nombre, guid=v.guid,
            volumen=v.volumen_m3, inicio=v.inicio_h, temperatura=v.temperatura_colocacion_C,
            material=v.tipo_hormigon, propiedades=v.propiedades,
            bbox=[v.bbox_min_m.tolist(), v.bbox_max_m.tolist()],
            vertices=v.vertices_m.tolist(), triangulos=v.triangulos.tolist()))
    for h in (1., .5, .25):
        vox = voxelizar_fundacion(fundacion, (h, h, h))
        asignacion = asignar_vertidas(fundacion, vox)
        superficies = clasificar_caras(asignacion)
        programa = preparar_construccion(fundacion, asignacion)
        eventos = []
        for t in (-1 / 3600, 0, 6, 12, 18, 24, 48, 72, 168, 336):
            estado = avanzar_construccion(iniciar_construccion(programa), t * 3600)
            caras = superficies_construidas(estado).caras
            eventos.append(dict(t=t, ocupados=int(estado.activos.sum()),
                exterior=caras.exteriores.area_total_m2, internas=caras.internas.area_total_m2,
                interfaces=caras.interfaces.area_total_m2))
        rle = [[int(k), sum(1 for _ in grupo)] for k, grupo in groupby(asignacion.vertida_id.ravel())]
        datos['grillas'].append(dict(h=h, forma=list(vox.grilla.forma_zyx), origen=vox.grilla.origen_m.tolist(),
            pasos=vox.grilla.pasos_m.tolist(), rle=rle, ocupados=vox.numero_ocupados,
            volumen=vox.volumen_voxelizado_m3 if hasattr(vox, 'volumen_voxelizado_m3') else vox.numero_ocupados*h**3,
            filas=[asdict(f) for f in comparar_volumenes(fundacion, asignacion)],
            exteriores=superficies.exteriores.area_total_m2, internas=superficies.internas.area_total_m2,
            interfaces=superficies.interfaces.area_total_m2,
            contactos=[asdict(c) for c in superficies.contactos_por_par],
            diagnostico=asdict(diagnosticar_contactos(superficies, [1, 2, 3, 4, 5], referencia_contactos)),
            eventos=eventos))
        print(f'h={h:g} m: {vox.numero_ocupados} voxeles; datos exportados')
    contenido = plantilla.read_text(encoding='utf-8')
    motor = plantilla.with_name('e07_termico.js').read_text(encoding='utf-8')
    if contenido.count('__MOTOR_TERMICO__') != 1:
        raise ValueError('Falta el marcador del motor térmico.')
    contenido = contenido.replace('__MOTOR_TERMICO__', motor)
    serializado = json.dumps(datos, ensure_ascii=False, separators=(',', ':'), allow_nan=False).replace('</', '<\\/')
    if contenido.count('__DATOS_E07__') != 1:
        raise ValueError('La plantilla debe contener exactamente un marcador de datos.')
    salida.write_text(contenido.replace('__DATOS_E07__', serializado), encoding='utf-8')
    print(f'HTML autónomo: {salida} ({salida.stat().st_size:,} bytes)')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raiz', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--plantilla', type=Path, default=Path(__file__).with_name('e07_plantilla.html'))
    parser.add_argument('--salida', type=Path, default=Path(__file__).with_name('E07.html'))
    args = parser.parse_args()
    exportar(args.raiz.resolve(), args.plantilla.resolve(), args.salida.resolve())
