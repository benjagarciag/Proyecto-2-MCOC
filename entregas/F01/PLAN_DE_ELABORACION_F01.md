    # F01: lista de contenidos y criterios de escritura

Revisión: 19 de noviembre de 2026. Documento de organización previo a redactar el artículo.

## 1. Documentos revisados y alcance

- Pauta principal: `Enunciados e Instrucciones/Enunciados/F01_PLAN_CONTROL_TEMPERATURA_FINAL.txt`, leída completa.
- Taller: `C:/Users/benja/Downloads/Taller Escritura 2026.pdf`, profesora Isabel Rivera Serrano, 37 páginas PDF con dos diapositivas por página en gran parte del documento. Se revisaron el texto completo y las páginas renderizadas. Las páginas indicadas abajo corresponden al PDF.
- Complementos expresamente relacionados con F01: guía E13 y pauta F02, especialmente las cautelas probabilísticas y las excepciones de comparación.
- Para orientar la futura recuperación de evidencia se consultaron `entregas/F02/cierre_revision_final/RESULTADOS_CIERRE.md` y `entregas/F02/CIERRE_PUNTOS_RESTANTES.md`. Esto no constituye una auditoría nueva de todos los archivos numéricos.

La solicitud actual es comprender y organizar. Este archivo no es el borrador del artículo, no certifica aprobación del centro de escritura ni supone que los pendientes históricos de F02 sigan abiertos: el usuario informa que ya entregó F02. No se modificó esa entrega ni se ejecutaron simulaciones.

La pauta F01 define los contenidos específicos del artículo. El taller aporta criterios de escritura y ejemplos de informes de laboratorio. Sus ejercicios son material didáctico; no son actividades nuevas que deban entregarse como parte del proyecto.

## 2. Qué debe demostrar el artículo

Responder qué plan termina de colocar todo el hormigón en el menor tiempo entre las alternativas consideradas, manteniendo una probabilidad conjunta de exceder 70 °C o un diferencial de 20 °C no mayor que 5%, bajo la incertidumbre modelada.

El argumento necesita conectar datos reales, hipótesis físicas, ecuaciones implementadas, método numérico verificado, incertidumbre explícita, comparación justa y recomendación operativa. Cada afirmación importante debe poder vincularse con datos, una fuente, una comprobación o un supuesto declarado. El plan de control es un resultado del estudio.

## 3. Lista maestra de contenidos

Las casillas son controles de elaboración del futuro artículo; no significan que la evidencia esté ausente del repositorio.

### A. Formato, identificación y trazabilidad

- [ ] PDF en español con título, autores, grupo, curso/afiliación y fecha.
- [ ] Texto principal de 4000–6000 palabras orientativas: priorizar claridad y completitud.
- [ ] Resumen de 150–250 palabras y 4–6 palabras clave.
- [ ] Secciones y subsecciones con jerarquía consistente.
- [ ] Figuras y tablas numeradas, con unidades, leyendas legibles, fuentes y llamadas desde el texto.
- [ ] Citas consistentes donde se usan parámetros, métodos y afirmaciones ajenas.
- [ ] Artículo autocontenido: el argumento central se entiende sin abrir código ni anexos.
- [ ] PDF acompañado de repositorio, SHA final, configuraciones, resultados por escenario y datos o instrucciones precisas de acceso.
- [ ] Conservar e identificar el SHA de defensa; no confundirlo con un commit base o un cierre técnico anterior.
- [ ] Registrar correcciones posteriores a defensa: cambio, motivo y efecto sobre la recomendación; conservar los resultados previos.
- [ ] Obtener la aprobación del centro de escritura antes del cierre de semestre, condición explícita de F01.

### B. Título, resumen y palabras clave

**Función:** permitir que un lector identifique problema, enfoque y resultado sin leer el cuerpo.

