# Contexto del repositorio

- Presentación final19/11: usuario pidió conservar todos sus cambios, añadir ecuaciones y dejar un soloPPT. `entregas/F02/presentacion/F02_Grupo6_FINAL.pptx` es el único PPTX deF02. Base fue Bordes_resumen guardado01:23:38;24láminas y recursos originales idénticos byte por byte, nuevaB16/diap25con8ecuacionesOMML editables. Índice original intacto;accederB16al final. Eliminados6PPTprevios(incluido temporizado) yPDFanteriores;MP4/materialoficial conservados. `VERIFICACION_FINAL.json` registra conservación,estructura/geometría aprobadas y diferencias previas de serialización de gráficos;no se reescribieron ni se afirma gate exacto de caché aprobado. Sin nuevas simulaciones ni publicación. No regenerar desde versiones anteriores ni restaurar residuales sin pedido del usuario.

- Video de práctica pedido 18/11 en `entregas/F02/presentacion/video_practica/`:
  `F02_video_practica.mp4` (≈5:52) desde S1–S8 de la pre-entrega, animaciones reales
  a tiempos del guion; Benjamín sin voz (texto amarillo, quiere practicar), Luis
  es-CL-LorenzoNeural y Matías es-MX-JorgeNeural vía edge-tts (usuario aceptó enviar
  el guion al servicio). Franja inferior con hablante/texto/«▶ CLIC n». Temporizar
  por XML (`temporizar_xml.py`), NO por COM: cambiar disparadores por COM deja los
  efectos «con el anterior» en el grupo previo. Corrección autorizada 19/11 en
  `F02_Grupo6_Pre_entrega.pptx`: ids duplicados (S4 s4_tabla, S7 s7_tabla, número de
  página en S2/S3/S6/S7 y no animados en 10/15/20) renumerados por XML; ahora clics
  2-3-3-3-3-3-3-2 = guion, 247 efectos, abre en PowerPoint. Guardar con COM ese PPTX
  lo dejó ilegible (restaurado del respaldo): editar por XML. PDF sin cambios (estático).
- Preentrega F02 integrada por petición del usuario: `presentacion/F02_Grupo6_Pre_entrega.pptx/.pdf` son vigentes (24láminas:8principales+índice+15respaldos). Guion conserva intervalos personales0:00–6:25, reparto y clics;577palabras frente a597. Notas1–8 idénticas al guion. Ocho árboles de animación originales idénticos (247efectos);9gráficos nativos/libros. Se actualizaron504h+sombra90%,336/672h,60/55,0,882K espacial y0,0014K temporal selectivo. `VERIFICACION_PRE_ENTREGA.json` registra checks;24renders inspeccionados, sin ensayo oral ni reproducción de animaciones enPowerPoint. Usuario autorizó publicar main con commit `Pre-entrega F02`. Identificar SHA real con git log, sin inventarlo en el PPT.

- Cierre de §§5–6 completado por petición «finalicemos puntos restantes».
  `cierre_f02.py/.json` congelados; no editarlos para reanudar piezas.
  Familia final q55/60, mismos504h+sombra90%,672h,24pares por tasa.
  Propuesta60:24pares finos completos0.20m/300s, Tmax47.0322/Delta15.7202,
  Punion0 y0alertas; base60:47.4941/16.5306/D10.6129; base55:
  47.5128/16.6011/D11.5777;ambasPunion0 y0alertas. Salidas
  `resultados/cierre_f02/`, todas las sesiones finalizaron. Auditor
  `auditar_cierre_f02.py`:72piezas(26reutilizadas/46nuevas),3matrices,
  2045transiciones aprobadas. Cambio espacial maxDelta672h0.881712K,
  distinto de1.174621K anterior336h. Residuo max0.000247955J/rel2.39e-15.
  Documentador`documentar_cierre_f02.py`:7figuras revisadas,144filas de
  métricas y balance con fases/posiciones,CSVparámetros/fuentes exactas.
  Principal`entregas/F02/cierre_revision_final/RESULTADOS_CIERRE.md`;
  teoría/contenido`CIERRE_PUNTOS_RESTANTES.md`;config completa
  `cierre_revision_final/CONFIGURACION_FINAL_REVISADA.json`. Entrada nueva
  `ejecutar_cierre_f02.py`consulta sin simular;caso individual M4_SS2024
  fino comprobado por reutilización. No se modificaron PPT/PDF/guion
  personalizado durante este cierre técnico;integración queda pendiente.
  Se ejecutaron24tests1D,error seno0.00257143K,y verificaciones físicas.
  El caso único continuo coincide con propuesto;no hay opción más rápida
  admisible por cotaV/60. q<55 no puede mejorarD; q>60 viola recursos.

- Estudio autorizado de las tres medidas postdesmolde completado: nuevas
  salidas `resultados/proteccion_postdesmolde/`, ejecutor/config
  `casos/sensibilidad_h/proteccion_postdesmolde.py/.json`, auditor
  `auditar_proteccion_postdesmolde.py`. No editar estos hashes para reanudar.
  Mantiene60m³/h,12°C,9circuitos,18°C,Uv5/tope15kW,19/18,414.016m³.
  Tres matrices completas24pares0.40m/300s a672h: solo última manta504h,
  Tmax49.9166/Delta33.0081/Punion100%/16alertas; sombra sola tras360h,
  Tmax47.4941/Delta23.4772/Punion20.8333%(5/24)/0alertas; combinación
  manta504h+sombra90%, Tmax47.4941/Delta16.5306/Punion0/0alertas.
  Sombra ideal: tauSW0.10 en TODAS caras de aire tras retiro por edad local;
  h y cielo/LW se conservan; no se resuelve cubierta real ni su desmontaje.
  Combinación:3paresM4_SS×2023/24/25 finos0.20m/300s, maxDelta15.7202,
  Tmax47.0322;2temporales0.40m/150s cambioDelta≤0.0013651; todos sinalertas.
  Sombra sola2pares finos siguen excediendo(22.9890,21.7710):peso fallido
  mínimo8.3333% en fina, sin matriz fina completa. Auditoría79piezas,
  3matrices/2787transiciones, balances y coincidencia anterior336h aprobados.
  Informe/CSV/figuras `entregas/F02/proteccion_postdesmolde/`.
  No se cambió entrada vigente, IFC, PPT/PDF, guion o brief; usuario pide
  incorporarlo al finalizar revisión de todaF02.504h es edad probada, no
  mínimo retiro optimizado.55/50/45 no recalculados con estas protecciones.
  Cubierta permanece hasta672h; no afirmar riesgo real≤5%, instalación
  validada o cumplimiento ilimitado después de retirar sombra.

