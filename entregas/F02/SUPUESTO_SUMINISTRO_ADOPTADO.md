# Suministro adoptado: escenario idealizado de60 m³/h

**Procedimiento y condiciones de aceptación completados posteriormente:**
[CIERRE_BENJAMIN.md](CIERRE_BENJAMIN.md). Se conserva el caudal docente
adoptado;12 °C en recepción y ventana local150 min son condiciones del
plan, no comprobaciones comerciales ni ensayos de mezcla realizados.

Demostración, comparación de caudales y gráfico en
[justificación de duración mínima](JUSTIFICACION_DURACION_MINIMA.md).

El usuario informa que el profesor permite establecer60 m³/h como supuesto
del contexto ideal. Se adopta como capacidad efectiva total disponible para
la familia principal de planificación, no como rendimiento medido de El Rosal.

## Condiciones declaradas

- Colocación continua, con dos frentes coordinados de30 m³/h cada uno.
- Caudal total60 m³/h, no60 por frente ni por vertida.
- Se supone suministro suficiente, mezcla a12 °C en recepción, bombeo,
  distribución y compactación compatibles con ese caudal durante la operación.
- Las interrupciones logísticas no se modelan en este escenario idealizado.
  No afirmar disponibilidad garantizada ni calibración del proceso real.
- El esquema7,5 m³/mixer,16 activos y2 de reserva a ciclo completo2 h
  queda como ilustración logística consistente, no dato de flota contratada.
- Se conservan controles térmicos de la candidata: enfriamiento equivalente
  limitado a15 kW. Su circuito y regla construible de operación siguen pendientes.

## Consecuencia temporal

Con volumen IFC636,7751927 m³, el límite inferior del tiempo de colocación
es `D≥V/q_max=636,7751927/60=10,6129199 h`.
La operación continua sin esperas alcanza esa cota constructiva del escenario.
Solo podrá recomendarse si cumple las restricciones térmicas con activación
y control coherentes y resolución numérica confirmada. El tiempo posterior
de enfriamiento se informa separado deD.

Los ritmos menores y/o esperas permiten estudiar mayorD con los mismos
recursos. Menos de10,613 h exige cambiar el supuesto de capacidad: sería
una sensibilidad de recursos, no un plan admisible dentro de esta familia.
No hace falta fabricar una falla térmica en una opción más rápida que los
recursos declarados no permiten. Las curvas por escenario requieren nuevas
simulaciones para cada duración admisible.

## Qué se cierra y qué sigue abierto

Queda cerrado para el ejercicio docente el escenario de suministro a60 m³/h.
No hace falta confirmar con proveedores esa disponibilidad para usarlo como
supuesto, dada la autorización informada. La consulta comercial/ruta real
queda como mejora opcional de viabilidad, no bloqueo de la búsqueda docente.

Se mantienen pendientes: aclaración de dosificaciones/fuentes; coordinación
por capas y frentes; colocación progresiva con refrigeración; dimensionamiento
equivalente del frío; comparación de planes; refinamiento y sensibilidades
decisivas; protecciones, monitoreo y cierre de evidencia.

Redacción para defensa: «Suponemos una capacidad efectiva total de60 m³/h,
con suministro continuo y dos frentes coordinados de30 m³/h. Bajo esa
restricción, colocar636,775 m³ requiere al menos10,613 h. Se evalúa después
si ese plazo es térmicamente factible bajo los escenarios y controles declarados».
