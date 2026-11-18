# Base de decisión: material y suministro

**Decisión posterior:** el profesor permite adoptar60 m³/h como supuesto
del escenario ideal, según confirmó el usuario. Se cierra con ese alcance
en [suministro adoptado](SUPUESTO_SUMINISTRO_ADOPTADO.md). Las verificaciones
locales pendientes de esta nota no bloquean su uso como supuesto docente.

## 1. Material: decisión metodológica

El usuario confirmó que el profesor todavía no aclaró si M1–M4 corresponden
a la misma dosificación. `source_terms.txt` las denomina probetas, identifica
SS como campaña13–20 abril2025 y22A como campaña22 abril2025, de menor
confianza. Informaρ2476 kg/m³, cp1023 J/(kg K) y contenido de cemento
350,77 kg/m³ de una dosificación de referencia Arrieta. No contiene ocho
recetas completas ni demuestra correspondencia de dosificaciones/campañas.

**Decisión de trabajo:** especificar conceptualmente un solo hormigón para
la fundación y representar su fuente de calor mediante las ocho historias
completas como escenarios de modelo admisibles por hipótesis. No elegir
M1_22A ni otra curva favorable como si fuera un producto seleccionable.
No afirmar que se demostró que todas las curvas son réplicas independientes
de una receta. La identificación comercial/estructural de la mezcla sigue
pendiente y no se inventa una clase resistente.

Se mantienen ocho pesos1/8 y tres climas1/3, con independencia material–clima
y curva común a todas las vertidas por realización como hipótesis. Hay24
escenarios de peso1/24. Revisar sensibilidad de pesos/admisibilidad sin
excluir curvas para obtener cumplimiento. Si el profesor identifica mezclas
distintas elegibles, revisar conjunto y propiedades asociadas antes de
recomendar una mezcla: la decisión metodológica actual es condicional.

Esto satisface el tratamiento explícito de metadatos faltantes permitido
en F02§4, no certifica probabilidades reales del material de obra.
No se modifica el manifiesto original ni resultados calculados.

**Consulta docente pendiente, concreta:** «¿M1–M4 de SS y22A son probetas
de una misma dosificación o mezclas diferentes seleccionables? ¿Qué
correspondencia/dependencia existe entre ambas campañas?» La ausencia
de respuesta no obliga a escoger una curva; se declara el alcance anterior.

## 2. Suministro: escenario de recursos de referencia

Investigación posterior: [respaldo externo y límites de los60 m³/h](RESPALDO_CAUDAL_COLOCACION.md).
Las referencias permiten discutir ritmos menores y mayores; no certifican
que60 sea máximo real de El Rosal. V/60 es condicional al escenario de recursos.

Se fija para la familia principal una capacidad efectiva total máxima
supuestamente disponible de60 m³/h. Se sustenta aritméticamente mediante:

| Elemento | Hipótesis de planificación |
| --- | --- |
| Carga útil por despacho | 7,5 m³ |
| Ciclo completo de camión | 120 min, incluye carga, viajes, espera, descarga y retorno |
| Camiones activos | 16 |
| Reserva propuesta | 2 adicionales, no incluidos en la producción nominal |
| Despachos a régimen | 8 por hora, intervalo7,5 min |
| Planta | Capaz de sostener≥60 m³/h a12 °C de recepción |
| Bombeo/recepción/compactación | Capacidad efectiva conjunta≥60 m³/h |
| Simultaneidad | Una operación de colocación;60 es total, no por cada vertida |
| Inicio t0 | Primer hormigón colocado; logística inicial preparada bajo igual criterio en todos los planes |

`q_transporte=N_activos*V_camión/ciclo_h=16*7,5/2=60 m³/h`.
El caudal efectivo es el mínimo entre planta, transporte, bombeo y
colocación/compactación. La aritmética de flota no demuestra que planta,
ruta o cuadrilla alcancen esas prestaciones. La reserva cubre contingencias
según organización, no garantiza continuidad ni se trata como producción
adicional gratuita. Si se usa de forma sostenida para aumentar caudal,
se redefine el escenario de recursos y se evalúa nuevamente.

