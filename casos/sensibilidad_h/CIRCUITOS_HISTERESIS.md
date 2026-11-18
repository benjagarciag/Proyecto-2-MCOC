# Simulación de apertura/cierre19–18 °C por circuito

El usuario pidió ejecutar las reglas propuestas. Esta instrucción autoriza
las nuevas corridas de esta etapa, manteniendo la preferencia general de
ejecución personal en otros estudios no solicitados explícitamente.

## Condiciones del estudio

- Una operación continua a60 m³/h total y12 °C de colocación.
-11 capas físicas de hasta0,40 m; cronograma obtenido de secciones delIFC.
- Agua idealizada uniforme18 °C,9 circuitos paralelos según esquemaIFC.
- Cada circuito abre solo si su recorrido ya está cubierto por hormigón
  y todas las temperaturas muestreadas junto a sus tramos son≥19 °C.
- Cierra si cualquier temperatura muestreada es≤18 °C o falta hormigón.
  Entre18 y19 mantiene el estado previo; puede reabrir al recuperar≥19.
- Caudal18 L/min por ramal abierto. Sistema nominal162 L/min con bypass
  del resto; se registra circulación embebida y derivada sin sumar caudales
  como potencia térmica.
- U_equivalente5 W/(m³ K) y tope de extracción global15 kW.
- Madera18 mm hasta72 h y dos capas40 mm hasta240/360 h de edad de cada
  capa de hormigón. No se usan aquí las tres capas del estudio sin tubos.
- h horario, k_hormigón2,ρ2476 ycp1023; suelo equivalente15 °C/k1,2/L0,5.
- No se impone el encendido antiguo a6 h ni apagado global a432 h: en
  este estudio gobiernan cobertura e histéresis durante todo el horizonte.
-24 pares completos de8 fuentes y3 climas congelados; pesos1/24.
  Métricas a336 h y600 h, extendiendo hasta672 h si hay alertas.

## Representación numérica y alcance

Se genera una máscara nueva desdeIFC a0,40 m para alinear estratos con las
capas propuestas. Última capa física0,30 m se aproxima con voxel0,40 m;
el resto también tiene error geométrico habitual de la máscara. Volumen
voxel640,704 m³ frente aIFC636,775 m³: diferencia+0,617%. Se conservaD
físico10,6129 h y cronograma de capas de geometríaIFC. No se interpreta
el volumen numérico como nuevo volumen físico contratado.

Se muestrean los tramos de serpentinas y se vinculan a centros de celdas
de hormigón cercanas. Se controla la mínima de ese conjunto por circuito,
incluyendo segmentos cuyo vecino aún no esté activo como bloqueo. Se
requiere además terminar la capa física que cubre el tubo antes de abrir.
Esto aproxima «todos los tramos»: no mide temperatura exacta en pared del
tubo ni resuelve gradientes a escala de su diámetro25 mm. El error máximo
de muestreo geométrico se guarda junto con la procedencia.

Las celdas interiores se asignan al circuito geométricamente más cercano
para distribuir extracción. Se excluye una capa de voxeles exteriores
en esta malla: queda volumen refrigerable equivalente414,016 m³. Es una
aproximación distinta de la máscara366 m³ de la referencia antigua.
No atribuir cambios frente a aquella únicamente a la histéresis: también
cambian malla, activación, asignación espacial y programación del frío.

La potencia por celda esU·V·max(T−18,0) si su circuito está abierto, con
escalamiento proporcional para que el conjunto no supere15 kW. Se limita
además para que la extracción por sí sola no cruce18 °C en un paso.
Conducción y bordes sí pueden enfriar una celda, cerrando el circuito en
la siguiente evaluación. La misma extracción se registra en balance.

Se usa paso máximo300 s y estabilidad de conducción/bordes y sumidero,
con control evaluado en cada paso. El instante de cruce de un umbral
queda discretizado temporalmente; no se busca su raíz dentro del paso.
La temperatura/caudal ideal del agua no calibranU ni certifican15 kW
para la redreal. Confirmar resolución espacial/temporal, montaje y
transferencia antes de afirmar diseño validado o cumplimiento definitivo.

## Pruebas realizadas antes de ejecutar

