# F02: cierre revisado con manta504h y sombra90%

**Preentrega F02:** [PPT/PDF](presentacion/README.md) y [guion](GUION_ORAL_F02.md) actualizados con el cierre. Ocho principales, índice yB01–B15;24láminas.
**Resultado técnico de cierre:** [matrices, resultados y reproducción](cierre_revision_final/RESULTADOS_CIERRE.md). La propuesta60m³/h/12°C tiene24pares completos0,20m/300s hasta672h: Tmax47,0322°C,ΔT15,7202K,Punión0 y sin alertas. La matriz gruesa60 y su vecina55 usan la misma protección y también cumplen. Auditoría72piezas/2045transiciones aprobada;se conservan336h y seguimiento672h. Entrada nueva`casos/sensibilidad_h/ejecutar_cierre_f02.py`,sin simulación por defecto. Configuración[final revisada](cierre_revision_final/CONFIGURACION_FINAL_REVISADA.json),[desarrollo de puntos5–6](CIERRE_PUNTOS_RESTANTES.md). Siete figuras,parámetros y144filas de métricas/balance disponibles en`cierre_revision_final/`. PPT/PDF y guion integrados en la preentrega: [presentación vigente](presentacion/README.md). Se conserva la estructura personalizada de6:25.

## Antecedentes de la revisión

Los textos siguientes conservan la evolución anterior. En particular,`modelo_f02.py`y`MODELO_VIGENTE.json`corresponden a la configuración anterior360h sin sombra;para reproducir el cierre revisado usar la entrada nueva y su configuración indicadas arriba.

**Nuevo ensayo de protección posterior:** [tres alternativas simuladas](proteccion_postdesmolde/RESULTADO_TRES_ALTERNATIVAS.md). La combinación última manta hasta504h de edad local+sombra solar90% posterior cumple24pares gruesos a672h, Tmax47,4941°C/ΔT16,5306K/Punión0 y sin alarmas. Tres confirmaciones finas y dos temporales también cumplen, selectivas. Las medidas por separado no cumplen. Estudio79piezas/2787transiciones auditado; no sustituye automáticamente configuración vigente ni actualiza aún PPT/guion. La sombra es idealizada y permanece hasta672h; no se acredita su retiro ni instalación real.

**Revisión en curso de la pauta:** [desarrollo de apartados1–3.3](revision_puntos_1_3/DESARROLLO_PUNTOS_1_A_3_3.md). Incluye t₀, cronograma completo, dominio/S25 e indicadores y compara24pares a336/672h. El cumplimiento336h no acredita el plan extendido:24/24excedenΔT y16conservan alarma de cola. La recomendación completa requiere revisar protección/control. PPT y guion se actualizarán después de revisar el resto deF02, según instrucción del usuario.

Se incorporan solar y onda larga, con el enfriamiento equivalente de nueve circuitos. Entrada: `casos/sensibilidad_h/modelo_f02.py`. Sin opciones consulta el estado sin simular. `--ejecutar` resuelve o reutiliza los24 pares de la candidata. `--comparar-planes --ejecutar` incluye60/55/50/45m3/h. `--malla 0.2 --ejecutar` reproduce la matriz fina de la candidata. `--auditar` revisa la evidencia.

- [Comparacion completa y resultados](COMPARACION_CIRCUITOS_FINAL.md).
- [Ecuaciones del modelo](ECUACIONES_MODELO_VIGENTE.md).
- [Interaccion real y equivalente de tuberias](INTERCAMBIO_TUBERIAS.md).
- [Guion oral actualizado](GUION_ORAL_F02.md).
- [Brief detallado de diapositivas](BRIEF_DIAPOSITIVAS_F02.md).
- [Presentacion y reproduccion](presentacion/README.md).
- [Configuracion y hashes vigentes](MODELO_VIGENTE.json).

## Evidencia actual

Ventana comun0-336h desde la primera colocacion. Cuatro matrices gruesas de24 pares a0,40m/300s y matriz fina completa de la candidata a0,20m/300s. Todas sin excedencias en14dias bajo el catalogo discreto. Candidata fina: Tmax47,0322C y diferencial15,7202K. Seis contrastes finos de alternativas y tres temporales son selectivos. Auditoria5matrices/129piezas/1161registros aprobada.

La refrigeracion usa Uvol5W/(m3K), agua uniforme18C, tope global15kW y control19/18 con cobertura. No resuelve pared de tubo, pelicula interior o agua axial. El caudal operativo18L/min por ramal no determina la extraccion del solver. Los resultados no acreditan una instalacion real ni riesgo real <=5%.

Seguimiento posterior con radiacion600-672h:24 excedencias del diferencial y16picos pendientes. No confundir ese diagnostico con el requisito14dias ni autorizar retiros posteriores por cumplirlo. La ultima manta se retira nominalmente a360h de edad local.

Resultados vigentes: `resultados/familia_radiacion_336h/`. Tablas y siete figuras: `evidencia_f02_radiacion/`. La sensibilidad inicial se conserva en [su informe](SENSIBILIDAD_RADIACION.md). Matrices sin radiacion y sus figuras permanecen como antecedentes en `resultados/comparacion_circuitos/` y `evidencia_circuitos/`.

El grupo prepara conjuntamente el informe y debe ensayar la defensa. La publicacion/SHA final y ensayo oral no forman parte de esta actualizacion. No se altero el IFC ni se fusionaron ramas nuevas.
