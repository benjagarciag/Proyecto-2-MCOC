# E07 — Etapa 2: primer voxelizador 3D

Desarrollo únicamente en `E07_pruebas`, sobre main e281ec4 y la extracción de
Etapa 1. No se modificaron IFC, propiedades, BIM, lector `bim.py`, solvers,
dependencias ni las 353 pruebas previas. No hay commits ni publicaciones.
El remoto consultado continúa en e281ec4.

## Datos y uso

`mcplan.voxel` recibe `FundacionIFC`, la estructura de Etapa 1. No abre el IFC:
el ejecutor llama una sola vez a `extraer_fundacion_ifc` y entrega ese resultado.

```python
from mcplan.bim import extraer_fundacion_ifc
from mcplan.voxel import voxelizar_fundacion

fundacion = extraer_fundacion_ifc('desarrollo/fundacion/fundacion.ifc')
r = voxelizar_fundacion(fundacion, pasos_m=(0.5, 0.5, 0.5))
x, y, z = r.grilla.centros_xyz_m
ocupada = r.ocupacion  # bool [z,y,x], geometría; no actividad temporal
```

`GrillaCartesiana` conserva origen XYZ en metros, pasos dx/dy/dz, forma ZYX,
centros por eje, dimensiones, límite superior y volumen de celda. `Voxelizacion`
contiene máscara booleana, centros cercanos a alguna malla, SHA256 del IFC y
referencia de volumen. Estas formas/coordenadas permiten añadir arrays de IDs
en etapas futuras, pero aquí no existe asignación de vertida/material por voxel.

## Construcción de grilla

`crear_grilla` usa por defecto el mínimo real de la geometría como esquina
de origen. Para cada eje:

    N = ceil((bbox_max-origen)/paso)
    centro[i] = origen + (i+0.5)*paso
    extremo_superior = origen + N*paso

Todas las celdas mantienen el paso pedido, incluida la última. La grilla puede
extenderse por encima del máximo del IFC; no se recorta la geometría ni se
reajusta dx para que entre en una cantidad nominal de metros.

Se admite un origen explícito siempre que permita cubrir todo el bbox. No se
recentra el modelo. Hay un límite configurable de 2 millones de celdas para
evitar asignaciones accidentales excesivas de memoria; no es un límite físico.

## Cómo se decide la ocupación

1. El bbox de cada cuerpo filtra puntos lejanos, sin decidir su pertenencia.
2. Se mide la distancia al triángulo más próximo: proyección dentro de cara o
   distancia a aristas/vértices.
3. Si la distancia es <= tolerancia, se devuelve FRONTERA=0.
4. Para los otros puntos se suman ángulos sólidos orientados de los triángulos.
   Una malla cerrada rodea al punto interior con aproximadamente ±4π; al exterior
   con aproximadamente cero. Se clasifica DENTRO=1 si |suma|>2π; FUERA=-1 si no.

Para a,b,c vectores desde el punto hacia un triángulo, se calcula:

    angulo = 2 atan2(a dot (b cross c),
                   |a||b||c| + (a dot b)|c| + (b dot c)|a| + (c dot a)|b|)

El valor absoluto permite invertir globalmente la orientación de la malla sin
cambiar la ocupación. No se lanzan rayos que puedan contar dos veces una arista.
Se exige la calidad topológica de `analizar_malla` ya implementada en Etapa 1.
La decisión usa superficies trianguladas: funciona también con inclinaciones
y geometría cóncava; no utiliza una caja o envolvente convexa como sustituto.

Un voxel está ocupado si su centro está dentro o en frontera de CUALQUIERA de
las cinco piezas. Se combina con OR: no hay preferencia de propietario ni
dependencia del orden de las vertidas. No se cuentan dos veces los solapes.
No se devuelve qué pieza reclamó el centro; eso corresponde a Etapa 3.

El trabajo se divide por planos z y lotes de puntos, limitando los arrays de
pares punto×triángulo. No se crea una matriz global de todos esos pares.

## Tolerancia y casos ambiguos

Default: **1e-7 m = 0.1 micrómetros**, configurable. Es mayor que las pequeñas
discrepancias de juntas observadas en el IFC (~3e-8 a 6e-8 m), pero muchísimo
menor que el voxel de 0.5 m. No es un ajuste para mejorar el volumen estimado.
El voxelizador exige tolerancia <0.001 del menor paso para evitar usarla como
una expansión macroscópica del sólido.

