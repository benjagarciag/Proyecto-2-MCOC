# F02: sensibilidad al coeficiente convectivo h

Este documento conserva el diseño inicial del estudio de h. Ya existen
resultados ejecutados durante la revisión; consultar el
[estado integrado F02](../../entregas/F02/README.md) y los documentos por tema.
Los parámetros de las distintas etapas no deben mezclarse.
Base congelada: `6718163118123c4b05667b91ad5b4d50124dcf2d`.

## Pregunta y diseño

¿Cambian la clasificación térmica o el menor D factible cuando aumenta el
intercambio convectivo con el aire? Se evalúan h = 5 (base), 10 y
20 W/(m²·K), como perturbaciones exploratorias, sin asignarles probabilidad
ni equivalencia con velocidades o percentiles de viento. El rango es una
elección del estudio, no una calibración del sitio. FHWA explica la dependencia
del intercambio convectivo del viento y la geometría:
https://www.fhwa.dot.gov/publications/research/infrastructure/pavements/pccp/04127/04127.pdf

Los cuatro planes por defecto son única, rápida, referencia y lenta, con
encendido a las 6 h de edad en todos. Se mantiene el control equivalente
U=5 W/(m³·K), tope 12 kW, apagado global a 432 h; colocación 13/12 °C,
o media ponderada en la única, mantas y retiros de la evidencia publicada.
Para estudiar además la única con encendido al término físico, se dispone
del plan `publicada_tras_colocacion`; no mezclar sus resultados con otra
regla de encendido sin identificarla.

Se conservan geometría, caudal de colocación, cronogramas, ocho fuentes,
tres historias ERA5, pesos 1/24, malla 0,50 m, paso máximo 900 s y S25 a
25 mm. Cambia únicamente h. Su resistencia 1/h sigue en serie con moldaje,
aislación y media celda; el coeficiente no sustituye esas resistencias.
El solver conserva su cota automática de estabilidad: los pasos efectivos
pueden cambiar al cambiar h. Cada realización usa 336 y 600 h; si hay alerta
de cola se amplía hasta 672 h. Una alerta persistente deja la clasificación
indeterminada y requiere ampliar clima y horizonte antes de concluir.

Son 288 pares plan/h/curva/clima por defecto. Cada par implica más de una
integración temporal por las comprobaciones de horizonte. No son 288 ensayos
independientes ni se agregan distintos valores de h en una sola probabilidad.

## Ejecución personal, desde la raíz

```powershell
.\.venv\Scripts\python.exe -B casos/sensibilidad_h/ejecutar.py
.\.venv\Scripts\python.exe -B casos/sensibilidad_h/ejecutar.py --comprobar-insumos
.\.venv\Scripts\python.exe -B casos/sensibilidad_h/ejecutar.py --ejecutar
```

El primer comando solo imprime el diseño. El segundo lee los insumos e
importa el código; ninguno simula. Solo `--ejecutar` inicia el solver.
Para avanzar por etapas, añadir `--h 5`, luego `--h 10` y `--h 20`.

La copia aislada vive en `.venv/cache/f02_sensibilidad_h`, extraída del commit
mediante `git archive`. Se reconstruye automáticamente en otro clon y no
requiere copiar la caché personal. No cambia main ni el solver del proyecto. Si falta
el objeto Git, descargarlo con `git fetch origin 6718163118123c4b05667b91ad5b4d50124dcf2d`.
Requiere las dependencias del entorno del proyecto, principalmente NumPy;
permite usar máscaras exportadas con hash de IFC comprobado, sin releer IFC.

Los resultados nuevos se guardan en `resultados/sensibilidad_h/h_5`, `h_10`
y `h_20`. Los JSON existentes se conservan y se omiten al reanudar.
`procedencia.json` registra h, commit y hashes de la adaptación. Los hashes
originales del solver y parámetros en las matrices describen las fuentes
congeladas; leerlos junto con esa procedencia para identificar el h ejecutado.
No editar manualmente las matrices para reanudar. Si hay resultados dudosos
o cambia el script, usar otro `--salida`.

## Interpretación pendiente de las corridas

`comparacion.csv` resume máximos, D, probabilidades marginales y unión,
residuo energético y alertas. Las probabilidades son fracciones entre 0 y 1.
No redondear antes de comparar P_f <= 0,05.