- Diálogo F02 reescrito 18/11 a pedido: tono conversacional y marcas
  «▶ CLIC n» (qué aparece y en qué frase avanzar) en `GUION_ORAL_F02.md`
  (sección «Cómo usar este guion» + S1–S8, 597 palabras ≈6:25 a ritmo lento de 110 ppm, margen ~35 s) y en las notas
  S1–S8 de `F02_Grupo6_radiacion_actualizada.pptx` (editado en sitio;
  láminas, 246 efectos y PDF sin cambios). Cifras con radiación conservadas.
  No re-ejecutar los generadores de documentación/postproceso de radiación
  sin reincorporar este diálogo, porque lo sobrescriben. Sin ensayo cronometrado.

- Revisión F02 §§1–3.3 posterior al material de presentación: usuario pide
  desarrollar pendientes ahora y modificar PPT solo después de revisar TODA
  la pauta. Desarrollo vigente en `entregas/F02/revision_puntos_1_3/`:
  documento `DESARROLLO_PUNTOS_1_A_3_3.md`, cronograma44filas, métricas24pares
  a336/672h, gráfico e inventario167archivos con hash. Ejecutor documental
  `casos/sensibilidad_h/desarrollar_revision_f02.py`, sin solver. t0 recuperado
  2026-11-19T10:00:00-03:00, America/Santiago. Todas24piezas nominales gruesas
  con radiación llegan672h: Tmax50.1885/Delta33.0074/Punion1;24ya tienen
  muestra fallida antes600h;16alertas conservadoras no acreditan máximos
  definitivos. No tratar extensión como irrelevante: pauta exige máximos
  relevantes cuando corresponde extender. Cota10.6129h de colocación y
  cumplimiento336h siguen válidos, pero programación de protección/control
  no es solución final factible acreditada para seguimiento. Requiere revisión
  física antes de afirmar cierre total. No se alteró PPT/PDF/guion/brief,
  scripts congelados, IFC ni resultados. Ensayo/traslado equipo siguen humanos.

- Actualización integral F02 con radiación pedida18/11: comparación vigente
  `entregas/F02/COMPARACION_CIRCUITOS_FINAL.md`, diálogo y brief reescritos,
  intercambio equivalente en `INTERCAMBIO_TUBERIAS.md`. Familia homogénea
  SOLO0–336h en `familia_radiacion.py/.json`; resultados separados en
  `resultados/familia_radiacion_336h/`. NO editar fuentes/config con hash.
  4planes60/55/50/45m3h ×24pares a0.40m/300s: peoresDelta
  16.530593/16.601131/16.690937/16.804644; Tmax47.494066/47.512825/
  47.534313/47.558226. Candidata60 completa24pares0.20m/300s:
  Tmax47.032242,Delta15.720233,0fallas14d bajo catálogo. Temporal3pares:
  cambioDelta máximo0.001365K; espacial24pares1.174621K. Seis refinos
  alternativos pasan14d, sin Pf fino completo de otras tasas.
  Auditor `auditar_familia_radiacion.py`:5matrices/129piezas/1161registros;
  25reutilizan métricas336h exactas previas con hash;104casos nuevos336h.
  No inventar energía por ramal336h no guardada. Figuras/tablas en
  `evidencia_f02_radiacion/` (7figuras), generadores `figuras_f02_radiacion.py`
  y `actualizar_documentacion_f02_radiacion.py`. Entrada `modelo_f02.py` y
  `MODELO_VIGENTE.json` usan la familia nueva. Seguimiento previo600–672h
  con24excedenciasDelta/16picos pendientes sigue diagnóstico posterior.
  Tubos: Uvol5/tope15kW, sin pared/contacto/película interior ni agua axial
  resueltas.18Lmin no determina transferencia numérica. Solar/LW acopladas
  simultáneamente al campo y control. Cielo/alpha/eps siguen supuestos.
  Presentación nueva `F02_Grupo6_radiacion_actualizada.pptx/.pdf` en
  `entregas/F02/presentacion/`,21láminas (8+índice+12), notas actualizadas,
  animaciones originales, tablas y9gráficos editables con libros sincronizados.
  Validación estructural/datos y renders, sin ensayo oral o ejecución de
  efectos en PowerPoint. PDF estático de renders2x con vínculos internos.
  Originales sin radiación conservados. No hubo push/fusión/cambioIFC/SHAfinal.

- Incorporación solicitada por usuario18/11: solar+LW adoptadas por defecto
  en nueva entrada `casos/sensibilidad_h/modelo_f02.py`. Selección operativa y
  hashes en `entregas/F02/MODELO_VIGENTE.json`, ecuaciones completas y comandos
  en `ECUACIONES_MODELO_VIGENTE.md`. Reutiliza exactamente motor/adaptador y
  resultados verificados de sensibilidad, variante ambas alpha0.6/eps0.9,
  albedo0.2; no modifica fuentes históricas con hash ni recalcula piezas idénticas.
  Sin opciones solo estado; --ejecutar nominal24; --escenario CURVA CLIMA,
  --malla0.4/0.2 y --paso-max300/150 permiten casos explícitos; --verificar
  acoplamiento pequeño, --auditar evidencia. Entrada F02 vigente en ambos
  README; las entradas anteriores siguen históricas, no todas ganaron radiación.
  No interpretar incorporación como matriz fina completa nueva, comparación
  nueva de cuatro rendimientos o actualización de PPTX/PDF.

