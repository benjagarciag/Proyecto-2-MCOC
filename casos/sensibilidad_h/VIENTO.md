# Elección de h con viento: fundamento y comprobación pendiente

## Datos examinados

Se reutilizan los tres snapshots ERA5 congelados del commit
`6718163118123c4b05667b91ad5b4d50124dcf2d`, con viento a 10 m en m/s,
desde las 10:00 del 19 de noviembre de cada año. La ventana de comparación
es [0,600 h), con 600 valores horarios por año; se comprueba cobertura
incluyendo la marca final hasta 672 h para posibles extensiones.
No se descargó ni modificó clima. Las coordenadas solicitadas son
(-37,277929; -72,368271); la respuesta de la grilla es (-37,25; -72,25).
No son mediciones a pie de la fundación ni un pronóstico de 2026.

| Historia | Viento medio a 10 m [m/s] | h medio derivado [W/(m²·K)] | h mínimo | h máximo |
| --- | ---: | ---: | ---: | ---: |
| 2023 | 4,432 | 19,144 | 6,792 | 31,817 |
| 2024 | 3,552 | 16,476 | 6,610 | 28,541 |
| 2025 | 3,277 | 15,639 | 6,185 | 30,119 |

Los rangos describen solo esos bloques; no son límites físicos ni
percentiles poblacionales del sitio.

## Modelo de exposición explícito

Se propone una aproximación de terreno abierto, sin obstrucciones resueltas,
con un mismo perfil de potencia entre 10 y 2 m:

    v_local(t) = v_10(t) * (2/10)^0,14

La altura representativa de 2 m es una decisión de simplificación para una
fundación de altura global 4,30 m: no es una altura medida de cada superficie,
ni un promedio ponderado por caras. No incorpora excavación, parapetos,
apantallamiento, dirección del viento o cambios de exposición por etapa.
El exponente 0,14 corresponde a campo abierto en la documentación EnergyPlus.
Al suponer igual terreno de referencia y local, el cociente de perfiles
reduce la fórmula general a la relación anterior. No se ha demostrado que
la rugosidad de ERA5 y la del emplazamiento sean idénticas.

Se usa la correlación de McAdams documentada por EnergyPlus:

    h_c(t) = 5,7 + 3,8 * v_local(t)     [W/(m²·K)], v en m/s

Esta formulación se aplica allí a las superficies exteriores y no distingue
dirección ni rugosidad superficial. La constante incorpora una aproximación
de convección natural; no se añade otro término natural ni radiativo.
Se adopta el mismo h para todas las caras expuestas como hipótesis global.
Las resistencias de media celda, moldaje y mantas se mantienen en serie:

    H = A / (d_celda/k + suma(e_capa/k_capa) + 1/h_c)

h_c no es la conductancia H de una cara ni el coeficiente equivalente con
aislación. Al cubrirse una cara con hormigón nuevo se conserva el contacto
interno conductivo del solver. No se modifica el suelo.

Fuente primaria: EnergyPlus, Engineering Reference, Outside Surface Heat
Balance, apartados Local Wind Speed Calculation y McAdams, ecuación 3.104:
https://energyplus.readthedocs.io/en/stable/guides/engineering-reference/3.5-outside-surface-heat-balance.html

Advertencia de unidades al comparar bibliografía: las ecuaciones 22–25 de
FHWA-HRT-04-127, página impresa 51 (PDF 69), se expresan en kJ/(m²·h·°C).
No debe copiarse `20+14*v` como si estuviera en W/(m²·K). La relación SI
anterior se toma directamente de la documentación de EnergyPlus.
https://www.fhwa.dot.gov/publications/research/infrastructure/pavements/pccp/04127/04127.pdf

## Selección y alcance

