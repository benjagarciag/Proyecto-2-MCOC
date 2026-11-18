# F02 · Verificación numérica de Luis

Candidata de la revisión integrada del 18 de noviembre. Operación continua
de 636,775 m³ a 60 m³/h, con 12 °C de colocación, tope de 15 kW, U = 5
W/(m³·K), referencia de 18 °C y apagado global a 432 h. Se usa h horario
derivado del viento, suelo equivalente a 15 °C, k = 2 W/(m·K) y retiros
por edad a 72, 240 y 360 h. El origen es el 19 de noviembre a las 10:00, hora
de Santiago. Los 24 escenarios usan las mismas ocho fuentes y tres climas
congelados, con peso 1/24. Los resultados anteriores de 12 kW corresponden
a otra configuración.

## Activación y sensibilidad numérica (L1–L2)

| Variante de única | Malla / paso máximo | Peor Tmax [°C] | Peor ΔT [K] | Excedencias / pares |
| --- | --- | ---: | ---: | ---: |
| Bloque, matriz publicada | 0,50 m / 900 s | 46,2843 | 17,3681 | 0/24 |
| Bloque, refino solo espacial | 0,25 m / 900 s | 46,1366 | 17,3997 | 0/24 |
| Bloque, refino solo temporal | 0,50 m / 450 s | 46,2805 | 17,3684 | 0/24 |
| Estratos, encendido a 6 h de edad | 0,50 m / 900 s | 46,4564 | 18,0172 | 0/24 |
| Estratos, encendido tardío a 10,613 h de edad | 0,50 m / 900 s | 46,4563 | 18,0171 | 0/24 |

En las cinco matrices el par crítico de diferencial fue **M4_SS × ERA5-2025**
a las **380 h**. Frente a la referencia, el máximo global del diferencial
creció **0,0316 K** al refinar la malla y **0,0003 K** al reducir el paso.
El mayor cambio absoluto al emparejar escenarios fue **0,3922 K**
en espacio y **0,0063 K** en tiempo. El diferencial de los estratos
aumentó alrededor de **0,65 K** respecto a la activación instantánea,
sin cambiar la clasificación. En la malla fina, los puntos caliente y S25
quedaron cerca de `(−0,125; −0,125; 3,625) m` y `(−3,625; −8,875; 1,225) m`,
respectivamente. Los JSON conservan las posiciones sin redondear.

El paso efectivo máximo alcanzó **900 s** en la malla fina y **450 s**
en la matriz temporal. Hay pasos menores al coincidir con eventos.
La suma de tiempos por escenario observados en ejecución concurrente
fue aproximadamente **1.605 s** en malla fina y **404 s** en el refino temporal.
Es una medida para presupuestar el cálculo. No es el tiempo de calendario
de la corrida paralela ni una comparación de prestaciones entre equipos.

## Robustez física exploratoria (L4)

Se probaron tres pares completos por variante: M4_SS con ERA5-2024 y
ERA5-2025, y M2_22A con ERA5-2023. Son casos de comprobación, con el mayor
diferencial publicado y contrastes de campaña y año. Se modifica una
hipótesis por vez respecto a la candidata con activación por bloque.

| Variación | Peor diferencial de los tres pares [K] |
| --- | ---: |
| k = 1,6 W/(m·K) | 17,94 |
| k = 2,4 W/(m·K) | 16,90 |
| Suelo a 12 °C | 17,33 |
| h constante igual a la media de 600 h | 16,93 |
| Retiro de la segunda manta a las 312 h | **21,99** |

El retiro adelantado produce el cambio más importante de esta selección.
Con 0,25 m y 450 s, ese par llegó a **22,25 K a 332 h** y volvió a exceder el límite.
Se recomienda conservar el retiro de 360 h como referencia de cálculo
y definir con Benjamín el criterio medible de obra. Los rangos son
exploraciones, pendientes de validación. Para ver casos, horas y residuos,
abrir el [resumen numérico](../../resultados/f02_luis/resumen.csv).

## Sensibilidad de la última manta

Se compararon cuatro edades con 24 pares por edad, manteniendo la vertida
única activada por estratos, la colocación a 12 °C, el tope de enfriamiento
de 15 kW con encendido tardío y el h horario. Se conservó el retiro de la
madera a 72 h y el de la primera manta a 240 h. Solo varió el retiro de
la segunda manta en coronación y laterales. Las edades se cuentan desde
la activación de cada estrato. Las horas de los picos se cuentan desde
el inicio de la vertida. Las corridas alcanzaron las 600 h sin alertas de
picos pendientes. Se reutilizó la matriz de 360 h y se hicieron 72
corridas nuevas a 0,50 m / 900 s.