- Sensibilidad a radiación solicitada y ejecutada por el usuario el18/11:
  `entregas/F02/SENSIBILIDAD_RADIACION.md` y `PROTOCOLO_RADIACION.md` son
  actualización física posterior a la comparación sin radiación. Conservados
  nueve circuitos,12°C/60m3h,U5/15kW,agua18,control19/18,protecciones72/240/360.
  Solar+LW no lineal en exterior de protecciones; alpha0.6,eps0.9 nominales
  supuestos,contrastesalpha0.2/0.9,cielo despejado,giro90. ERA5 complementario
  DNI/DHI/rocío/nubes en `datos/clima/radiacion/`; aire/viento/GHI idénticos.
  24 pares nominales0.40m/300s: Tmax336h47.4941,Delta336h16.5306,0fallas14d;
  seguimiento600–672h Tmax50.1885,Delta33.0074,24excedenciasDelta,16alertas
  de pico pendiente: máximos posteriores observados, no definitivos. No confundir
  falla posterior con requisito14d. M4_SS×2024 confirmado0.20m/300s:
  Tmax336h46.5397,Delta336h15.7187,Delta672h29.1367; aumentoDelta14d0.4180K
  frente al mismo par fino sin radiación. Temporal0.40m/150s Delta336h16.5292,
  Delta672h32.0649. Confirmación selectiva, NO matriz fina24 con radiación.
  M4_SS×2024 alpha0.2/0.9 Delta14d15.0048/18.3322. Efecto posterior fuerte
  tras última manta360h de edad. No declarar radiación despreciable ni riesgo
  real<=5%. Auditoría43piezas/2207registros aprobada (2piezas reutilizadas).
  Nuevos scripts `radiacion_*.py`, `sensibilidad_radiacion.py`,
  `agregar_radiacion.py`, `auditar_radiacion.py`, `figuras_radiacion.py`,
  `redactar_radiacion.py`; resultados separados `resultados/sensibilidad_radiacion/`.
  No editar runner/borde/config con hashes. Agregador separado corrige campo
  clima omitido en agregado336h interno; usarlo y excluir matriz.json al glob
  M*.json en Windows. Cuatro rendimientos NO reevaluados con radiación.
  Advertencias en README, comparación, modelo, cierre, guion, brief y README
  de presentación; PPTX/PDF binarios no actualizados en esta prueba.

- Presentación F02 construida 18/11 en `entregas/F02/presentacion/`: PPTX
  animado (8 principales, índice, B01–B12, 246 efectos, ecuaciones OMML,
  notas con diálogo) y PDF estático, elegidos por el usuario: PowerPoint,
  estilo mixto oscuro/claro, texto mínimo, ecuaciones en formato matemático.
  Gráficos desde datos existentes; sin nuevas simulaciones. Abierto y
  exportado con PowerPoint vía COM; no se revisó en modo presentación ni se ensayó.

- Preparación oral/diseño solicitada18/11: dos archivos vigentes en
  `entregas/F02/GUION_ORAL_F02.md` y `BRIEF_DIAPOSITIVAS_F02.md`.
  Guion≈820 palabras,8principales/420s: BenjamínS1–S3(140s), LuisS4–S5(135s),
  MatíasS6–S8(145s), dos relevos;35preguntas con énfasis físico y supuestos.
  Brief para otra IA:8principales+12consultas, estilo/maquetación/texto,
  animaciones causales por clic, notas, fuentes actuales, honestidad de
  malla/horizonte/escenario y PDF estático completo. No se creóPPTX/PDF,
  no se implementaron animaciones ni se ensayó oralmente. No correr
  nuevas simulaciones para este material. Reparto expositivo no implica
  autoría exclusiva ni que cada uno pueda ignorar los otros bloques.

- Comparación homogénea F02 cerrada18/11 por solicitud explícita del usuario,
  excluyendo respaldo final/SHA/ensayo. Conservar nuestros9circuitos18°C,
 18L/min por ramal,162L/min con bypass, U5/tope15kW, control19/18 y cobertura,
  sin corte432h. `COMPARACION_CIRCUITOS_FINAL.md` en `entregas/F02/` es
  evidencia vigente:4planes60/55/50/45m³h ×24pares a0.40m/300s, todos0fallas.
  D10.6129/11.5777/12.7355/14.1506h; peoresDelta19.3581/19.3692/19.3759/19.3750.
  Candidata60 con24pares completos0.20m/300s: Tmax46.0192,Delta336h15.3013,
  Delta600h19.1731, Pf0 bajo catálogo,sin alertas; mayor cambio pareadoTmax0.0785,
  Delta0.7607. Temporal0.40m/150s sigue selectivo3pares, cambioDelta≤0.0038.
 6contrastes finos de alternativas, todos bajo20 (máx19.4666), NO Pf fino
  completo para otras tasas. Auditoría5matrices/4.700transiciones aprobada.
  Resultados `resultados/comparacion_circuitos/`, ejecutor `comparar_circuitos.py`,
  config `familia_circuitos.json`, auditor `auditar_familia_circuitos.py`;
  no editar scripts/config con hash para reanudar. Figuras/tables en
  `entregas/F02/evidencia_circuitos/`, modelo en `MODELO_NUEVE_CIRCUITOS.md`.
  Luis07d6c035 yMatías ed866323 consultados por GitHub y capturados en
  `insumos_equipo.json`; integración documental, sin fusión/publicación de ramas.
  No volver a pedir matrices ya calculadas ni presentar las antiguas como
  actuales. IFC no alterado;12°C/cronograma son overrides externos del plan,
  IDs térmicos1..11 son capas, no11objetosIFC. Mantener alcance idealizado
  y sin validación de transferencia real, mezcla o riesgo real≤5%.

- Usuario eligió conservar nuestros nueve circuitos y autorizó cerrar todos
  los puntos de su parte, incluidas simulaciones necesarias. Propuesta vigente
  en `entregas/F02/CIERRE_BENJAMIN.md`, tabla `PARAMETROS_BENJAMIN.csv`,
  `CONFIGURACION_BENJAMIN.json` y croquis `PROTECCIONES_BENJAMIN.png`.
  B1–B7 documentados para alcance docente:60m3/h/12°C,11capas, ventana de
  unión150min como condición de aceptación NO ensayada, retiros72/240/360h
  sujetos a resistencia/monitoreo/predicción, sensores/contingencias y
  criterios de liberación sin fecha no calculada. Agua uniforme18°C ideal,
  U5/tope15kW no dimensionan instalación real. No reemplazar por3sectores,
 43Lmin ni corte432h propuestos en rama de Luis. Ramas de compañeros
  revisadas vía GitHub; no fusionadas en esta tarea. Confirmación selectiva
  espacial0.20m/300s y temporal0.40m/150s en `confirmar_circuitos.py`;
  preserva zona refrigerable414.016m3 por pertenencia al voxel0.40m y
  tiempos físicos11capas. Resultados separados bajo `circuitos_confirmacion`.
  No interpretar subconjunto refinado como matriz completa o riesgo fino.
  Completadas seis corridas de confirmación, sin alertas:Delta máximo
 19.3618K temporal,19.1731K espacial. Mayor cambio temporal0.0038K,
  espacial absoluto0.7607K (otro par sigue bajo20). Auditoría268 cambios
  de estado aprobada. Tabla `entregas/F02/CONFIRMACION_CIRCUITOS.md`.

