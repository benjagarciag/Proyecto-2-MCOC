# Respaldo y límites del suelo y las protecciones

Revisión documental y contraste de datos, sin simulaciones del agente.
No se modificaron parámetros ni se recalcularon las matrices de F02.

## Exposición constructiva

El usuario confirmó que el material recibido no especifica si los laterales
están enterrados o expuestos. Se declara como escenario de planificación
para interpretar las corridas actuales: excavación abierta y laterales
expuestos durante el hormigonado y el período de control térmico simulado,
sin relleno lateral dentro de ese horizonte. Esto no es una condición
confirmada de El Rosal ni un plano de excavación aprobado. No se asignaron
dimensiones, pendientes ni sistemas de sostenimiento a la excavación.
Si se decide rellenar antes o hay contacto lateral con terreno, deben
modificarse bordes y evaluarse esa alternativa.

El terreno verde de Blender no prueba contacto térmico: el dossier E06
declara que es de presentación y que se omite geometría del suelo.

## Temperatura de suelo: contraste adicional conservado

Se descargó ERA5 mediante Open-Meteo para las mismas coordenadas exactas
(-37,277929; -72,368271), años 2023/2024/2025 y fechas 19 noviembre–17
diciembre. Se conservaron snapshots nuevos `suelo_era5_*.json` bajo
`datos/clima/reanalisis/`, sin sobrescribir los de aire/viento.
Cada snapshot conserva URL, fecha de descarga UTC, coordenadas, modelo,
variables y respuesta original con marcas y unidades.

Se comprobó cobertura de 336/600/672 h desde las 10:00 locales del 19
noviembre. Medias para [0,600 h), en °C:

| Año | 28–100 cm | 100–255 cm |
| --- | ---: | ---: |
| 2023 | 22,000 | 12,940 |
| 2024 | 16,567 | 13,373 |
| 2025 | 18,529 | 14,477 |

Los 15 °C del modelo no representan las medias de todas estas capas/años.
El contraste muestra el orden de magnitud y la importancia de la profundidad,
no valida el reservorio elegido. Estas profundidades se miden bajo la
superficie del producto meteorológico, no bajo la cara inferior de nuestra
excavación, cuya cota respecto del terreno original no se ha confirmado.
No trasladar las series a la base del hormigón sin justificar esa relación.
ERA5 representa suelo sin el calentamiento impuesto por nuestra fundación.

Fuente oficial de variables y producto:
https://open-meteo.com/en/docs/historical-weather-api

Script: `suelo_datos.py` solo descarga/analiza meteorología. No ejecuta
el solver. Reutiliza snapshots si ya existen. Tabla completa:
`resultados/revision_suelo_protecciones/contraste_suelo_era5.csv`.

## Conductividad, longitud y contacto

k_suelo=1,2 W/(m·K), longitud=0,50 m y resistencia adicional de contacto
nula siguen siendo hipótesis de un borde equivalente. R_suelo=0,50/1,2
=0,4167 m²·K/W. No se halló un estudio geotécnico local que identifique
la conductividad/humedad o valide esa resistencia. La conductividad del
artículo base pertenece a otro suelo y no resuelve esta falta.

La longitud de 0,50 m no es un espesor de suelo calculado ni corresponde
automáticamente a las capas meteorológicas descargadas. El reservorio
carece de capacidad de almacenamiento y no se calienta. Para validar esta
aproximación se necesita contraste con un modelo transitorio del suelo
o datos térmicos independientes; una sensibilidad solo cuantifica su
influencia. Si se conserva el borde equivalente, declarar la limitación y
estudiar temperatura y resistencia por separado antes de afirmar robustez.

## Materiales de protección: respaldo documental

Se respalda el valor de conductividad empleado para madera de 18 mm con
el catálogo AraucoPly Australia/Nueva Zelanda, p.22, tabla 11:
https://arauco.com/aus-nz/wp-content/uploads/sites/16/2018/02/Product-Catalog-Australia-NZ-1.pdf

Para lana de vidrio de 40 mm se respalda k=0,042 W/(m·K), con R publicado
0,94 m²·K/W, en la ficha Volcán Aislanglass, p.1:
https://volcan.cl/wp-content/uploads/2022/05/lana_de_vidrio_ces.pdf

Esto respalda propiedades de referencia; no certifica el montaje temporal
propuesto. La ficha identifica usos de edificación y pide corroborar la
información específica del proyecto con el proveedor. No se ha verificado
que una manta desnuda de edificación mantenga sus propiedades expuesta al
agua, viento, compresión y condiciones de la obra.

Requisitos de la solución constructiva propuesta, pendientes de diseño:
dos capas de 40 mm sin compresión que reduzca el espesor previsto,
continuidad de cobertura, protección exterior contra ingreso de agua,
fijación contra desplazamiento y soporte independiente del moldaje que
permita mantener la lana después de retirar la madera. No se especifica
un producto de envoltura, anclajes ni dimensiones sin respaldo del proveedor.

## Retiros y control térmico

72 h para madera proviene del ejemplo docente. 240/360 h para mantas
provienen del ensayo de protección escalonada. Ninguna fuente revisada
establece esas edades como garantía universal de retiro seguro.

ACI explica que el control debe mantenerse considerando el estado térmico
al retirar protecciones y la diferencia entre interior y ambiente medio
diario; no prescribe aquí un retiro automático al cumplir cierta edad:
https://www.concrete.org/frequentlyaskedquestions.aspx?faqid=891

El valor de referencia ACI (19 °C en esa explicación) y su definición no
reemplazan el criterio docente: Tmax<=70 °C y max_t(Tmax-Omega−Tmin-S25)
<=20 °C por escenario, agregado al 5 % conjunto. Son comprobaciones distintas.

Para la defensa, las edades son decisiones del plan que se someten a
evaluación; las mediciones en obra deben acompañar cualquier retiro real.
Los fallos térmicos encontrados con el modelo horario impiden afirmar
que el plan actual y sus retiros están validados. El mayor diferencial
de la única aparece después del último retiro. Una propuesta modificada
debe simular sus retiros reales y cubrir los picos posteriores; mantener
protección indefinidamente no prueba cumplimiento.

## Estado de cierre

| Elemento | Estado |
| --- | --- |
| Propiedades de referencia de madera y lana | Respaldadas documentalmente |
| Temperatura 15 °C | Contrastada con datos históricos de suelo; no validada en la base |
| k_suelo, longitud equivalente y contacto | Hipótesis pendientes de comprobación |
| Laterales al aire | Escenario declarado, porque el material no lo especifica |
| Montaje de la protección | Requisitos formulados; falta solución específica |
| Retiros 72/240/360 h | Decisiones de estudio; no validadas como seguras |

Antes de cerrar la revisión física se retomará k del hormigón según lo
solicitado: elección defendible y sensibilidad, sin escogerlo para lograr
cumplimiento. Estos pendientes no se resuelven identificando un “k óptimo”.
