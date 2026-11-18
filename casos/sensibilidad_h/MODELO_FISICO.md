# Revisión física de F02

Revisión por etapas, sin nuevas simulaciones ni cambios de parámetros.
Base examinada: commit 6718163118123c4b05667b91ad5b4d50124dcf2d y
adaptadores locales de sensibilidad. No confundir con los parámetros
didácticos de E12 todavía presentes en main.

## 1. Propiedades del hormigón

| Parámetro | Valor efectivo en F02 | Procedencia | Alcance |
| --- | ---: | --- | --- |
| Densidad | 2476 kg/m³ | Cabecera de source_terms.txt y manifiesto de ocho curvas | Adoptada para el hormigón simulado; correspondencia de mezcla pendiente |
| Calor específico | 1023 J/(kg·K) | Mismo archivo | Constante, asociado a las fuentes de las probetas |
| Conductividad | 2 W/(m·K) | Parámetro docente heredado de Semana 4 | No se identificó medición de las probetas que lo confirme |

Se comprobó la ruta efectiva: `materiales()` toma rho y cp del manifiesto,
con prioridad sobre la configuración base. `CurvaTabular` guarda su producto
y el solver usa C=(rho*cp)*V. Los 2400/900 de la configuración base no se
usan como capacidad al cargar las fuentes tabulares del manifiesto.
La conductividad procede separadamente de `entorno.k_W_mK`.

Capacidad volumétrica efectiva: 2 532 948 J/(m³·K). Difusividad derivada
con k=2: 7,89594e-7 m²/s. No se prescribe alpha de forma independiente.
Q ya viene en W/m³ de hormigón y se integra a J/m³; no se multiplica otra
vez por el contenido de cementante ni por rho*cp. El incremento térmico
de la fuente es DeltaE/(rho*cp).

La Tabla 2 del artículo de Ju y Lei (2019), página 7, informa para su
hormigón k=8 kJ/(m·h·°C)=2,2222 W/(m·K), cp=0,97 kJ/(kg·°C)=970
J/(kg·K), rho=2400 kg/m³. Son parámetros de su caso; no sustituyen
automáticamente los asociados al archivo de fuentes del profesor.
Nuestro k=2 es un 10 % menor que 2,2222, pero cercanía no equivale a
calibración. El origen docente debe mantenerse explícito; justificarlo
mediante referencia aplicable o sensibilidad antes del cierre físico.

Hipótesis: material homogéneo/isótropo; k, rho y cp constantes en el
tiempo y con la temperatura. Se usa una curva por realización, común a
las vertidas, con fuente prescrita por edad; no hay aceleración/retardo
de hidratación por la temperatura simulada. Se evalúa transferencia
térmica, sin modelo mecánico de fisuración.

Estado: rho y cp tienen trazabilidad y se usan coherentemente con el
archivo del profesor; k conserva fundamento docente provisional. No se
modificaron parámetros y los resultados existentes conservan su configuración.

El usuario decidió conservar rho=2476 y cp=1023. Se preparó una sensibilidad
independiente de k (1,6; 2; 8/3,6; 2,4 W/(m·K)) con h horario y fuente
sin cambios, documentada en [CONDUCTIVIDAD.md](CONDUCTIVIDAD.md). k=2
se mantiene como referencia. El usuario ejecutó la sensibilidad: P_f fue
12,50 %, 8,33 %, 8,33 % y 4,17 %, respectivamente, en malla 0,50 m/900 s.
La clasificación depende de k en el rango explorado; el caso k=2,4 tiene
un margen individual pequeño que requiere confirmación si se utiliza para
la decisión. No se adopta ese valor por su resultado favorable. El valor
del artículo no cambia la clasificación de k=2. Detalles en CONDUCTIVIDAD.md.

## 2. Suelo y contacto

Configuración efectiva: reservorio a 15 °C, conductividad equivalente
1,2 W/(m·K), longitud de conducción equivalente 0,50 m, plano base z=0.
Se aplica solo a caras inferiores expuestas que coinciden con ese plano.
Las demás caras externas reciben borde de aire: el solver no distingue
laterales enterrados o apoyados contra una excavación. Esa exposición requiere
una hipótesis constructiva explícita; no se deduce solo de la geometría IFC.

El flujo por cara hacia la celda es:

    P_suelo = A*(15-T_celda)/(d_celda/k_hormigon + 0,50/1,2)

No se fija la temperatura del hormigón a 15 °C. Se supone resistencia de
contacto adicional nula, no hay capa de limpieza ni membrana modeladas.
La resistencia del suelo por unidad de área es 0,4167 m²·K/W. Los 0,50 m
son una longitud del modelo equivalente, no una cota de estrato verificada.
No se discretiza el terreno ni se usa su densidad/capacidad térmica.
El reservorio mantiene T fija sin calentarse: no se ha cuantificado el
error de esta aproximación durante los 25 días de evaluación.

No se identificó respaldo geotécnico o medición térmica local para 15 °C,
1,2 W/(m·K) ni la distancia equivalente. El artículo base usa para su suelo
5 kJ/(m·h·°C)=1,3889 W/(m·K), pero eso no valida los parámetros de El Rosal.
El tipo de suelo y su humedad pueden alterar la conducción; no se asignan
propiedades oficiales sin antecedente. Si se mantiene el reservorio,
declarar explícitamente temperatura y resistencia como hipótesis y valorar
su sensibilidad antes del cierre. No cambiar estos valores para aprobar.

