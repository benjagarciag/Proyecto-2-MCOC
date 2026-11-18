# Pendientes y distribución del equipo — F02

**Corte: 18 de noviembre de 2026.** Responsables propuestos: Benjamín García,
Luis Noriega y Matías Stierling. El informe/artículo lo redactan los tres y
queda fuera de esta distribución. La presentación y sus respaldos sí se incluyen.

Se revisaron la [pauta F02](../../Enunciados%20e%20Instrucciones/Enunciados/F02_DEFENSA_FINAL.txt)
y las instrucciones generales. F02 permite enumeración discreta local sin
Monte Carlo ni HPC adicionales; no agregar esos trabajos como requisito de
la defensa. La pauta F02 fija la fecha y prevalece sobre el calendario TBD antiguo.

## Base común: lo que ya tenemos

- Rama del compañero `f02-verificaciones-complementarias`, commit `6718163`,
  incorporada a main; IFC, voxelización y núcleo propio conservados.
- Ocho fuentes completas, tres historias ERA5, 24 combinaciones con pesos
  hipotéticos 1/24, métricas marginales y conjuntas, seguimiento a 336 y
  600 h y extensión cuando hay alerta.
- Cuatro cronogramas originales y verificaciones complementarias: colocación
  por estratos, encendido retrasado, temperatura y capacidad de enfriamiento.
  Esas comprobaciones corresponden a la física original, no a la nueva candidata.
- Estudios de h, viento horario, k, suelo y refinamiento espacial/temporal
  de casos anteriores, con resultados y procedencia guardados.
- Nueva candidata: única, 12 °C uniformes, tope equivalente 15 kW,
  h horario, k=2, suelo 15 °C. En 0,50 m/900 s: Tmax=46,2843 °C,
  ΔTmax=17,3681 K, 0/24 excedencias conjuntas hasta 600 h, sin alertas.
  Es evidencia exploratoria; falta confirmar su resolución y constructibilidad.
- Configuración y ejecutor de los cuatro planes a 12 °C/15 kW preparados.
  Solo la única tiene resultados nuevos: las otras tres matrices están pendientes.

## Benjamín — cerrar la propuesta física y de obra

| ID | Prioridad | Trabajo pendiente | Criterio de cierre y entrega a los compañeros |
| --- | --- | --- | --- |
| B1 | Alta | Justificar suministro de 60 m³/h y 12 °C en recepción | Hoja con capacidad de planta, transporte, ciclo, descarga/compactación, reservas y esperas. Separar hipótesis de confirmaciones reales. Verificar que precooling no invalida el caudal. No presentar el esquema provisional de camiones como capacidad contratada. |
| B2 | Alta | Convertir el sumidero de 15 kW en un control construible | Esquema de circuito, caudal, temperaturas, potencia útil, distribución y operación. Justificar U=5 y volumen refrigerado o delimitar su carácter equivalente. Precisar cuándo puede circular agua durante la colocación. Si se descartan tuberías, pedir un caso realmente sin extracción; bajar T inicial manteniendo el sumidero no lo demuestra. |
| B3 | Alta | Cerrar hipótesis de terreno y exposición | Declarar excavación abierta/sin relleno como supuesto, base en contacto con suelo y demás caras expuestas. Documentar suelo 15 °C, k=1,2 y longitud equivalente 0,5 m, resistencias/contacto y limitación de reservorio sin inercia. Usar contraste ERA5 como referencia, no medición de obra. |
| B4 | Alta | Fijar materiales y h con alcance defendible | Tabla ρ/cp de la fuente, k=2 como supuesto y sensibilidad existente; no elegir k para hacer pasar el plan. Explicar h horario, transformación del viento a altura local y límites de correlación. Entregar rangos físicamente pertinentes a Luis; no exigir una calibración sin mediciones. |
| B5 | Alta | Definir protección, montaje y retiros | Croquis de madera 18 mm y dos mantas de 40 mm, caras cubiertas, apoyo tras retirar madera, protección de humedad y retiros a 72/240/360 h de edad. Justificar o reconocer edades supuestas y proponer retiro condicionado por monitoreo/resistencia. No dejarlas entre vertidas en contacto. |
| B6 | Alta | Elaborar plan de instrumentación y contingencia | Ubicaciones con redundancia en núcleo y S25, ambiente y circuito; registro ≤30 min primeras 48 h y luego ≤1 h, compatible con 14 días y extensión. Definir responsables, alarmas anticipadas y acciones ante pérdida de frío, suministro, mal clima o retiro prematuro. |
| B7 | Media | Consolidar parámetros y consultas docentes | Tabla única de valor/unidad/fuente/supuesto/efecto. Consultar geometría faltante, exposición y material si procede. Entregar decisiones a Luis y Matías antes de congelar comparación. Si no hay respuesta, conservar la incertidumbre declarada. |

## Luis — confirmar implementación y confiabilidad numérica

