"""Audita seis comprobaciones selectivas y genera tabla; no ejecuta solver."""
from hashlib import sha256
import json
from pathlib import Path
import numpy as np
import simular_circuitos as base


def main():
    carpeta=base.RAIZ/'resultados/circuitos_confirmacion'
    d=base.viento.leer(carpeta/'resumen.json')
    esperados={(v,c,a) for v in ['espacial','temporal'] for c,a in
        [('M4_SS','ERA5-2024'),('M4_SS','ERA5-2025'),('M2_SS','ERA5-2024')]}
    assert {(r['variante'],r['curva'],r['clima']) for r in d['casos']}==esperados
    assert len(d['casos'])==6
    tabla=[];n_eventos=0
    for r in d['casos']:
        f=base.viento.leer(carpeta/f"{r['variante']}_{r['curva']}_{r['clima']}.json")
        assert {k:v for k,v in f.items() if k not in ['historia','control']}==r
        cf=f['procedencia']['confirmacion']
        assert cf['script_sha256']==sha256(Path(__file__).with_name('confirmar_circuitos.py').read_bytes()).hexdigest()
        assert abs(cf['volumen_refrigerable_m3']-414.016)<1e-6
        assert not f['pico_no_resuelto']
        assert abs(f['balance_J']['residuo'])<.01
        assert abs(sum(f['control']['energia_extraida_circuito_J'])+f['balance_J']['enfriamiento'])<.1
        assert f['balance_J']['enfriamiento_pico_W']<=15000.000001
        estado=[False]*9;previo=0
        for e in f['control']['eventos_circuitos']:
            j=int(e['circuito'][1:])-1
            assert e['tiempo_h']>=previo;previo=e['tiempo_h']
            assert estado[j]!=e['abierto'];estado[j]=e['abierto']
            if e['abierto']:
                assert e['Tmin_tramos_C']>=19
                assert e['tiempo_h']>=f['procedencia']['cubierto_desde_h'][j]
            else:assert e['Tmin_tramos_C'] is None or e['Tmin_tramos_C']<=18
            n_eventos+=1
        assert estado==f['control']['circuitos_abiertos_final']
        for rr in [f,f['base_336h']]:
            assert abs(rr['DeltaTmax']['valor']-(rr['DeltaTmax']['Tmax_C']-rr['DeltaTmax']['Tmin_S25_C']))<1e-10
            assert rr['excede_70']==(rr['Tmax']['valor']>70)
            assert rr['excede_20']==(rr['DeltaTmax']['valor']>20)
        assert all(h['caudal_embebido_L_min']+h['caudal_bypass_L_min']==162 for h in f['historia'])
        tabla.append(f"| {r['variante']} | {r['curva']} × {r['clima']} | {cf['lado_m']:.2f} / {cf['paso_max_s']} | "
            f"{r['Tmax']['valor']:.4f} | {r['base_336h']['DeltaTmax']['valor']:.4f} | {r['DeltaTmax']['valor']:.4f} | "
            f"{r['cambio_DeltaTmax_K']:+.4f} |")
    texto='''# Comprobación selectiva de nueve circuitos

Se separan espacio y tiempo respecto a0,40 m/300 s, conservando controles,
11 capas físicas, tiempos de colocación y zona equivalente414,016 m³.
En espacio se refina el dominio IFC a0,20 m, manteniendo pertenencia a los
voxeles refrigerables de referencia; el control usa monitores de la malla
fina. Así no se amplía el enfriamiento al reducir espesor de voxel exterior.

| Comprobación | Par | Malla m / paso máximo s | Tmax °C | ΔT336h K | ΔT600h K | Cambio ΔT600h K |
| --- | --- | --- | ---: | ---: | ---: | ---: |
'''+ '\n'.join(tabla)+'\n\n'
    texto+=f'Auditoría aprobada: seis pares/variantes y{n_eventos} transiciones, umbrales, cobertura, caudal, balance y métricas.\n\n'
    texto+='''Son tres pares decisivos por variante, no una matriz fina completa.
No se asignan probabilidades agregadas al subconjunto ni se estima orden
asintótico con dos niveles. Los restantes21 pares no tienen aquí sensibilidad
fina comprobada. Estos resultados respaldan estabilidad de los casos
seleccionados; no validan la física del sumidero ni sustituyen robustez ante
incertidumbres omitidas. El volumen del dominio cambia al refinar geometría:
640,704→638,944 m³ frente aIFC636,775 m³.

Reproducir desde raíz:

```powershell
.\\.venv\\Scripts\\python.exe -X utf8 -B casos/sensibilidad_h/confirmar_circuitos.py --ejecutar
.\\.venv\\Scripts\\python.exe -X utf8 -B casos/sensibilidad_h/auditar_confirmacion_circuitos.py
```

Los JSON individuales conservan procedencia, métricas a336/600 h, tiempos,
ubicaciones, controles y trazas. Las salidas con procedencia distinta no
se sobrescriben. El estudio original y sus scripts se conservan intactos.
'''
    (base.RAIZ/'entregas/F02/CONFIRMACION_CIRCUITOS.md').write_text(texto,encoding='utf-8')
    print('Auditoría aprobada; tabla generada.',n_eventos,'transiciones')


if __name__=='__main__':main()
