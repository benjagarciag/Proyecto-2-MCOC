# Contexto para Matías y su agente

## Encargo y base

Cerrar datos/escenarios, búsqueda, comparación y presentación de F02 del
grupo6. Benjamín cierra física/obra y Luis confirma el cálculo. El informe
es conjunto. Leer `AGENTS.md`, la pauta
`Enunciados e Instrucciones/Enunciados/F02_DEFENSA_FINAL.txt` y
`entregas/F02/README.md`. F02 admite enumeración local sin añadir Monte
Carlo/HPC. Defensa19-11-2026, 7 min de exposición y5 de preguntas;
no exige simular en vivo.

La rama hasta6718163 está integrada; avance publicado
`29c2fff608054b7cc91a7800b0586f3009547dd5`. Hay8 fuentes M1–M4×SS/22A
y3 historias ERA5 (2023/24/25). La hipótesis actual es24 combinaciones
equiprobables, con curva común a todas las vertidas de cada realización.
La candidata única a12 °C uniformes/15 kW/h horario obtiene
Tmax46,2843 °C, ΔTmax17,3681 K y0/24 excedencias hasta600 h en
0,50 m/900 s. Falta confirmación fina y constructiva. Las otras tres
configuraciones a12 °C/15 kW están listas, sin resultados nuevos todavía.

## Qué falta determinar y por qué

| Tarea del reparto | Falta determinar | Por qué importa |
| --- | --- | --- |
| M1: material | Si M1–M4 y SS/22A son recetas, réplicas o condiciones comparables, y qué conjunto es admisible | No se pueden sortear recetas distintas como variabilidad de una mezcla elegida sin fundamento. Si faltan metadatos, la conclusión debe limitarse a escenarios de modelo. |
| M1: fuente | Explicación reproducible del balance de inversión, unidades, inicio retenido, integral/interpolación y cola | La fuente suministrada no se interpreta como temperatura ambiente ni se sustituye por el antiguo exponencial docente. Cada curva se conserva completa y su edad reinicia por vertida. |
| M2: clima | Qué representa cada bloque histórico, cobertura, metadatos, alineación temporal y limitaciones | ERA5 2023/24/25 alineado con noviembre2026 no es forecast ni percentiles observados. También un clima frío puede agravar el diferencial. |
| M2: pesos | Fundamento de pesos y dependencia material–clima/lotes | Tener8 archivos y3 años no demuestra equiprobabilidad ni independencia. Fijar hipótesis comunes antes de comparar; no escoger pesos después para mejorar el resultado. |
| M3: búsqueda | Familia construible, variables, rangos, paso y alternativas competitivas bajo recursos comunes | Una comparación favorable elegida a mano no demuestra menor tiempo. Con60 m³/h, D≥636,775/60=10,613 h; si la única es factible y construible alcanza esa cota, sin necesidad de inventar otra opción más rápida. |
| M4: agregación | P_T, P_Δ y P_f conjunto de las matrices finales, más al menos una sensibilidad fundamentada de pesos/escenarios | Una fila que falla ambos límites cuenta una sola vez. Los estudios antiguos de pesos no reemplazan la comprobación sobre la propuesta final. |
| M4: interpretación | Qué cambia al modificar pesos o escenarios y qué incertidumbres persisten | Enumerar todo el catálogo da su probabilidad exacta sin error Monte Carlo; no certifica riesgo real≤5%. Con24 pesos iguales una falla pesa4,167%, dos8,333%; clasificar sin redondeo. |
| M5: resultados visibles | Escenario común, escalas y gráficos que expliquen mecanismo y decisión | Cronogramas, D–P_f, curvas núcleo/S25/diferencial, corte y máximos deben corresponder a la misma configuración declarada. No reutilizar figuras antiguas rotulándolas como12 °C/15 kW. |
| M6–M7: defensa | Selección de evidencia para7 min, respaldos, comandos y SHA final, y comprensión de los tres | La rúbrica incluye preguntas individuales sobre cualquier parte. El SHA del avance no se convierte automáticamente en el de defensa; todo debe estar disponible sin internet. |

## Evidencia a consultar

`datos/hidratacion/source_terms.txt` conserva los datos del profesor; su
copia recibida está en `Enunciados e Instrucciones/source_terms.txt`.
Consultar documentación/manifiestos de hidratación, clima y
`casos/incertidumbre/`, además de `casos/f02_verificaciones/README.md`.
Los documentos de revisión en `casos/sensibilidad_h/` distinguen
configuraciones históricas y candidata nueva. Confirmar unidades y
metadatos en archivos antes de explicarlos; las dudas docentes siguen en
`Enunciados e Instrucciones/Dudas_profesor_pre_evaluacion.txt`.

Sitio: lat−37.277929, lon−72.368271; registrar también grilla realmente
devuelta por ERA5. Inicio común19-11-2026 10:00 America/Santiago
(UTC−03). Se evalúan336 h y se extiende para capturar máximos; el peor
ΔT de la candidata ocurre a380 h. D es fin de colocación, no enfriamiento.

## Entrega y coordinación

Entregar catálogo de escenarios/pesos con fundamento, familia de planes
y tabla agregada auditable, sensibilidad probabilística, figuras y PDF
de presentación con respaldos. Límites docentes: Tmax≤70 °C y
ΔTmax≤20 K; P_f≤5%. ΔT usa Tmax del hormigón colocado menos TminS25
del mismo instante, luego maximiza en tiempo.

Definir familia/pesos con Benjamín antes de solicitar matrices a Luis.
Se puede revisar datos y preparar agregación/presentación en paralelo;
esperar matrices finales para cerrar probabilidades y gráficos. Pedir a
Luis trazas/campos que falten y a Benjamín sensores/contingencias.

Rama sugerida: `codex/matias-escenarios-comparacion`. Trabajar principalmente
en catálogo, agregación, figuras y presentación, coordinando archivos
compartidos. Conservar resultados históricos; no relanzar simulaciones ni
alterar fuentes/pesos para obtener cumplimiento sin acuerdo del equipo.
