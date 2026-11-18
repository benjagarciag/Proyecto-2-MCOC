# Brief vigente de presentación F02 con radiación

Crear o actualizar PowerPoint académico en español para Benjamín García, Luis Noriega y Matías Stierling, grupo6. Defensa19/11/2026. Conservar ocho principales con los intervalos personalizados del guion (6:25; máximo permitido7:00), índice de consulta y quince láminasB01–B15:24láminas totales. Usar estilo mixto oscuro/claro existente, texto mínimo, ecuaciones editables matemáticas y animaciones por clic. El PDF muestra el estado final completo de cada lámina.

**Fuentes vigentes:** cierre_revision_final/RESULTADOS_CIERRE.md, CONFIGURACION_FINAL_REVISADA.json, METRICAS_144_FILAS.csv, CIERRE_PUNTOS_RESTANTES.md y GUION_ORAL_F02.md. Archivo principal: presentacion/F02_Grupo6_Pre_entrega.pptx. Sustituir todos los valores anteriores sin radiación. Evaluar672h y reportar también336h desde el mismo t₀. La protección final combina manta504h de edad local y sombra solar90% después de retirarla.

## Datos exactos

| Caudal [m³/h] | Malla [m] | D[h] | Tmax672h[°C] | ΔT672h[K] | P(unión) |
|---|---:|---:|---:|---:|---:|
|60|0,40|10,6129|47,4941|16,5306|0,00%|
|55|0,40|11,5777|47,5128|16,6011|0,00%|
|60|0,20|10,6129|47,0322|15,7202|0,00%|

Confirmación: cambio espacial máximoΔT0,881712K en24pares hasta672h; temporal≤0,0013652K en2casos selectivos. Auditoría3matrices/72piezas/2045transiciones. El criterio de S25 se reconstruye bajo las superficies del hormigón y la máxima incluye centros y caras.

Constantes:ρ2476kg/m³,cp1023J/(kgK),k2W/(mK), suelo15°C conR=0,50/1,2m²K/W. Madera18mm/k0,158 hasta72h; mantas40mm/k0,042 hasta240/504h de edad local. No hay aislación entre capas. Fuente tabular por edad común a todas las capas de una realización. Cinco objetosIFC y once capas térmicas son conceptos distintos.

Radiación activa:α0,6 yε0,9 del acabado exterior equivalente, albedo0,2, orientación+xeste/+ynorte, sombra solar idealτ0,10 tras retirar la última manta y difusa isotrópica. Cielo estimado mediante rocío y nubosidad total como proxy de opaca. Resolver q″=(Ts−Ti)/R=h(Ta−Ts)+ατI+εσ(Trad,K⁴−Ts,K⁴), con R=Δx/(2k)+Σe/k. Definir cada símbolo en notas y kelvin en términosT⁴. No aplicar toda la solar al hormigón a través de las mantas ni añadir radiación otra vez al h.

Refrigeración:Uvol5W/(m³K) es equivalente, agua18°C uniforme, tope15kW conjunto y regla por circuito19/18 con cobertura. Caudal18L/min por ramal es un supuesto operativo y no determina Uvol ni Q en el solver. No se discretiza tubo, espesor, material, contacto ni película interior, ni se resuelve agua axial. Los nueve trazados sirven para cobertura, muestreo y asignación de celdas. No presentar un cálculo deΔTagua≈1,33K como retorno simulado.

## 4. Dirección visual

- Formato 16:9,1920×1080 o 13,333×7,5 pulgadas. Estilo científico contemporáneo,
  con una composición principal por diapositiva y bastante espacio libre.
- Fondo marfil muy claro `#F5F3EE`; texto carbón `#202B33`; verde petróleo
  `#166C65` para propuesta; rojo térmico `#B54830` paraTmax; azul `#1B74AA`
  paraTmin, S25; violeta `#743E99` paraΔT. Umbrales oscuros discontinuos.
