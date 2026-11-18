> Actualizacion posterior: la [comparacion vigente](COMPARACION_CIRCUITOS_FINAL.md) contiene cuatro planes con radiacion y matriz fina completa de24pares a336h. Este documento conserva el estudio inicial y su alcance original.

# Comprobación selectiva de nueve circuitos

Se separan espacio y tiempo respecto a0,40 m/300 s, conservando controles,
11 capas físicas, tiempos de colocación y zona equivalente414,016 m³.
En espacio se refina el dominio IFC a0,20 m, manteniendo pertenencia a los
voxeles refrigerables de referencia; el control usa monitores de la malla
fina. Así no se amplía el enfriamiento al reducir espesor de voxel exterior.

| Comprobación | Par | Malla m / paso máximo s | Tmax °C | ΔT336h K | ΔT600h K | Cambio ΔT600h K |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| temporal | M4_SS × ERA5-2024 | 0.40 / 150 | 45.7444 | 14.9138 | 19.3618 | +0.0037 |
| temporal | M4_SS × ERA5-2025 | 0.40 / 150 | 46.0445 | 14.8117 | 18.3770 | -0.0001 |
| temporal | M2_SS × ERA5-2024 | 0.40 / 150 | 44.6704 | 14.1337 | 18.2321 | +0.0035 |
| espacial | M4_SS × ERA5-2024 | 0.20 / 300 | 45.8000 | 15.3007 | 19.1731 | -0.1849 |
| espacial | M4_SS × ERA5-2025 | 0.20 / 300 | 46.0192 | 15.1397 | 19.1378 | +0.7607 |
| espacial | M2_SS × ERA5-2024 | 0.20 / 300 | 44.7050 | 14.4965 | 17.8151 | -0.4135 |

Auditoría aprobada: seis pares/variantes y268 transiciones, umbrales, cobertura, caudal, balance y métricas.

Son tres pares decisivos por variante, no una matriz fina completa.
No se asignan probabilidades agregadas al subconjunto ni se estima orden
asintótico con dos niveles. Los restantes21 pares no tienen aquí sensibilidad
fina comprobada. Estos resultados respaldan estabilidad de los casos
seleccionados; no validan la física del sumidero ni sustituyen robustez ante
incertidumbres omitidas. El volumen del dominio cambia al refinar geometría:
640,704→638,944 m³ frente aIFC636,775 m³.

Reproducir desde raíz:

```powershell
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/confirmar_circuitos.py --ejecutar
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/auditar_confirmacion_circuitos.py
```

Los JSON individuales conservan procedencia, métricas a336/600 h, tiempos,
ubicaciones, controles y trazas. Las salidas con procedencia distinta no
se sobrescriben. El estudio original y sus scripts se conservan intactos.
