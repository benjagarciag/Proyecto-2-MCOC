# Estimación de suministro específica de El Rosal: evidencia y faltantes

Consulta pública18-11-2026. Se conserva el sitio docente exacto
lat−37,277929, lon−72,368271. La geometría636,775 m³ es el caso IFC
del curso, no una cubicación demostrada de las fundaciones comerciales
del parque real. No cambiarla al consultar documentos del proyecto.

## Antecedentes localizados

| Antecedente primario | Qué permite afirmar | Qué no demuestra |
| --- | --- | --- |
| Polpaico, listado de plantas/oficinas | Publica planta Los Ángeles en Ruta5 Sur km505 y La Suerte en Ruta180 km21 | Disponibilidad para este proyecto, capacidad efectiva, enfriamiento, flota, tiempos de ruta o selección de proveedor |
| Hormigones Quilancó, sitio de la empresa | Publica fabricación/distribución de hormigón y ubicación Lote15 El Maitén, Los Ángeles | Capacidad para una vertida masiva continua ni suministro a12 °C |
| Ficha inicial EIA El Rosal2023 | Identifica emplazamiento en comuna Los Ángeles y antecedentes del proyecto | No se obtuvo un rendimiento de hormigonado confirmado de esa ficha |
| RCA y expediente | Se localizaron referencias documentales oficiales | No se pudo extraer en esta consulta el detalle logístico del PDF RCA ni anexos de construcción; no atribuirles una flota/capacidad no leída |

Fuentes:

- [Polpaico, plantas y oficinas](https://www.polpaico.cl/somos-polpaico/plantas-y-oficinas/).
- [Hormigones Quilancó](https://hormigonesquilanco.cl/).
- [SEA, ficha EIA inicial](https://infofirma.sea.gob.cl/DocumentosSEA/MostrarDocumento?docId=2023%2F06%2F20%2Fdff0-cb97-455f-b4ff-8be13edfd0d5).
- [Expediente oficial2159460415](https://seia.sea.gob.cl/expediente/ficha/fichaPrincipal.php?modo=ficha&id_expediente=2159460415).
- [RCA oficial localizada](https://seia.sea.gob.cl/archivos/2026/03/10/RCA_202608101101_PARQUE_EOLICO_EL_ROSAL_FIRMADA.pdf).

Los antecedentes iniciales pueden haber sido modificados por adendas/RCA:
no inferir cantidades o cronogramas definitivos de versiones antiguas.
La distancia aproximada a la ciudad no equivale a distancia por carretera
desde una planta específica ni incluye recorridos internos del parque.

Actualización: [propuesta condicional con dos frentes](DOS_FRENTES_COLOCACION.md).
Se respaldó carga7,5 m³ y tiempos óptimos de descarga con documentos
de proveedores chilenos; capacidad de planta y ciclo local siguen pendientes.

## Cómo obtenerq efectivo

1. Identificar una planta candidata por ubicación y mezcla admisible,
   sin presentarla como contratada. Confirmar si hay planta temporal en obra
   antes de asumir transporte externo exclusivamente.
2. Establecer ruta real planta→acceso→punto de descarga; tiempos de ida y
   retorno, restricciones de camión cargado y caminos internos. No estimar
   ciclo solamente con distancia en línea recta o tiempo de automóvil.
3. Obtener capacidad asignable de producción a12 °C, carga útil y flota
   disponibles; incorporar carga, descarga, esperas y retorno en el ciclo.
4. Contrastar con bombeo, distribución/compactación y recursos de reserva.
5. Usar `q_ef=min(q_planta_asignable, N*V_util/ciclo_h, q_bombeo_ef, q_colocación_ef)`
   como comprobación de régimen; simular/lograr continuidad y documentar
   interrupciones. No descontar pérdidas dos veces si ya están en los ciclos.

## Hoja de datos para completar

| Dato | Estado actual |
| --- | --- |
| Planta/proveedor seleccionado | No definido; opciones locales identificadas |
| Planta temporal prevista dentro del parque | Sin confirmar |
| Mezcla y capacidad de suministro a12 °C | Sin confirmar |
| Ruta, distancia vial y restricciones hasta fundación | Sin confirmar |
| Ciclo completo cargado/vacío, carga/descarga/esperas |2 h es hipótesis anterior, no dato del sitio |
| Carga útil |7,5 m³ es hipótesis anterior, validar por mezcla/vehículo/ruta |
| Flota activa/reserva |16+2 es propuesta, no disponibilidad confirmada |
| Capacidad efectiva de bombeo y compactación |Sin confirmar |
| Duración garantizable y margen de contingencia |Sin determinar |

Consulta breve que el equipo puede hacer a un proveedor o al profesor:
«Para una colocación continua de aproximadamente637 m³ en el punto
−37,277929,−72,368271, ¿qué caudal efectivo podrían sostener a12 °C en
recepción, con qué carga útil, cantidad de mixers y ciclo completo, y qué
restricciones de acceso, preenfriamiento y horario habría?»
No se envió comunicación a terceros ni se solicitó cotización.

## Decisión provisional

No se encontró un rendimiento público verificado para esta colocación
particular en El Rosal.60 m³/h continúa como escenario a contrastar,
no resultado local ni capacidad certificada. Si no hay respuesta de obra,
presentar una estimación condicional de logística con sensibilidad a sus
datos; nunca cambiar la etiqueta a «rendimiento real» por haber localizado
una planta cercana. Las curvas térmicas deben calcularse para esos escenarios.