- Una tipografía sans serif de fácil lectura, por ejemploAptos oInter si
  está disponible. Títulos32–38 pt, cifra inicial52–64 pt, cuerpo22–26 pt,
  etiquetas de gráficos18–20 pt y fuentes16–18 pt. Reducir texto antes
  de reducir tamaño. No usar texto pequeño como solución a una lámina densa.
- Nada de pantallazos de código, ventanas del terminal, fondos de código,
  decoración de chips, engranajes o fotos genéricas como elemento dominante.
- Preferir geometría del proyecto, gráficos de datos y esquemas técnicos.
  La geometría estilizada debe identificarse como esquema cuando no sea
  una captura del IFC. No usar un render generado como evidencia de montaje real.
- No usar retículas de tarjetas, medidores circulares de «seguridad»,
  semáforos gigantes ni sellos «validado». El0 % no es un certificado.
- Máximo una ecuación central por principal; las derivaciones van a consulta.
  Cada símbolo importante debe tener significado y unidad en notas o consulta.
- Mantener leyendas y colores coherentes. Si una figura fuente tiene otra
  paleta, reconstruirla con sus datos o conservar su leyenda sin falsear colores.
- Titulares que informen; evitar frases publicitarias o «riesgo cero».
- Los gráficos deben ser legibles al proyectarse. LosPNGs existentes son
  referencias fieles; si quedan pequeños, reconstruir a tamaño final con
  los datos, sin inventar puntos, eliminar límites o alterar ejes silenciosamente.

## 5. Lenguaje de animación

La animación debe explicar causalidad. No usar giros, rebotes, letras
individuales, zooms bruscos, sonidos ni transiciones aleatorias.

| Recurso | Aplicación | Duración orientativa |
| --- | --- | ---: |
| Aparición suave | Ecuación, cifra o etiqueta que acompaña el habla |0,25–0,40 s |
| Barrido horizontal | Revelar una historia temporal de izquierda a derecha |0,6–1,0 s |
| Morph/transición equivalente | Mantener la geometría al pasar de físico a capas |0,5–0,7 s |
| Construcción por grupos | Mostrar etapas de colocación en el mismo objeto |≤2 s total |
| Resaltado | Señalar un punto o tramo ya existente, sin cambiar sus datos |0,2–0,3 s |
| Pulsos en tuberías | Representar cualitativamente circulación en un ramal abierto |1–2 s; después detener |

Avance manual, con 2–3 clics por principal como máximo. Las animaciones
se superponen al discurso; no reservar20 s de espera para ver una secuencia.
Ningún efecto automático debe adelantar una diapositiva. No necesitar
internet ni unmouse preciso para continuar.

No animar la historia térmica como si fuera una simulación nueva en vivo.
Si se revela una curva precalculada, conservar ejes y marcas de tiempo.
Los flujos esquemáticos no son vectores cuantitativos calculados. La
aparición de capas se rotula «secuencia esquemática»; no confundirla con
movimiento horizontal de descarga que el solver no resuelve.

El PDF debe contener en cada página el estado final completo. Ningún texto
esencial puede desaparecer o quedar tapado por una animación. Si el
software no exporta bien estados, producir una composición estática
equivalente, sin duplicar las 8 principales en decenas de páginas.



## Recorrido principal

### S1: Decisión y objetivo
Responsable: Benjamín. Intervalo: 0:00–0:43.

**Contenido visible:** 10,61h de colocación,60m³/h,12°C, nueve circuitos y0/24excedencias EN14Y28D. Malla fina0,20m/300s,24pares.

**Composición y animación:** Conservar fundación oscura y revelar primero recursos, después resultado y horizonte. Añadir solar+onda larga en el rótulo del modelo.

Usar las notas exactas del guion oral para esta lámina. Revelaciones por clic con fundidos o barridos de300–700ms. Mantener unidades, ejes y fuente de cada cifra. Las figuras no se recalculan durante la exposición.

