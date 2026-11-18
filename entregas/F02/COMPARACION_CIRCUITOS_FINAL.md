# Comparación final homogénea con radiación

Ventana obligatoria:336h desde la primera colocación. Solar y onda larga activas en todos los planes. Conservamos12°C, nueve circuitos, agua ideal18°C,Uv5 y tope15kW, control19/18, once capas y retiros72/240/360h de edad local. Cambia el caudal y los tiempos físicos de colocación y cobertura asociados.

| Caudal [m³/h] | Malla [m] | D[h] | Tmax336h[°C] | ΔT336h[K] | P(unión) |
|---|---:|---:|---:|---:|---:|
|60|0,40|10,6129|47,4941|16,5306|0,00%|
|55|0,40|11,5777|47,5128|16,6011|0,00%|
|50|0,40|12,7355|47,5343|16,6909|0,00%|
|45|0,40|14,1506|47,5582|16,8046|0,00%|
|60|0,20|10,6129|47,0322|15,7202|0,00%|

La candidata60m³/h alcanza la cotaV/Qmax=636,7752/60=10,6129h. Dos frentes de30m³/h y suministro continuo constituyen el recurso máximo idealizado adoptado. La capa mayor requiere107,4min a60 y143,2min a45, dentro de la condición de aceptación150min aún no ensayada. No se afirmó falla de una tasa mayor no admisible.

Las cuatro matrices gruesas tienen24pares completos. La candidata tiene además24pares finos completos, sin extrapolar ese riesgo fino a las otras tasas. Se realizaron seis contrastes finos de alternativas y tres temporales. El mayor cambio espacial deΔT es1,1746K y el temporal0,0014K. Dos mallas no demuestran convergencia asintótica. La zona refrigerable permanece414,016m³ y los tiempos físicos de las once capas se conservan.

La ley térmica de tubos continúa como extracción equivalente, sin pared ni calentamiento axial del agua. Ver [interacción](INTERCAMBIO_TUBERIAS.md). La radiación usaα0,6 yε0,9 supuestos, cielo estimado con rocío/nubes, albedo0,2 y exposición sin sombras. No se presentaP(unión) del catálogo como garantía de riesgo real≤5%.

La probabilidad es la suma de pesos1/24 de realizaciones que exceden70°C o20K en336h. Se conservan fuentes completas y clima compartido entre todas las capas de una realización. La reponderación de años y campañaSS aparece en las matrices. Son escenarios discretos enumerados y no24ensayos aleatorios para un intervalo binomial.

El seguimiento anterior con radiación600–672h registra24excedencias del diferencial, máximo observado33,0074K y16picos pendientes. Es diagnóstico posterior y no modifica la ventana exigida. La última manta se retira a360h de edad, por lo que el cumplimiento14d no acredita liberación térmica posterior.

Auditoría:5matrices completas,129piezas y1161registros de transiciones. Se verifica procedencia, balance global y exterior, cobertura, control19/18 y tope15kW. Las piezas reutilizadas conservan hash de su origen y métricas336h exactas. No se inventa energía por ramal336h que no se había guardado en los estudios extensos.

Resultados: `resultados/familia_radiacion_336h/`. Resumen auditado: `resumen.json`. Tablas y siete figuras: [evidencia vigente](evidencia_f02_radiacion/). Históricos sin radiación conservados en `resultados/comparacion_circuitos/` y `evidencia_circuitos/`, sin usarlos como cifras actuales.

Ejecutores: `familia_radiacion.py`, `auditar_familia_radiacion.py` y `figuras_f02_radiacion.py` bajo `casos/sensibilidad_h/`. No cambiar scripts/config con hash para reanudar sus salidas. El IFC sigue intacto y12°C/cronograma son condiciones externas del plan. El respaldo final/SHA y ensayo oral no se realizaron en esta actualización.
