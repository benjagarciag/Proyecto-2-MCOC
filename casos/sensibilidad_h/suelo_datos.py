"""Contrasta 15 °C con temperatura de suelo ERA5; no ejecuta el solver."""
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

import numpy as np

RAIZ=Path(__file__).resolve().parents[2]
VARIABLES=('soil_temperature_28_to_100cm','soil_temperature_100_to_255cm')


def main():
    carpeta=RAIZ/'datos/clima/reanalisis'
    carpeta.mkdir(parents=True,exist_ok=True)
    filas=[]
    for ano in (2023,2024,2025):
        previas=sorted(carpeta.glob(f'suelo_era5_{ano}-11-19_{ano}-12-17_*.json'))
        if previas:
            ruta=previas[-1]
            d=json.loads(ruta.read_text(encoding='utf-8'))
        else:
            url='https://archive-api.open-meteo.com/v1/archive?'+urlencode(dict(
                latitude=-37.277929,longitude=-72.368271,models='era5',
                start_date=f'{ano}-11-19',end_date=f'{ano}-12-17',
                hourly=','.join(VARIABLES),timezone='GMT',timeformat='unixtime',temperature_unit='celsius'))
            with urlopen(url,timeout=40) as conexion:
                respuesta=json.load(conexion)
            ahora=datetime.now(timezone.utc)
            d=dict(metadata=dict(fuente='Open-Meteo Historical Weather API',modelo='era5',
                descargado_utc=ahora.isoformat(),coordenadas_solicitadas=dict(latitud=-37.277929,longitud=-72.368271),
                zona_horaria='UTC',variables=list(VARIABLES),url=url,
                alcance='Suelo de reanálisis sin fundación: contraste, no medición geotécnica ni suelo calentado por hormigón.'),
                respuesta=respuesta)
            ruta=carpeta/f'suelo_era5_{ano}-11-19_{ano}-12-17_{ahora:%Y%m%dT%H%M%S%fZ}.json'
            with ruta.open('x',encoding='utf-8') as archivo:
                json.dump(d,archivo,ensure_ascii=False,indent=2,allow_nan=False)
        r=d['respuesta']
        if d['metadata']['coordenadas_solicitadas']!={'latitud':-37.277929,'longitud':-72.368271}:
            raise ValueError('Coordenadas distintas del sitio autorizado.')
        inicio=int(datetime.fromisoformat(f'{ano}-11-19T10:00:00-03:00').timestamp())
        i=r['hourly']['time'].index(inicio)
        for variable in VARIABLES:
            if r['hourly_units'][variable]!='°C':
                raise ValueError('Unidad de temperatura inesperada.')
            todos=np.asarray([np.nan if v is None else v for v in r['hourly'][variable]],dtype=float)
            for ventana in (336,600,672):
                valores=todos[i:i+ventana]
                marcas=r['hourly']['time'][i:i+ventana]
                if len(valores)!=ventana or not np.isfinite(valores).all() or marcas!=[inicio+3600*j for j in range(ventana)]:
                    raise ValueError('Serie de suelo incompleta.')
                filas.append(dict(ano=ano,variable=variable,ventana_h=ventana,
                    minimo_C=float(valores.min()),media_C=float(valores.mean()),maximo_C=float(valores.max()),
                    inicial_C=float(valores[0]),snapshot=str(ruta.relative_to(RAIZ))))
                if ventana==600:
                    print(ano,variable,'mín/media/máx:',np.round([valores.min(),valores.mean(),valores.max()],3))
    salida=RAIZ/'resultados/revision_suelo_protecciones'
    salida.mkdir(parents=True,exist_ok=True)
    with (salida/'contraste_suelo_era5.csv').open('w',encoding='utf-8',newline='') as archivo:
        tabla=csv.DictWriter(archivo,fieldnames=list(filas[0]));tabla.writeheader();tabla.writerows(filas)
    print('Contraste guardado. Sin simulaciones de fundación.')


if __name__=='__main__':
    main()
