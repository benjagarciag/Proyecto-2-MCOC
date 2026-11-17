# F02 · Comparación de cronogramas con 12 kW

Se compararon la vertida única, la variante rápida y la referencia
de cinco vertidas con separación de 6 h en El Rosal. Comparten el IFC
y el volumen de **636,78 m³**, una cuadrilla, un ritmo provisional de
**60 m³/h**, sin colocaciones simultáneas, y un origen común
**19-11-2026 10:00 (Chile)**. Las duraciones físicas se calculan con
volumen IFC dividido por el ritmo, contando las esperas.

Se conservó el [control de 12 kW](Defensa_F02_enfriamiento.md):
coeficiente equivalente U = 5 W/(m³·K), consigna de 18 °C, encendido
a las 6 h de edad y apagado a la hora 432 del proyecto. La colocación
es a 13 °C en V01 y 12 °C en las demás. En la vertida única se usó
**12,23 °C** uniforme, la media ponderada por volumen. El moldaje
se retira a las 72 h de edad y las dos mantas a las 240 y 360 h.
La vertida única se representa con la unión de todas las celdas del
IFC, con un solo identificador para la activación y la edad.

## Resultados

| Plan | Inicios desde t₀ [h] | D [h] | Peor Tmax [°C] | Peor diferencial [K] | P_T | P_Δ | P_f |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| **Vertida única** | 0 | **10,61** | **46,90** | **17,30** | 0 % | 0 % | 0 % |
| Variante rápida | 0 / 3 / 6 / 12 / 15 | 15,64 | 47,10 | 17,87 | 0 % | 0 % | 0 % |
| Referencia | 0 / 6 / 12 / 18 / 24 | 24,64 | 47,30 | 18,30 | 0 % | 0 % | 0 % |

Cada fila agrega las ocho curvas y tres climas, con 24 escenarios de igual
peso. Se evaluaron 336 h y se amplió a 600 h para revisar el retiro y
el apagado. La vertida única alcanza el límite de duración
**636,78/60 = 10,61 h** con el recurso supuesto, ahorrando **5,03 h**
frente a la variante rápida y **14,03 h** frente a la referencia.
Los tres planes pasan el criterio bajo el modelo evaluado.

En la vertida única el mayor diferencial ocurre en **M4_SS × ERA5-2024**
a la **hora 428**, con un máximo de **30,70 °C** en
`(−0,25; −0,25; 3,25) m` y S25 de **13,39 °C** en
`(−3,75; −8,75; 0,975) m`. La corrida alcanza ese diferencial
después de retirar las mantas y antes de apagar la extracción.

## Alcance

La activación térmica de la vertida única sigue siendo instantánea,
aunque el cronograma contabiliza **10,61 h** de colocación física. El
control original habilita el enfriamiento a la hora 6. Se agregó
una sensibilidad que lo inicia al término físico de la colocación,
manteniendo el resto del control. En esa sensibilidad pasaron los **24 escenarios**
y el peor diferencial fue **17,30 K**.

Los tres escenarios más exigentes de la vertida única dieron hasta **17,01 K** al refinar la malla a 0,25 m y hasta **17,31 K** al reducir el paso a 450 s, por separado.

La recomendación depende de poder sostener 60 m³/h sin interrupción,
suministrar la mezcla a 12,23 °C y dimensionar un circuito que entregue
la extracción equivalente. Las corridas no detallan la secuencia
del frente de colocación en obra ni modelan los gradientes locales
cerca de las tuberías.

## Reproducción

~~~sh
python -B casos/incertidumbre/comparar_controles.py retiro_escalonado --enfriamiento 5 12 --plan unica
python -B casos/incertidumbre/comparar_controles.py retiro_escalonado --enfriamiento 5 12 --plan separacion_3h
python -B casos/incertidumbre/comparar_controles.py retiro_escalonado --enfriamiento 5 12 --plan unica --enfriar-tras-colocacion
python -B casos/incertidumbre/comparar_controles.py retiro_escalonado --enfriamiento 5 12 --plan unica --cercanos --lado 0.25
python -B casos/incertidumbre/comparar_controles.py retiro_escalonado --enfriamiento 5 12 --plan unica --cercanos --paso-max 450
~~~

[Vertida única](../resultados/incertidumbre/enfriamiento/u5_tope12/unica/escenarios.csv) ·
[Variante rápida](../resultados/incertidumbre/enfriamiento/u5_tope12/separacion_3h/escenarios.csv) ·
[Referencia](../resultados/incertidumbre/enfriamiento/u5_tope12/escenarios.csv) ·
[Encendido al término físico](../resultados/incertidumbre/enfriamiento/u5_tope12/unica/tras_colocacion/escenarios.csv)
