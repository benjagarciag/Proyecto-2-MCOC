# Cierre técnico de la revisión F02: apartados 5 y 6

Este documento desarrolla las capturas finales de la pauta: familia y
argumento temporal, contenido de la exposición, teoría, resultados visibles
y respaldo técnico. La estrategia es última manta hasta504 h de edad local
y sombra solar90 % posterior. Las cifras finales se leen en
`cierre_revision_final/COMPARACION_PLANES.csv` y `DATOS_CIERRE.json`, generados
una vez completadas y auditadas las matrices. Se conservan guion conversacional,
notas, PPTX y PDF sin sobrescribirlos durante esta revisión técnica.

## 5. Familia, restricciones y por qué se recomienda el plazo menor

La familia de cierre está fijada antes de calcular su comparación homogénea
en `casos/sensibilidad_h/cierre_f02.json`: **q∈{55,60}m³/h**, paso5m³/h.
Se estudia el vecino inmediatamente más lento frente al máximo disponible.
Se recorren ambos valores con24pares cada uno,0,40m/300s, hasta672h.
La propuesta60 se confirma con matriz completa de24pares,0,20m/300s,
en el mismo horizonte. Los contrastes temporales separados300→150s de
M4_SS×2024/2025 conservan las condiciones físicas y protección de la propuesta.

No se cambia temperatura o protección al reducir q para favorecer una fila.
Se mantienen geometría, volumen físico, dos frentes disponibles de hasta30
m³/h cada uno,11capas,12°C, nueve circuitos,18°C ideal,18L/min por ramal,
Uv5W/(m³K), tope15kW, histéresis19/18, cobertura previa y ausencia de corte
global. Madera72h, primera manta240h y última504h son edades locales;
la sombra posterior transmite10% de la solar y mantiene los demás bordes
del ensayo. Se conservan fuentes, clima y pesos. Solo se escalan los
tiempos físicos de colocación y cobertura de ramales por60/q.

Se excluyenq>60 porque superan la capacidad máxima adoptada. Valoresq<55
no pueden mejorar la cota de duración si el volumen y la capacidad se
mantienen: no hace falta atribuirles una falla térmica. Las pruebas antiguas
50/45m³/h a336h son antecedentes, no resultados extendidos bajo esta
protección. La protección de sombra no representa una instalación real validada.

Para toda planificación admisible, con posibles esperas y retraso inicial:

\[
D=\max_jt_{j,fin}-t_0\ge\frac{V}{q_{max}}
=\frac{636.7751548866}{60}=10.6129192481\ \mathrm h.
\]

La propuesta coloca desde t₀=19/11/2026a10:00UTC−03:00, utiliza la capacidad
total y no introduce esperas. Por eso alcanza la cota de colocación; el
control térmico posterior no se suma aD. El vecino55 requiere11,5777300888h,
es decir0,9648108407h más, aproximadamente57,89min. Los datos térmicos
de ambas filas deben leerse de las matrices de esta familia, no de los
retiros originales360h sin sombra.

### Cómo representar los casos que pide la tabla

Se supone que suministro,equipos,moldajes y circuitos están preparados para
no introducir esperas adicionales durante la operación. El montaje real de
tubos/armadura y el recorrido de los frentes no están dimensionados por el
solver. Si generan pausas,deben incorporarse al cronograma y aD;no queda
acreditada una duración de obra completa de10,61h incluyendo preparativos.

- **Una sola vertida continua / propuesta:** una operación continua de todo
  el volumen, ejecutada en11capas físicas sin esperas de endurecimiento. Es
  el mismo caso constructivo y aparece una sola vez, como permite la pauta.
  No equivale a activar instantáneamente toda la fundación en el solver.
- **Desviación más rápida admisible:** no existe con estos recursos y ese
  volumen, puesD<V/60 violaría la capacidad. No inventar una probabilidad ni
  una corrida de75m³/h para completar una fila. Si se muestra la fila, indicar
  «no admisible por capacidad; no evaluada térmicamente», con probabilidadNA.
- **Desviación más lenta:**55m³/h, mismos controles y24pares, cuantificando
  su costo temporal y cambio de margen/riesgo. No presumir que más lento
  es más seguro; mostrar lo que realmente dio el cálculo.

