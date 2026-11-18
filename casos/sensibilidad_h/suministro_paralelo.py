"""Calcula logística condicional de colocación; no ejecuta simulaciones térmicas."""
import argparse
import json
from math import ceil, isfinite
from pathlib import Path


def calcular(config):
    claves = ('volumen_m3','carga_mixer_m3','ciclo_completo_h','camiones_activos',
        'capacidad_planta_asignable_m3_h','capacidad_bombeo_efectiva_por_frente_m3_h',
        'capacidad_compactacion_por_frente_m3_h')
    if any(not isfinite(config[k]) or config[k] <= 0 for k in claves):
        raise ValueError('Volumen, recursos y capacidades deben ser positivos y finitos.')
    if config['camiones_activos'] != int(config['camiones_activos']):
        raise ValueError('Cantidad de camiones debe ser entera.')
    filas = []
    for nombre, caso in config['casos'].items():
        n, atencion = caso['frentes'],caso['atencion_mixer_min']
        ciclo = caso.get('ciclo_completo_h',config['ciclo_completo_h'])
        if n < 1 or n != int(n) or atencion <= 0 or ciclo <= 0 or atencion > ciclo*60:
            raise ValueError('Frentes, atención o ciclo incompatibles.')
        capacidades = dict(planta=config['capacidad_planta_asignable_m3_h'],
            transporte=config['camiones_activos']*config['carga_mixer_m3']/ciclo,
            recepcion=n*config['carga_mixer_m3']*60/atencion,
            bombeo=n*config['capacidad_bombeo_efectiva_por_frente_m3_h'],
            compactacion=n*config['capacidad_compactacion_por_frente_m3_h'])
        q = min(capacidades.values())
        filas.append(dict(caso=nombre,frentes=n,**{f'q_{k}':v for k,v in capacidades.items()},
            q_efectivo=q,D_h=config['volumen_m3']/q,
            intervalo_despacho_global_min=60*config['carga_mixer_m3']/q,
            intervalo_por_frente_min=60*config['carga_mixer_m3']*n/q,
            camiones_minimos_regimen=ceil(q*ciclo/config['carga_mixer_m3']-1e-12),
            despachos_totales=ceil(config['volumen_m3']/config['carga_mixer_m3']),
            limites=[k for k,v in capacidades.items() if abs(v-q)<1e-9]))
    return filas


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config',type=Path,default=Path(__file__).with_suffix('.json'))
    args = p.parse_args()
    config = json.loads(args.config.read_text(encoding='utf-8'))
    print(config['advertencia'])
    for fila in calcular(config):
        print(json.dumps(fila,ensure_ascii=False))


if __name__ == '__main__':
    main()