| Edad de retiro [h] | Mayor Tmáx [°C] | Peor ΔT [K] | Escenario y hora del peor ΔT | Excedencias de 20 K | Peor ΔT refinado [K] |
| ---: | ---: | ---: | --- | ---: | ---: |
| 324 | 46,46 | 25,01 | M4_SS × ERA5-2023, 332 h | 8/24 (33,33 %) | 24,34 (3 pares) |
| 336 | 46,46 | 20,73 | M4_SS × ERA5-2023, 356 h | 1/24 (4,17 %) | 20,82 (4 pares) |
| 348 | 46,46 | 21,51 | M4_SS × ERA5-2023, 356 h | 2/24 (8,33 %) | 20,47 (4 pares) |
| 360 | 46,46 | 18,02 | M4_SS × ERA5-2025, 380 h | 0/24 (0,00 %) | 18,27 (2 pares) |

El refinamiento a 0,25 m / 450 s se hizo en un subconjunto que incluye
el par dominante de cada edad. El porcentaje de excedencias se calcula
con los 24 pares de la malla base y sus pesos iguales.

**Retiro recomendado a 360 h de edad (15 días).** Fue la única opción
sin excedencias en los 24 escenarios. El margen bajo 20 K fue de 1,98 K
en la matriz base y de 1,73 K en el peor par refinado. A las 336 h, el
4,17 % queda dentro de la meta ponderada del 5 % en la malla base, con
una excedencia individual. A las 348 h, el 8,33 % supera esa meta.
En la malla base, el horario relativo al clima explica que adelantar
12 h, de 348 a 336 h, reduzca el máximo. En ERA5-2023 el aire bajó de
15,5 °C a la hora 348 a 7,7 °C a la hora 356. En esa última hora, con
retiro a 348 h el hormigón alcanzaba 33,74 °C frente a 32,54 °C con
retiro a 336 h. El S25 mínimo era 12,23 y 11,82 °C, respectivamente.
El refinamiento invirtió el orden de estas dos opciones, y ambas
conservaron al menos un caso por sobre 20 K. El resultado respalda el cronograma simulado. En obra,
la decisión de retiro se condiciona al monitoreo térmico y al pronóstico.

[Corridas y refinamientos nuevos](../../resultados/f02_luis/retiro_mantas/)
y [matriz de referencia a 360 h](../../resultados/f02_luis/estratos_tardio.json).

~~~sh
python -X utf8 -B casos/sensibilidad_h/verificacion_luis.py --activacion estratos-tardio --retiro-final-h 348 --salida salida_f02/retiro_348h.json
~~~

Para una corrida refinada, agregar `--lado 0.25 --paso-max 450` y seleccionar
el par con `--escenario M4_SS ERA5-2023`.

## Comparación provisional de planes (L5)

Todos los planes de esta tabla tienen 12 °C uniformes, 15 kW, h horario,
encendido a 6 h de edad y activación por bloque. Cada fila enumera los
mismos 24 pares desde el mismo inicio común. La matriz publicada de única
sirve de referencia y se reprodujo su caso crítico; las otras tres
matrices se ejecutaron para esta verificación.

| Plan | D [h] | Peor Tmax [°C] | Peor ΔT [K] | P_T [%] | P_Δ = P_f [%] |
| --- | ---: | ---: | ---: | ---: | ---: |
| Única | 10,61 | 46,28 | 17,37 | 0 | 0 |
| Rápida | 15,64 | 46,65 | 18,73 | 0 | 0 |
| Referencia | 24,64 | 46,88 | 20,62 | 0 | 4,17 |
| Lenta | 36,64 | 47,12 | 21,28 | 0 | 20,83 |

La referencia contiene una excedencia de diferencial, por lo que cumple
el criterio ponderado en la malla base. La lenta contiene cinco y excede
el 5 %. La única es la más rápida entre las que cumplen en este catálogo
y alcanza la cota de duración volumen/caudal bajo los recursos supuestos.
Todas las matrices completas resolvieron las alertas de cola. Los máximos
de diferencial reportados para la única, rápida, referencia y lenta
ocurrieron después de 336 h, entre 379 y 380 h. No debe truncarse el análisis
en el día 14.

En un refinamiento selectivo combinado a 0,25 m/450 s, la excedencia de
la referencia bajó de 20,62 a **19,92 K**. En la lenta se recalcularon sus
cinco excedencias de malla base y persistieron **4**, que suman al menos
**16,67 %** del catálogo en la resolución fina. Ese refino no enumera
todos los pares del plan lento y no estima su riesgo total fino.
El escenario crítico de la única por estratos dio **18,27 K** con ambos
refinamientos aplicados juntos, tanto con el encendido normal como tardío.

Los resultados y las trazas están en
[`resultados/f02_luis`](../../resultados/f02_luis/).

## Balance, estabilidad y S25 (L3)

Para cada celda activa se usa capacidad $C_i=\rho_i c_{p,i}V_i$ y
conductancia $G=kA/\Delta x$ entre vecinas. El avance explícito suma
la energía de hidratación integrada en la edad de la celda, más el paso
temporal por la potencia neta de vecinas, aire y suelo, menos la extracción.
Cada flujo entre vecinas entra con signos opuestos, de modo que cancela
en el balance total. El balance global compara energía final con energía
de colocación, hidratación, aire, suelo y enfriamiento.

