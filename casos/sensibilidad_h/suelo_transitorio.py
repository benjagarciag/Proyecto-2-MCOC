"""Contraste de suelo transitorio:10 °C/tres capas/sin extracción, ejecución personal."""
import argparse
from hashlib import sha256
from pathlib import Path
import sys
from types import ModuleType

import controles_pasivos as pasivos
from suelo_columnas import Columnas, adaptar

CONFIG = Path(__file__).with_suffix('.json')


def construir_solver(config):
    viento = pasivos.base.viento
    ruta = viento.COPIA/'desarrollo/mcplan/termica_fundacion.py'
    codigo = ruta.read_text(encoding='utf-8')
    codigo = viento.cambiar(codigo,'intervalo_salida_s=3600., enfriamiento=None):',
        'intervalo_salida_s=3600., enfriamiento=None, h_aire_horario_W_m2K=None):')
    codigo = viento.cambiar(codigo,'    def preparar(t):', '''    serie_h = np.asarray(h_aire_horario_W_m2K, dtype=float)
    if serie_h.shape != aire.shape or not np.isfinite(serie_h).all() or (serie_h < 0).any():
        raise ValueError('h horario incompatible.')

    def h_en(t):
        return float(serie_h[min(int(t//3600), len(serie_h)-1)])

    def preparar(t):''')
    assert codigo.count('h_W_m2K=entorno.h_aire_W_m2K') == 2
    codigo = codigo.replace('h_W_m2K=entorno.h_aire_W_m2K','h_W_m2K=h_en(t)')
    codigo = adaptar(codigo,viento.cambiar)
    nombre = 'mcplan.termica_fundacion_suelo_columnas'
    modulo = ModuleType(nombre)
    modulo.__file__ = str(ruta)
    modulo.__package__ = 'mcplan'
    modulo.Columnas = Columnas
    modulo.SUELO_CONFIG = config
    sys.modules[nombre] = modulo
    exec(compile(codigo,str(ruta),'exec'),modulo.__dict__)
    return modulo, sha256(codigo.encode()).hexdigest()


def main():
    config = pasivos.base.viento.leer(CONFIG)
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument('--variante',choices=config['variantes'],default='nominal')
    p.add_argument('--verificar',action='store_true')
    args, restantes = p.parse_known_args()
    elegido = config['variantes'][args.variante]
    print('Suelo transitorio:',args.variante,elegido)
    print('Capacidad del suelo es hipótesis; se mantienen k1.2 y T inicial/fondo15 °C.')
    cargar_original = pasivos.base.cargar_motor

    def cargar(series):
        insumos,motor,_,hashes = cargar_original(series)
        modulo,huella = construir_solver(elegido)
        importar_original = insumos.importar_solver

        def importar(origen):
            partes = list(importar_original(origen))
            partes[3] = modulo.simular
            return tuple(partes)

        insumos.importar_solver = importar
        hashes.update(suelo_transitorio=elegido,hipotesis_suelo=config['hipotesis'],
            solver_suelo_adaptado_sha256=huella,
            modulo_columnas_sha256=sha256(Path(__file__).with_name('suelo_columnas.py').read_bytes()).hexdigest(),
            script_suelo_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
            configuracion_suelo_sha256=sha256(CONFIG.read_bytes()).hexdigest())
        return insumos,motor,modulo,hashes

    if args.verificar:
        pasivos.base.viento._preparacion.preparar()
        # Importa las clases congeladas antes de construir el adaptador.
        cargar_original({'prueba':[0,0]})
        from verificar_suelo_transitorio import verificar
        verificar(construir_solver(elegido)[0])
        return
    pasivos.base.cargar_motor = cargar
    validar_original = pasivos.validar

    def validar_acoplado(d, temperatura, procedencia):
        validar_original(d,temperatura,procedencia)
        for f in d['corridas']:
            for m in (f,f['base_336h']):
                b = m['balance_J']
                escala = max(1,abs(b['suelo_almacenado_J']),abs(b['suelo_fondo_J']),abs(b['suelo']))
                if abs(b['suelo_residuo_J']) > 1e-9*escala or abs(b['conjunto_residuo_J']) > 1e-9*max(escala,abs(b['final'])):
                    raise ValueError('No cierra el balance acoplado hormigón/suelo.')

    pasivos.validar = validar_acoplado
    if not any(a == '--casos' or a.startswith('--casos=') for a in restantes):
        restantes += ['--casos','t10_tres_capas']
    if not any(a == '--salida' or a.startswith('--salida=') for a in restantes):
        restantes += ['--salida',str(pasivos.base.viento.RAIZ/'resultados/suelo_transitorio'/args.variante)]
    sys.argv = [sys.argv[0],*restantes]
    pasivos.main()


if __name__ == '__main__':
    main()