### S2: Mecanismo físico con radiación
Responsable: Benjamín. Intervalo: 0:43–1:46.

**Contenido visible:** Hidratación en el volumen y tres intercambios en el exterior: convección, solar y onda larga. ΔT=Tmax,Ω−Tmin,S25 simultáneo.

**Composición y animación:** Conservar corte editable. Revelar fuente, luego puntos, luego exterior. El sol actúa en la manta; el punto caliente puede ser una cara. No animar un máximo fijo como si siempre estuviera en el núcleo.

Usar las notas exactas del guion oral para esta lámina. Revelaciones por clic con fundidos o barridos de300–700ms. Mantener unidades, ejes y fuente de cada cifra. Las figuras no se recalculan durante la exposición.

### S3: Colocación y extracción equivalente
Responsable: Benjamín. Intervalo: 1:46–2:43.

**Contenido visible:** Once capas≤0,40m, dos frentes×30m³/h, nueve ramales en cotas0,5/1,5/2,5/3,8m. Agua18°C ideal,18L/min por ramal abierto y162con bypass. Tope conjunto15kW.

**Composición y animación:** Mostrar capas progresivamente, cuatro niveles3/3/2/1 y banda19/18. Texto explícito: Uv equivalente, sin pared ni agua axial resueltas. Movimiento del agua solo como esquema operativo.

Usar las notas exactas del guion oral para esta lámina. Revelaciones por clic con fundidos o barridos de300–700ms. Mantener unidades, ejes y fuente de cada cifra. Las figuras no se recalculan durante la exposición.

### S4: Método y sensibilidad
Responsable: Luis. Intervalo: 2:43–3:36.

**Contenido visible:** Balance conservativo por celda. Solar+LW no lineal en superficie exterior. Espacio24pares, máximo cambioΔT0,882K; tiempo2pares,0,0014K.

**Composición y animación:** Mantener tabla editable y celda de balance. Animar aportes y después dos refinamientos separados. Conservar volumen refrigerable414,016m³ y tiempos físicos de capas; no confundir resolución con parámetros físicos.

Usar las notas exactas del guion oral para esta lámina. Revelaciones por clic con fundidos o barridos de300–700ms. Mantener unidades, ejes y fuente de cada cifra. Las figuras no se recalculan durante la exposición.

### S5: Temperaturas hasta28 días
Responsable: Luis. Intervalo: 3:36–4:39.

**Contenido visible:** M4_SS×ERA5-2024,0,40m/300s. Evento267h:42,12−25,59=16,53K. Pico46,6574°C a128,25h. Máximo del catálogo finoΔT15,72K.

**Composición y animación:** Curvas NATIVAS editables de0a672h con Tmax/S25 arriba yΔT abajo, límite20K y evento267h. El corte corresponde al evento267h y muestra centros, mientras el indicador incluye caras. Revelar primero temperaturas, después resta y corte. La nota distingue la combinación final de las alternativas que fallaron y mantiene sombra posterior al retiro504h.

Usar las notas exactas del guion oral para esta lámina. Revelaciones por clic con fundidos o barridos de300–700ms. Mantener unidades, ejes y fuente de cada cifra. Las figuras no se recalculan durante la exposición.

### S6: Escenarios y probabilidad
Responsable: Matías. Intervalo: 4:39–5:18.

**Contenido visible:** Ocho fuentes completas por tres historiasERA5, pesos1/24. Unión de los límites evaluada en0–336h y0–672h. α/ε nominales fijos.

**Composición y animación:** Conservar gráfico nativo de fuentes y matriz8×3. Los climas incluyen aire, viento y radiación de cada año. No reducir fuentes a recetas seleccionables ni llamar el catálogo una muestraMonteCarlo.

Usar las notas exactas del guion oral para esta lámina. Revelaciones por clic con fundidos o barridos de300–700ms. Mantener unidades, ejes y fuente de cada cifra. Las figuras no se recalculan durante la exposición.