El orden de capacidad de un mixer es técnicamente plausible: por ejemplo,
[Liebherr HTM804](https://www.liebherr.com/en-int/p/644575-5379125) declara8 m³
nominales. Los7,5 m³ útiles y ciclo120 min son hipótesis nuestras, no datos
de ese fabricante ni de una flota contratada localmente. La carga legal
real depende del vehículo, densidad y ruta; no se deduce del tambor nominal.

Como contraste de orden de magnitud, la ficha de una
[Putzmeister36-4](https://www.putzmeister.com/documents/20127/71252/M36-4%2BData%2BSheet%2BEN.pdf/2a810d14-d606-9a22-9793-e66143a8c5c1?t=1626243731885)
incluye160 m³/h nominales en una configuración. No se selecciona esa bomba
ni se infiere rendimiento efectivo local: faltan alcance, tuberías, mezcla,
pérdidas y operación. Dimensionar bombeo efectivo además de suministro.

**Pendiente real de obra:** cotización/capacidad de planta con preenfriamiento,
distancias y ciclos, disponibilidad/pesos de camiones, equipos de colocación,
turnos, reserva y plan de interrupciones. Mantener estas condiciones como
supuestos explícitos mientras no exista información local. No atribuir60
m³/h a una exigencia del profesor ni a una medición del paper.

## 3. Duración y significado del mínimo

Volumen IFC636,7751927 m³: se requieren85 despachos de hasta7,5 m³
(84 completos y último≈6,775 m³), sin añadir pérdidas no cuantificadas.
Con60 m³/h sostenidos, D=10,6129199 h. Es tiempo desde primera colocación
hasta última, no duración del enfriamiento ni de todos los trabajos previos.

Para los recursos declarados, `D≥V/q_max=10,613 h`. La única continua
alcanza la cota si mantiene caudal y cumple las restricciones térmicas y
de ejecución. Esto no prueba un óptimo térmico ni que ninguna flota mayor
pueda superar el plazo. Debe confirmarse la colocación progresiva con frío.

## 4. Familia para estudiar más y menos tiempo

Primera familia: misma flota/capacidad máxima, variar ritmo continuo
q=45/50/55/60 m³/h (paso5), manteniendo12 °C y control disponible15 kW.
Estos ritmos son decisiones del plan, no climas aleatorios. Simular activación
progresiva en cada uno; fuente, clima, protecciones y regla de frío comunes.

| Caudal [m³/h] | D=V/q [h] | Camiones activos mínimos ideales a ciclo2 h y7,5 m³ |
| --- | ---: | ---: |
| 45 | 14,151 | 12 |
| 50 | 12,736 | 14 |
| 55 | 11,578 | 15 |
| 60 | 10,613 | 16 |
| 75, recurso alternativo | 8,490 | 20 |

En los ritmos menores puede mantenerse la misma flota con despachos
espaciados.75 requiere20 activos como mínimo ideal, con reserva/planta/
bombeo/compactación acordes: es otra familia de recursos, no aceleración
gratuita de la original. Se puede estudiar para responder qué pasa con
menos de10,61 h, identificando el cambio y su viabilidad, sin mezclarlo
con el argumento de mínimo con16 activos.

Por separado, la familia de cinco vertidas varía esperas con caudal60 y
duraciones15,64/24,64/36,64 h. No tratar esos puntos como si fueran solo
una reducción uniforme de caudal: cambia el cronograma de edades/exposición.

La búsqueda de caudales todavía no está implementada ni simulada. No
modificar horas de resultados existentes para generar una curva. Cada
alternativa requiere calcular24 realizaciones y extraer Tmax/ΔT por
escenario, más P_f conjunta. Confirmar resolución de las decisivas.

## 5. Qué queda cerrado y qué no

- Cerrado como método de trabajo: no seleccionar una curva favorable sin
  evidencia; ocho escenarios de fuente con alcance condicional explícito.
- Cerrado como escenario de planificación:60 m³/h con recursos/logística
  supuestos y volumen/D trazables; no capacidad garantizada de una obra real.
- Definido el rango inicial para comparar duraciones y el recurso extra
  necesario para explorar menos tiempo.
- Pendientes: aclaración docente de dosificaciones, confirmación de recursos
  locales, capacidad a12 °C, dimensionamiento de frío y simulaciones de
  colocación progresiva para esta búsqueda. No afirmar cierre físico total.