- [ ] Título informativo, compatible con el alcance realmente demostrado.
- [ ] Problema y objetivo de decisión.
- [ ] Datos reales de geometría, hidratación y meteorología empleados.
- [ ] Método físico, numérico y de incertidumbre, descritos brevemente.
- [ ] Alternativas comparadas y recursos comunes.
- [ ] Duración elegida, probabilidad conjunta y resultados térmicos relevantes.
- [ ] Intercambio cuantificado frente a otra opción.
- [ ] Principal condición de validez o limitación.
- [ ] Informar ausencia de solución factible si ese fuera el resultado.
- [ ] Redactar el resumen al final, aunque aparezca al inicio.

### C. Introducción

**Función:** explicar por qué el problema importa y qué pregunta resolverá el estudio.

- [ ] Generación de calor por hidratación y mecanismos de disipación.
- [ ] Conflicto entre rapidez de colocación y control de indicadores térmicos.
- [ ] Razón para considerar incertidumbre del material y del clima.
- [ ] Antecedentes pertinentes y bibliografía del curso, conectados con las decisiones del estudio.
- [ ] Un objetivo general concreto y objetivos específicos verificables.
- [ ] Pregunta principal y preguntas secundarias que puedan responderse con los resultados.
- [ ] Alcance docente de 70 °C y 20 °C; evitar atribuirlos indistintamente a cualquier norma o exposición.
- [ ] Si se formula una hipótesis de trabajo, identificarla como provisional y comprobable; la pauta F01 no exige inventar una hipótesis experimental para una decisión de optimización.

### D. Caso de estudio y datos

**Función:** mostrar qué realidad se representó y de dónde procede cada entrada.

**Geometría y construcción**

- [ ] Sitio, coordenadas y geometría oficial.
- [ ] Dimensiones, volumen geométrico, partición de vertidas/capas y superficies relevantes.
- [ ] Simplificaciones y flujo BIM/IFC a voxelización.
- [ ] Información del IFC realmente consumida por el solver y overrides externos del plan.
- [ ] Volumen discretizado frente al geométrico, con diferencia cuantificada.
- [ ] Esquema que distinga objetos IFC, capas térmicas y circuitos.

**Parámetros**

- [ ] Tabla con símbolo, significado, unidad, valor/rango, fuente y clasificación: medido, bibliográfico, ajustado o supuesto.
- [ ] Densidad, calor específico y conductividad.
- [ ] Hidratación, temperatura y capacidad de colocación.
- [ ] Suelo, convección, moldajes y aislantes.
- [ ] Parámetros adicionales efectivamente usados: radiación, refrigeración equivalente, histéresis y sombra.

**Ocho curvas de hidratación**

- [ ] Identificar ensayo, magnitud medida, unidades, origen temporal y condiciones conocidas.
- [ ] Mostrar las ocho curvas y establecer qué se sabe sobre réplicas, mezclas o condiciones distintas.
- [ ] Declarar metadatos faltantes y consecuencias para su interpretación probabilística.
- [ ] Justificar cualquier exclusión sin seleccionar curvas para favorecer el resultado.
- [ ] Explicar limpieza, interpolación/ajuste, suavizado si existe, derivación y conversiones.
- [ ] Explicar extrapolación y cola fuera del registro.
- [ ] Mostrar la fuente volumétrica resultante y comprobar su integral/calor acumulado.
- [ ] Explicar cómo se conserva una curva completa por escenario y cómo se relacionan las vertidas/lotes.
- [ ] Evitar reemplazar la incertidumbre por una única curva promedio.

**Meteorología**

- [ ] Fuente/modelo, coordenadas, tipo de producto, descarga y zona horaria.
- [ ] Variables, unidades, cobertura temporal y series realmente utilizadas.
- [ ] Tratamiento de faltantes y continuación del horizonte.
- [ ] Coherencia entre aire, viento, radiación y otras variables acopladas.
- [ ] Snapshots congelados comunes a todos los planes y conservación de anteriores si existen.
- [ ] Diferenciar reanálisis histórico y escenario hipotético de un pronóstico de obra.
- [ ] No inventar otra descarga retrospectiva ni probabilidades meteorológicas observadas.

### E. Modelo continuo

**Función:** explicar qué ecuaciones representan los procesos y bajo qué supuestos.