Se propone comprobar h horario como representación nominal derivada del
viento, junto a un h constante común de 17,0862387477 W/(m²·K), calculado
con pesos 1/3 y las 600 horas de cada historia. La elección de correlación,
altura y terreno antecede a las nuevas corridas y no se ajusta para aprobar.
La media no garantiza equivalencia térmica con la historia horaria: cambia
la coincidencia entre frío, viento, hidratación y retiros. Su validez como
simplificación depende de la comparación de resultados, todavía pendiente.

La sensibilidad anterior 5/10/20 no envuelve todos los h horarios derivados.
No extrapolar sus resultados ni interpolar probabilidades para estimar el
nuevo caso. Se conservan como antecedentes del efecto del parámetro.
Sin mediciones de viento o intercambio local, esto es una elección física
trazable bajo hipótesis, no una calibración o validación de obra.
Los efectos de radiación solar, intercambio con cielo, evaporación y humedad
siguen fuera del modelo.

## Preparar y ejecutar personalmente

```powershell
# Solo analiza datos y genera estadísticas/gráfico: sin solver.
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/viento.py
# Solo lectura/importación y comprobación de máscara: sin solver.
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/viento.py --comprobar-insumos
# Dos verificaciones sintéticas, sin fundación.
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/viento.py --verificar
# Comparar h horario y media constante: cuatro planes x 24 escenarios x dos modelos.
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/viento.py --ejecutar
```

El agente ejecutó solo el análisis meteorológico y la comprobación de
importaciones. No ejecutó pruebas sintéticas ni simulaciones de fundación.
`--ejecutar` comprueba primero la adaptación mediante dos casos sintéticos:
h constante reproduce exactamente el solver congelado, y un cambio horario
reproduce un balance independiente de una celda sin fuente.

Se modifica únicamente una copia del código compilada en memoria; main,
solver e insumos congelados no se editan. En la adaptación h es constante
por intervalo horario, con el valor de la marca inicial. Las conductancias
y la cota explícita se recalculan al cambiar la hora; se miden ambos lados
de cada cambio. La temperatura del aire conserva su interpolación lineal.

Por defecto: malla 0,50 m, paso máximo 900 s, mismas fuentes, pesos y cuatro
cronogramas de la sensibilidad previa, extracción desde 6 h y tope 12 kW.
No cambia la capacidad constructiva ni se adoptan controles nuevos.
Se evalúan 336 y 600 h, con extensión automática hasta 672 h si hay alerta.
Los resultados se guardan bajo `resultados/sensibilidad_h/viento/` y no
reemplazan las corridas 5/10/20. Las matrices incorporan `modelo_viento`
con parámetros y hashes del código adaptado; leerlo junto a los hashes de
fuentes congeladas. `series_h.json` conserva las series calculadas.

Opciones: `--modo horario` o `--modo constante_media` para separar el trabajo;
`--planes publicada_unica` para comenzar por un solo plan; `--lado 0.25`
para confirmación espacial; `--paso-max 450` para sensibilidad temporal.
Se conservan y reanudan resultados existentes con igual procedencia.
Los pares individuales de refinamiento no se agregan como matrices completas:
la tabla final usa solo archivos con los 24 pares.

Para estudiar el supuesto de altura: `--altura 1` y `--altura 3.3`, cada uno
con un `--salida` diferente. Para otra rugosidad: `--exponente 0.22` con otra
salida, explícitamente como sensibilidad de terreno, no como identificación
real del sitio. No es necesario ejecutar estas variantes antes de ver si
la comparación nominal cambia la decisión, pero su omisión limita el alcance.

## Qué podremos responder al profesor

“El coeficiente se estimó a partir del viento horario de los mismos bloques
ERA5 que proporcionan la temperatura del aire. Se aproximó la exposición a
2 m mediante un perfil de campo abierto y se aplicó la correlación de
McAdams documentada en EnergyPlus. Las protecciones se modelaron mediante
resistencias adicionales. Se comparó la serie horaria con una media común
para evaluar la simplificación.”

