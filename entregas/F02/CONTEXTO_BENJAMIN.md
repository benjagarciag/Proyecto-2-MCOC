# Contexto para Benjamín y su agente

## Encargo

Cerrar la propuesta física y constructiva de F02 del grupo 6. El informe
lo escriben los tres integrantes; este encargo produce decisiones y evidencias
para Luis (solver/verificación) y Matías (escenarios/comparación/presentación).
Leer `AGENTS.md`, la pauta `Enunciados e Instrucciones/Enunciados/F02_DEFENSA_FINAL.txt`
y `entregas/F02/README.md`. No rehacer el trabajo ya documentado.

## Punto de partida

La rama del compañero hasta `6718163` está integrada. El avance publicado es
`29c2fff608054b7cc91a7800b0586f3009547dd5`. La candidata es una operación
continua de 636,775 m³ a 60 m³/h: D=10,613 h para toda la fundación.
Se adoptaron 12 °C en todas las vertidas, h horario derivado del viento,
k=2 W/(m K), suelo 15 °C y extracción volumétrica equivalente limitada
a 15 kW. Con malla 0,50 m/paso máximo 900 s, 8 fuentes ×3 climas de pesos
1/24: Tmax46,2843 °C, ΔTmax17,3681 K y P_f=0 hasta 600 h, sin alertas.
Esto todavía no prueba que los controles puedan ejecutarse en obra.

## Qué falta determinar y por qué

| Tarea del reparto | Falta determinar | Por qué importa |
| --- | --- | --- |
| B1: suministro | Si 60 m³/h pueden mantenerse con planta, transporte, descarga, compactación y reservas; y si los 12 °C son alcanzables en recepción con ese caudal | El plazo mínimo depende del caudal efectivo. Un suministro precalentado o interrumpido cambia tanto D como la historia térmica. El esquema provisional de camiones no equivale a una confirmación de planta. |
| B2: refrigeración | Circuito y equipo capaces de extraer calor del hormigón según la ley modelada; caudal, temperaturas, distribución, potencia útil y comienzo de operación | Un tope de 15 kW es una capacidad máxima del sumidero, no una extracción constante ni un equipo ya dimensionado. El modelo no resuelve tubos ni sus gradientes locales. |
| B2/L1: inicio | Cuándo se puede encender físicamente el circuito, posiblemente por zonas colocadas | El cálculo actual activa toda la única al inicio y permite enfriar desde 6 h, aunque su colocación física termina a 10,613 h. Luis necesita una regla construible para contrastarlo. |
| B3: terreno | Exposición real de laterales, contacto de base, temperatura y resistencia equivalente del suelo | No se especificó si hay relleno. Se asumió excavación abierta y suelo sin almacenamiento térmico. La sensibilidad existente muestra que cambiar estas hipótesis puede cambiar el riesgo de casos anteriores. |
| B4: propiedades | Fundamento y rango defendible de k y de la correlación convectiva; conservar ρ=2476 kg/m³ y cp=1023 J/(kg K) de la fuente | k=2 no está calibrado en esta fundación. El viento a 10 m se convierte con altura local y exposición supuestas. Escoger k o h para aprobar el límite no valida el material. |
| B5: protección | Instalación y soporte de madera 18 mm y dos mantas de 40 mm, caras cubiertas y criterio de retiro | Las edades 72/240/360 h son supuestas. Tras retirar madera debe existir soporte para mantas; humedad y discontinuidades pueden alterar su resistencia real. |
| B6: monitoreo | Sensores redundantes de núcleo/S25, ambiente y circuito, frecuencia, alarmas y respuesta | La propuesta debe detectar condiciones fuera del modelo y definir qué hacer; cumplir indicadores térmicos no demuestra ausencia de fisuración. |
| B7: cierre | Qué valores están respaldados, cuáles son supuestos y qué incertidumbres requieren consulta docente | Evita que el equipo presente decisiones provisionales como mediciones o validaciones. Las cotas/exposición faltantes no deben inventarse. |

**Aclaraciones:** h medio≈17,09 W/(m² K) es referencia; la candidata usa
su historia horaria. El sumidero usa U=5 W/(m³ K), referencia 18 °C,
encendido a 6 h de edad y apagado global a 432 h. Si se quiere una solución
sin tuberías, hay que evaluar un caso con extracción deshabilitada: bajar
la colocación a 10 o 12 °C conservando el sumidero no prueba esa alternativa.

## Evidencia a consultar

En `casos/sensibilidad_h/`: `MODELO_FISICO.md`, `VIENTO.md`,
`CONDUCTIVIDAD.md`, `SUELO_PROTECCIONES.md`, `SENSIBILIDAD_SUELO.md`
y `CONTROLES_OBRA.md`. Consultar las referencias y resultados enlazados
allí antes de buscar otras fuentes. Los estudios antiguos no son todos
de 12 °C/15 kW; conservar su procedencia.

## Entrega y coordinación

Entregar una tabla valor/unidad/fuente/supuesto/rango, un esquema de suministro
y refrigeración, croquis de protecciones y plan de sensores/contingencias.
Pasar a Luis las reglas de activación y rangos que se deben comprobar;
a Matías, recursos y restricciones para comparar planes justamente.
Se puede avanzar en paralelo con ellos. Acordar parámetros antes de las
corridas finales; no cambiar valores silenciosamente.

Trabajar preferentemente en documentos físicos y configuraciones acordadas,
en rama `codex/benjamin-modelo-fisico`. No sobrescribir resultados históricos,
propiedades IFC de práctica ni scripts con hashes para reanudar resultados.
El usuario prefiere ejecutar personalmente nuevas variantes: preparar y
explicar las corridas antes de lanzarlas salvo autorización expresa.