- [ ] Derivar el balance local de energía y la ley de Fourier hasta la ecuación implementada.
- [ ] Definir dominio, materiales, temperatura, tiempo, fuente, parámetros y unidades.
- [ ] Fundamentar propiedades constantes u otras hipótesis y procesos omitidos.
- [ ] Definir dominio activo y edad local desde la activación de cada vertida.
- [ ] Condiciones iniciales del terreno y de cada colocación, con cronología y temperatura inicial.
- [ ] Relación matemática entre ensayo real de hidratación y fuente en W/m³; conversión de horas a segundos cuando corresponda.
- [ ] Si se interpreta incremento adiabático, justificar esa interpretación; una temperatura no adiabática necesita balance adicional.
- [ ] Declarar si se ignora dependencia de la cinética con la temperatura.
- [ ] Tabla de bordes por superficie y etapa: ecuación, parámetros, procedencia y fundamento.
- [ ] Normal saliente, signos y distinción entre fuente volumétrica y flujo superficial.
- [ ] Convección y resistencias de protecciones; explicar validez de omitir capacidad térmica propia y evitar duplicar resistencias.
- [ ] Retiros por edad local y cambios efectivos del borde.
- [ ] Suelo, borde remoto y estado inicial.
- [ ] Interfaces entre vertidas: continuidad de temperatura/flujo o ley de resistencia usada.
- [ ] Actualización de las caras cuando una vertida cubre otra.
- [ ] Radiación solar y de onda larga: flujos, orientación, datos y uso de kelvin en potencias radiativas.
- [ ] Refrigeración implementada: término equivalente, máscara, límites de potencia y lógica de control, con sus idealizaciones.
- [ ] Sombra: transmisión solar y superficies afectadas, sin atribuirle una cubierta real ya validada.
- [ ] Correspondencia entre ecuaciones e implementación propia; citar referencias de apoyo sin atribuirles el desarrollo del solver.

### F. Discretización y algoritmos

**Función:** permitir comprender cómo se transforma el modelo continuo en cálculo.

- [ ] Derivar balance de celda, capacidad térmica, volúmenes y términos de intercambio.
- [ ] Definir conductancias/resistencias, áreas, distancias e interfaces entre materiales.
- [ ] Explicar máscara geométrica, celdas activas, bordes y aproximación escalonada.
- [ ] Explicar extracción de temperaturas aproximadamente a 25 mm y reconstrucción de caras.
- [ ] Escribir la actualización temporal efectivamente usada.
- [ ] Fundamentar restricción local de paso y restricciones adicionales por radiación, extracción y eventos según la formulación implementada.
- [ ] Si correspondiera un esquema implícito, detallar sistema, solución y tolerancias. No describir una alternativa que el código no utiliza.
- [ ] Explicar alineación con activaciones, retiros y cambios de control.
- [ ] Pseudocódigo desde lectura de datos hasta agregación de escenarios.
- [ ] Mallas, pasos, hardware local, duración de una corrida y costo total recuperados de registros.
- [ ] Distinguir estabilidad de exactitud temporal y duración constructiva de tiempo de CPU.

### G. Verificación y evaluación del modelo

**Función:** establecer cuánta confianza merece el cálculo para esta decisión.

- [ ] Distinguir verificación del método/código, calibración y validación independiente.
- [ ] Caso conocido con ecuación y condiciones relevantes, error y configuración.
- [ ] Balance energético con fuentes y flujos identificados y signos coherentes.
- [ ] Sensibilidad espacial separada: al menos dos mallas y cambios de máximos/clasificación.
- [ ] Sensibilidad temporal separada: al menos dos pasos y cambios de máximos/clasificación.
- [ ] Identificar si cada contraste cubre todos los escenarios o un subconjunto.
- [ ] No afirmar orden asintótico a partir de solo dos niveles.
- [ ] Evaluar error geométrico y aproximación de la profundidad superficial.
- [ ] Relacionar diferencias observadas con márgenes frente a los límites; no tratar una diferencia entre mallas como cota rigurosa del error sin fundamento.
- [ ] Si la incertidumbre numérica puede cambiar cumplimiento, refinar o declarar decisión indeterminada.
- [ ] Discutir efectos de datos e idealizaciones sobre la recomendación.
- [ ] Reconocer ausencia de validación integral de la fundación si no hay mediciones térmicas independientes.