- Control por circuito ejecutado explícitamente a petición del usuario el
  18/11/2026: `casos/sensibilidad_h/simular_circuitos.py` y
  `control_circuitos.py`, resultados `resultados/circuitos_histeresis/`.
  Nueve circuitos: cobertura previa, abre mínima muestreada≥19°C, cierra≤18°C,
  agua18°C,18L/min por ramal abierto,162L/min total con bypass; sin apagado
  global432h. Colocación12°C/60m³h,11capas, malla0.40m/dtmax300s,
  máscara refrigerable414.016m³ distinta de366m³ anterior, U5/tope15kW.
  24 pares completos600h sin alertas: Tmax46.0454,Delta336h14.9147,
  Delta600h19.3581; margen extendido0.6419K pendiente de refinamiento.
  Auditoría aprobada941 transiciones. P_f0 solo bajo catálogo discreto,
  no garantía estadística real≤5% ni validación física de tubos/caudal/U.
  Detalles en `casos/sensibilidad_h/CIRCUITOS_HISTERESIS.md` y figura
  `resultados/circuitos_histeresis/control_y_temperaturas.png`.
  La autorización fue para estas corridas; mantener preferencia general
  del usuario por ejecutar personalmente variantes futuras.

- Decisiones posteriores F02: profesor permite tubos y escenario ideal
  de60 m³/h (dos frentes30), según usuario. Retomada candidata12°C/15kW;
  los estudios sin extracción son alternativas, no propuesta vigente.
  Usuario permite agua idealizada18°C y pidió definir caudal/circuitos/capas,
  dejando habilitación/regulación/apagado para después. Anteproyecto en
  `entregas/F02/CIRCUITOS_Y_CAPAS_ADOPTADOS.md`:9 ramales paralelos18L/min
  cada uno, total162L/min nominal, diámetro interior de cálculo25mm,
  cotas0.5/1.5/2.5/3.8m con3/3/2/1 circuitos; capas físicas≤0.40m.
  Esquema leído delIFC,≈639m internos,11capas,10.613h a60. No modifica
  IFC ni solver; no calibraU5/máscara366m³ ni acredita15kW reales. Debe
  revisarse montaje, hidráulica, trabajabilidad y adaptar activación de capas.
  No confundirlo con estratos0.50m ni atribuir cumplimiento antiguo al diseño.

- Avance integrado F02 del 18/11/2026: main incorpora por fast-forward la
  rama `f02-verificaciones-complementarias` hasta `6718163`. El usuario
  autorizó publicar main con mensaje `Avance miercoles entrega final`.
  Estado y comandos en `entregas/F02/README.md`; pendientes humanos de
  Benjamín/Luis/Matías en `entregas/F02/PENDIENTES_EQUIPO.md`, informe conjunto.
  Sensibilidades en `casos/sensibilidad_h/` reconstruyen automáticamente
  base congelada 6718163 en `.venv/cache/f02_sensibilidad_h` mediante Git.
  No modificar los scripts históricos con procedencia hash para reanudar
  sus salidas; usar otra salida si cambian. Última candidata única a 12 °C
  exactos/15 kW/h horario: 24 pares, 0,50 m/900 s, 600 h, sin alertas,
  Tmax46,2843/DeltaT17,3681 y P_f0 bajo catálogo discreto. Es exploratoria:
  faltan confirmación de malla/tiempo, activación/control construibles y
  comparación final. Los otros tres planes a12°C/15kW están habilitados
  en `colocacion_12c.py`, aún no ejecutados. No confundir resultados antiguos
  de12kW o12,231833°C con este caso. Mantener preferencia de ejecución
  personal; no lanzar nuevas simulaciones al integrar/publicar.

- E12 cerrada el 13 de noviembre de 2026 en `Reportes/Reporte_E12.md`, bajo
  1400 palabras, con figuras leídas de resultados existentes (sin nuevas
  simulaciones del agente). Corridas del usuario del 12/11: 336 h, mallas
  0,50/0,25 m; madera 18 mm/k0,158 (referencia de familia AraucoPly) y lana
  Aislanglass 40 mm/k0,042, capas solo laterales, retiros por edad 72/96 h
  aún docentes. Tmax62,167/61,821 °C, DeltaTmax43,264/43,156 °C: no satisface
  diferencial. Clima ERA5 2025 por hora relativa a escenario hipotético 2026;
  no es forecast de obra. Comparación 50 mm guardada separada, no elegida.
  Scripts Semana4 con menú Run Python File; visor PyVista pregunta caso,
  malla y estado. Generador HTML añade definiciones por ecuación y guardado
  con reintentos de bloqueos Windows, conservando temporal si persisten.
  `figuras_reporte_e12.py` regenera curvas/capturas sin solver. Vista previa
  `Reportes/Reporte_E12.html` eliminada por solicitud; no recrearla.
  Usuario autorizó publicar main con mensaje `Entrega E12`; identificar SHA
  con git log, no usar el SHA base de los resúmenes. Apuntes personales de
  `Estudio_entregas/` siguen excluidos. Mantener preferencia del usuario de
  ejecutar personalmente variantes numéricas.

- E08 implementada el 5 de noviembre de 2026 en la entrada existente
  `Visualizadores/E07.html` (encabezado E08). La plantilla y el motor compartidos
  conservan sus nombres e07. Tabla de secuencia editable con Aplicar/Restaurar IFC,
  visibilidad individual solo gráfica y guardar/cargar escenarios JSON.
  Fuente de hidratación exponencial directa q0 [W/m³], tau [h], integrada
  exactamente por paso y acoplada a conducción/bordes del navegador. Default900/30
  equivalente al ejemplo Python; no volver a presentar derivación adiabática,
  calibración ni cinética dependiente de T. IFC/BIM y solvers Python conservados.
  Pruebas JS E07/E08 aprobadas, incluida corrida IFC 0,5m/336h con hidratación;
  Tmax61,778214 didáctica. No pytest completo ni revisión visual de navegador:
  su política bloqueó archivos locales. Guía en entregas/E08/README.md.
  El usuario autorizo publicar en main con el mensaje de commit `Entrega E08`.
  Identificar el SHA con git log; no confundir SHA base del HTML con entrega.

