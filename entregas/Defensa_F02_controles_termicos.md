# F02 · Pruebas de preenfriamiento y protección superficial

Se comparan las mismas cinco vertidas y sus inicios 0/6/12/18/24 h en
El Rosal. La terminación física permanece en **24,64 h** a 60 m³/h
provisionales. Aplicar las medidas se presupone compatible con ese ritmo
para aislar su efecto térmico. La planificación de suministro, montaje,
retiro y validación en obra queda fuera de esta comparación.

Cada alternativa se ejecutó con las ocho fuentes del ensayo y los tres
climas ERA5 congelados, con pesos iguales (1/24 por combinación). El
aire alimenta Robin con h = 5 W/(m²·K). Se conservan el IFC, el suelo
equivalente a 15 °C y las curvas de hidratación por edad. Se usó malla
de 0,50 m, tope temporal de 900 s y S25 a 25 mm.

El [ensayo posterior de extracción interior](Defensa_F02_enfriamiento.md)
usa el retiro escalonado como punto de partida y queda documentado por separado.

## Medidas y resultados

| Variante | Colocación [°C] | Aislación y retiro por edad | Peor Tmax [°C] | Rango de ΔTmáx [K] | Excedencias conjuntas | P_f |
| --- | --- | --- | ---: | --- | ---: | ---: |
| Base | 19 / 18 | 40 mm laterales hasta 96 h | 56,89 | 26,43–41,52 | 24/24 | 100 % |
| Preenfriamiento | 15 / 14 | Igual a la base | 53,09 | 22,96–38,13 | 24/24 | 100 % |
| Protección | 19 / 18 | 40 mm laterales y superiores hasta 240 h | 57,13 | 25,27–41,25 | 24/24 | 100 % |
| Combinada | 15 / 14 | 40 mm laterales y superiores hasta 240 h | 53,24 | 21,88–37,79 | 24/24 | 100 % |
| Retiro escalonado | 13 / 12 | 80 mm laterales y superiores, con 40 mm retirados a 240 h y el resto a 360 h | 51,36 | 18,83–35,18 | 22/24 | 91,67 % |

La primera temperatura de colocación corresponde a V01, la segunda a las
cuatro restantes. Las temperaturas de 12–15 °C son objetivos de ensayo
que debe confirmar la planta. Se simula el efecto de la temperatura
inicial que podría conseguirse con preenfriamiento; la cantidad de hielo
y su efecto en el ritmo de producción no se estimaron. Las fuentes
térmicas siguen prescritas por edad.

El moldaje lateral permanece en todas las variantes hasta 72 h. Las
mantas se aplican solo a caras superiores o laterales expuestas, con
conductividad 0,042 W/(m·K). No modifican el contacto con el suelo ni
la conducción al quedar una cara en contacto con una vertida posterior.
Los retiros se miden desde la activación de la vertida.

**Ninguna variante cumple el 5 % conjunto con los escenarios evaluados.**
Todos los máximos absolutos quedaron bajo 70 °C y el diferencial controla.
El retiro escalonado mejora en **6,34 K** el peor diferencial frente al
caso base, aunque pasan solo dos escenarios, ambos de M1_22A.
En el máximo de esa alternativa (`M4_SS × ERA5-2024`, hora 428),
el interior está a 49,25 °C (V04) y el S25 más frío a 14,07 °C (V02).
En las primeras 336 h el peor diferencial de la misma alternativa
es 27,41 K. La simulación extendida hasta 552 h registra el pico
posterior al último retiro, que ocurre en la hora 384 del plan.

El mayor espesor y el retiro tardío conservan calor durante la protección.
Al retirar las mantas, el exterior queda expuesto mientras el interior
aún está caliente. La mejora observada no resuelve el gradiente tardío.
Cambiar la estación no corresponde al origen común de F02 y aquí se
mantuvieron fecha, hora y clima para medir el efecto de cada medida
sobre el mismo cronograma.

## Evidencia y reproducción

- [Base](../resultados/incertidumbre/controles/base/escenarios.csv)
- [Preenfriamiento](../resultados/incertidumbre/controles/frio/escenarios.csv)
- [Protección superficial](../resultados/incertidumbre/controles/proteccion/escenarios.csv)
- [Combinada](../resultados/incertidumbre/controles/combinada/escenarios.csv)
- [Retiro escalonado](../resultados/incertidumbre/controles/retiro_escalonado/escenarios.csv)

~~~sh
python -B casos/incertidumbre/comparar_controles.py base
python -B casos/incertidumbre/comparar_controles.py frio
python -B casos/incertidumbre/comparar_controles.py proteccion
python -B casos/incertidumbre/comparar_controles.py combinada
python -B casos/incertidumbre/comparar_controles.py retiro_escalonado
python -B casos/incertidumbre/comparar_controles.py retiro_escalonado --cercanos --lado 0.25
python -B casos/incertidumbre/comparar_controles.py retiro_escalonado --cercanos --paso-max 450
~~~

El resumen de cada variante conserva el resultado original de 336 h y
el horizonte extendido para capturar máximos o registrar el efecto del
retiro. Los CSV de refinamiento contienen solo la selección de tres
escenarios más próxima al umbral. El riesgo agregado de la tabla se
calcula sobre el conjunto completo de malla 0,50 m.

En los tres casos cercanos al umbral, refinar solo la malla a 0,25 m dio 19,48, 21,70 y 18,20 K. Reducir solo el paso a 450 s dio 19,71, 21,94 y 18,83 K. Se mantuvieron las dos corridas que pasan y la que excede el umbral en esa selección.