### H. Incertidumbre y optimización

**Función:** definir con precisión qué se minimiza y qué significa cumplir.

- [ ] Definir D como último fin de colocación menos t₀, incluyendo esperas y retraso inicial.
- [ ] Conservar t₀ del jueves 19 de noviembre de 2026 y declarar hora/zona comunes; la fecha de redacción no desplaza la construcción.
- [ ] Decisiones, capacidad, simultaneidad, secuencia, esperas y controles disponibles.
- [ ] Distinguir duración física de vertidas y activación térmica instantánea si se usa.
- [ ] Definir máximo térmico en hormigón activo y diferencial simultáneo antes de maximizar en tiempo.
- [ ] Definir superficies existentes S25 y actualización al colocar nuevas capas.
- [ ] Evento conjunto de excedencia de cualquiera de los límites y requisito Pf ≤ 0,05.
- [ ] Mantener 336 h y justificar extensión hasta capturar máximos relevantes; reportar ambos horizontes y alertas si existen.
- [ ] Escenarios completos, pesos conjuntos, dependencia/independencia y parámetros fijados.
- [ ] Justificar comparabilidad de curvas y representatividad climática.
- [ ] Enumeración: suma de pesos fallidos, marginales y unión sin doble conteo; exactitud condicionada al catálogo discreto.
- [ ] Resolución probabilística y sensibilidad fundamentada a pesos o escenarios omitidos.
- [ ] Si se utiliza Monte Carlo, informar N, semillas, incertidumbre binomial y separación selección/comprobación. No es obligatorio añadirlo a la enumeración completa.
- [ ] Familia explorada, rangos, paso, cribado, calidad de evaluaciones finales y exclusiones.
- [ ] Alcance de optimalidad: mejor entre opciones estudiadas y, cuando proceda, argumento de cota por capacidad.

### I. Resultados

**Función:** presentar evidencia cuantitativa de la comparación y explicar qué muestra.

- [ ] Vertida única, propuesta, variante más rápida y más lenta, o excepciones físicas justificadas según F02.
- [ ] Mantener recursos, geometría, datos, física y horizontes comparables.
- [ ] Cronogramas de inicio/fin, duración y retiro de protecciones, distinguiendo tiempo global y edad local.
- [ ] Tabla por plan: D, probabilidades marginales y conjunta, cumplimiento y máximos.
- [ ] Para cada máximo relevante: instante, ubicación y escenario; no asumir que Tmax y diferencial provienen del mismo caso.
- [ ] Curvas de núcleo/superficie y diferencial, con umbrales y escenarios identificados.
- [ ] Cortes/campos con instante, orientación, escala y zonas críticas.
- [ ] Duración frente a probabilidad conjunta, línea del 5% y candidato elegido.
- [ ] Sensibilidades numéricas y probabilísticas relacionadas con la elección.
- [ ] Distinguir realización, extremo del conjunto y promedio.
- [ ] No sustituir distribución de máximos por máximo del campo promedio.
- [ ] Cuantificar cambios de duración/riesgo/margen; revisar elección si otra opción más rápida cumple.
- [ ] Presentar contrastes de controles/protecciones con contexto suficiente para explicar por qué se adoptaron, sin mezclar familias históricas incompatibles.

### J. Discusión y plan de control resultante

**Función:** interpretar los mecanismos y traducir la recomendación en acciones condicionadas.

- [ ] Acumulación/disipación, edades relativas, clima, aislación y efecto de retiros.
- [ ] Papel de radiación, refrigeración y combinación de protecciones.
- [ ] Representatividad de ocho curvas, pesos, recursos y margen numérico.
- [ ] Distinguir excedencia térmica de probabilidad mecánica de fisuración.
- [ ] Alcance de idealizaciones de tubos, agua y sombra, y sensibilidad no estudiada.
- [ ] Plan de colocación, secuencia, protecciones y condiciones de retiro.
- [ ] Sensores de núcleo, superficie crítica y ambiente; ubicación y finalidad.
- [ ] Redundancia, frecuencia, duración del seguimiento y responsables.
- [ ] Disparadores fundamentados, acciones y escalamiento ante temperaturas o clima no previstos.
- [ ] Retiro condicionado a resistencia/monitoreo/predicción y diferencial inducido; no convertir una edad simulada en autorización automática de obra.
- [ ] Separar medidas simuladas de contingencias propuestas que aún requieren evaluación.
- [ ] Si no hay solución factible, identificar qué cambio concreto habría que estudiar.