- E07 HTML actualizado por solicitud del usuario: `Visualizadores/E07.html` es
  autónomo; fuentes `e07_plantilla.html`, `e07_termico.js` y `exportar_e07.py`.
  El profesor aún no explicó la conversión de curva adiabática a fuente: no
  volver a exponer esa derivación en el HTML. El calor interno se ingresa
  directamente en W/m³. El navegador resuelve conducción cartesiana sobre la
  máscara IFC bajo botón, con activaciones y bordes D/N/R por orientación,
  Tmax/Tmin de centros+caras y balance conservativo. Parámetros didácticos;
  no afirmar predicción real, validación de malla, S25 o confiabilidad.
  Reproducción hasta 336 h, ×10 más rápida después de 30 h. Los cambios de
  parámetros invalidan resultados. Pruebas opcionales propias en
  `desarrollo/tests/test_e07_termico_web.cjs`; se verificaron en esta tarea,
  sin volver a ejecutar pytest ni modificar solvers/BIM/IFC anteriores.
  El usuario autorizó publicar en main con commit `E07 entrega`.

- Unificación solicitada tras mostrar el caso al ayudante: la única entrada del visualizador está ahora en `Visualizadores/visualizador.py` (carpeta raíz pedida explícitamente por el usuario, fuera de E05). Contiene los once casos existentes. Se trasladaron sin cambios los parámetros a `Visualizadores/parametros.json`, documentación detallada a `Visualizadores/BARRA_3D.md` y se escribió `Visualizadores/README.md`. Se retiró el lanzador duplicado y la carpeta `casos/e05` (solo quedaba caché); no recrearla. Núcleo renombrado a `desarrollo/mcplan/visualizador_termico.py` y `barra_fuente_3d.py`, imports/tests/índices actualizados. Futuras movies solo bajo botón a `resultados/visualizadores/<caso>/evolucion.mp4`; resultadosanteriores conservados. Abrir no calcula nada. No ejecutar pruebas/casos por el usuario; solo validación de sintaxis/importación/controles en esta reorganización. Las referencias anteriores a las rutas E05 son históricas y quedan reemplazadas por esta nota. Ventanas antiguas deben cerrarse y reabrirse en nueva ruta para evitar guardar en la ubicación retirada.

- Entradas vectoriales solicitadas: GUI E05 agrupa dimensiones(x,y,z), malla(Nx,Ny,Nz), centrofuente, tamañofuente y observación en un campo porvector; tablaParámetros también agrupada. Ejemplos(0,0,0), (1,1,1), (15,15,31), decimales conpunto. Parserast.literal_eval exige3números finitos y mallaentera. ClavescomponentesdelJSON/solver conservadas. Solo se verificó parser/GUI con datos de entrada, no simulaciones.

- Panel E05 pedido por usuario: resultados y parámetros en Treeview separados, con pestañas Resultados/Parámetros/Notas. Verificación numérica independiente de límites docentes. Barra3D ahora evalúa a cada paso Tmax y DeltaT=TmaxOmega−TminS25, límites70/20, sin recortarT. S25 en seis planos a25mm y aristas del cubo interior, interpolación entre centros/caras físicas, Tmax incluye reconstrucción del contorno. Defaultcentros≈100mm => valoresestimados con nota de refinamiento. Tabla marca Dentro(estim.)/EXCEDE(estim.), tiemposmáximos, TminS25, resolución y horizonte48h vs336h comoPARCIAL. No se afirma cumplimiento14d/ausencia grietas ni probabilidades. Módulo `criterios_termicos.py`; pruebas `test_criterios_termicos.py` para usuario. Solo se comprobaron sintaxis, casos sintéticosS25 y tablas; no solver/pytest delusuario. El panel previo aún no evaluaba límites: esta actualización los añade explícitamente.

- Preferencia visual E05 actualizada: Cortes interiores es la vista principal; Volumen3D queda secundaria porque oculta la fuente. Reproducción usa caché/blit en cortes y objetivo25fps, reloj continuo12s porhistoria, pausa cancela callbacks para evitar buclesduplicados. Interpolación temporal solo visual (incluida movie25fps); solver/dt/tests no cambian. Arrastrarselectorpausa. Verificación de dibujo con campos sintéticos: interpolación/caché correctas y≈19,82ms/cuadro en comprobación local; no se ejecutaron los casos numéricos del usuario. Es necesario reabrir la ventana para cargar estas mejoras.

- Vista volumétrica solicitada para la barra 3D: `Visualizador_E05.py` permite alternar Volumen3D/Cortes interiores y Superficies físicas/Celdas exteriores. Dibuja las seis caras con Poly3DCollection, colores por celda, cámara girable y botóncarasopuestas; actualiza colores sin recalcular ni resetear cámara. Helperpuro `vista_caras_3d.py`. Se distingue temperatura de cara Dirichlet constante20/30 de centro vecino; Neumann0 extrapolaTc y Robin reconstruyeTface20+(Tc−20)/(1−beta*d/2). Movie guarda vista/cámara elegidas. Solo se verificó sintaxis y render con datos sintéticos en caché, no se ejecutaron las simulaciones/tests del usuario ni se generaron resultados físicos.

- Caso 3D específico para E05 solicitado el 29 de octubre: abrir `casos/e05/Barra_3D_E05.py`. Largo x3m/ancho y3m/alto z6m, origen centrado, inicial20 °C. Cuatro modos nuevos en la ventana: barra_d20, barra_d30 (todas las caras Dirichlet20/30), barra_n0 (Neumann cero), barra_beta. Usuario eligió fuente localizada en zona alrededor del centro, con posición y tamaño editables; beta debe ser editable. Se conserva literalmente dT/dn=beta*(Tsuperficie−20) con normal exterior: beta<0 pasivo h=−k beta, beta0 adiabático, beta>0 introduce calor paraT>20. Defaultbeta−5 1/m es elección editable; no se afirma que usuario eligió enfriamiento ni otra convención de normal. Fuente inicial caja1×1×1m en0, Qmax5001 W/m³, pulso12h/horizonte48h editables, material anterior, malla15×15×31, dt300s. Observación xyz independiente de centrofuente; Q en punto exacto según caja, T por interpolación trilineal con limitación cerca de caras documentada. Cortes siguiendo observación, gráficaQfuente/Qpunto yTobservada. Fuente en celdas ponderada por intersección volumétrica. `fuente_temporal_3d.py` extiende balances con integral temporal exacta; `barra_e05_3d.py` prepara fuente/bordes. Beta exterior exige beta*d/2<1 y tiene cota de dt con valores absolutos; beta>0 puede crecer por la ley aun con dt pequeño. Tests nuevos en `test_barra3d_fuente.py` NO ejecutados; solo sintaxis/importaciones por preferencia del usuario de ejecutar él mismo. Guía `casos/e05/BARRA_3D.md`. No se generaron resultados ni se corrieron simulaciones al preparar/abrir la ventana.

