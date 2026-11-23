# E07 — Etapa 1: extracción reutilizable de la fundación IFC

Base comprobada de GitHub: main `e281ec4bc6d96f8e3481d08112cc94dcfff5f51c`.
Desarrollo solo en `E07_pruebas`, sin commits ni publicación. No se instalaron
dependencias ni se modificaron los solvers, el proyecto original, la copia E04,
la geometría IFC, sus propiedades o el archivo Blender.

## Implementación y estructuras

`desarrollo/mcplan/bim.py` contiene `extraer_fundacion_ifc(ruta)`. Traslada y
amplía la lógica de lectura del verificador existente: abrir IFC, buscar cinco
IfcFooting y nombres Vertida_01..05, leer psets y triangular con IfcOpenShell.
`desarrollo/fundacion/verificar_ifc.py` conserva su función `verificar` y comando
de consola, delegando en ese módulo. No hay dos extractores geométricos.

La extracción devuelve `FundacionIFC`, que contiene:

- Ruta, SHA256, schema, unidad IFC y factor de conversión de longitud a metros.
- Sistema de coordenadas explícito, envolvente global y advertencias.
- Tupla de cinco `VertidaIFC`, ordenadas por ID.

Cada vertida contiene:

- ID entero 1–5, nombre, GUID y clase IFC.
- Propiedades constructivas, inicio en horas/segundos y temperatura de colocación.
- Etiqueta `TipoHormigon` y lista de materiales IFC asociados (si existen).
- Vértices XYZ en metros, triángulos como índices enteros y bbox min/max.
- Dimensiones, volumen, área y comprobaciones de calidad de la malla.

Los arrays geométricos se copian y devuelven como solo lectura para evitar
modificaciones accidentales. No se exportan formatos nuevos ni se cambia el IFC.

## Unidades y coordenadas

El IFC actual es IFC4, declara METRE y tiene escala de longitud 1.0.
`use-world-coords=True` aplica los placements anidados. IfcOpenShell entrega
esta triangulación en SI; NO se multiplica otra vez por la escala de unidad.
Se comprueba con una variante temporal en milímetros y con un placement trasladado.

El sistema es XYZ del proyecto IFC, sin recentrar. No se declara un CRS
cartográfico ni se aplica IfcMapConversion. El modelo actual no tiene esa
conversión; si una futura entrada la incluye, se informa explícitamente.
Envolvente aproximada: (-9,-9,0) a (9,9,4.30) m. La coordenada exacta tiene
pequeñas desviaciones por la precisión de los datos guardados desde Blender.

## Volumen y geometría

`analizar_malla` calcula volumen por suma de tetraedros firmados:

    V_firmado = sum[(v0-c) dot ((v1-c) cross (v2-c))]/6
    V = abs(V_firmado)

Se usa un origen c próximo a la malla para reducir cancelación con coordenadas
grandes. El volumen es de la malla IFC, no de su bounding box, no de un cilindro
ideal reconstruido y NO de voxeles. El pedestal está facetado en el propio IFC.

| Vertida | Z aproximada [m] | Dimensiones aproximadas [m] | V obtenido [m³] | Referencia redondeada [m³] |
|---|---|---|---|---|
| 01 | 0–0.55 | 18×18×0.55 | 147.625737812 | 147.626 |
| 02 | 0.55–1.10 | 18×18×0.55 | 147.625737812 | 147.626 |
| 03 | 1.10–2.20 | 18×18×1.10 | 214.224337891 | 214.224 |
| 04 | 2.20–3.30 | 12.5×12.5×1.10 | 88.924678992 | 88.925 |
| 05 | 3.30–4.30 | 7×7×1.00 | 38.374700187 | 38.375 |
| Suma | | | 636.775192693 | 636.775 |

Las referencias están redondeadas a 0.001 m³: se admite **0.00050001 m³** por
valor (medio último decimal más margen numérico de 1e-8 m³), sin tolerancia
relativa adicional. El total se compara con su propia referencia, no con la
suma de los cinco valores ya redondeados, que da 636.776 m³.