### K. Conclusiones

**Función:** contestar la pregunta inicial con resultados y límites precisos.

- [ ] Plan recomendado, duración, diferencia temporal con la alternativa y probabilidad conjunta bajo el modelo.
- [ ] Principales condiciones que hacen válida la recomendación.
- [ ] Respuesta a objetivos específicos y a hipótesis, si se formuló.
- [ ] Fortalezas y limitaciones del estudio, relacionadas con su objeto.
- [ ] Separar lo demostrado de validación, instalación o ampliaciones pendientes.
- [ ] Proponer comprobaciones futuras pertinentes; evitar conclusiones sobre aprendizaje o trabajo en equipo.
- [ ] No introducir resultados nuevos sin haberlos presentado antes.

### L. Referencias y anexos de reproducción

- [ ] Bibliografía del curso y fuentes académicas de física/métodos.
- [ ] Datos del profesor, meteorología y métodos/bibliotecas realmente utilizados, con procedencia fiel.
- [ ] Correspondencia entre citas y lista final, con metadatos completos y formato consistente.
- [ ] Entorno, dependencias y comandos exactos para un caso y una comparación.
- [ ] Configuraciones, escenarios/pesos, semillas si corresponden, métricas y figuras archivadas.
- [ ] Tablas completas, derivaciones largas y registros detallados en anexos identificados y citados desde el cuerpo.
- [ ] Resultados principales consultables sin repetir toda la campaña.

## 4. Revisión completa del taller y aplicación al F01

|Páginas PDF|Contenido del taller|Aplicación al artículo|
|---|---|---|
|1–3|Propósito del informe y estructura general|Describir e interpretar un estudio realizado. Usar la estructura específica F01 para organizar el desarrollo técnico.|
|4–5|Resumen y ejercicio de análisis|Incluir objetivo, enfoque, resultados y conclusión. Revisar que ninguna de estas funciones quede implícita. Redactarlo al final.|
|6|Índice|Si se incorpora, usar títulos/subtítulos numerados, páginas correctas y jerarquía visible. F01 no exige expresamente índice.|
|7–8|Introducción y análisis de ejemplo|Contexto, objetivo principal, objetivos específicos e hipótesis cuando sea pertinente. Evitar un inicio que solo anuncie que se presenta un informe.|
|9–10|Revisión bibliográfica|Explicar objeto, importancia, variables y ecuaciones con fuentes académicas. El taller menciona generalmente tres o más fuentes; no es un mínimo numérico explícito de F01. Importa que cada afirmación necesaria esté respaldada.|
|10–12|Citas directas e indirectas, narrativas y parentéticas|Adoptar Harvard como criterio del taller: autor/año y página en citas textuales. Diferenciar palabras propias de transcripciones y citar también las paráfrasis.|
|13|Método y ejemplo|Describir materiales/insumos y acciones realmente realizadas, en presente o pasado coherente; no escribir instrucciones futuras ni un manual de uso como método principal.|
|14–15|Resultados e inserción de gráficos|Presentar, explicar y analizar resultados, errores y comparaciones. Cada figura/tabla requiere título, número, fuente y explicación; títulos sin punto final según el taller.|
|16–17|Conclusión y ejercicio|Responder objetivos/hipótesis, reconocer fortalezas/debilidades y sugerir nuevos estudios. Evaluar el estudio y sus límites, no a las personas.|
|18|Bibliografía y ejemplos|Usar fuentes académicas y Harvard. Complementar con documentación primaria de datos/software exigida por F01; no ocultar los datos del profesor por no ser un paper.|
|19–20|Anexos y ejemplo|Reservar material complementario extenso; citarlo y mantener el razonamiento esencial en el cuerpo.|
|21–22|Coherencia e idea principal|Un tema central por párrafo, secuencia lógica y relación de todas las secciones con la pregunta de decisión.|
|23–24|Cohesión y correferencia|Enlazar ideas y usar referentes inequívocos. Reducir repeticiones innecesarias sin cambiar términos técnicos que tienen significado preciso.|
|25–26|Conectores y ejercicio|Usar enlaces de adición, causa/consecuencia, continuidad, equivalencia, ejemplo, oposición, orden y cierre según la relación real.|
|26–27|Punto, coma y simplificación|Una idea principal por oración y un tema por párrafo; evitar acumular comentarios. El taller recomienda hasta tres puntos seguidos por párrafo, como pauta de simplificación.|
|28–30|Gramática y concordancia|Revisar sujeto/verbo y género/número; toda oración del cuerpo debe tener núcleo verbal. Un infinitivo o participio aislado no completa una oración.|
|31–32|Perífrasis y reconocimiento de núcleos verbales|Reconocer auxiliar conjugado con forma no personal, tiempos compuestos y pasivas al comprobar que la oración está completa. Los ejercicios ayudan a detectar fragmentos.|
|33|Adecuación e impersonalidad|Usar registro académico y construcción con «se», como recomienda el taller; evitar emociones o valoraciones sin evidencia.|
|34–35|Formalidad, precisión y ejercicio|Sustituir coloquialismos y palabras comodín por verbos y magnitudes concretos. Mejorar claridad sin volver el texto artificioso.|
|36–37|Presentación, estilo, portada y contraportada|Mantener identidad, tipografía y jerarquía consistentes. Las portadas de laboratorio son ejemplos; F01 exige identificación, pero no impone esos diseños ni contraportada. El taller indica que la estilística no se evalúa en su rúbrica.|

