"""Caché de mapa fino para no reconstruirlo en cada proceso de contraste."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import numpy as np
import comparar_circuitos as f

RUTA=f.RAIZ/'.venv/cache/f02_mapa_circuitos_02.npz'


def huellas():
    rutas=['casos/sensibilidad_h/comparar_circuitos.py','casos/sensibilidad_h/control_circuitos.py',
        'resultados/diseno_circuitos_colocacion/esquema.json']
    return {p:sha256((f.RAIZ/p).read_bytes()).hexdigest() for p in rutas}


def guardar():
    f.iniciar();ids,origen,mapa,centros=f.geometria(.2)
    contenido=dict(ids=ids,origen=np.array(origen),centros=centros,asignacion=mapa[1],
        cubiertos=np.array(mapa[2]),metadata=np.array(json.dumps(mapa[3])),huellas=np.array(json.dumps(huellas())))
    contenido.update({f'monitor_{j}':a for j,a in enumerate(mapa[0])})
    np.savez_compressed(RUTA,**contenido)
    recuperado=cargar()
    assert np.array_equal(ids,recuperado[0]) and np.array_equal(centros,recuperado[3])
    assert np.array_equal(mapa[1],recuperado[2][1])
    assert all(np.array_equal(a,b) for a,b in zip(mapa[0],recuperado[2][0]))
    print('Caché fina exacta guardada y verificada.',flush=True)


def cargar():
    with np.load(RUTA,allow_pickle=False) as a:
        assert json.loads(str(a['huellas']))==huellas()
        mapa=([a[f'monitor_{j}'].copy() for j in range(9)],a['asignacion'].copy(),a['cubiertos'].tolist(),json.loads(str(a['metadata'])))
        return a['ids'].copy(),a['origen'].copy(),mapa,a['centros'].copy()


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--crear',action='store_true');a=p.parse_args()
    if a.crear:guardar()
    else:print(__doc__)