La expresión defendible es «la más rápida entre los planes evaluados bajo
los recursos adoptados», indicando familia y paso. La cotaV/60 añade un
argumento temporal más fuerte que una comparación entre vecinos: ninguna
otra secuencia que respete esa capacidad puede terminar antes. La afirmación
sigue condicionada a continuidad constructiva, suministro,12°C y modelo
térmico. No se demuestra óptimo global entre otras geometrías, recursos,
mezclas o sistemas de protección, ni se optimiza la edad mínima de retiro.

## 6. Contenido listo para organizar la presentación

No es obligatorio copiar el orden sugerido de la pauta. La secuencia actual
de ocho principales puede conservarse si se cubren los contenidos siguientes
y se mantienen los respaldos para preguntas. El guion conversacional con
marcas de clic debe editarse después por integración, conservando su tono,
sin ejecutar generadores antiguos que lo sobrescriben.

|Lámina|Responsable|Contenido esencial que debe quedar|Tiempo objetivo|
|---|---|---|---|
|S1 Decisión|Benjamín|El Rosal, geometría IFC, operación continua10,61h, estrategia504h+sombra y probabilidad conjunta con horizonte/resolución|0:30|
|S2 Física|Benjamín|Hidratación, conducción, tubos equivalentes, viento/solar/onda larga, suelo;Ωactivo,S25 y resta simultánea|0:55|
|S3 Construcción y controles|Benjamín|t₀,11capas,duración física frente a activación instantánea, dos frentes, protecciones72/240/504h y sombra posterior; histéresis19/18|0:55|
|S4 Método y comprobación|Luis|Balance propio por celda,Euler explícito, estabilidad, caso conocido,balance y sensibilidad espacial/temporal separadas|1:00|
|S5 Mecanismo y resultados|Luis|CurvasTmax/sonda/S25/ΔT con umbrales, escenario e instante; corte comparable;por qué combinación funciona y medidas aisladas fallan|1:15|
|S6 Datos y probabilidad|Matías|Ocho curvas completas, tres climas,1/24 e independencia supuesta; ejemplo de falla real en alternativa,suma de pesos y alcance del5%|0:45|
|S7 Comparación y búsqueda|Matías|TablaD,P_T,P_Δ,P_f,cumple;Gantt yD–Pf;vecina55,cotaV/60 y exclusión de una opción más rápida|1:05|
|S8 Cierre|Matías|Cifras finales, principal limitación,cubierta ideal,tubos,sensores y contingencias;qué cambio exige reevaluar|0:35|
|Total|||7:00|

Los tiempos son presupuesto y no ensayo. Hay que practicar con los tres
integrantes, clics y transición. Cualquier integrante puede recibir preguntas
de cualquier sección. Los respaldos no forman parte del recorrido de7min.

### Resultados que deben verse

1. Tabla comparativa conD[h],P_T[%],P_Δ[%],P_f[%],cumplimiento,horizonte y
   resolución. La fila fina confirma la propuesta; no comparar su temperatura
   como si un cambio de malla fuera una mejora física del plan.
2. Cronogramas de11capas por plan con inicio y duración, escala común y t₀.
3. GráficoD–Pf con línea5%. Si ambos planes dan0%, mostrarlo: no alterar
   pesos, inventar fallas o cambiar ejes para obtener una curva atractiva.
4. Curvas de sonda interior, temperaturas máximas y mínimaS25, junto conΔT
   y los umbrales70°C/20K. La sonda interior no sustituyeTmax del dominio.
5. Corte de temperatura con unidades, posición, instante, fuente y clima.
   Los cortes comparativos conservan escala y hora. Centros de celda no son
   necesariamente el punto más caliente si una cara reconstruida lo supera.
6. Sensibilidad cuantitativa de las métricas:24cambios espaciales a672h y
   los contrastes temporales separados. Informar el tamaño del cambio y
   si cambia la clasificación, sin convertir dos niveles en prueba de orden.

Recursos nuevos en `cierre_revision_final/`: tablas completas y siete figuras
paraD–Pf,cronogramas,curvas comparables,cortes a672h,sensibilidad24pares,
ocho fuentes y tres climas completos.
Los gráficos de fuentes/clima y la comparación de las tres medidas se
conservan como respaldo, con sus hipótesis visibles.

