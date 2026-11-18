"""Consulta/reproduccion del cierre504h+sombra, sin simulacion por defecto."""
import argparse
import cierre_f02 as m


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ejecutar',action='store_true');p.add_argument('--comparar',action='store_true')
    p.add_argument('--auditar',action='store_true');p.add_argument('--escenario',nargs=2)
    p.add_argument('--q',type=int,choices=[55,60],default=60)
    p.add_argument('--malla',type=float,choices=[.4,.2],default=.2)
    a=p.parse_args()
    if a.auditar:
        from auditar_cierre_f02 import main as auditar
        auditar();return
    if not a.ejecutar:
        ruta=m.S/'resumen.json'
        if not ruta.exists():print('Cierre en ejecucion; aun no hay resumen auditado.');return
        d=m.p.leer(ruta)
        print('Cierre504h+sombra90%; agua18C/control19-18/Uv5/tope15kW. Horizonte672h.')
        print('Auditoria',d['estado'],'piezas',d['piezas'])
        for r in d['matrices']:print(r)
        return
    if not(a.escenario or a.comparar):p.error('--ejecutar requiere --escenario o --comparar')
    if a.q==55 and a.malla==.2 and not a.comparar:p.error('La familia no incluye matriz fina55; usar --malla 0.4')
    m.p.f.iniciar()
    if a.comparar:
        pares=[(x['id'],c) for x in m.p.f.ESTADO[6] for c in m.p.f.ESTADO[7]]
        for q,h in [(60,.4),(55,.4),(60,.2)]:
            for curva,clima in pares:m.resolver(q,h,curva,clima)
    else:m.resolver(a.q,a.malla,*a.escenario)


if __name__=='__main__':main()
