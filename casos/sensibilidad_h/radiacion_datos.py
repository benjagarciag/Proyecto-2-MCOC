"""Snapshots ERA5 complementarios para radiación; conserva los anteriores."""
import argparse
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen
import numpy as np

RAIZ=Path(__file__).resolve().parents[2]
VARIABLES=['temperature_2m','wind_speed_10m','shortwave_radiation','direct_radiation',
    'diffuse_radiation','direct_normal_irradiance','dew_point_2m','cloud_cover']


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--descargar',action='store_true');a=p.parse_args()
    if not a.descargar:print(__doc__);return
    cfg=json.loads((RAIZ/'casos/incertidumbre/parametros.json').read_text(encoding='utf-8'))
    destino=RAIZ/'datos/clima/radiacion';destino.mkdir(parents=True,exist_ok=True)
    manifiesto={}
    for c in cfg['historias']:
        year=c['id'][-4:]
        existentes=sorted(destino.glob(f'era5_radiacion_{year}_*.json'))
        if existentes:
            ruta=existentes[-1];d=json.loads(ruta.read_text(encoding='utf-8'))
        else:
            params=dict(latitude=-37.277929,longitude=-72.368271,models='era5',
                start_date=f'{year}-11-19',end_date=f'{year}-12-17',hourly=','.join(VARIABLES),
                wind_speed_unit='ms',timeformat='unixtime',timezone='GMT')
            url='https://archive-api.open-meteo.com/v1/archive?'+urlencode(params)
            with urlopen(url,timeout=90) as res:respuesta=json.load(res)
            ahora=datetime.now(timezone.utc)
            d=dict(metadata=dict(fuente='Open-Meteo Historical Weather API',modelo='era5',url=url,
                descargado_utc=ahora.isoformat(),coordenadas_solicitadas=dict(latitud=-37.277929,longitud=-72.368271),
                variables=VARIABLES,zona_horaria='UTC',tipo='Reanálisis complementario; no forecast'),respuesta=respuesta)
            ruta=destino/f'era5_radiacion_{year}_{ahora.strftime("%Y%m%dT%H%M%SZ")}.json'
            ruta.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        previo=json.loads((RAIZ/c['snapshot']).read_text(encoding='utf-8'))['respuesta']
        hr=d['respuesta']['hourly'];ant=previo['hourly']
        assert hr['time']==ant['time'] and len(hr['time'])==696
        assert all(np.isfinite(hr[v]).all() for v in VARIABLES)
        diferencias={v:float(np.max(abs(np.array(hr[v])-np.array(ant[v])))) for v in VARIABLES[:3]}
        # No sustituye T/v/GHI originales: registra cambios del proveedor.
        assert d['respuesta']['latitude']==previo['latitude'] and d['respuesta']['longitude']==previo['longitude']
        assert np.min(hr['direct_normal_irradiance'])>=0
        assert np.min(hr['diffuse_radiation'])>=0
        assert np.min(hr['cloud_cover'])>=0 and np.max(hr['cloud_cover'])<=100
        manifiesto[c['id']]=dict(snapshot=str(ruta.relative_to(RAIZ)),sha256=sha256(ruta.read_bytes()).hexdigest(),
            snapshot_original=c['snapshot'],original_sha256=sha256((RAIZ/c['snapshot']).read_bytes()).hexdigest(),
            max_diferencia_variables_comunes=diferencias)
        print(c['id'],diferencias,str(ruta),flush=True)
    (destino/'manifiesto.json').write_text(json.dumps(manifiesto,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