- Preferencia de estudio E05 aclarada por el usuario: quiere ejecutar personalmente los tests, modificar parámetros y entender el resultado; no correr automáticamente las variantes por él. Se creó `casos/e05/Visualizador_E05.py`, ventana Tkinter/Matplotlib con siete casos, parámetros editables, ejecución bajo botón, resultado del test y reproducción/pausa/selector temporal. Apertura sin simulación. Cortes XY/XZ/YZ en3D, mapa2D y perfil1D. Entradas guardadas solo al ejecutar en `casos/e05/parametros.json`; cálculo/verificación compartidos en `desarrollo/mcplan/visualizador_e05.py` y `desarrollo/tests/test_e05_visualizador.py`. Exporta movie solo al pulsar Guardar movie a `resultados/e05/<caso>/evolucion.mp4` o GIF. Casos no sinusoidales permiten2D/3D; 1D usa alpha directo,2D/3D k/rho/cp. Solo se validaron sintaxis/importaciones y Tkinter; NO se ejecutaron los siete nuevos tests ni las simulaciones. Recuento anterior296 verificados; los siete casos nuevos no están verificados numéricamente aún. Ventana abierta para que el usuario empiece. Guía en `casos/e05/README.md`.

- Práctica E05 del 29 de octubre: se ejecutaron por separado los siete grupos del enunciado (35 instancias originales aprobadas) y se agregó `desarrollo/tests/test_e05_parametros.py` con 29 variantes editables: seno1D/2D/3D, adiabático no uniforme, fuente uniforme, Neumann, Robin y rechazo de pasos en1D/2D/3D. Con `pytest -q -s` imprime parámetros/errores/balances, sin exportar resultados. Propiedades sintéticas para ejecutar rápido; referencias analíticas y balances independientes. Guía con comandos, resultados y preguntas en `entregas/E05/README.md`. Batería completa actual:296 tests aprobados. No se generaron figuras ni se modificaron solvers. README principal y README_TESTS actualizados. SHA de E05 pendiente; siguen existiendo cambios locales no confirmados.

- Restauración solicitada el 29 de octubre: `casos/2d/Ejecutar_2D.py` vuelve al ejemplo anterior a las modificaciones: placa 1×1 m, espesor1 m, malla30×30, inicio20+50*sin(pi*x/Lx)*sin(pi*y/Ly), cuatro caras20 °C, sin fuente, tf24h, dt automático180 s (límite200 s), k2/rho2400/cp900. Se conserva el caso de barra4×2 m moviendo su ejecutor a `casos/2d/Barra_Enfriamiento_2D.py`; tests y demo de inestabilidad apuntan a ese archivo. La fuente temporal sigue separada. No se regeneraron resultados al restaurar el código; las figuras y películas existentes corresponden a ejecuciones previas hasta ejecutar de nuevo el caso correspondiente. Esta nota reemplaza las referencias anteriores a `Ejecutar_2D.py` como barra4×2 m.

- Fuente temporal 2D solicitada el 28 de octubre: caso separado `casos/2d/Fuente_Temporal_2D.py`, barra 4 × 2 m, inicio/contorno 20 °C, propiedades didácticas k=2/rho=2400/cp=900, dx=dy=0,10 m, dt=300 s, horizonte 48 h. Usuario eligió duración principal del pulso 12 h. Q(t) uniforme en W/m³, coseno elevado Qmax/2*(1-cos(2*pi*t/D)) hasta D y cero después. Nuevo módulo `fuente_temporal_2d.py` reutiliza conducción e integra Q exactamente por paso; protección de estabilidad conservada. Qmax umbral central (máximo durante 48 h) ≈5000,37 W/m³; usando 5001 alcanza 70,006 °C a 11,9167 h, queda 64,027 °C a 48 h. Se comparan amplitudes, duraciones 12/24/48 y formas coseno/triangular/constante a igual energía. Salidas autorizadas fijas `resultados/2d/fuente_temporal/pulsos_y_temperatura.png` y `formas_y_campos.png`. Refinamiento conjunto 80×40/dt75 da umbral5000,18 (cambio0,0037 %). No es hidratación calibrada. Caso previo de enfriamiento conservado; su dt actual fue editado por el usuario a1800 s.

- Ejemplo 2D modificado por petición del usuario el 28 de octubre: `casos/2d/Ejecutar_2D.py` usa barra de 4 × 2 m, origen en el centro, interior inicial uniforme a 20 °C y cuatro caras Dirichlet a 10 °C desde t>0, sin fuente. Conserva k=2, rho=2400, cp=900 didácticos. Malla 81 × 41, dt=360 s; estabilización práctica `max|T-10| <= 0.1 K` a 495 h (20.625 días), Tmáx final=10.099900 °C. Por solicitud explícita se ejecutó y generó `perfiles_temperatura.png`, `temperatura_centro.png` y `evolucion_temperatura.mp4` en `resultados/2d/base/`, actualizados en el mismo sitio. Película con cuadros en horas exactas 0..495 a 10 fps; FFmpeg requerido para MP4, GIF con Pillow como alternativa. La solución sinusoidal anterior queda como verificación del solver en tests y documentación histórica; no aplicarla a este inicio uniforme. Seis pruebas adicionales en `test_barra_2d.py` verifican serie de Fourier, criterio, muestras horarias y entradas inválidas. El solver y el BIM no se modificaron.

