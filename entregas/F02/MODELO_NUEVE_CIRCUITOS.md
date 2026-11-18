# Modelo vigente de nueve circuitos con radiacion

La entrada vigente es `casos/sensibilidad_h/modelo_f02.py`. Las ecuaciones, datos de borde y resolucion estan en [ECUACIONES_MODELO_VIGENTE.md](ECUACIONES_MODELO_VIGENTE.md), y el intercambio equivalente de refrigeracion en [INTERCAMBIO_TUBERIAS.md](INTERCAMBIO_TUBERIAS.md).

Se conserva IFC, once capas,12C,60m3/h nominales, agua18C, Uvol5 y tope15kW, control19/18 con cobertura y sin corte global432h. La radiacion se aplica al exterior de las protecciones y se resuelve su balance no lineal antes de obtener el flujo hacia las celdas. La madera y mantas siguen como resistencias sin inercia propia. La fuente tabular por edad y el suelo equivalente se conservan.

La comparacion actual de cuatro rendimientos y la matriz fina completa de la candidata usan336h desde la primera colocacion. Auditoria: cinco matrices y129piezas. Las metricas y las limitaciones estan en [COMPARACION_CIRCUITOS_FINAL.md](COMPARACION_CIRCUITOS_FINAL.md). El seguimiento600–672h anterior con radiacion es diagnostico adicional con excedencias y picos pendientes.

Se usa un solver cartesiano conservativo propio, reconstruccion de caras y S25, integracion de hidratacion y activacion progresiva. Se conserva zona refrigerable414,016m3 por pertenencia a la malla de referencia al refinar. No se calcula transferencia de pared ni temperatura axial de agua. Los trazados definen cobertura, muestreo y asignacion de celdas. La ubicacion caliente no esta fijada en el nucleo y el minimoS25 puede cambiar de cara.

Las matrices y figuras sin radiacion se mantienen como antecedentes. El conjunto de parametros y hashes vigentes esta en [MODELO_VIGENTE.json](MODELO_VIGENTE.json). No se modifican las fuentes de los ejecutores historicos para reanudar nuevas salidas.
