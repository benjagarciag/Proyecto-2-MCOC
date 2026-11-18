"""Audita24 resultados guardados del control19/18°C; no simula."""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]


def main():
    carpeta = RAIZ/'resultados/circuitos_histeresis'
    matriz = json.loads((carpeta/'matriz.json').read_text(encoding='utf-8'))
    filas = matriz['corridas']
    assert len(filas)==24 and len({(f['curva'],f['clima']) for f in filas})==24
    assert abs(sum(f['peso'] for f in filas)-1)<1e-12
    eventos_total = 0
    for f in filas:
        d = json.loads((carpeta/f'{f["curva"]}_{f["clima"]}.json').read_text(encoding='utf-8'))
        assert d['procedencia']==matriz['procedencia'] and d['corrida']==f
        for control in (d['control'],d['control_336']):
            estado = [False]*9
            ultimo = -1.
            for e in control['eventos_circuitos']:
                j = int(e['circuito'][1:])-1
                assert e['tiempo_h']>=ultimo
                ultimo = e['tiempo_h']
                assert e['abierto']!=estado[j]
                estado[j] = e['abierto']
                if e['abierto']:
                    assert e['Tmin_tramos_C']>=19
                    assert e['tiempo_h']+1e-8>=d['procedencia']['cubierto_desde_h'][j]
                else:
                    assert e['Tmin_tramos_C'] is None or e['Tmin_tramos_C']<=18
            assert estado==control['circuitos_abiertos_final']
        for m,control in ((f,d['control']),(f['base_336h'],d['control_336'])):
            b = m['balance_J']
            assert abs(sum(control['energia_extraida_circuito_J'])+b['enfriamiento'])<.05
            assert 0<=b['enfriamiento_pico_W']<=15000.000001
            assert abs(b['residuo'])<.005
            delta = m['DeltaTmax']
            assert abs(delta['valor']-delta['Tmax_C']+delta['Tmin_S25_C'])<1e-10
            assert m['excede_70']==(m['Tmax']['valor']>70)
            assert m['excede_20']==(delta['valor']>20)
        for h in d['historia']:
            assert h['caudal_embebido_L_min']+h['caudal_bypass_L_min']==162
            assert h['caudal_embebido_L_min']==h['circuitos_abiertos']*18
            assert 0<=h['extraccion_W']<=15000.000001
        eventos_total += len(d['control']['eventos_circuitos'])
    for nombre,fs in [('riesgo',filas),('riesgo_336',[dict(f['base_336h'],peso=f['peso']) for f in filas])]:
        for clave,condicion in [('P_T',lambda f:f['excede_70']),('P_delta',lambda f:f['excede_20']),
            ('P_union',lambda f:f['excede_70'] or f['excede_20'])]:
            assert abs(matriz[nombre][clave]-sum(f['peso'] for f in fs if condicion(f)))<1e-12
    print('Auditoría aprobada:24 pares, estados/umbrales/cobertura, caudal+bypass, energía, métricas y unión.')
    print('Transiciones verificadas en horizontes extendidos:',eventos_total)


if __name__=='__main__':main()