- Práctica E02 del 21 de octubre: demo Bonsai→IFC→Python realizada. Se leyó Vertida_01 a 18 °C desde disco, se cambió TemperaturaColocacion_C a 19 °C mediante operadores de edición de Psets de Bonsai, se comprobó que disco conservaba 18 antes de guardar, se guardó el IFC y un proceso Python independiente leyó 19 con el mismo GUID 31Auww6L95uPtdfMwkzuh4. El IFC actual conserva 19 °C en Vertida_01 como dato de práctica, no como decisión validada; las demás siguen a 18 °C. No sobrescribir este valor al completar propiedades. Evidencia explicada en desarrollo/fundacion/README.md. El usuario pidió avanzar paso a paso: siguiente etapa pendiente es ejecutar el solver 1D, después variar Delta x/Delta t y explicar resultados. No se ha creado ni publicado un commit E02.

- Archivos de fundación unificados por petición del usuario: conservar un solo `desarrollo/fundacion/fundacion.blend` (fundación, hormigón, pasto, iluminación y cámara) y un solo `desarrollo/fundacion/fundacion.ifc` (geometría, GUID y siete propiedades de las cinco vertidas). Se eliminaron las copias de presentación, las `.blend1` redundantes y el IFC separado con sufijo `_props`. Bonsai y el .blend apuntan a `fundacion.ifc` con vínculo relativo. No recrear variantes de trabajo sin petición explícita. `agregar_propiedades.py` actualiza el mismo IFC de forma predeterminada, completa solo campos faltantes y conserva valores existentes; usa escritura temporal y reemplazo al terminar. `verificar_ifc.py` lee `fundacion.ifc` sin modificarlo. Verificada la conservación de nombres, GUID, propiedades y geometrías; prueba temporal de actualización idempotente y de conservación del archivo ante nombres inválidos aprobada.

- Punto 25 de Bonsai realizado: `desarrollo/fundacion/verificar_ifc.py` lee el IFC con propiedades, exige cinco IfcFooting y siete campos por vertida, triangula e imprime GUID, psets y bounding boxes en metros. Verificado el 21 de octubre: IFC4, dimensiones globales 18 × 18 × 4.30 m, base z=0, cinco geometrías legibles. Resumen en README de fundacion/. Esta lectura básica no valida solapes, estanqueidad o todas las cotas; la demo de cambios Bonsai→IFC→Python aún está pendiente. No genera archivos ni modifica el IFC.

- Avance BIM del 21 de octubre: `desarrollo/fundacion/fundacion.ifc` es IFC4 en metros, con cinco IfcFooting nombrados Vertida_01 a Vertida_05. El punto 23 de GUIA_BONSAI_FUNDACION.md se implementa en `desarrollo/fundacion/agregar_propiedades.py`. IfcOpenShell 0.9.0.post1 está instalado en .venv y fijado en requirements.txt con sus dependencias nuevas. Las siete propiedades del set custom UANDES_HormigonMasivo siguen el ejemplo de §24: Inicio_h=0/6/12/18/24, temperatura=18 °C, M1, moldaje/aislación=TBD, retiro=72 h. Son valores docentes, no decisiones validadas; Inicio_h es un inicio planificado relativo y la referencia temporal de RetiroMoldaje_h queda por aclarar. La validación geométrica detallada y la demo de cambios Bonsai→IFC→Python siguen pendientes.

- Proyecto docente del grupo 6: planificación de vertidas de hormigón masivo mediante simulación térmica y confiabilidad. Entorno Python 3.12 con dependencias fijadas en `requirements.txt`, incluido JupyterLab. Solver propio `desarrollo/mcplan/difusion_1d.py` (difusión sin fuente, Dirichlet independientes y constantes), caso `casos/1d/ejecutar.py` con entradas JSON y 31 tests en `desarrollo/tests/test_difusion_1d.py`. Cuaderno ejecutado `documentacion/explicacion_solver_1d.ipynb`. Los comandos y el índice están en el README. Faltan IFC/Bonsai y preparación oral para E01; Los ejemplos Neumann/Robin y calor interno están incorporados en desarrollo/mcplan/ejemplos_1d.py y en el ejecutor; aún no hay hidratación.
- Caso base adoptado el 20 de octubre: script del video `casos/1d/codigos/01_1d_dirichlet_verification.py`. Interior inicial 20 °C, extremos 0/10 °C, L=1 m, alpha=1e-4 m²/s, 101 nodos (100 intervalos), r objetivo=0.45, tf=4500 s. `casos/1d/parametros.json` reproduce sus entradas. Alpha se ingresa directamente; no inventar k/rho/cp. El paso se ajusta uniformemente al final como en el script; el paso propuesto inestable se rechaza.
- Verificación independiente: `casos/1d/verificacion_seno.json` reproduce §7 de la guía extensa (extremos 20 °C, amplitud 50 K, tf=1500 s). No aplicar su solución exacta al caso uniforme del video. El estado estacionario lineal del video no es su solución transiente ni una medida de error numérico. Tests comparan los 20 perfiles originales y verifican separadamente el seno analítico. Guías G00–G08 y guía extensa disponibles en `Enunciados e Instrucciones/Guias/`; el material recibido está disponible extraído; los ZIP ya no están presentes.
- Verificación: `.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider`; ejecutar caso: `.\.venv\Scripts\python.exe casos/1d/ejecutar.py`; verificar seno: agregar `--parametros casos/1d/verificacion_seno.json`; abrir Jupyter: `.\.venv\Scripts\python.exe -m jupyterlab documentacion/explicacion_solver_1d.ipynb`. Por petición del usuario, NO crear una carpeta por ejecución: `ejecutar.py` actualiza los mismos archivos en `resultados/1d/base/` o `resultados/1d/verificacion_seno/`. `ejecutar.py` sin opciones ejecuta los cuatro casos y agrega las carpetas fijas neumann/, robin/ y calor_interno/. `--caso` permite elegir uno; con --parametros y sin --caso se ejecuta solo Dirichlet. `--salida` reutiliza la carpeta indicada; para todos contiene una subcarpeta por caso. Por petición del usuario se genera ÚNICAMENTE perfiles_temperatura.png en la carpeta fija de cada caso. No generar CSV, gráficos adicionales ni README de resultados. Por petición posterior del usuario, guardar las MISMAS figuras de casos/1d/codigos: el ejecutor sin cambios de parámetros llama directamente a esos scripts sin ventanas; Robin incluye sus dos paneles originales. Los scripts individuales también guardan su figura en la carpeta fija correspondiente antes de mostrarla. Con JSON/overrides, el ejecutor mantiene el modo parametrizable de perfiles. NO exportar fuentes/, metadatos.json, historia.npz, metricas.json ni parametros.json. Conservar los JSON de entrada en casos/1d/. El historial y los errores se calculan en memoria, sin exportaciones adicionales. El refinamiento inicial del seno mantiene r objetivo; el estudio espacial y temporal independiente está pendiente.
- Organización simplificada: seis carpetas raíz de trabajo: `casos/` (ejecuciones y parámetros), `documentacion/` (física y notebook), `entregas/` (evaluaciones), `Enunciados e Instrucciones/` (material recibido), `resultados/` (salidas generadas al ejecutar) y `desarrollo/` (paquete `mcplan`, tests y ejecutor del notebook). El README es el índice principal. No recrear carpetas de etapas futuras solo con un README; `datos/` y `modelos/` se eliminan hasta que exista contenido real. El caso 1D se explica en `documentacion/caso_1d.md` y el estado de E01 está en `entregas/E01/README.md`. Los cuatro scripts están en `casos/1d/codigos/`; conservan su cálculo y gráficos y se ajustó solo el guardado a resultados/ y la posibilidad de ejecutarlos sin ventana. Las guías y scripts recibidos se conservan extraídos; los ZIP ya no están presentes. Por petición explícita del usuario se eliminó TODO el contenido de `resultados/`, incluidos históricos, README y copias de código. Mantener la carpeta vacía hasta que el usuario ejecute los casos; no regenerar resultados como parte de verificaciones posteriores sin que lo pida. No crear .gitkeep ni README dentro de resultados.
- Mantener limpia la raíz: `.venv` contiene las dependencias, se conserva y tiene atributo oculto en Windows. Las cachés de Matplotlib/IPython/Jupyter se configuran en `.venv/cache/`; no generar `.tmp/`, `.ipython/` ni `.matplotlib/` en la raíz. `desarrollo/ejecutar_notebook.py` ejecuta y guarda el cuaderno. `pytest.ini` raíz usa `testpaths=desarrollo/tests` y `pythonpath=desarrollo`. El ejecutor de casos agrega `desarrollo/` al import path. Conservar requirements.txt, pytest.ini, .gitignore y AGENTS.md en la raíz como archivos de configuración.
- Preferencia del usuario para `documentacion/explicacion_solver_1d.ipynb`: los códigos de clase son la base del trabajo, sin narrativa de comparación entre "nuestro código" y "el del profesor". El notebook explica directamente los cuatro scripts (Dirichlet, Neumann, Robin y calor interno), con bloques numéricos tomados de los archivos recibidos, ecuaciones, unidades y gráficos ejecutados. No importa `mcplan` ni ejecuta comparaciones o pytest. Los tres ejemplos adicionales también están implementados en desarrollo/mcplan/ejemplos_1d.py, conservando sus actualizaciones; el notebook mantiene su explicación directa. Explicar fielmente la inicialización Neumann (borde impuesto desde el primer update), los muestreos Robin y la fuente `r*Q0`, cuya tasa efectiva es `alpha*Q0/dx**2`; no etiquetar Q0 directamente como W/m³.
- La fuente principal es `Enunciados e Instrucciones/Instrucciones/Proyecto 2 - Introducción General.txt`; consultar también `Caso base, criterios y referencias.txt` en esa carpeta antes de modificar hipótesis físicas. Los comandos `mcplan ...` del enunciado son ejemplos del flujo final esperado, no una CLI implementada.

