# Comparación de moldaje y aislación: térmica, montaje y costos

Consulta web: 12 de noviembre de 2026. Moneda: CLP. Preselección para el estudio
docente de El Rosal, no presupuesto de ejecución ni dimensionamiento estructural.
Los precios son los observados en las páginas citadas, sujetos a ubicación,
promociones, existencias y despacho. No se contactó a proveedores ni se ejecutaron
simulaciones. No se modificaron los parámetros de entrada con esta comparación.

## Aislación: comparación comercial

| Producto | Precio publicado | Cobertura | Material por m² |
| --- | --- | --- | --- |
| Aislanglass Rollo Libre 40 mm | 62.590 por rollo | 28,8 m² | 2.173 |
| Aislanglass Rollo Libre 50 mm, 1,2 x 12 m | 33.090 por rollo | 14,4 m² | 2.298 |
| EPS Aislantes Parral 50 mm, 20 kg/m³, 12 planchas de 0,5 x 1 m | 25.406 en promoción | 6 m² | 4.234 |
| FibranXPS ETICS GF 40 mm | 12.290 netos por m² | Tabla para compras desde 60 m² | 14.625 con IVA calculado al 19 % |
| Manta específica de curado Norseman | Cotización necesaria | Según modelo | Sin precio local verificado |