| ID | Prioridad | Trabajo pendiente | Criterio de cierre y entrega a los compañeros |
| --- | --- | --- | --- |
| L1 | Alta | Revisar activación y encendido en la candidata actual | Reutilizar las herramientas de estratos/encendido existentes con 12 °C, 15 kW y h horario. Contrastar activación instantánea con duración física 10,613 h y regla construible acordada en B2. No transferir resultados de 12 kW/h constante a esta variante. |
| L2 | Alta | Confirmar malla y tiempo por separado | Misma candidata y catálogo: 0,50 frente a 0,25 m a dt máximo 900 s; 900 frente a 450 s a igual malla. Preparar referencias requeridas por los ejecutores antes de cada corrida. Tabla de cambios en Tmax, ΔTmax, localización, P_f y costo. Refinar casos cuya clasificación pueda cambiar. Dos niveles dan sensibilidad, no orden asintótico. |
| L3 | Alta | Auditar balance, bordes, interfaces y S25 | Explicar actualización explícita, conductancias y estabilidad; exterior que se vuelve interior, edad de fuente/retiros, exclusión de celdas futuras y S25 a 25 mm con reconstrucción en malla gruesa. Vincular verificación conocida y balance energético al algoritmo usado, más hashes del adaptador de h. |
| L4 | Alta | Comprobar robustez física de la candidata | Con rangos de B3–B5, repetir casos decisivos de k/suelo/h/protecciones y revisar máximos tardíos. Los estudios antiguos orientan cuáles probar; no certifican el nuevo caso. Documentar si cambia la recomendación y no convertir sensibilidades sin probabilidades en riesgo agregado. |
| L5 | Alta | Ejecutar matrices finales comparables | Recibir de Matías familia/pesos y de Benjamín controles cerrados. Ejecutar planes seleccionados, guardar configuraciones y cada fila con máximos/instantes/ubicaciones, balance, 336 h y extensión. Entregar matrices completas sin alertas sin resolver. No sobreescribir evidencia histórica. |
| L6 | Media | Hacer reproducible el flujo en otra máquina | Verificar instalación, lectura IFC→máscara y coincidencia de hashes; reconstrucción de caché congelada desde Git; comandos para un caso, comparación y verificaciones. Parámetros editables sin reescribir solver. Identificar límites del sumidero volumétrico frente a tubos reales. |

## Matías — escenarios, búsqueda, comparación y defensa

| ID | Prioridad | Trabajo pendiente | Criterio de cierre y entrega a los compañeros |
| --- | --- | --- | --- |
| M1 | Alta | Cerrar significado y admisibilidad de las ocho fuentes | M1–M4 y campañas SS/22A, unidades, inversión del ensayo, desfase inicial, interpolación/integral y cola. Intentar aclarar mezcla/réplicas con profesor; si faltan metadatos, mantener escenarios de modelo y no afirmar variabilidad de una receta conocida. No excluir curvas para favorecer cumplimiento. |
| M2 | Alta | Documentar clima, pesos y dependencia | Catálogo único: ERA5 2023/24/25, coordenadas solicitadas y grilla devuelta, descarga, zona, unidades, cobertura y alineación histórica relativa a t0. Fijar pesos antes de comparar; explicar curva común a todas las vertidas e independencia material–clima como hipótesis. No presentarlo como forecast ni percentiles medidos. |
| M3 | Alta | Definir familia de planes y argumento de menor D | Usar controles y recursos comunes: única, referencia y desviaciones competitivas. Indicar variables/rangos/paso/exclusiones. Con caudal máximo 60, D≥636,775/60=10,613 h: si única cumple y es construible alcanza esa cota; justificar por qué no hay alternativa más rápida sin inventar una falla ni duplicar el mismo plan. Pasar configuraciones a Luis. |
| M4 | Alta | Agregar y auditar probabilidades finales | Tabla por escenario y tabla por plan con D, P_T, P_Δ y P_f=unión, suma de pesos=1 y clasificación sin redondeo. Recalcular al menos una sensibilidad fundamentada a pesos o escenarios omitidos sobre matrices finales. Enumeración completa: sin error Monte Carlo; persisten incertidumbres de física, datos y pesos. 0/24 no certifica riesgo real cero. |
| M5 | Alta | Regenerar gráficos finales consistentes | Ocho fuentes, clima, cronogramas, D–P_f con línea 5%, curvas núcleo/S25/diferencial con límites, corte con escala/tiempo y máximos identificados, malla/tiempo y mecanismo de desviaciones. Usar escenario y escalas comunes; no rotular gráficos antiguos como nueva configuración. Si hace falta campo temporal, coordinar exportación con Luis. |
| M6 | Alta | Armar presentación y paquete de defensa sin internet | PDF con autores/grupo y respaldos para 7 min +5 de preguntas; incluir decisiones B, evidencia L y comparación M. Configuraciones, escenarios, datos, métricas, comandos y SHA explícito disponibles localmente. La defensa no requiere simular en vivo. Esta tarea es presentación, no el informe conjunto. |
| M7 | Media | Ensayar con los tres y congelar versión de defensa | Cada uno explica balance, código, probabilidad de una fila, gráficos y límites de la recomendación. Registrar SHA real al finalizar todo; el commit de avance de hoy no se vuelve automáticamente SHA de defensa. Conservar trazabilidad si el artículo posterior corrige observaciones. |

## Orden para trabajar en paralelo

1. Benjamín cierra B1–B5; Luis comienza L1–L3; Matías comienza M1–M3.
2. Con decisiones comunes congeladas, Luis ejecuta L4–L5 y entrega matrices;
   Matías prepara estructura de agregación/gráficos mientras espera.
3. Matías termina M4–M6 con resultados finales; Benjamín completa B6–B7;
   Luis verifica reproducción L6. Los tres ensayan M7.

**Para decir «cerrado»:** candidata construible y parámetros defendidos;
comparación consistente y menor D acotado; resolución confirmada; escenarios,
pesos y sensibilidad explícitos; máximos y balance auditados; sensores y
contingencias; PDF y respaldo reproducible con SHA. Si un punto no se logra,
marcar su efecto y limitar la conclusión, sin presentarlo como validado.

**Fuera del reparto:** informe/artículo y su revisión final, a cargo de los tres.
Los responsables de arriba aportan sus tablas y evidencias a ese documento.
