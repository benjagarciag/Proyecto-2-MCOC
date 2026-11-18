# Evidencia externa del caudal de colocación

Consulta de fuentes primarias el18-11-2026. Caudalq se expresa enm³/h;
el tiempoD se expresa enh. MinimizarD requiere maximizar el caudal factible,
sin perder cumplimiento térmico ni calidad constructiva. No existe un único
«mínimo tiempo» publicable para cualquier fundación, independientemente
de recursos, suministro, mezcla, geometría y sitio.

## Fuentes de construcción y fabricantes

| Fuente | Lo que publica | Lectura válida para nuestro estudio |
| --- | --- | --- |
| Mathern y Magnusson2022, estudio de construcción de fundaciones eólicas en Suecia | Volumen aproximado550 m³ por fundación; tiempo medio de hormigonado15,6 h | Cociente calculado≈35,3 m³/h como orden de magnitud del ritmo medio; no es curva de producción individual ni capacidad máxima del equipo. |
| CEMEX UK, Moor House Wind Farm | Material especificado para bombeo de aproximadamente40 m³/h;8 mixers y2 plantas | Caso de suministro/ritmo previsto por proveedor; no presentarlo como registro horario medido ni extrapolar flota/ruta. |
| DNV North American Civil Engineering Team2022 | Descripción de fundación de850–900 yd³ y colocación de7–9 h | Convertidos,≈650–688 m³; cocientes extremos≈72–98 m³/h. Es una inferencia nuestra de los rangos descritos por DNV, no una campaña experimental de caudales ni garantía para El Rosal. |
| Putzmeister PUMI25-4, ficha técnica | Distintas configuraciones de bomba con capacidades máximas teóricas; especifica que máximos de presión/caudal no son simultáneos | Un valor de catálogo no equivale al caudal sostenido de una obra. No seleccionar equipo porq nominal solamente. |

Enlaces directos:

- [Mathern y Magnusson, DOI10.3390/app12031443, secciones2 y3.2](https://www.mdpi.com/2076-3417/12/3/1443).
- [CEMEX, Energy and Power Projects, Moor House](https://www.cemex.co.uk/solutions/renewable-energy/energy-power-projects).
- [DNV, Foundation concrete voids](https://www.dnv.com/article/foundation-concrete-voids-229998/).
- [Putzmeister, ficha PUMI25-4](https://www.putzmeister.com/documents/20127/68709/Pumi%2B25-4%2BData%2BSheet%2BEN.pdf/d3d34e17-427c-b8c4-93be-ab81ed207cce?t=1739880981742).

Estos ejemplos son contextos distintos, no una muestra con la que estimar
percentiles o asignar probabilidades a nuestro caudal. No usar un récord
de bombeo de otra clase de estructura como objetivo de esta fundación.

## Qué representan nuestros60 m³/h

Son una hipótesis de caudal efectivo continuo para simular, no un valor
demostrado en la obra ni rendimiento extraído de estas fuentes.
La flota hipotética16 activos×7,5 m³/ciclo2 h da60 m³/h **en régimen**:
los ciclos incluyen todas las actividades y deben sostenerse sin colas
ni pérdidas adicionales no contabilizadas. No se aplicó un factor de
disponibilidad medido; los2 camiones de reserva no prueban esa continuidad.

Por ello, V/60=10,613 h es una duración condicional idealizada. Podría
ser alcanzable con recursos adecuados, pero no puede llamarse menor
tiempo real ni máximo físico de colocación sin más evidencia.

Ejemplo puramente logístico: con los mismos16 activos y7,5 m³, si el ciclo
real es2,5 h, el transporte baja a48 m³/h yD=13,266 h, antes de otras
restricciones. Si se conocen pérdidas, evitar descontarlas dos veces:
o bien se incluyen en el caudal efectivo promedio, o se agregan esperas
explícitas al tiempo de operación, identificando qué representa cada dato.

El caudal efectivo depende del cuello de botella entre planta a12 °C,
transporte, bombeo y distribución/compactación. Necesitamos rutas/ciclos,
rendimiento de planta preenfriando, mezcla bombeable, cuadrilla, equipos
y continuidad. La variación de caudal cambia también la colocación
progresiva y por tanto debe reevaluarse térmicamente.

## Cómo usar esta evidencia

Mantener60 como referencia y ampliar el estudio, si se desea explorar más
rápido y más lento, a escenarios40/60/80 m³/h como primera exploración.
Es una propuesta de búsqueda respaldada en orden de magnitud, no una
recomendación de recurso contratado.80 exigiría≈22 activos ideales con
carga7,5 m³/ciclo2 h (capacidad82,5, operada con límite80), además de planta,
bombeo, compactación y reservas suficientes. No compararlo con60 como
si la capacidad extra no cambiara el escenario de recursos.

Para V636,775 m³:40→15,919 h;60→10,613 h;80→7,960 h. Refinar cerca
del candidato decisivo y declarar alcance de búsqueda. Esas duraciones
son cálculosV/q, no resultados térmicos ni compromiso de obra.

El límiteV/60 sigue válido **dentro de la familia cuyo recurso máximo
se fija a60**. Queda corregida cualquier interpretación de10,61 h como
mínimo universal o como caudal de obra validado bibliográficamente.

Investigación posterior de oferta local y hoja de datos para estimar
rendimiento del sitio: [suministro en El Rosal](SUMINISTRO_EL_ROSAL.md).