## Teoría y método que debe dominar el grupo

### Balance continuo, unidades y activación

\[
\rho c_p\partial_tT=\nabla\cdot(k\nabla T)+\dot q_h(a)-\dot q_f,
\qquad a=t-t_{activacion,j}.
\]

ρ=2476kg/m³,cp=1023J/(kgK),k=2W/(mK). Las dos fuentes son volumétricas,
W/m³;ρycp proceden de los antecedentes del ensayo yk es un supuesto del
modelo, no un valor calibrado para cumplir. Cada capa se activa a12°C.
La edad se reinicia por capa y una fuente completa es común a todas las
capas de la realización. No hay cinética dependiente de temperatura.

El solver activa una capa completa en su inicio, mientrasD conserva su
duración física. El frente horizontal de llenado no se resuelve. Solo el
hormigón ya activado aporta temperaturas al dominio de evaluación; el aire,
el suelo y las capas futuras quedan excluidos.

### Fuente del profesor y control del calor total

El archivo suministrado ya contieneQ(a)enW/m³, obtenido por inversión de
probetas conβ2,5W/(m²K). No se interpreta temperatura no adiabática como
fuente ni se vuelve a multiplicar porρcp. Se integra la tablaQ con trapecios
de600s para formarE_h(a)[J/m³]. El solver interpolaE_h linealmente y usa
E_h(a+Δt)−E_h(a);la potencia equivalente por tramo es su pendiente. Se
conserva el calor integrado. Se adopta cola nula al terminar cada registro
(240,333hSS,163h22A),no hidratación física terminada a esa edad. El origen
de ventana retenida aproxima edad cero;faltan las primeras dos horas del
registro original.22A tiene menor confianza y la comparabilidad de recetas
no está confirmada. Se declaran escenarios de modelo, no recetas sorteadas.

### Bordes e interfaces por etapa

En caras al aire se resuelve la superficie exterior de la protecciónTs:

\[
q''_{in}=\frac{T_s-T_i}{h_m/(2k)+R_{protecciones}}
=h_c(t)(T_a-T_s)+\alpha\tau I+
\varepsilon\sigma(T_{rad,K}^4-T_{s,K}^4).
\]

q″positivo entra al hormigón.τ=1 antes del retiro local de la última manta,
y0,10 después,para el ensayo de sombra.α0,6,ε0,9 y el cielo estimado son
hipótesis. Las potencias cuartas usan kelvin. La cubierta no se discretiza;
el ensayo modifica solar y conserva convección/onda larga originales.

Si no hay protección,Ts es la cara de hormigón. Sin radiación, con normal
saliente, se recupera Robin−k∇T·n=h_c(T_s−T_a). Con protecciones hay que
distinguirTs exterior deT_face,hormigón y su conducción en serie. Se usa
h_c(t)=5,7+3,8v₂(t),v₂=v₁₀(2/10)^0,14;17,09 es solo una media de referencia.

En base se adopta un reservorio15°C sin inercia y resistencia equivalente
0,50/1,2m²K/W,además de media celda. No se simula un campo térmico de suelo.
Al cubrir una cara con otra capa, deja de ser borde exterior y pasa a
conducción interna con contacto perfecto: continuidad de temperatura/flujo
en el continuo,aproximada mediante el enlace conservativo entre centros.
Las superficies existentes yS25 se actualizan;no hay manta entre hormigones.

Protecciones nominales: madera18mm,k0,158 hasta72h;dos mantas40mm,k0,042,
retiros240/504h. Las edades no sustituyen resistencia y monitoreo. Laterales
expuestos sin relleno son una hipótesis de exposición. Agua18°C uniforme,
Uv5W/(m³K) y tope15kW son una extracción equivalente;no se calculan pared,
contacto ni agua axial. El caudal operativo no determinaUv ni acredita15kW.

### Balance discreto y actualización realmente utilizados

\[
C_i=\rho c_pV_i,\quad G_{ij}=kA_{ij}/\Delta x,
\]
\[
T_i^{n+1}=T_i^n+\frac{\Delta t}{C_i}
\left[\sum_jG_{ij}(T_j^n-T_i^n)+\sum_fA_fq''_{in,f}-P_{frio,i}\right]
+\frac{V_i}{C_i}[E_h(a_i^{n+1})-E_h(a_i^n)].
\]