Primero contrastar h=5 con los resultados publicados. Después comparar
incrementos de Tmax, DeltaTmax y P_f, escenarios controlantes y plan más
rápido factible para cada h. No suponer monotonicidad del diferencial.
Si una clasificación depende de diferencias pequeñas respecto de 20 K,
refinar malla y paso por separado antes de afirmar cumplimiento.
Pasar todos los valores probados solo establece robustez en este conjunto;
no valida toda la exposición ambiental de la obra.

## Relación con F02

F02 recomienda tres historias como ejemplo manejable, sin exigir una cuarta.
Exige al menos una sensibilidad fundamentada a pesos o escenarios omitidos.
La sensibilidad a h evalúa una hipótesis física; no reemplaza por sí sola
la sensibilidad de pesos climáticos o del catálogo. La rama ya incluye
sensibilidades de pesos que deben mostrarse y explicarse en la defensa.

## Resultados de la ejecución del usuario

Se revisaron las 12 matrices completas (288 pares), con 24 combinaciones
únicas y pesos que suman uno en cada matriz. h=5 reproduce las métricas
publicadas. Todos los horizontes efectivos son de 600 h, sin alertas de
cola; el mayor residuo energético absoluto es inferior a 0,0001 J.
El agente solo leyó y agregó los resultados; no ejecutó las simulaciones.

| Plan | D [h] | DeltaTmax, h=5 [K] | DeltaTmax, h=10 [K] | DeltaTmax, h=20 [K] | P_f, h=5 [%] | P_f, h=10 [%] | P_f, h=20 [%] |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Única | 10,613 | 17,304 | 19,521 | 21,150 | 0 | 0 | 4,167 |
| Rápida | 15,640 | 17,871 | 20,111 | 21,686 | 0 | 4,167 | 12,500 |
| Referencia | 24,640 | 18,296 | 20,593 | 22,211 | 0 | 8,333 | 29,167 |
| Lenta | 36,640 | 20,900 | 21,150 | 22,814 | 16,667 | 25,000 | 41,667 |

P_T es cero en las doce matrices; P_f=P_delta. El mayor Tmax permanece
por debajo de 48 °C. Aumentar h reduce ligeramente el peor Tmax de cada
plan, mientras aumenta el peor diferencial en esta comparación. Es
consistente con un mayor enfriamiento superficial; para atribuir el cambio
cuantitativo a una ubicación o mecanismo concreto deben examinarse las
trazas del mismo escenario. Con h=10 y 20, el escenario de peor diferencial
en todos los planes es M4_SS × ERA5-2024 a 428 h.

La única conserva la menor D que pasa el criterio en los tres h probados,
condicionada a pesos iguales y malla base. Para h=20 hay un fallo
(M4_SS × ERA5-2024, 21,1501 K). Otro par, M4_SS × ERA5-2025, alcanza
19,9891 K: su margen de solo 0,0109 K exige sensibilidad espacial y temporal
separadas antes de declarar resuelta la clasificación. Si también excediera,
el riesgo sería 2/24=8,333 %.

Sin nuevas simulaciones se recalculó la sensibilidad de pesos de esa matriz:
duplicar el peso de ERA5-2024 y renormalizar eleva P_f de la única a 6,25 %;
duplicar 2023 o 2025 lo deja en 3,125 %. A h=5 y 10 la única conserva
cero excedencias al modificar estos pesos. No se ha demostrado robustez
de la propuesta frente a la combinación h alto/pesos alternativos.

Estos resultados usan activación por bloque y enfriamiento desde las 6 h
de edad. No trasladar sus cifras automáticamente a la variante de encendido
al término físico ni a colocación por estratos. La sensibilidad numérica
de h=5 ya publicada no cuantifica el error del caso h=20.

## Refinamiento independiente para la única con h=20

`refinar.py` conserva el solver y modifica una discretización cada vez:

| Comprobación | Celda [m] | Paso máximo [s] |
| --- | ---: | ---: |
| Base ya ejecutada | 0,50 | 900 |
| Sensibilidad espacial | 0,25 | 900 |
| Sensibilidad temporal | 0,50 | 450 |

