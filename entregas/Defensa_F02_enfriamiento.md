# F02 · Enfriamiento interior equivalente

Se mantuvo la fundación de El Rosal y el plan de cinco vertidas de
**24,64 h** con la capacidad provisional de 60 m³/h. La colocación se
modela a 13 °C en V01 y 12 °C en las demás. La aislación superficial usa
dos capas de 40 mm, con retiros a las 240 h y 360 h de edad. Se aplicó
la extracción solo en celdas interiores de la geometría final, dejando
aproximadamente 0,50 m de espesor sin sumidero junto a las caras exteriores.
La máscara enfriada ocupa **366 m³** en la malla de 0,50 m.

La [comparación posterior de cronogramas con 12 kW](Defensa_F02_cronogramas_12kW.md)
incluye la vertida única y la variante rápida.

## Resultado en los 24 escenarios

| Variante | Peor temperatura máxima [°C] | Peor diferencial [K] | Excedencias conjuntas | Peso de excedencia |
| --- | ---: | ---: | ---: | ---: |
| Preenfriamiento y mantas, sin extracción interior | 51,36 | 35,18 | 22/24 | 91,67 % |
| U = 4 W/(m³·K), tope 10 kW | 47,52 | 20,86 | 1/24 | 4,17 % |
| **U = 5 W/(m³·K), tope 12 kW** | **47,30** | **18,30** | **0/24** | **0 %** |
| U = 6 W/(m³·K), tope 15 kW | 46,98 | 16,51 | 0/24 | 0 % |

Las opciones de **12 y 15 kW** cumplen ambos límites en todos los escenarios
del modelo discreto. **12 kW** es la menor potencia probada que logró
cero excedencias en el conjunto completo. A **10 kW** ocurre una falla en
M4_SS × ERA5-2024. Con el doble de peso para ERA5-2024, esa falla pesa 6,25 %.
Si solo se usa la campaña SS con pesos iguales, pesa 8,33 %. El diagnóstico
a 12 kW se mantiene en ambas sensibilidades porque pasan los 24 casos.
Los topes de 5 y 8 kW fallaron en tres de seis corridas de cribado (dos
curvas y tres climas). Esos resultados no estiman probabilidad, pero los
tres fallos bastan para descartar ambas opciones con los pesos actuales.

A **12 kW**, el mayor diferencial ocurre a las **428 h** en M4_SS × ERA5-2024.
El punto caliente de V04 está a **31,79 °C** y el S25 de V02 a **13,49 °C**.
Es el mismo par de vertidas y la misma hora que controlaban sin extracción.
Se conservaron tanto las métricas de 336 h como las de **600 h (25 días)**.
El último retiro ocurre a las 384 h del proyecto, el apagado a las 432 h
y se simulan **168 h** adicionales después del apagado.

Los tres casos más cercanos al límite con 12 kW conservaron el cumplimiento
al refinar por separado. El máximo de esos tres fue **18,17 K** con
malla de 0,25 m y **18,30 K** con paso máximo de 450 s. La enumeración
completa se ejecutó a 0,50 m y 900 s.

## Cómo se modeló y qué falta para llevarlo a obra

En cada celda habilitada se extrae (U V max(T-18,0)) en W.
Si la suma supera el tope de potencia, se reduce proporcionalmente la
extracción en todas las celdas habilitadas. Se activa a las 6 h de edad
de cada vertida. El término se resta en el balance de energía y su
conductancia se incluye en la cota del paso explícito. La referencia
de 18 °C es un parámetro del sumidero equivalente.

El pico calculado llega al tope de **12 kW térmicos**. La mayor energía
extraída en un escenario es **4,88 MWh térmicos**. Como referencia de escala,
extraer 12 kW con agua que gana 5 °C equivale a aproximadamente **34 L/min**
en total, mediante (P=\dot m c_p\Delta T). Esa cuenta se refiere al
balance del agua. El ensayo no resuelve tuberías reales, circulación,
temperatura de retorno, separación entre tubos ni gradientes locales junto
a ellos. Para convertirlo en plan construible habría que verificar que
el circuito alcanza la conductancia y potencia simuladas, que el suministro
permite colocar a 12–13 °C y que el retiro/montaje mantiene el ritmo usado
para calcular (D). Solo se evaluó esta combinación con la partición
e inicios del plan de cinco vertidas, sin demostrar un óptimo global.

[Comparación por escenario](../resultados/incertidumbre/enfriamiento/comparacion_enfriamiento.png) ·
[Escenarios de 10 kW](../resultados/incertidumbre/enfriamiento/u4_tope10/escenarios.csv) ·
[Escenarios de 12 kW](../resultados/incertidumbre/enfriamiento/u5_tope12/escenarios.csv) ·
[Escenarios de 15 kW](../resultados/incertidumbre/enfriamiento/u6_tope15/escenarios.csv)

## Reproducir

~~~sh
python -B casos/incertidumbre/comparar_controles.py retiro_escalonado --enfriamiento 4 10
python -B casos/incertidumbre/comparar_controles.py retiro_escalonado --enfriamiento 5 12
python -B casos/incertidumbre/comparar_controles.py retiro_escalonado --enfriamiento 6 15
python -B casos/incertidumbre/comparar_controles.py retiro_escalonado --enfriamiento 5 12 --cercanos --lado 0.25
python -B casos/incertidumbre/comparar_controles.py retiro_escalonado --enfriamiento 5 12 --cercanos --paso-max 450
~~~