### S7: Comparación y duración mínima
Responsable: Matías. Intervalo: 5:18–5:52.

**Contenido visible:** Tabla editable de60y55m³/h con probabilidades CALCULADAS hasta672h y exclusión de>60por recursos. D≥V/60=10,61h.

**Composición y animación:** Conservar Gantt y curva nativa duración–riesgo. Todos los planes usan misma física radiativa y resolución. La cota surge de la capacidad máxima supuesta; no de demostrar un fallo térmico de75m³/h.

Usar las notas exactas del guion oral para esta lámina. Revelaciones por clic con fundidos o barridos de300–700ms. Mantener unidades, ejes y fuente de cada cifra. Las figuras no se recalculan durante la exposición.

### S8: Recomendación condicionada
Responsable: Matías. Intervalo: 5:52–6:25.

**Contenido visible:** Confirmación fina:47,03°C,15,72K y0/24excedencias a14y28d. MargenΔ=4,28K.

**Composición y animación:** Mantener cierre oscuro y barra hasta20K calculada con el nuevo valor. Condicionar retiros y medir hormigón/agua. Explicitar transferencia equivalente sin validar y propiedades radiativas supuestas. La recomendación no autoriza automáticamente retirar la última manta después de14d.

Usar las notas exactas del guion oral para esta lámina. Revelaciones por clic con fundidos o barridos de300–700ms. Mantener unidades, ejes y fuente de cada cifra. Las figuras no se recalculan durante la exposición.

## Consulta B01–B15

### B01: Geometría, capas y tubos
Conservar planta de los nueve ramales y tabla de cotas3/3/2/1, longitudes aproximadas639m y diámetro interior de cálculo25mm. Diferenciar cinco objetosIFC de once capas y mostrar que la geometría no acredita transferencia ni montaje.

### B02: Clima, viento y radiación
Mostrar aire, h yGHI en0–672h paraERA5 2023/24/25, coordenadas exactas−37.277929/−72.368271, fechas de snapshots y celda devuelta. h=5,7+3,8v2 y perfil10a2m con exponente0,14. hmedio17,09 es referencia, no constante. DHI/DNI, rocío y nubes se incorporan de snapshots complementarios coincidentes en aire/viento/GHI.

### B03: Balance exterior con radiación
PDE de hidratación y extracción, balance de la superficie de la protección y resistencia en serie. DefinirTs exterior,Ti centro, temperatura radiativa efectiva y kelvin. El suelo permanece reservorio equivalente sin inercia; caras cubiertas pasan a conducción interna. Tabla debe decir solar+LW explícitas, nunca radiación omitida.

### B04: Mantas y retiros
Mostrar tabla de las tres protecciones y edades72/240/504h de la propuesta. Solo retiro tardío falla24/24; solo sombra falla5/24; combinación0/24 hasta672h. Se conserva10% solar; no se ha validado retirar la sombra. Requiere resistencia, monitoreo y predicción; las edades no son autorizaciones automáticas.

### B05: Fuente y propiedades
Conservar ocho fuentes, identificación de probetas/campañas y tablaρ/cp/k. No elegir una supuesta mezcla favorable sin correspondencia de dosificaciones. Qpor edad no incluye cinética dependiente deT ni retraso de reacción por colocar a12°C.

### B06: Intercambio equivalente de tuberías
Ecuación de potencia sumada sobre celdas de circuitos abiertos, tope15kW y control. Rotular Uv[W/(m³K)] frente a h_interior[W/(m²K)]. Enumerar pared/contacto/convección interior/agua axial como pendientes de validación real. Conservar balance de referencia P=ṁcpΔTagua y ejemplo1,33K condicionado a162L/min y15kW, sin atribuirlo a salida del solver.

