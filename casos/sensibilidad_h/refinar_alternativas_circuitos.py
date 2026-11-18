"""Contrastes finos de las alternativas: dos pares M4_SS por caudal.

Incluye el caso de mayor Delta base (2024) y el de cambio espacial alto
en la candidata (2025). No presenta el subconjunto como probabilidad fina.
"""
import argparse
from hashlib import sha256
from pathlib import Path
import comparar_circuitos as familia


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ejecutar',action='store_true')
    p.add_argument('--lote',type=int,choices=[0,1,2])
    a=p.parse_args()
    if not a.ejecutar:print(__doc__);return
    familia.iniciar()
    import cache_geometria_circuitos as cache
    if cache.RUTA.exists():familia.GEOMETRIAS[.2]=cache.cargar()
    tareas=[(q,.2,'M4_SS',clima,False) for q in [55,50,45] for clima in ['ERA5-2024','ERA5-2025']]
    if a.lote is not None:tareas=tareas[a.lote::3]
    for t in tareas:
        familia.resolver_tarea(t)
    if a.lote is None:
        familia.base.escribir(familia.SALIDA/'seleccion_refinos_alternativas.json',dict(
            tareas=[list(t) for t in tareas],script_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
            alcance='Seis pares de contraste; no matriz fina completa para alternativas'))


if __name__=='__main__':main()
