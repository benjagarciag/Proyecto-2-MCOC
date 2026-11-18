# Pendientes actualizados después de retomar tuberías

**Actualización final de la comparación:** cerrados los tres puntos
solicitados: integración de aportes, familia de duraciones y gráficos/
conclusión. Ver [COMPARACION_CIRCUITOS_FINAL.md](COMPARACION_CIRCUITOS_FINAL.md).
Cuatro matrices base24pares y candidata fina24pares, más seis contrastes
finos de alternativas; auditoría aprobada4.700 transiciones. Se conservan
nueve circuitos y límites del modelo ideal. Solo quedan fuera los trabajos
de presentación/respaldo final, SHA y ensayo que el usuario excluyó.
Las listas posteriores conservan el diagnóstico histórico y no significan
que deban repetirse estas simulaciones ni rehacerse sus gráficos.

**Actualización posterior: cierre de decisiones B1–B7.** Prevalece
[CIERRE_BENJAMIN.md](CIERRE_BENJAMIN.md): nueve circuitos, agua uniforme18°C,
18L/min cada uno, bypass hasta162L/min; capas0.40m y control19/18 con
cobertura, sin corte432h. Colocación y protección, instrumentación,
contingencias y tabla única están documentadas. Mantener las condiciones
de obra e idealizaciones explícitas. Los pendientes siguientes conservan
el diagnóstico anterior; no pedir de nuevo definiciones ya adoptadas.
La evidencia de Luis/Matías y la comparación/gráficos ya quedaron integrados
en la configuración común; congelar versión/SHA de defensa quedó excluido.

Esta lista sustituye, para el estado actual de la conversación, la nota
anterior que descartaba tuberías. El usuario informa autorización docente
para utilizarlas y retoma la candidata calculada12 °C/15 kW. No convertir
esa autorización en validación del dimensionamiento ni del modelo.

## Base que no es necesario rehacer

Existe candidata única12 °C/15 kW con h horario, k2, suelo equivalente15 °C,
aislación80→40→0 mm a240/360 h, madera18 mm hasta72 h: Tmax46,2843 °C,
ΔTmax17,3681 K y0/24 excedencias a336 h y hasta600 h, sin alertas.
Fue calculada en0,50 m/900 s con activación instantánea y frío desde6 h.
Los estudios sin extracción y sus protecciones se conservan como evidencia
de alternativas ensayadas; no mezclar sus parámetros con los anteriores.

## Decisiones y verificaciones pendientes

**Actualización:** suministro60 m³/h cerrado como supuesto idealizado
autorizado por el profesor, según informó el usuario. Ver
[condiciones adoptadas](SUPUESTO_SUMINISTRO_ADOPTADO.md). Las tareas de
validación comercial/local quedan opcionales para el alcance docente;
la factibilidad térmica y el procedimiento constructivo siguen pendientes.

Avance de los tres primeros puntos: [material y suministro](MATERIAL_Y_SUMINISTRO.md).
Usuario confirmó que el profesor no aclaró dosificaciones: se mantiene
hipótesis explícita de ocho fuentes, sin elegir la favorable. Se documentó
escenario60 m³/h y flota/logística; confirmación local sigue pendiente.