En el escenario M4_SS × ERA5-2024 de la única, h horario, malla 0,50 m,
la energía acumulada perdida al suelo hasta 600 h es 15,216 GJ. Es una
salida del modelo, no una medición, y muestra que este término no es
despreciable frente a los demás intercambios. No prueba que el suelo sea
la superficie que controla el diferencial: el S25 crítico de ese caso
está próximo a un lateral.

## 3. Moldaje y aislación de las corridas actuales

No confundir con E12, que usaba una capa lateral de 40 mm hasta 96 h.
Las sensibilidades de F02 parten de la variante de retiro escalonado:

| Elemento | Aplicación | Conductividad | Retiro desde activación |
| --- | --- | ---: | ---: |
| Madera 18 mm | Laterales expuestos | 0,158 W/(m·K) | 72 h |
| Primera capa de lana 40 mm | Laterales y caras superiores expuestas | 0,042 W/(m·K) | 240 h |
| Segunda capa de lana 40 mm | Mismas caras | 0,042 W/(m·K) | 360 h |

Se modelan 80 mm iniciales de lana, que pasan a 40 mm y luego a cero.
Las capas no se añaden al suelo ni a interfaces con hormigón vecino.
Al activarse la vertida adyacente, el borde expuesto se vuelve conducción
interna. No se modela una manta atrapada entre vertidas.

La conductancia a aire suma resistencias de media celda, capas y película
convectiva. R_madera=0,1139 m²·K/W; R_lana40=0,9524 m²·K/W; dos capas
suman 1,9048 m²·K/W. La ficha Volcán publica R=0,94 para 40 mm, con k
redondeado a 0,042; el código usa e/k. No confundir esta resistencia de
capas con h ni con la conductancia de cara H en W/K.

Fuentes: catálogo AraucoPly Australia/Nueva Zelanda, p.22, tabla 11, para
conductividad de 18 mm; ficha Volcán Aislanglass Rollo Libre, p.1, para 40 mm:
https://arauco.com/aus-nz/wp-content/uploads/sites/16/2018/02/Product-Catalog-Australia-NZ-1.pdf
https://volcan.cl/wp-content/uploads/2022/05/lana_de_vidrio_ces.pdf

Son referencias de propiedades, no una especificación validada de montaje
temporal para esta obra. Correspondencia del grado chileno de madera,
protección contra humedad, compresión de lana, fijación y continuidad
de mantas requieren definición. Tras retirar el moldaje a 72 h, la lana
lateral debe poder permanecer hasta 360 h: su soporte no está modelado.
Las capas se tratan sin inercia térmica y sin resistencias de contacto
adicionales, puentes o huecos.

Los retiros 72/240/360 h son decisiones docentes/de estudio. El código no
comprueba resistencia mecánica, madurez ni condiciones de retiro seguro.
Los cambios de resistencia ocurren instantáneamente por edad y no mediante
un criterio de monitoreo. Para la única, el retiro final es a 360 h; los
picos diferenciales de h horario ocurren después, a 380 y 428 h. Debe
explicarse el enfriamiento exterior posterior al retiro y conservar el
horizonte extendido; prolongar la aislación no demuestra por sí solo mejora.

Estado: propiedades térmicas de capas trazables; montaje y retiros aún
condicionados. Suelo equivalente explícito, sin validación local identificada.
No se han cambiado parámetros ni ejecutado simulaciones al revisar este punto.

Revisión posterior: el usuario confirmó que no se especifica exposición
lateral en el material. Se documentó excavación abierta/laterales expuestos
como escenario del plan, sin presentarlo como condición real confirmada.
Se conservaron descargas adicionales de temperaturas de suelo ERA5 para
contrastar 15 °C, sin simular ni cambiar el borde. Las medias dependen
materialmente de profundidad y año: los datos no validan un reservorio
universal a 15 °C. Alcance, fuentes, requisitos de montaje y pendientes
en [SUELO_PROTECCIONES.md](SUELO_PROTECCIONES.md).

Por autorización explícita posterior del usuario se ejecutó la sensibilidad
independiente del suelo: cinco matrices nuevas, 120 pares, verificadas.
La temperatura 12/15/18 °C conserva 8,33 % y 22 °C lo eleva a 12,50 %;
resistencias mitad/doble también dan 12,50 %, con diferentes mecanismos.
No quedó ninguna alerta de horizonte. Son resultados en malla exploratoria,
no validación geotécnica. Detalle en [SENSIBILIDAD_SUELO.md](SENSIBILIDAD_SUELO.md).

## Etapas siguientes

4. Vertidas: temperatura inicial, activación y contacto entre bloques.
5. Enfriamiento: ley, potencia, máscara y viabilidad física.
6. Cierre ambiental: exposición, h y limitaciones de radiación/humedad.

Antes de cerrar la revisión física, retomar la elección defendible de k y
su efecto sobre la recomendación. La sensibilidad no identifica un “k óptimo”
intrínseco del material ni permite seleccionarlo para cumplir el límite.
