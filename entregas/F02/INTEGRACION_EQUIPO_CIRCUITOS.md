> Actualizacion con radiacion: [comparacion vigente](COMPARACION_CIRCUITOS_FINAL.md), cinco matrices completas en336h y presentacion actualizada. Este documento conserva el contexto de reparto o integracion anterior.

# Integración de evidencia del equipo en la configuración de nueve circuitos

La configuración adoptada por Benjamín conserva nueve circuitos, agua
idealmente uniforme a18 °C,18 L/min por ramal y162 L/min nominales con
bypass. El control exige cobertura completa y mínima19/18 °C, sin apagado
global432 h. No se sustituye por tres sectores ni por el circuito axial
propuesto por Luis. La fuente de decisiones es
[CIERRE_BENJAMIN.md](CIERRE_BENJAMIN.md).

## Qué se integra de Luis

Se consultó la rama `codex/f02-circulacion-sectores`, fijada en
`07d6c0357d0839ef06545851d7853193f428937e`.
[Documento consultado](https://github.com/benjagarciag/Proyecto-2-MCOC/blob/07d6c0357d0839ef06545851d7853193f428937e/entregas/F02/VERIFICACION_LUIS.md).

Su explicación del balance de celda, conductancias, reconstrucción S25,
estabilidad explícita y contraste de activación forma parte del fundamento
del método compartido. Sus562 pruebas son un resultado informado por
Luis para aquella versión: no se presentan como pruebas nuevas ejecutadas
por este agente. Sus sensibilidades de mantas, materiales y sectores son
antecedentes de otra configuración. La recomendación de conservar segunda
manta hasta360 h se toma como antecedente y se vuelve a evaluar con
nuestros controles. El nuevo control tiene además verificaciones sintéticas
y auditorías propias.

No se transfieren a la candidata los18,28 K refinados de tres sectores,
ni sus probabilidades, mallas o volúmenes refrigerables. Tampoco se afirma
que su propuesta de43 L/min y agua calentándose por tramos fue simulada.
Las nuevas matrices contienen los nueve ramales y cronogramas comunes.

## Qué se integra de Matías

Se consultó `codex/f02-matias-evidencia`, fijada en
`ed8663234324f952416384d50b7917ead97e6853`.
[Fuentes](https://github.com/benjagarciag/Proyecto-2-MCOC/blob/ed8663234324f952416384d50b7917ead97e6853/entregas/F02/Matias/M1_Hidratacion.md),
[clima y escenarios](https://github.com/benjagarciag/Proyecto-2-MCOC/blob/ed8663234324f952416384d50b7917ead97e6853/entregas/F02/Matias/M2_Escenarios.md),
[agregación probabilística](https://github.com/benjagarciag/Proyecto-2-MCOC/blob/ed8663234324f952416384d50b7917ead97e6853/entregas/F02/Matias/M4_Probabilidad.md).

Se conservan sus fundamentos: ocho fuentes completas como escenarios de
modelo, pesos materiales1/8, tres bloques ERA5 con pesos1/3, independencia
material–clima supuesta, curva común a las capas de cada realización.
Se mantiene la advertencia sobre correspondencia de dosificaciones y
menor confianza de22A; no se escoge solo la curva más favorable.

Se reprodujo la integración de las ocho columnas originales con paso
exacto600 s y se contrastó con los acumulados usados por el solver.
El origen es la ventana retenida tras descartar dos horas del registro;
no se reconstruyen esas primeras horas. La fuente proviene de inversión
térmica y ya está enW/m³. Se interpola el acumulado por edad y se adopta
cola de fuente nula después del ensayo. No se inventa otra conversión
adiabática ni calibración térmica de la fundación.

La copia local Windows y la usada por Matías tienen igual contenido con
normalizaciónLF. SHA-256LF del original:
`182b4a500dd02060b89dc452f007a379c7ab6cdc569e67de59a04c00d3497956`.
La huella de bytes locales se conserva separada en
`evidencia_circuitos/huellas_datos.json`; no se declara identidad de bytes
CRLF/LF. También se verificaron las tres huellasLF climáticas coincidentes
con las documentadas por Luis. No se modificaron los snapshots.

Cada clima conserva696 marcas consecutivas; el índice13 corresponde a
19 noviembre10:00 de Santiago(13:00UTC) del año histórico. Las marcas
relativas0–682 h cubren el máximo configurado672 h. Se usan las mismas
series relativas desde19-11-2026 10:00UTC−03 para todos los planes.
ERA5 histórico no es pronóstico de la fecha de obra; no se descargaron
datos nuevos ni se mezclaron distintos instantes de descarga.

Se conservan las reglas de probabilidad de Matías y se recalculan las
tablas/figuras sobre las nuevas matrices. La unión cuenta una vez cada
escenario con cualquiera de los dos límites excedidos. No se suman las
marginales ni se divide por48. Los pesos son hipótesis, no frecuencias
medidas; reponderar las mismas filas no incorpora extremos ausentes.

## Evidencia nueva y trazabilidad

Las copias de los cuatro documentos consultados, rutas y commits quedan
en [insumos_equipo.json](insumos_equipo.json). Es una integración de
fundamentos y evidencia, sin fusionar ni ejecutar código remoto de las
ramas sobre el trabajo local. Se conserva el núcleo propio congelado y
los adaptadores de los nueve circuitos; los resultados anteriores siguen
identificados como antecedentes.

Familia común:60/55/50/45 m³/h,11capas,12 °C, mismos recursos y controles.
Las tablas y gráficos vigentes son los de
[comparación final](COMPARACION_CIRCUITOS_FINAL.md), no los de la candidata
instantánea anterior. La candidata y sus alternativas distinguen336 h
de la extensión y declaran el alcance de los refinamientos.

Esta tarea reúne contenido técnico, tablas y figuras; no genera elPDF
de la presentación. Respaldo final sin internet, commit/SHA de defensa
y ensayo del grupo se excluyen por instrucción del usuario.
Los commits de las fuentes anteriores identifican aportes consultados,
no un nuevo SHA final de defensa.
