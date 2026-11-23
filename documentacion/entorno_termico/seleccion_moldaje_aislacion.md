# Selección preliminar de moldaje y aislación

Consulta: 12 de noviembre de 2026. Escenario de estudio implementado en las
entradas, posterior a «Entrega E11». El IFC y los resultados publicados se
conservan. No constituye selección constructiva validada.

## Moldaje candidato

ARAUCOPLY Moldaje de pino radiata, espesor comercial 18 mm según la
[ficha chilena de ARAUCO](https://arauco.com/chile/wp-content/uploads/sites/14/2018/03/Ficha-T%C3%A9cnica-Moldaje-Chile.pdf).

El [catálogo AraucoPly Australia/Nueva Zelanda](https://arauco.com/aus-nz/wp-content/uploads/sites/16/2018/02/Product-Catalog-Australia-NZ-1.pdf),
página 22, tabla 11, publica conductividad de 0,158 W/(m·K) para 18 mm.
Ese dato de la familia internacional es una referencia propuesta: falta
confirmar correspondencia con el grado chileno y humedad/temperatura de uso.
No equivale a un certificado térmico específico del tablero chileno.

Resistencia calculada de referencia: 0,018/0,158 = 0,114 m²·K/W.
La elección de tablero no dimensiona apoyos, amarres ni arriostramiento.

## Aislación candidata para evaluación térmica

**Aislanglass Rollo Libre, Volcán: lana de vidrio sin revestimiento.**
La [ficha CES alojada por el fabricante](https://volcan.cl/wp-content/uploads/2022/05/lana_de_vidrio_ces.pdf),
página 1, publica:

| Alternativa | Espesor | Conductividad publicada | R calculada con e/k | R publicada |
| --- | --- | --- | --- | --- |
| Primera alternativa de estudio | 40 mm | 0,042 W/(m·K) | 0,952 m²·K/W | 0,94 m²·K/W |
| Alternativa de mayor resistencia | 50 mm | 0,041 W/(m·K) | 1,220 m²·K/W | 1,22 m²·K/W |

La pequeña diferencia entre R calculada y publicada para 40 mm se conserva
explícita: no se atribuye una precisión mayor a los valores redondeados.
El solver actual usa espesor y conductividad para calcular R, no ingresa
simultáneamente R publicada.

La ficha remite al certificado IDIEM 808.181. Describe aplicaciones de
edificación; no certifica por sí sola este montaje temporal sobre moldaje ni
el contacto con hormigón fresco. La propuesta es evaluar una capa exterior
protegida, no declarar un sistema de curado aprobado.

## Alcance implementado y decisiones pendientes para obra

- Compatibilidad de la aislación con la temperatura de servicio, humedad,
  protección exterior y fijaciones. Confirmar con documentación aplicable al
  montaje; no asumir que el comportamiento en seco se conserva si se moja o
  comprime.
- Cobertura del escenario: solo laterales expuestos, conservando el tratamiento
  existente. La cara superior continúa sin capas. Aislarla sería otro escenario
  y exigiría ampliar la asignación en el solver.
- Retiro del moldaje y de la aislación: los actuales 72/96 h desde cada vertida
  son supuestos docentes, no valores del fabricante. Deben diferenciarse las
  condiciones de resistencia para desencofrar de las condiciones térmicas para
  retirar protección. En el escenario se asume soporte independiente ideal
  para conservar la aislación cuando se retira el moldaje; su ejecución en obra
  sigue pendiente de definir.
- Comparar escenarios durante 336 h y comprobar ambos límites docentes:
  Tmax <= 70 °C y DeltaTmax <= 20 °C con S25. Una mayor resistencia puede reducir
  pérdidas y aumentar la temperatura máxima; no garantiza cumplimiento.

La [guía de curado de Sika](https://gbr.sika.com/en/construction/concrete/concrete-installation/concrete-curing.html)
describe cubiertas térmicas y protección de estas frente a humedad. Es contexto
de ejecución, no certificación del producto Volcán para esta aplicación.

## Archivos actualizados

- `casos/semana4/parametros.json` y las dos configuraciones `comparacion_q*.json`:
  moldaje 0,018 m / 0,158 W/(m·K), aislación 0,040 m / 0,042 W/(m·K).
- `documentacion_capas_laterales` conserva nombres, fuentes y alcance junto a
  los parámetros. Se incorpora al resumen de las nuevas ejecuciones y a la
  tabla de materiales del HTML generado.
- La demo E10 lee esas mismas capas, evitando mantener otros valores en código.

Las simulaciones las ejecutará el usuario. Los resultados anteriores mantienen
sus parámetros y procedencia; aún no hay temperaturas calculadas con las capas
nuevas. Al ejecutar E11/E12 se actualizarán sus salidas normales.