Se incluyen deliberadamente los centros dentro de esa banda de distancia,
sean interiores o exteriores estrictos. Se guardan en `centros_sobre_malla` para
que la decisión sea visible; la máscara puede incluir juntas internas y NO es
un detector de superficies exteriores. En la resolución predeterminada no hay
centros en esa banda; los tests sí ejercitan esos casos.

En juntas compartidas basta que cualquiera de los sólidos incluya el punto.
Separaciones menores que la banda de tolerancia pueden quedar cubiertas; huecos
físicos mayores no deben cerrarse aumentando tolerancia. No se usa azar ni
se selecciona la primera vertida encontrada. La atribución única de un ID en
juntas requiere una política posterior, que no se implementó aquí.

## Resultado preliminar, una sola resolución real

Entrada: `casos/e07/voxelizacion.json`. Tamaño de voxel: 0.5×0.5×0.5 m.

| Magnitud | Valor |
|---|---|
| Origen XYZ [m] | (-9.00000083, -9.00000083, 0) aproximadamente |
| Cantidad XYZ | 37×37×9 |
| Forma del array ZYX | (9,37,37) |
| Dimensiones físicas de grilla [m] | 18.5×18.5×4.5 |
| Celdas totales | 12321 |
| Celdas ocupadas | 5140 |
| Celdas vacías | 7181 |
| Volumen por celda [m³] | 0.125 |
| Volumen ocupado [m³] | 642.5 |
| Referencia suma mallas IFC [m³] | 636.775192693 |
| Diferencia firmada [m³] | +5.724807307 |
| Error relativo absoluto | 0.899031 % |

El ancho IFC es aproximadamente 18.00000166 m. Al conservar coordenadas y paso
exactos, ceil da 37 celdas, no 36. La última fila en X/Y queda fuera y vacía.
Esta extensión de la grilla no agrega volumen ocupado. El voxel superior puede
sobresalir de z=4.30 hasta z=4.50 si su centro está dentro: ese sí es el efecto
staircase de la clasificación por centros.

La referencia es una suma de volúmenes por sólido y no una unión booleana
validada. Se usa como comprobación preliminar del IFC actual; los tests de
solapamiento muestran explícitamente que una unión no coincide con la suma si
los cuerpos se superponen. No se realizó aquí el estudio formal de tres
resoluciones ni volúmenes por vertida, reservados a Etapa 3.

## Pruebas y figura

**389 aprobadas = 353 anteriores + 36 nuevas.** Se comprueban puntos interiores,
exteriores y en caras/aristas/vértices; distancia euclídea de tolerancia; caja,
tetraedro inclinado y prisma cóncavo; grillas anisótropas; centros y unidades;
traslación del modelo; orientación invertida; independencia de lotes; juntas
con variación de ±5e-8 m y orden invertido; unión sin doble conteo; refinamiento
en sólidos sintéticos; fundación real; preservación del IFC y validaciones.

El refinamiento sintético no reemplaza el estudio de volumen del IFC. No se
exige que el error de un staircase arbitrario baje monótonamente en todas las
mallas. No se simularon temperaturas ni se tocaron las pruebas térmicas.

`casos/e07/voxelizar_ifc.py` genera una figura fija:
`resultados/e07/voxelizacion/geometria_y_voxeles.png`. Azul: aristas IFC;
naranja: voxeles ocupados; corte XZ con ocupadas/vacías. El corte usa el centro
Y más próximo a cero, Y≈0.249999 m; no se presenta como un corte exactamente Y=0.
La función estándar de dibujo de voxeles muestra sus caras visibles; eso no
crea una clasificación de caras/interfaz utilizable por el solver.

## Límites y punto de detención

El método de centros pierde detalles menores que el paso y produce escalones.
No calcula fracciones de volumen ni garantiza error nulo en superficies oblicuas.
Depende de mallas cerradas y orientadas; la Etapa 1 no certifica ausencia de
autointersecciones. La unión puede ocultar cuerpos superpuestos: los conflictos
de pertenencia deben revisarse antes de asignar IDs. La máscara NO implica
material activo ni una condición de borde térmica.

Para Etapa 3 se reutilizarán esta grilla y el clasificador por malla, añadiendo
atribución de vertida y comparación de volúmenes por ID/resolución. No se
implementaron IDs por voxel, interfaces, activación, hidratación o cambios en
el BIM. Detener aquí para revisión.