La última frase solo corresponde después de ejecutar y revisar ambas
modalidades. Antes de eso debe decirse “se preparó la comparación”.

## Resultados ejecutados por el usuario: comparación inicial

Se comprobaron ocho matrices completas, con 24 pares cada una, pesos que
suman uno e indicadores coherentes con los máximos. Horizonte efectivo
600 h en todos los casos, sin alertas de cola; residuo máximo <0,0001 J.
Malla 0,50 m y paso máximo 900 s; extracción desde 6 h de edad.

| Plan | P_f constante 17,0862 [%] | P_f horario [%] | Peor DeltaT constante [K] | Peor DeltaT horario [K] |
| --- | ---: | ---: | ---: | ---: |
| Única | 4,1667 | 8,3333 | 20,8377 | 21,0150 |
| Rápida | 8,3333 | 12,5000 | 21,3845 | 21,5777 |
| Referencia | 20,8333 | 25,0000 | 21,9014 | 22,4937 |
| Lenta | 41,6667 | 41,6667 | 22,4953 | 23,1139 |

P_T=0 en todos los planes. En la única, M4_SS × ERA5-2025 cambia de
19,6245 K (constante) a 20,4604 K (horario), a diferencia del único fallo
que ya aparece en M4_SS × ERA5-2024. La mayor diferencia absoluta del
diferencial por par entre ambos modelos es 0,83585 K para la única.
La media constante no reproduce la clasificación de la propuesta: no
adoptarla como sustituto equivalente ni seleccionarla porque arroja un
resultado favorable. El modelo horario conserva la coincidencia temporal
del viento y aire del catálogo; sigue condicionado a correlación, altura,
exposición y otras simplificaciones declaradas.

Ninguno de los cuatro planes pasa con h horario en la malla base. Es una
conclusión de esa resolución, no prueba de imposibilidad constructiva.
Antes de cerrar la decisión, confirmar la única con los 24 pares a
0,25 m/900 s. El refinamiento previo con h=20 constante no reemplaza esta
comprobación del modelo horario. Comando para ejecución personal:

```powershell
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/viento.py --ejecutar --modo horario --planes publicada_unica --lado 0.25
```

Si el modelo horario refinado mantiene P_f>5 %, estudiar un cambio de
control o planificación con nueva evidencia; no reducir h para aprobar.

### Confirmación espacial del modelo horario

El usuario completó los 24 pares de la única a 0,25 m/900 s. Se verificó
catálogo completo, suma de pesos e indicadores; no cambió ninguna
clasificación respecto de 0,50 m. Todos los casos alcanzan 600 h sin
alertas de cola y con 2400 pasos efectivos. El residuo máximo absoluto
es 0,000103 J.

| Malla [m] | Paso máximo [s] | Peor Tmax [°C] | Peor DeltaT [K] | Fallos | P_f [%] |
| --- | ---: | ---: | ---: | --- | ---: |
| 0,50 | 900 | 46,7954 | 21,0150 | 2/24 | 8,3333 |
| 0,25 | 900 | 46,7538 | 20,6898 | 2/24 | 8,3333 |

Los dos fallos se mantienen: M4_SS × ERA5-2024 alcanza 20,6898 K a
428 h y M4_SS × ERA5-2025 alcanza 20,3872 K a 380 h. El siguiente par
más cercano al límite, M2_SS × ERA5-2024, alcanza 19,2093 K.
El refinamiento espacial sostiene el incumplimiento en las dos mallas
probadas. No constituye una cota formal de error ni reemplaza una
sensibilidad temporal específica del modelo horario. El resultado a
h=20 constante con 450 s es un antecedente, no esa comprobación.

La propuesta actual (controles de 12 kW y parámetros fijados) no es
factible bajo el modelo horario y pesos iguales en estas resoluciones.
Se requiere estudiar una modificación de controles/plan y luego confirmarla;
no atribuir cumplimiento al caso con media constante.