Las dimensiones se comparan con tolerancia absoluta **3e-6 m**, sin relativa:
el ancho nominal 18 m llega aproximadamente a 18.00000166 m por la precisión
float32 de coordenadas/rotaciones de Blender. No se redondean los datos de
trabajo para esconder esas diferencias. Las tolerancias de clasificación
geométrica de futuros voxeles se decidirán en la etapa siguiente.

La suma `volumen_total_mallas_m3` NO es una unión booleana: no certifica ausencia
de solapes entre vertidas. La altura 4.30 m sigue la simplificación docente:
3.30 m del cuerpo central más pedestal de 1 m, según la guía de Bonsai.

## Calidad comprobada y límites

Se rechazan coordenadas no finitas, índices inválidos, vértices sin usar,
triángulos repetidos/degenerados, aristas abiertas o con más de dos caras,
orientaciones inconsistentes, enlaces de vértices no manifold y componentes
separadas. Para esta etapa se exige un sólido conexo cerrado por vertida.
Las cinco mallas reales pasan estas comprobaciones; tienen 28,28,28,28 y 188
triángulos respectivamente.

Estas comprobaciones dejan datos adecuados para comenzar la clasificación de
puntos, pero NO constituyen un detector completo de autointersecciones, una
validación de contactos entre sólidos o conformidad con todas las cotas docentes.
No se implementaron superficies de voxeles ni detección de interfaces por grilla.

## Propiedades y advertencias del modelo

Se conservan Inicio_h=0,6,12,18,24; temperatura 19 °C en la primera vertida y
18 °C en las otras. Leer los horarios no significa activar materiales.
Los GUID se preservan y son únicos. RetiroMoldaje_h=72 se informa literalmente;
su referencia temporal no se interpreta todavía.

No hay asociaciones IfcMaterial explícitas en las cinco piezas. La lista se
devuelve vacía y se advierte; M1 es la etiqueta del pset, no una asociación
material ni valores k/rho/cp. Un test con una asociación material añadida SOLO
a una copia temporal comprueba que el lector sí la recupera cuando existe.
Moldaje y Aislacion siguen como TBD y tampoco se completan automáticamente.

## Pruebas y preservación del IFC

**353 pruebas aprobadas: 320 existentes + 33 nuevas.** Se verifican:

- Cinco objetos, nombres/IDs coherentes, GUID únicos y propiedades correctas.
- Dimensiones y volúmenes de referencia, triangulación cerrada y orientada.
- Bytes y SHA256 antes/después de lecturas; arrays independientes y de solo lectura.
- Compatibilidad del comando de verificación anterior.
- Rechazo de 4/6 vertidas, IDs/GUID duplicados, propiedades ausentes y horarios inválidos.
- Materiales asociados presentes/ausentes, escala milimétrica y placements globales.
- Volumen analítico de tetraedro, traslación grande y orientación global invertida.
- Rechazo de mallas abiertas, no manifold, desconectadas, degeneradas o inválidas.

Las variantes de prueba se escriben en `.venv/cache/pytest_*` de ESTA copia.
El IFC de trabajo conserva SHA256:

`eba180b5cab9fe46a652c854fd8983f7b5d1175567762cf947b31b4bd1bb34e0`

## Visualización y próximos pasos

`casos/e07/extraer_ifc.py` consume los datos devueltos y guarda una sola figura
en `resultados/e07/extraccion_ifc/geometria_ifc.png`. Muestra aristas del modelo
ensamblado y una vista separada (3 m de desplazamiento gráfico por nivel), con
un color por vertida. La separación se aplica a una copia solo para dibujar.
No hay interpretación térmica de los colores, grilla o simulación.

Archivos nuevos: módulo `bim.py`, tests `test_bim.py`, ejecutor y README del caso,
este documento y la figura. Archivos adaptados: verificador anterior e índice
README raíz de la copia E07. No se cambiaron dependencias ni el modelo IFC.

Para la Etapa 2 ya se dispone de triángulos, envolventes, unidades y volúmenes
de referencia. Falta diseñar la grilla y clasificación de centros con política
de tolerancias; esa implementación requiere autorización. No se desarrollaron
voxelización, asignación de voxeles, activación ni hidratación. Detener aquí.