### Reglas editoriales que aplicaremos

1. **Coherencia global.** Pregunta, objetivos, método, resultados y conclusión deben referirse a la misma decisión y familia de planes. Los antecedentes históricos solo entrarán cuando expliquen una elección.
2. **Coherencia del párrafo.** Abrir con una idea reconocible, desarrollarla con evidencia y explicar su efecto. Separar temas distintos aunque compartan una ecuación o figura.
3. **Cohesión.** Aclarar a qué se refieren «este», «ello», «dicho resultado» y «la alternativa». Identificar el plan cuando haya varios candidatos.
4. **Terminología estable.** Conservar «probabilidad conjunta de excedencia» para ese concepto. No alternarlo con «fisuración» o «confiabilidad real». Diferenciar colocación física, activación numérica y refrigeración.
5. **Conectores con sentido.** «Por lo tanto» necesita una inferencia respaldada; «sin embargo» una oposición real. Un conector no reemplaza la explicación de un mecanismo.
6. **Puntuación.** Limitar subordinadas y precisiones. Evitar coma entre sujeto y verbo. Dividir oraciones sobrecargadas antes de agregar conectores.
7. **Concordancia y núcleo verbal.** Por ejemplo, «La probabilidad de las excedencias es…» y «Las diferencias observadas se atribuyen…». Los títulos pueden ser nominales; el cuerpo necesita oraciones completas.
8. **Tiempos verbales.** Presente para ecuaciones, definiciones y lectura de tablas; pasado para datos descargados y corridas realizadas; formulación condicional para medidas futuras o dependientes de comprobación.
9. **Registro.** Preferir «Se evaluaron 24 escenarios» a «Probamos varios casos». Eliminar «creemos», «desafortunadamente», «obviamente» y expresiones equivalentes sin función argumental.
10. **Precisión.** Indicar variable, plan, horizonte, resolución y fuente cuando cambien la interpretación. Evitar «el modelo funciona bien» sin métrica.
11. **Citas.** Priorizar paráfrasis fiel con referencia. El taller distingue citas breves de menos de 40 palabras y extensas de más de 40, con bloque separado; no resuelve expresamente el caso de exactamente 40. Evitar citas extensas innecesarias y mantener una convención coherente.
12. **Referencias.** Verificar autores, año, título, edición/páginas y localización. No inventar página para un recurso sin paginación ni autor para datos de origen desconocido.
13. **Figuras y tablas.** Introducirlas por número y explicar su hallazgo. Identificar elaboración propia y datos de origen. Usar escalas comparables, unidades, escenarios y resolución legibles.
14. **Ecuaciones.** Introducir qué expresan y definir símbolos/unidades. La numeración y el glosario son decisiones de organización útiles; no sustituyen la explicación física.
15. **Notación y cifras.** Unificar separador decimal, símbolos y cifras significativas. Diferenciar temperatura en °C, diferencias en K y temperatura absoluta radiativa. Clasificar con precisión completa, aunque el texto redondee.
16. **Revisión final.** Leer el texto seguido, sin código ni anexos, para comprobar que un lector puede reconstruir el argumento. Revisar después referencias, diagramación y PDF renderizado.