| Prioridad | Pendiente | Qué se necesita para cerrarlo | Responsable inicial |
| --- | --- | --- | --- |
| 1 | Material elegible y significado de fuentes | Aclarar si M1–M4/SS/22A son mezclas seleccionables o realizaciones/estimaciones; no escoger curva favorable sin respaldo. Definir conjunto admisible y propiedades asociadas. | Matías + consulta docente |
| 1 | Caudal y recursos | Justificar60 m³/h, suministro12 °C, transporte/compactación, interrupciones y posibilidad de más capacidad. D≥V/60 solo si60 es capacidad máxima disponible. | Benjamín |
| 1 | Familia de búsqueda | Definir qué cambia: caudal o esperas/partición, con rangos/pasos y recursos explícitos. Comparar más lento y más rápido cuando sea físicamente admisible. | Benjamín + Matías |
| 1 | Refrigeración construible | Circuitos, caudales, agua, equipo, transferencia equivalenteU5 y tope15 kW; distinguir temperatura de referencia18 °C de entrada real de agua. | Benjamín |
| 1 | Activación y encendido | Confirmar12 °C/15 kW/h horario con colocación progresiva y regla de frío por zonas o tras colocación. No atribuir la instantánea a ese caso nuevo. | Luis + Benjamín |
| 1 | Protección final | Seleccionar montaje, cobertura, soporte tras desmolde, material/espesor y retiro condicionado a monitoreo; mantener configuración común al comparar. | Benjamín |
| 1 | Modelo de suelo y contacto | Resolver alcance del borde equivalente, exposición y contacto, limitaciones de S25 y sensibilidad para candidata con tubos. El contraste transitorio sin tubos no valida automáticamente aquella. | Benjamín + Luis |
| 1 | Resolución numérica final | Misma candidata, dos mallas a igual paso y dos pasos a igual malla; métricas/clasificación/costo y refinamiento de casos marginales. | Luis |
| 1 | Comparación térmica y búsqueda | Matrices de alternativas con mismo material admisible, clima, controles y recursos. Confirmar candidatos que puedan mejorar el plazo. No está completa la familia a12 °C/15 kW. | Luis + Matías |
| 1 | Escenarios, pesos y alcance | Documentar tres bloques históricos, independencia, curva común por realización, pesos y sensibilidad final. Calcular P_T/P_Δ/unión a336 h y extendido sin redondear para clasificar. | Matías |
| 2 | Robustez física | Mantenerρ/cp aportados; documentar k2 y h horario como hipótesis y comprobar consecuencias relevantes en candidata final. No repetir todos los estudios antiguos indiscriminadamente. | Benjamín + Luis |
| 2 | Gráficos de decisión | Curvas D–ΔTmax y D–Tmax por escenario; D–P_f agregado; cronogramas, núcleo/S25, corte y máximos con escenario/unidades/tiempo. Unir solo puntos calculados y no inventar monotonicidad. | Matías |
| 2 | Instrumentación/contingencias | Sensores redundantes núcleo/S25, ambiente/circuito, frecuencias, alarmas y respuestas por pérdida de frío, cambios de suministro/clima y retiro. | Benjamín |
| 2 | Paquete reproducible y defensa | Tabla de parámetros/fuentes, configuración, métricas, comandos de caso/comparación, verificación/balance, PDF/respaldo local, ensayo oral de los tres y SHA final. | Los tres; coordinación Matías |
| 2 | Publicación de cambios posteriores | Los últimos estudios locales aún no están todos en main. Revisar qué se integra, conservar procedencia y separar SHA de avance del de defensa. | Coordinación del equipo |

El informe/artículo se redacta entre los tres, fuera de este reparto.

## Evidencias locales todavía pendientes de integrar o cerrar

- Retiro10/20 días sin tubos mejora respecto de10/15 pero no cumple.
- Única/rápida progresivas sin tubos están calculadas y no cumplen;
  referencia/lenta de esa estrategia no constan calculadas. Al retomar
  tubos, completarlas no es requisito automático para cerrar la nueva candidata.
-10 °C/tres capas sin tubos está calculado y no cumple; efectos aislados
  preparados no ejecutados. Son secundarios si se prioriza solución con tubos.
- Hay resultado nominal de suelo transitorio sin tubos: su resumen informa
  Tmax49,4049 °C, ΔTmax34,1699 K, P_f95,83% ysin alertas. Queda revisar
  su matriz/balances y sensibilidad si se usa como evidencia física. No
  sustituye el contraste del suelo de la candidata con extracción.
- El gráfico duración–riesgo actual contiene solo un punto comparable a
 12 °C/15 kW; faltan las otras duraciones. La curva por escenario requiere
  simular cada alternativa y conservar trazabilidad de qué variable cambia.

## Orden recomendado de cierre

Primero material, capacidad y alcance de búsqueda; en paralelo circuito,
protecciones y suelo. Después activación/encendido y comparación de planes;
confirmar resolución y robustez decisivas. Finalmente gráficos, monitoreo,
defensa, integración y SHA. No exigir una solución diferente solo para
producir una falla: si única alcanzaV/q y cumple, justificar esa cota.