Por defecto repite los 24 escenarios en cada resolución: 48 pares nuevos,
cada uno con ventanas de 336 y 600 h y extensión hasta 672 h si hace falta.
Así se podrá recalcular la probabilidad completa en cada resolución, sin
suponer que solo los casos cercanos en la malla base pueden cambiar.

```powershell
.\.venv\Scripts\python.exe -B casos/sensibilidad_h/refinar.py --comprobar-insumos
.\.venv\Scripts\python.exe -B casos/sensibilidad_h/refinar.py --ejecutar
```

Sin argumentos solo describe el diseño. `--resolucion malla_025_paso900`
o `--resolucion malla_050_paso450` permite ejecutarlas por separado.
`--cercanos` restringe a las excedencias y escenarios a <=1 K del límite,
pero entonces no se estima riesgo total. Los pares conservan sus pesos
originales y no se renormalizan subconjuntos. Una ejecución posterior sin
`--cercanos` puede completar la matriz conservando los resultados existentes.

Salidas bajo `resultados/sensibilidad_h/refinamiento_unica_h20/`:
JSON por resolución y par, `comparacion_por_escenario.csv` con diferencias
respecto de la base y `riesgo_por_resolucion.csv` con probabilidad solo al
completar los 24 pares. Se guardan tiempos de máximos, ubicaciones, pasos
efectivos y residuos; el tiempo de ejecución figura en cada JSON.

Los 900/450 s son topes. La cota de estabilidad y los eventos pueden reducir
el paso real. Por ello, conservar el mismo tope al refinar espacialmente no
garantiza pasos efectivos idénticos. Si el paso real cambia materialmente,
hay que comprobar el efecto espacial con un paso común suficientemente
pequeño antes de atribuir toda diferencia a la malla.

Este estudio cuantifica sensibilidad numérica: no calibra h ni demuestra un
orden de convergencia con solo dos niveles. Se busca una resolución de costo
razonable con métricas y clasificación suficientemente estables para la
decisión. Si las diferencias pueden cambiar el cumplimiento, el estudio
no está cerrado; considerar otro refinamiento o uno conjunto tras separar
los efectos. La sensibilidad selectiva no valida automáticamente los demás
planes ni el encendido al término físico.

### Resultados del refinamiento ejecutado por el usuario

Se comprobaron los 24 pares de cada resolución, pesos unitarios al sumar,
indicadores de excedencia coherentes y ninguna alerta de cola a 600 h.

| Celda [m] | Paso máximo [s] | Peor Tmax [°C] | Peor DeltaT [K] | Fallos conjuntos | P_f [%] |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0,50 | 900 | 46,7825 | 21,1501 | 1/24 | 4,1667 |
| 0,25 | 900 | 46,7446 | 20,6873 | 1/24 | 4,1667 |
| 0,50 | 450 | 46,7791 | 21,1513 | 1/24 | 4,1667 |

En los 24 pares no cambia ninguna clasificación individual en ambos
refinamientos. El único fallo sigue siendo M4_SS × ERA5-2024. El escenario
M4_SS × ERA5-2025, cercano al límite en la base, pasa de 19,989114 K a
19,884126 K con malla fina y 19,989777 K con paso menor.

La máxima diferencia absoluta por escenario debida al refinamiento espacial
es 0,09067 K para Tmax y 0,46276 K para DeltaTmax. Al reducir el paso,
esas diferencias máximas son 0,00343 K y 0,00599 K. Los cambios del peor
valor de la tabla no sustituyen estas comparaciones por escenario.

Las integraciones de 600 h emplearon 2400 pasos en la malla fina/900 s
y 4800 en la malla base/450 s, compatibles con pasos efectivos de 900 y
450 s en este caso. No se aprecia reducción extra del paso por estabilidad.
El mayor residuo energético absoluto del refinamiento es <0,0001 J.

La decisión conserva P_f=4,1667 % con pesos iguales en las tres resoluciones
evaluadas. Se tiene evidencia de estabilidad de clasificación, no una cota
formal del error ni convergencia asintótica. La sensibilidad espacial es
mayor que la temporal; no se ha identificado una malla óptima universal.
La sensibilidad de pesos sigue siendo material: duplicar el peso de 2024
y renormalizar mantiene P_f=6,25 % también en las matrices refinadas,
porque el único par fallido no cambia. El refinamiento no calibra h ni
elimina esa dependencia del modelo probabilístico.