### Diferencias que no debemos convertir en requisitos inventados

- La revisión bibliográfica puede integrarse en introducción y modelo; el taller no obliga a crear un capítulo adicional que duplique F01.
- Índice, portada independiente y contraportada no aparecen como exigencias expresas de F01. Su inclusión dependerá de una plantilla o indicación concreta.
- El taller no fija para F01 una familia tipográfica, tamaño, interlineado o márgenes numéricos. Esos valores serán decisiones de maquetación mientras no exista plantilla específica.
- La recomendación de sinónimos no debe producir ambigüedad técnica. Repetir un término definido puede ser necesario.
- Los ejemplos didácticos no son fuentes científicas del proyecto ni prueba de corrección de sus afirmaciones físicas.
- No se ha recibido una rúbrica independiente del centro de escritura. Este plan recoge el taller entregado y no anticipa aprobación automática.

## 5. Aplicación inicial a nuestra evidencia existente

El cierre técnico consultado permite orientar la recuperación de materiales, sin volver a simular por el hecho de redactar:

|Tema|Evidencia localizada|Tratamiento al elaborar F01|
|---|---|---|
|Propuesta y vecina|`entregas/F02/cierre_revision_final/RESULTADOS_CIERRE.md` y `COMPARACION_PLANES.csv`|Operación continua 60 m³/h, 10,6129 h; vecina 55 m³/h, 11,5777 h. Comparación a 672 h con controles comunes.|
|Resolución final|Mismo cierre y `SENSIBILIDAD_ESPACIAL_24_PARES.csv`|Propuesta con 24 pares finos 0,20 m/300 s; Tmax 47,0322 °C y diferencial 15,7202 K. No presentar cambio de malla como mejora constructiva.|
|Verificación|`VERIFICACION.json`, `VERIFICACIONES_EJECUTADAS.txt` y balances|Recuperar errores, balance y configuraciones; separar 24 pares espaciales de los dos contrastes temporales selectivos.|
|Trazabilidad de máximos|`METRICAS_144_FILAS.csv`|Recuperar escenario, tiempo, posición y horizonte; 144 filas no significan 144 escenarios independientes.|
|Física y decisión|`entregas/F02/CIERRE_PUNTOS_RESTANTES.md`|Usar como base documental y comprobar correspondencia con ecuaciones/código vigente.|
|Figuras|Siete figuras del cierre|Seleccionar y adaptar legibilidad al artículo; no reutilizar una imagen solo porque apareció en defensa.|

Puntos que requieren especial atención durante el inventario:

