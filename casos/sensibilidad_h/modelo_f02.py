"""Entrada vigente F02: nueve circuitos con solar y onda larga activas.

Reutiliza el motor y las piezas verificadas, sin modificar sus fuentes con hash.
Sin --ejecutar no lanza simulaciones.
"""
import argparse
from hashlib import sha256
from pathlib import Path
import sensibilidad_radiacion as motor
import familia_radiacion as familia

RAIZ=motor.RAIZ
CONFIG=RAIZ/'entregas/F02/MODELO_VIGENTE.json'


def cargar():
    config=motor.f.base.viento.leer(CONFIG)
    for ruta,esperado in config['implementacion_sha256'].items():
        if sha256((RAIZ/ruta).read_bytes()).hexdigest()!=esperado:
            raise ValueError(f'Cambió la implementación adoptada: {ruta}')
    fisica=motor.f.base.viento.leer(RAIZ/config['configuracion_radiacion'])
    if (config['variante']!='ambas'
            or fisica['variantes'][config['variante']]!=config['radiacion']
            or fisica['albedo_suelo']!=config['albedo_suelo']):
        raise ValueError('Los parámetros activos no coinciden con la configuración verificada.')
    return config


def estado(config):
    p=RAIZ/config['evidencia']['matriz_nominal']
    if not p.exists():
        print('Radiación activa. Matriz nominal aún no disponible; usar --ejecutar.')
        return
    m=motor.f.base.viento.leer(p);filas=m['corridas']
    motor.f.base.comun.validar_filas(filas)
    for a in m['archivos']:
        if sha256((RAIZ/a['ruta']).read_bytes()).hexdigest()!=a['sha256']:
            raise ValueError(f"Cambió la evidencia: {a['ruta']}")
    print('F02 vigente: solar + onda larga; alpha=0.6, epsilon=0.9, albedo=0.2.')
    print('12°C / 60m³/h; nueve circuitos; agua18°C; U5 / tope15kW; control19/18.')
    print('Comparación actual: cuatro planes gruesos y candidata fina,24 pares cada uno,336h.')
    print('Máximos336h: Tmax={:.4f}°C, Delta={:.4f}K.'.format(
        max(r['Tmax']['valor'] for r in filas),
        max(r['DeltaTmax']['valor'] for r in filas)))
    print('Riesgo del catálogo336h:',m['riesgo'])
    fina=motor.f.base.viento.leer(RAIZ/config['evidencia']['matriz_fina'])
    print('Matriz fina completa24 pares: Tmax={:.4f}°C, Delta={:.4f}K.'.format(
        max(r['Tmax']['valor'] for r in fina['corridas']),max(r['DeltaTmax']['valor'] for r in fina['corridas'])))
    print('Frío equivalente Uv5: sin pared de tubo ni agua axial resueltas; caudal no determina transferencia.')
    print('Seguimiento posterior600–672h conserva excedencias y16 picos pendientes.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ejecutar',action='store_true')
    parser.add_argument('--verificar',action='store_true')
    parser.add_argument('--auditar',action='store_true')
    parser.add_argument('--escenario',nargs=2,metavar=('CURVA','CLIMA'))
    parser.add_argument('--malla',type=float,choices=[.4,.2],default=.4)
    parser.add_argument('--paso-max',type=int,choices=[300,150],default=300)
    parser.add_argument('--caudal',type=int,choices=[60,55,50,45],default=60)
    parser.add_argument('--comparar-planes',action='store_true')
    args=parser.parse_args();config=cargar()
    if args.escenario and not args.ejecutar:
        parser.error('--escenario requiere --ejecutar')
    if args.auditar:
        import auditar_familia_radiacion
        auditar_familia_radiacion.main()
    if args.verificar or args.ejecutar:motor.f.iniciar()
    if args.verificar:motor.verificar()
    if args.ejecutar:
        fuentes=[f['id'] for f in motor.f.ESTADO[6]];climas=list(motor.f.ESTADO[7])
        tareas=[tuple(args.escenario)] if args.escenario else [(f,c) for f in fuentes for c in climas]
        if any(f not in fuentes or c not in climas for f,c in tareas):
            parser.error('Fuente o clima desconocidos; consultar el catálogo del modelo vigente.')
        for caudal in ([60,55,50,45] if args.comparar_planes else [args.caudal]):
            for fuente,clima in tareas:
                ruta=familia.resolver(caudal,args.malla,fuente,clima,args.paso_max)
                print('Resultado con radiación:',ruta.relative_to(RAIZ))
        if not args.escenario and args.paso_max==300:
            familia.agregar()
    estado(config)


if __name__=='__main__':main()
