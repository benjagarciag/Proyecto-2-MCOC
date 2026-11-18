"""Retiro de dos capas de40 mm: variante sin extracción a12 °C, sin cálculo por defecto."""
import argparse
from hashlib import sha256
from pathlib import Path
import sys

import sin_extraccion_12c as base


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--retiros', nargs=2, type=int, default=(360, 480),
                        metavar=('PRIMERA_H', 'SEGUNDA_H'))
    args, restantes = parser.parse_known_args()
    retiros = tuple(args.retiros)
    if retiros not in ((240, 480), (360, 480)):
        parser.error('Estudio previsto: --retiros 240 480 o --retiros 360 480.')
    # Salidas y procedencia propias; no se cambia el ejecutor ya calculado.
    base.NOMBRE = f'unica_12c_retiros_{retiros[0]}_{retiros[1]}'
    cargar_original = base.cargar_motor

    def cargar(series):
        insumos, motor, solver, hashes = cargar_original(series)
        controles = insumos.importar_solver('exportada')[0]
        anterior = controles.VARIANTES['retiro_escalonado']
        if anterior != (-6, .04, (240, 360)):
            raise ValueError('La protección congelada cambió; revisar la variante.')
        controles.VARIANTES['retiro_escalonado'] = (-6, .04, retiros)
        hashes.update(retiros_aislacion_edad_h=list(retiros),
            espesor_por_capa_m=.04, moldaje_retiro_edad_h=72,
            script_retiros_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
        ejecutar_original = motor.ejecutar

        def ejecutar(argumentos, configuraciones):
            ejecutar_original(argumentos, configuraciones)
            ruta = argumentos.salida/f'{argumentos.experimento}_{"_".join(argumentos.escenario)}.json'
            d = base.viento.leer(ruta)
            d['protecciones_estudio'] = dict(espesor_por_capa_m=.04,
                retiros_aislacion_edad_h=list(retiros), moldaje_retiro_edad_h=72,
                caras='laterales y superiores expuestas; base sin mantas')
            import json
            ruta.write_text(json.dumps(d, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')

        motor.ejecutar = ejecutar
        return insumos, motor, solver, hashes

    base.cargar_motor = cargar
    if not any(a == '--salida' or a.startswith('--salida=') for a in restantes):
        restantes += ['--salida', str(base.viento.RAIZ/'resultados/retiros_sin_extraccion'/f'retiros_{retiros[0]}_{retiros[1]}')]
    print(f'Aislación: 80 mm hasta {retiros[0]} h; 40 mm hasta {retiros[1]} h; luego0 mm.')
    print('Moldaje lateral: retiro a72 h. Base/suelo sin cambios. Sin enfriamiento interno.')
    sys.argv = [sys.argv[0], *restantes]
    base.main()


if __name__ == '__main__':
    main()