## Restricciones de implementación

- Flujo exigido: Bonsai/Blender → IFC → IfcOpenShell → geometría y propiedades → voxelización → solver. El solver debe funcionar sin depender del estado interno de Blender; el IFC representa construcción y propiedades, no el campo de temperatura.
- El núcleo numérico debe ser propio, con grilla cartesiana regular y balance térmico por celda (diferencias finitas/volúmenes finitos cartesianos). Un solver externo como Kratos, ANSYS u OpenSees no puede sustituirlo.
- Cada vertida debe ser identificable en IFC y aportar información equivalente a `VertidaID`, `TipoHormigon`, `InicioPlanificado`, `TemperaturaColocacion_C`, `Moldaje`, `Aislacion` y `RetiroMoldaje_h`.
- La geometría de referencia es aproximadamente 18 × 18 m, espesor 3,30 m y parte superior cilíndrica de diámetro 7 m. Las cotas faltantes requieren geometría oficial/validación docente; documentar simplificaciones, sin inventar dimensiones silenciosamente.

## Clima y criterios de evaluación

- Sitio del grupo 6: Los Ángeles, Biobío, Parque Eólico El Rosal. Usar exactamente latitud `-37.277929`, longitud `-72.368271` en todos los scripts meteorológicos salvo autorización docente. Fuente: `Enunciados e Instrucciones/Instrucciones/Sitios de construcción por grupo.txt`.
- Horizonte: 14 días desde la primera vertida. El inicio hipotético corresponde a la entrega/defensa final, cuya fecha sigue TBD en los documentos.
- Límites docentes: `Tmax <= 70 °C` y `Delta Tmax <= 20 °C`. Definición operacional: `Delta T(t) = Tmax,Ω(t) - Tmin,S25(t)`, con S25 aproximadamente 25 mm bajo las superficies exteriores; maximizar en el tiempo durante los 14 días. No sustituirlo por el rango de temperatura de todo el dominio.
- Reportar `P(Tmax > 70 °C)` y `P(Delta Tmax > 20 °C)` con incertidumbre estadística. Los límites son criterios del curso: no afirmar que ICH exige siempre 70 °C o que cumplir el diferencial demuestra ausencia de grietas.
- Conservar snapshots de cada pronóstico con fuente, modelo, fecha/hora de descarga, coordenadas, unidades, horizonte y variables; no sobrescribir pronósticos anteriores. Documentar cómo se completan los días que no cubra el forecast.

## Primeras verificaciones y entregas

- Requisitos iniciales en `Enunciados e Instrucciones/E01_Semana_1_Revision_oral_BIM_difusion_y_solver_1D.txt` y `Enunciados e Instrucciones/E02_Lab_round_trip_IFC_y_demo_1D.txt`: entorno reproducible, solver 1D ejecutable y al menos un test automatizado; demo IFC con tres objetos identificables y detección desde Python de cambios guardados en Bonsai; variar `Delta x`/`Delta t` y explicar su efecto.
- Toda actividad evaluada declara repositorio y SHA explícito; ese SHA queda congelado al comenzar la revisión. El `SHA inicial` del README corresponde al registro inicial, no identifica automáticamente la entrega actual.