Cada enlace entre vecinos activos agrega a una celda lo mismo que resta
a la otra. Las capas inactivas no conducen como hormigón colocado. La
refrigeración se reparte sobre celdas asignadas a ramales abiertos y se
limita globalmente a15kW. El control abre con cobertura y mínima monitoreada
≥19°C,cierra si algún tramo≤18°C,y mantiene estado entre18y19°C.

El avance es Euler explícito,conΔt≤300s y límite conservador
Δt≤0,8C/max(ΣG_ef). Incluye conductancias internas,de contorno yUvV;
para el borde no lineal se acota la conductancia efectiva porA/R_total.
No basta usar solo el número de Fourier de una celda interior. Los pasos
se recortan en eventos de activación,cobertura,retiro y cambio horario.
El balance superficial no lineal se resuelve porNewton con comprobación
del residual;y se contrastó con bisección independiente. No es un solver
térmico externo que reemplace el balance propio.

### Qué significa verificar, calibrar y validar

- **Verificación:** comparación con soluciones o cálculos independientes.
  Se ejecutaron24tests del solver1D,incluida la solución sinusoidal exacta.
  Su error cuantitativo se guarda en`VERIFICACION.json`. También pasaron
  sol–aire analítica,equilibrio radiativo,Newton frente a bisección,control
  de circuitos y una celda comparada con recurrenciaEuler independiente.
  El caso1D comprueba difusión;no acredita por sí solo toda la fundación3D.
- **Conservación:** residuos de energía global y descomposición del flujo
  exterior se auditan por corrida. El máximo residuo observado y las
  matrices auditadas quedan en`DATOS_CIERRE.json`.
- **Sensibilidad numérica:** se separa0,40→0,20m a300s de300→150s a0,40m.
  Se mantienen volúmenes físicos de referencia,414,016m³ refrigerables y
  tiempos de capas. Se informan cambios de métricas y clasificación.
- **Calibración:** no se ajustóUv,k o parámetros radiativos con medidas
  independientes de esta fundación. La inversión de probetas es antecedente
  de la fuente del profesor,no calibración experimental del conjunto.
- **Validación:** no hay registros independientes de la fundación para
  contrastar su predicción. No se afirma validación de tubos,cubierta o
  ausencia de fisuración mediante un análisis mecánico.

## Probabilidad y respaldo disponible, continuidad del punto4

Los escenarios son8fuentes completas×3historiasERA5del mismo período y
sitio,1/24 por par,bajo independencia supuesta. Una realización usa una
historia coherente de aire,viento y radiación;no valores horarios sorteados
de distintas curvas. Las fechas de descarga,coordenadas,unidades y zonas
están en los snapshots. Reponderar años o usar soloSS se informa como
sensibilidad de pesos;no añade escenarios meteorológicos ausentes.

\[
I_T=\mathbf1(M_T>70),\quad I_\Delta=\mathbf1(M_\Delta>20),
\quad I_F=\max(I_T,I_\Delta),\quad P_f=\sum_sw_sI_F.
\]

La tabla completa guarda144filas:3matrices×24pares×2horizontes336/672h,
con pesos,indicadores,posiciones e instantes. No dividir por48 ni contar
dos veces una corrida que excede ambos límites. Con1/24,una falla pesa
4,1667% ydos8,3333%. La decisión usa números sin redondear. El5% es
probabilidad de excedencia del modelo,no confianza estadística ni riesgo
real certificado. La enumeración no tiene error de muestreoMonteCarlo;
sí incertidumbre de entradas,representatividad,pesos y física.

Para mostrar una falla real sin inventarla en la propuesta,usar la variante
de sombra solaM4_SS×ERA5-2024 a428h:30,2942−6,8170=23,4772K,
I_Δ=I_F=1. Es una alternativa descartada con peso1/24,no una falla del
plan504h+sombra. Sus dos contrastes finos fallidos suman al menos8,3333%
de peso fallido en esa resolución,sin pretender tener su matriz fina completa.

## Sensores, contingencias y condiciones de cambio de decisión