- La propuesta y la vertida única continua son el mismo caso físico; no duplicarlas como si fueran alternativas diferentes.
- Con capacidad máxima 60 m³/h, la cota V/60 justifica que no exista una variante admisible más rápida. No fabricar una corrida fallida para completar la tabla.
- El cierre conserva manta hasta 504 h y luego sombra ideal del 90% durante el horizonte. No reutilizar resultados de retiro a 360 h como si representaran esa protección.
- Diferenciar 336 h y 672 h; conservar el argumento de extensión y verificar máximos relevantes en la evidencia.
- Mantener Pf = 0% condicionado a escenarios/pesos; no convertirlo en garantía real de ausencia de excedencia o fisuración.
- No afirmar que caudal y temperatura ideal del agua validan transferencia real de tubos, montaje o capacidad hidráulica.
- No afirmar que 504 h es retiro mínimo optimizado ni que la sombra puede desmontarse con seguridad después del horizonte.
- Localizar sensibilidad probabilística ya existente antes de decidir si falta evidencia. Con cero fallas en todos los escenarios, cambiar solo sus pesos no modifica Pf; explicarlo no sustituye discutir escenarios omitidos.
- Recuperar del registro las fechas de descarga, condiciones de ensayo, costos computacionales y bibliografía. No rellenar faltantes de memoria.
- Identificar SHA real de defensa y observaciones recibidas. El cierre documental puede contener pendientes históricos anteriores a la entrega que el usuario ya completó.

## 6. Organización de la elaboración

### Orden de trabajo propuesto

1. **Inventario de evidencia.** Vincular cada punto de esta lista con archivo, dato o fuente; marcar «disponible», «requiere explicación», «requiere verificación documental» o «no disponible».
2. **Cerrar el argumento.** Fijar pregunta, alcance, propuesta, alternativas y límites que se sostendrán, conservando trazabilidad de defensa.
3. **Seleccionar tablas y figuras.** Preparar el conjunto mínimo que demuestra el argumento; reservar tablas extensas para anexos.
4. **Redactar datos, modelo, método y verificación.** Deben corresponder a la implementación utilizada.
5. **Redactar incertidumbre, resultados, discusión y plan operativo.** Cada recomendación necesita evidencia o condición explícita.
6. **Redactar introducción y conclusiones.** Comprobar correspondencia entre objetivos y respuestas.
7. **Redactar título, resumen y palabras clave.** Ajustarlos al artículo completo.
8. **Revisar con el taller.** Pasadas separadas de coherencia, cohesión, gramática, adecuación, citas y presentación.
9. **Preparar revisión del centro de escritura.** Incorporar observaciones con registro y verificar nuevamente cifras, referencias y PDF.
10. **Congelar entrega.** PDF, repositorio/SHA, insumos, configuraciones, métricas, reproducción y nota de cambios.

### Distribución orientativa de palabras

Esta distribución es una propuesta editorial, no una exigencia adicional. Suma 5300 palabras para las nueve secciones principales; el resumen se controla aparte.

|Sección|Palabras objetivo|
|---|---:|
|Introducción|400|
|Caso de estudio y datos|800|
|Modelo continuo|800|
|Discretización y algoritmos|600|
|Verificación y evaluación|500|
|Incertidumbre y optimización|650|
|Resultados|650|
|Discusión y plan de control|650|
|Conclusiones|250|
|Total principal|5300|

### Control de evaluación

|Criterio F01|Puntos de la rúbrica publicada|
|---|---:|
|Problema, datos reales y trazabilidad|1,2|
|Continuo, ecuaciones, parámetros, bordes y fundamento|2,0|
|Discretización, algoritmos y verificación|1,8|
|Incertidumbre, evento conjunto y limitaciones|1,5|
|Comparación, búsqueda temporal y recomendación|1,8|
|Discusión, monitoreo y contingencias|0,8|
|Escritura, figuras, referencias y reproducibilidad|0,9|
|Total de la tabla|10,0|

La pauta F01 presenta una inconsistencia administrativa: su encabezado dice 20 puntos y su rúbrica suma 10. No se deduce una conversión sin confirmación docente. La guía E13 dice que el artículo inicialmente anunciado para el viernes 20 se movió al lunes siguiente, que corresponde al 23 de noviembre de 2026; la fecha definitiva debe comprobarse en el aviso vigente de Canvas. Esto no impide organizar el contenido ahora.

## 7. Condición para pasar a la redacción

La lectura de la pauta y del taller está completada. El siguiente paso es llenar el inventario de evidencia y desarrollar las secciones, conservando esta lista como control. La existencia de material F02 facilita la elaboración, pero no demuestra por sí sola que cada exigencia documental del artículo esté cubierta.