Casos sintéticos: banda de histéresis; cierre por un solo tramo frío;
bloqueo antes de cobertura; reapertura; tope global; celda de hormigón
con conducción a suelo y extracción comparada con Euler independiente;
energía retirada y residuo de balance. Todos aprobados.
Se conservan también cobertura temporal y cantidad de celdas monitoras
de cada circuito para auditar la asignación.

## Ejecución y resultados

```powershell
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/simular_circuitos.py --verificar
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/simular_circuitos.py --comprobar-insumos
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/simular_circuitos.py --ejecutar
```

Salida `resultados/circuitos_histeresis/`: pieza por curva/clima con
historia y transiciones por circuito; `matriz.json` y `resumen.csv` al
completar24 pares. Los escenarios terminados se conservan al reanudar
con igual procedencia. Si cambia el código/configuración, usar otra
`--salida`. La matriz conserva probabilidades a336 h y extendidas,
sensibilidad de pesos y alertas. Los circuitos abiertos al final no
equivalen a que ya se pueda retirar el sistema o liberar la obra.

## Resultado ejecutado el 18-11-2026

Propuesta constructiva final en
[CIERRE_BENJAMIN.md](../../entregas/F02/CIERRE_BENJAMIN.md).
Confirmación posterior independiente de espacio/tiempo en tres pares:
[tabla y alcance](../../entregas/F02/CONFIRMACION_CIRCUITOS.md).
No se alteraron los scripts ni las salidas originales de esta matriz.

Completados los 24 pares, todos hasta 600 h, sin alertas de picos pendientes.
Los máximos de cada columna pueden corresponder a escenarios o instantes distintos.

| Horizonte desde primera colocación | Mayor Tmax | Mayor ΔT | P(T>70) | P(ΔT>20) | P(unión) |
| --- | ---: | ---: | ---: | ---: | ---: |
| 336 h (14 días exigidos) | 46,0454 °C | 14,9147 K | 0 % | 0 % | 0 % |
| 600 h (25 días, diagnóstico adicional) | 46,0454 °C | 19,3581 K | 0 % | 0 % | 0 % |

La mayor Tmax corresponde a M4_SS × ERA5-2025 a129,333 h. El mayor
diferencial corresponde a M4_SS × ERA5-2024: a216 h para el horizonte
docente, y a428 h para la extensión. En este último instante,
Tmax simultánea=28,7009 °C y Tmin,S25=9,3429 °C. El margen extendido
es apenas0,6419 K: falta confirmar resolución espacial y temporal antes
de cerrar la decisión. No mezclar Tmax absoluta con Tmin de otro instante.

En el escenario de mayor diferencial, C01–C03 abren por primera vez a
14,167 h; C04–C06 a19,25 h; C07–C08 a21,333 h; C09 a22,667 h. Más tarde
se observan cierres y reaperturas; por ejemplo C07 cierra a404,833 h y
reabre a414,417 h. La programación se obtiene de temperaturas, sin
imponer estos tiempos como calendario fijo para otros escenarios.

La auditoría independiente de las salidas aprobó los24 pares y941
transiciones: cobertura, umbrales, alternancia de estados, caudal+bypass,
tope de potencia, energía y cálculo de métricas/riesgo. Residuo máximo
absoluto del balance final:0,000218 J. Esto comprueba implementación y
conservación; no valida por sí solo la representación física del tubo.

Las probabilidades0 % son exactas **dentro del catálogo discreto supuesto**
de24 pares equiponderados. No son una demostración estadística de riesgo
real≤5 %: los pares enumerados no son24 ensayos aleatorios independientes
y no abarcan incertidumbre deU, geometría, propiedades y operación.
Tampoco acreditan que18 L/min logren15 kW en la instalación real.

Figura: [temperaturas y estados por circuito](../../resultados/circuitos_histeresis/control_y_temperaturas.png).
Arriba se muestran temperaturas y diferencial del escenario de peorΔT;
abajo, verde significa abierto y gris cerrado. La línea vertical marca14 días.
La figura no combina en una misma historia extremos de escenarios diferentes.

```powershell
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/auditar_circuitos.py
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/graficar_control_circuitos.py
```