Se usa $\Delta t\leq\min(\Delta t_{\rm tope},0{,}8 C/\max_i\sum_jG_{ij})$,
donde la suma incluye contactos activos, conductancias de borde y la
conductancia de enfriamiento habilitada. También se corta el paso en
marcas de clima y eventos de activación, retiro o enfriamiento. El tope
global de potencia solo reduce la extracción respecto de la conductancia
usada en esa cota.

El adaptador deja h constante por intervalo horario, con el valor al
inicio de cada hora. Para una cara Robin, la conductancia es el área
dividida por la suma de resistencias por área de media celda, capas y
película convectiva. En la base se usa la resistencia equivalente del
suelo. Cuando entra una celda vecina, su cara compartida deja de
intercambiar con el exterior y pasa a conducir internamente. Las celdas
que aún no se colocan quedan fuera de la búsqueda de extremos.
La hidratación y el retiro de cada capa usan la edad de la celda o
estrato, no la hora común del proyecto.

Con potencia $P$ positiva hacia el hormigón y distancia centro–cara
$d=\Delta x/2$, se reconstruye
$T_{S25}=T_i+P(d-0{,}025)/(kA)$.
El diferencial de decisión es el máximo temporal de la resta
$T_{\max,\Omega}(t)-T_{\min,S25}(t)$ al mismo instante.
La reconstrucción de S25 usa el gradiente normal aproximado dentro de
una celda gruesa. El contraste de mallas mide sensibilidad de la
clasificación, con dos niveles de resolución.

**Casos conocidos.** En una celda, la adaptación con h constante reproduce
el solver congelado y con h variable reproduce una recurrencia de Euler
evaluada de forma independiente a tolerancia de $10^{-12}$ °C.
La reconstrucción inicial S25 de otra celda es **14,7222222222 °C**.
Al agregar una segunda celda a las 0,5 h, quedan cinco caras de intercambio
para esa nueva celda y el cálculo da **111,1111111111 W**, como en el
balance independiente. Pasaron **562 pruebas Python**. La conservación
energética y estas pruebas verifican la implementación, mientras la
calibración de los parámetros y la validación con mediciones de obra
siguen siendo tareas distintas.

## Reproducción e insumos (L6)

Desde la raíz de un clon Git con historial, instalar `requirements.txt`
en Python 3.12. El ejecutor reconstruye la referencia `6718163` con
`git archive` cuando falta la caché. Compara los hashes del adaptador con
la matriz publicada y exige coincidencia de los snapshots, admitiendo LF
o CRLF únicamente cuando una variante coincide con el SHA esperado.
La ruta de geometría exportada verifica de la misma manera la identidad
del IFC. La ruta directa con IfcOpenShell y la exportada dieron máscaras
idénticas, con **5.140** y **40.536** celdas para 0,50 y 0,25 m.

~~~sh
python -X utf8 -B casos/sensibilidad_h/verificacion_luis.py --comprobar
python -X utf8 -B casos/sensibilidad_h/verificacion_luis.py --escenario M4_SS ERA5-2025 --salida /tmp/f02-piloto.json
python -X utf8 -B casos/sensibilidad_h/verificacion_luis.py --activacion estratos --salida salida_f02/estratos.json
python -X utf8 -B casos/sensibilidad_h/verificacion_luis.py --activacion estratos-tardio --salida salida_f02/estratos_tardio.json
python -X utf8 -B casos/sensibilidad_h/verificacion_luis.py --lado 0.25 --salida salida_f02/malla025.json
python -X utf8 -B casos/sensibilidad_h/verificacion_luis.py --paso-max 450 --salida salida_f02/numerica_450.json
python -X utf8 -B casos/sensibilidad_h/verificacion_luis.py --caso rapida_15kw_12c --salida salida_f02/rapida.json
~~~

Para la matriz de referencia o lenta, sustituir el argumento de caso por
`referencia_15kw_12c` o `lenta_15kw_12c`. Las rutas deben ser nuevas.
`--geometria ifc` habilita la lectura directa. En Windows se puede usar
`python.exe` del entorno y una ruta local nueva en lugar de `/tmp`.
El JSON conserva métricas a 336 h y en el horizonte efectivo, máximos
con ubicación, residuo y traza del par de mayor diferencial.
El escenario crítico de la referencia se reprodujo exactamente:
**17,368140448 K a las 380 h**. Los máximos, el número de pasos y todo el
balance energético coincidieron al resolver ese par leyendo el IFC
directamente. El entorno Python local pasó la comprobación de dependencias.

## Alcance de coordinación

Los resultados de cronograma y física son candidatos bajo los datos del
avance publicado. El inicio tardío por estratos espera una edad de
10,613 h desde cada estrato. El primero nunca se enfría antes del fin
físico de la única. La regla constructiva de circulación, los rangos
físicos y la familia/pesos finales requieren confirmación de Benjamín y
Matías. Las perturbaciones físicas son sensibilidad con pares seleccionados
y conservan riesgo agregado nulo en el archivo (`null`), ya que ese
subconjunto no define una probabilidad. La extracción volumétrica
equivalente no determina trazado ni gradientes locales de tubos.