Fuentes comerciales: [Volcán, 40 mm](https://tienda.volcan.cl/products/lana-de-vidrio-aislanglass-rollo-libre-40-mm-r100-94-1-2-x-24-m),
[Volcán, lista 50 mm](https://tienda.volcan.cl/collections/marca-aislanglass),
[Dimaco, EPS](https://www.dimaco.cl/materiales-de-construccion/aislacion/planchas-de-poliestireno),
[XPS Chile, tabla de precios](https://www.xpschile.cl/).
Se conserva el precio al público mostrado por los comercios; confirmar IVA al
cotizar. XPS declara precio neto, por eso se convirtió explícitamente.
La cifra de XPS no corresponde al producto FOAMULAR investigado anteriormente.

No son costos instalados: faltan soporte, protección, fijaciones, sellos, pérdidas,
mano de obra, transporte a Los Ángeles, desmontaje y disposición o reutilización.
No trasladar estos valores automáticamente a toda el área de la fundación:
se deben medir superficies y etapas de cobertura.

## Cómo controlan el calor

Todas estas alternativas pasivas dificultan el paso del calor. No enfrían
activamente. Su efecto depende de resistencia, continuidad, cobertura y tiempo
de permanencia. Más resistencia puede mantener la superficie más caliente,
pero también elevar Tmax; no garantiza satisfacer ambos criterios del curso.

| Alternativa | Resistencia de referencia | Alcance del dato |
| --- | --- | --- |
| Lana de vidrio 40 mm | e/k = 0,952 m²·K/W | k=0,042; ficha publica R=0,94 |
| Lana de vidrio 50 mm | e/k = 1,220 m²·K/W | k=0,041; ficha publica R=1,22 |
| EPS 50 mm | Pendiente para el producto cotizado | No atribuirle automáticamente la ficha de otra marca de igual densidad |
| FibranXPS ETICS GF 40 mm | e/k = 1,25 m²·K/W como referencia | k=0,032 en catálogo europeo; confirmar declaración del suministro chileno |
| Manta de curado | Depende del modelo y ensayo | No usar valores con cámara de aire si no existe esa cámara en el montaje |

Fuentes técnicas: [Volcán, ficha CES, página 1](https://volcan.cl/wp-content/uploads/2022/05/lana_de_vidrio_ces.pdf),
[FIBRAN, catálogo de producto](https://fibran.si/wp-content/uploads/sites/7/2024/12/0100_FIBRAN_Product_Catalogue.pdf),
[Norseman, mantas con resistencia ensayada](https://www.norsemansolutions.com/en/concrete-curing-blankets).
Los valores comerciales de R se distinguen de e/k calculado con cifras redondeadas.
FIBRAN declara un límite de uso de +75 °C en la
[ficha ETICS GF](https://fibran.si/wp-content/uploads/sites/7/2023/04/SI_TDS_FIBRANxps_ETICS_GF.pdf).
Verificar la temperatura real de la capa, además de efectos de exposición solar;
el máximo del hormigón no es por sí solo su temperatura de servicio.

## Montaje a estudiar sobre el moldaje

Estos son esquemas conceptuales para comparar constructibilidad, no instrucciones
de anclaje ni detalles aprobados por los fabricantes para esta obra.

- **Lana de vidrio:** capa exterior continua con soporte que mantenga su espesor
  y protección frente a lluvia y desplazamiento. Evitar comprimirla; revisar
  encuentros y huecos. Es flexible, lo que puede facilitar acomodarla alrededor
  de la geometría, pero el conjunto debe poder retirarse/reinstalarse si el
  moldaje se desencofra antes. Volcán recomienda proteger el rollo de lluvia en
  obra en su página del producto de 40 mm.
- **EPS:** planchas exteriores sujetas con un sistema desmontable a definir,
  juntas continuas y protección compatible. Las caras curvas exigen estudiar
  el despiece. Su rigidez evita el problema de sostener una colchoneta, pero
  no elimina necesidad de fijación frente al viento. Temperatura admisible y
  conductividad del producto cotizado siguen pendientes.
- **XPS:** esquema de planchas semejante, con datos del fabricante para ambiente
  húmedo. Exige continuidad entre paneles, fijación y revisión de temperatura
  de servicio. No debe confundirse una aplicación permanente de fachada con
  un montaje temporal ya validado sobre encofrado.
- **Manta de curado:** paños flexibles sobre moldaje o superficies autorizadas,
  unidos y sujetos mediante los accesorios del producto. Norseman declara
  ojales y construcción reforzada. La disponibilidad, el modelo apropiado y su
  precio puesto en obra deben cotizarse; no se verifica una venta local.

La cubierta superior requiere diseño de curado/protección y asignación propia
en el solver. Las capas actuales del programa se aplican solo a los laterales.
Mantener humedad de curado y aportar resistencia térmica son funciones distintas.

## Comparación del moldaje

| Sistema | Montaje y uso | Precio y límite de comparación |
| --- | --- | --- |
| Tablero ARAUCOPLY Moldaje 18 mm con estructura diseñada | Corte, sellado de cantos, fijación sobre apoyos y arriostramiento según diseño | Easy mostraba 47.070 por tablero 1,22 x 2,44 m: 15.812/m² de tablero. No incluye el sistema completo |
| Modular Doka Frami Xlife, marco metálico y tablero | Paneles unidos con grapas, anclajes y accesorios del sistema; opciones para cimientos | Requiere cotización por configuración y duración; no hay precio local completo verificado |
| Polímero PERI DUO | Paneles modulares y accesorios propios, orientado a manipulación manual | Requiere cotización; conductividad o resistencia del conjunto pendiente |

Fuentes: [precio Arauco en Easy](https://www.easy.cl/materiales-de-construccion/maderas-y-tableros/terciados-estructurales),
[ficha de tablero ARAUCO](https://arauco.com/chile/wp-content/uploads/sites/14/2018/03/Ficha-T%C3%A9cnica-Moldaje-Chile.pdf),
[Doka Frami Xlife](https://www.doka.com/es/system-groups/doka-wall-systems/framed-formwork/frami-xlife/index),
[PERI DUO](https://www.peri.cl/productos/duo-formwork.html).
No comparar el precio de compra de una placa con el arriendo de un moldaje
completo. Tampoco equiparar marco de acero con cara de contacto de acero.
Para el tramo circular deben verificarse tolerancias y solución específica;
no asumir que un tablero de 18 mm puede curvarse hasta cualquier radio.

## Resultado de la preselección

**Recomendación provisional para comparar térmicamente:** conservar la madera
como referencia y contrastar lana de vidrio de 40 y 50 mm. Según estas ofertas,
50 mm cuesta 5,7 % más por m² y aporta 28 % más resistencia calculada. Es una
candidata económica para el estudio, no una selección definitiva para obra.

XPS ofrece una alternativa rígida con documentación para humedad, a un costo
de suministro sensiblemente mayor. EPS queda como opción intermedia cuyo dato
térmico específico debe obtenerse. Una manta de curado podría resolver mejor
la ejecución temporal, pero faltan cotización local y modelo comparable.

Para determinar el ganador real: comparar Tmax y DeltaTmax durante 336 h con
la misma malla, clima, fuente y plan; comparar cobertura/retiros; después cerrar
costo instalado por uso. Si no satisface los límites, el menor costo no basta.
Considerar que una mayor inversión reutilizable puede convenir con varias
puestas, pero no se conoce aún un número de reutilizaciones para presupuestar.

Faltan cantidades por etapa, cotizaciones de sistemas completos, transporte,
protección/fijaciones y mano de obra. No se asignaron valores inventados a esos
ítems ni se presentaron resultados térmicos de corridas no ejecutadas.

## Ejecutar la comparación de 40 y 50 mm

Abrir `casos/semana4/comparar_aislacion.py` en VS Code y pulsar **Run Python File**.
Elegir **1: E12, 14 días**, y una malla común a las dos corridas. Para una primera
comparación usar 0,50 m; antes de adoptar una conclusión revisar también 0,25 m.

El ejecutor usa `aislacion_40mm.json` y `aislacion_50mm.json`: cambia la pareja
espesor/conductividad (40 mm / 0,042 y 50 mm / 0,041), manteniendo iguales las
demás entradas. No se trata de cambiar solo el espesor con k idéntica: son las
dos presentaciones documentadas. Ambos casos conservan retiro a 96 h y cobertura
solo lateral; por tanto, el resultado compara ese escenario de protección.

Cada corrida guarda su HTML y VTI en
`resultados/e12/comparacion_aislacion/malla_050/lana_40mm/` o `lana_50mm/`
(para 0,25 m, usar `malla_025`). La tabla `comparacion.md` del directorio de malla
informa Tmax, DeltaTmax, tiempos y ambos criterios. El visor PyVista también
descubre los archivos dentro de estas subcarpetas. Las salidas principales de
E11/E12 se conservan.

Si ninguna opción satisface ambos límites del ensayo, no declarar ganadora por
cumplimiento a la de 50 mm. Revisar además cobertura superior, retiros y otros
parámetros de control. Los retiros tempranos pueden dominar el diferencial a
tiempos posteriores. Si ambas satisfacen los criterios y la sensibilidad de malla
es aceptable, comparar costos instalados antes de adoptar la alternativa final.