Conservar sensores de núcleo/pedestal,S25 y tramos representativos de
circuitos;medir aire,caudal y agua de entrada/retorno,y comprobar exposición
de la cubierta. Los umbrales65/68°C y18/19K son propuestas operativas de
anticipación,no límites normativos. Ante tendencia adversa:detener retiros,
verificar datos,cobertura y refrigeración,y actualizar la predicción. No
incrementar automáticamente frío suponiendo que siempre reduceΔT.

La decisión cambia si no se sostiene12°C,60m³/h,la continuidad de unión,
la sombra requerida o la transferencia equivalente adoptada;si cambia la
exposición;si aparece un clima relevante fuera del catálogo;o si el
refinamiento cambia la clasificación. No se declara fecha definitiva de
apagado o retiro de sombra:no se simuló desmontarla después de672h.

## Cierre de esta revisión y pendientes humanos

Esta etapa prepara evidencia y contenido;no declara ensayo oral realizado,
equipos contratados o instalación real validada. Quedan ensayo cronometrado,
apertura de archivos sin internet en el equipo de defensa y formación cruzada
de los tres integrantes. El SHA final de entrega y publicación no se inventan
ni se realizan sin el flujo autorizado correspondiente.

Al integrar al PPT deben actualizarse de forma coordinada decisión,protecciones,
comparación,gráficos,notas y preguntas,conservando el diálogo personalizado y
sus marcas de clic. La tabla antigua60/55/50/45 a336h no se presenta como
una tabla extendida de esta familia. La matriz fina completa nueva debe
distinguirse de las confirmaciones selectivas antiguas.

## Material de entrega del apartado7 del documento completo

La copia local `Enunciados e Instrucciones/Enunciados/F02_DEFENSA_FINAL.txt`
incluye además el material que se entrega al comenzar la sesión y la rúbrica.
Se prepara el siguiente índice, sin declarar realizadas las tareas excluidas:

|Elemento exigido|Dónde queda o qué falta|
|---|---|
|PDF con autores,grupo y respaldo|Existe presentación anterior;pendiente integrar este cierre y exportar PDF coherente|
|Repositorio ySHA de defensa|Repositorio del grupo identificado;SHA final pendiente de congelación/publicación,no usar elSHA del solver base comoSHA de la entrega|
|Entorno y comandos|requirements.txt,Python3.12 y entrada`ejecutar_cierre_f02.py` para estado,caso individual,comparación y auditoría|
|Curvas,sitio,t₀,snapshots|manifiestos de hidratación/clima,documentación de inicio y procedencia de cada pieza|
|Planes,escenarios,pesos y métricas|configuración de cierre,JSON individuales,CSV144filas y tablas agregadas|
|Clima congelado e información no incorporada|se conservan snapshots usados;datos posteriores no sustituyen las corridas ni se presentan como ya evaluados|

La rúbricaC1–C8 no es una certificación automática por tener archivos. Este
cierre aporta evidencia paraC1–C6;C7requiere exposición clara dentro del tiempo
yC8comprensión individual demostrada. No se asignan puntajes al grupo o sus
integrantes sin la evaluación del profesor.

## Fuentes y alcance de la sombra

Las fuentes técnicas y climáticas del modelo están reunidas en
`ECUACIONES_MODELO_VIGENTE.md`,`PROTOCOLO_RADIACION.md` y los snapshots.
Los fabricantes ofrecen productos con alto sombreo:el catálogo deProtekta
incluye90%,y las fichasGALEdistinguen factor de sombra y transmisiónUV-visible.
Eso respalda disponibilidad de materiales de sombreo,pero no demuestra por
sí soloτsolar0,10 de toda la energía incidente en la instalación real.

- https://www.protekta.cl/catalogo.pdf
- https://www.galecommercial.com/uploads/gale_commercial/documents/Commercial_NinetyFive_340_Product_Profile.pdf

La hipótesis del cálculo conserva10% solar residual,no lo desprecia. Debe
acreditarse transmisión solar efectiva y montaje que cubra laterales y
coronación. Los cambios reales de viento o emisión de la cubierta no se
resolvieron. No se presenta el porcentaje de una etiqueta comercial como
validación de ese balance energético.