### B07: Colocación fría y unión
Conservar107,4/117,1min de capa mayor frente a ventana150min no ensayada y338kW sensibles aproximados para preenfriar20a12°C a60m³/h. Comparación con55m³/h. Son cálculos constructivos distintos del frío embebido. No afirmar equipos contratados o tolerancias térmicas no simuladas.

### B08: Balance discreto y resolución
Fórmula conservativa, integración de hidratación y balance no lineal de caras. Mostrar los24 cambios pareados deΔT a672h con datos nuevos, ejes que permitan cambios negativos. Actualizar el máximo temporal de dos pares. El límite de estabilidad incorpora conductancias de contorno y frío, no solo vecinos internos.

### B09: Unión y pesos
Fila realM4_SS/ERA5-2024:46,6574°C y16,5306K en672h, peso1/24 e indicadores calculados. Reponderación de años/SS desde matrices nuevas. Conservar ejemplos aritméticos1/24y2/24 como ejemplos, no fallas observadas ni intervalos estadísticos binomiales.

### B10: Comparación completa
Tabla de60/55gruesos y60fino,24pares cada uno hasta672h. Margen hasta20K; también cumplen336h. Cortes de60y55a267y672h, con misma escala, plano, fuente y clima. No atribuir matriz fina completa a55.

### B11: Medición y contingencias
Conservar sensores propuestos y umbrales operativos65/68°C y18/19K como propuestas, no normativa. Añadir medidas de caudal, entrada/retorno y condiciones de exposición solar. Cambios de frío, mantas o clima requieren nueva predicción y no heredan la matriz nominal.

### B12: Alcance físico y trazabilidad
Auditoría y sensibilidades nuevas. Radiación activa conα/ε y cielo supuestos, sombra idealizada sin geometría resuelta. Suelo sin inercia, fuente por edad, agua ideal y Uvol sin calibrar. No se resolvieron tensiones/fisuración. La combinación final cumple hasta672h; no valida retiro de sombra ni apagado definitivo, ni hay liberación automática. El commit de preentrega identifica la versión congelada.

## Evidencia y comprobación final

Los gráficos obligatorios son editables y sus libros embebidos contienen los valores actuales. Fuentes y climas conservados pueden reutilizar recursos originales porque no cambian, pero historias térmicas, sensibilidad, tabla de planes, evento y cortes se sustituyen. Mantener datos en evidencia_f02_radiacion/datos_presentacion.json y CSV junto a figuras01–07. El PPTX conserva navegación del índice y animaciones de las ocho principales.

Comprobar cada diapositiva a tamaño completo: sin recortes, ejes/unidades visibles, leyendas legibles, cifras consistentes con tablas auditadas y notas por responsable. Inspeccionar estado final estático y conservar vínculos de consulta. Repetir ecuaciones como texto matemático editable y verificar signos del flujo. El PDF es una versión estática completa, no una demostración de las animaciones.

El guion conserva los intervalos del usuario y termina en6:25 como objetivo; no afirmar un ensayo realizado. No añadir citas de aprobación real, validación experimental o certeza de cumplimiento en obra. La conclusión se limita a los recursos y escenarios declarados.


### B13: Cronograma físico
Tabla de11capas con cotas,volumen,inicio,duración y fin; t₀19/11/2026 10:00 UTC−03:00. Activación instantánea al inicio, duración física conservada enD.

### B14: S25 y tratamiento de la fuente
Dominio activo sin suelo/aire/celdas futuras; caras desaparecen al cubrirse. Reconstrucción normal a25mm con el mismo balance de cara. Qya está enW/m³: no convertirla otra vez conρcp. Integral trapezoidal600s, interpolación acumulada lineal y cola nula declarada.

### B15: Mecanismo de las protecciones
Comparar24pares por alternativa: retiro504sin sombraΔ33,01K/Pf100%; sombra90con retiro360Δ23,48K/Pf20,8333%; combinaciónΔ16,53K/Pf0. Son resultados gruesos; la propuesta también tiene24pares finos completosΔ15,72K.
