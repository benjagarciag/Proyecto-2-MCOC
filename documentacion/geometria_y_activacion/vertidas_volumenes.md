# E07 — Etapa 3: identificación de vertidas y análisis de volumen

Solo copia `E07_pruebas`, sobre main e281ec4 y las etapas 1/2. El remoto sigue
en e281ec4. No hubo commits, merges, PR, publicaciones o instalaciones; no se
modificaron IFC, Blender, propiedades, solvers, dependencias o proyecto original.

## Implementación reutilizable

`mcplan.vertidas_voxel` recibe `FundacionIFC` de `bim.py` y `Voxelizacion` de
`voxel.py`. No abre el IFC ni inventa otra geometría. La Etapa 2 comparte ahora
el generador `iterar_clasificacion_malla`, que conserva exactamente su filtro
bbox, clasificación triangular, lotes y tolerancia.

```python
from mcplan.bim import extraer_fundacion_ifc
from mcplan.voxel import voxelizar_fundacion
from mcplan.vertidas_voxel import asignar_vertidas, comparar_volumenes

fundacion = extraer_fundacion_ifc('desarrollo/fundacion/fundacion.ifc')
voxelizacion = voxelizar_fundacion(fundacion, (.5,.5,.5))
asignacion = asignar_vertidas(fundacion, voxelizacion)
ids = asignacion.vertida_id       # int8 [z,y,x]: 0 vacío, 1..5 vertidas
filas = comparar_volumenes(fundacion, asignacion)
```

La ocupación recibida se compara con la unión de las reclamaciones. Si no
coinciden, se rechaza la entrada; no se agregan o quitan celdas para ocultarlo.
`AsignacionVertidas` conserva ese mismo objeto de voxelización, el array de
IDs de solo lectura y un `InformeAsignacion` de conflictos. No contiene un
`material_id` ni actividad temporal: las cinco vertidas conservan M1 en el IFC,
pero cinco IDs de vertida NO significan cinco materiales.

## Reclamaciones y criterio de fronteras

Se diagnostican todas las clases de centro por sólido: fuera=-1, frontera=0,
interior=1. La tolerancia sigue en 1e-7 m. Antes de resolver se cuentan:

1. Centros con más de una reclamación.
2. Centros claramente interiores a varios sólidos: **error geométrico**. Se
   lanza `ConflictoGeometrico` con el informe, sin devolver una asignación válida.
3. Interior único más reclamaciones de frontera: se elige el interior inequívoco.
4. Solo fronteras compartidas: se aplica la convención geométrica siguiente.

Las superficies cerradas de dos cuerpos pueden reclamar el mismo punto de
contacto. La pertenencia única de ese punto no la define la geometría cerrada:
es necesaria una convención de etiquetado, que NO representa una decisión térmica.

Se ensaya una sonda a 4*tolerancia del centro en las 26 direcciones XYZ de la
vecindad {-1,0,1}, excluyendo cero. El orden prioriza Z creciente, luego Y y
luego X, en orden lexicográfico descendente. En una junta horizontal interior
esto atribuye el centro al cuerpo situado hacia +Z, equivalente al convenio
semiabierto de capas. Las direcciones sucesivas permiten hallar un interior
sin salir por una arista exterior. No se usa el primer objeto ni el menor/mayor ID.

La primera sonda que encuentra un único interior de los reclamantes determina
la etiqueta. Si entra en varios, o ninguna permite distinguir un propietario,
se detiene con informe: no hay elección arbitraria de ID. Se registra índice,
coordenadas originales, IDs/clases reclamantes, decisión y dirección. El centro
y la ocupación NO se mueven. La sonda es microscópica y no calcula fracciones de
volumen. No es una demostración de pertenencia mayoritaria del volumen del voxel.

El informe mantiene conteos completos y hasta 100 ejemplos de decisiones; si
ocurre un fallo tardío se conserva una muestra de ese fallo. Un solape puede
existir sin que los centros muestreados lo detecten: esto NO reemplaza una
intersección booleana entre sólidos ni una validación CAD completa.

En el IFC real y las tres resoluciones estudiadas hubo **cero reclamaciones
múltiples de centros**, por lo que no fue necesario desempatar ninguno. Los
tests sintéticos ejercitan las fronteras, pequeñas discrepancias y solapes.

## Cálculo y conservación de volúmenes

    V_voxel = dx*dy*dz
    V_h,vertida = N_vertida * V_voxel
    diferencia_firmada = V_h - V_IFC
    diferencia_absoluta = abs(V_h-V_IFC)
    error_relativo_pct = 100*abs(V_h-V_IFC)/V_IFC

Se usan las referencias completas de `bim.py`, sin redondear. Se verifica que
`ids>0` sea exactamente la ocupación anterior, que cada ocupado tenga un ID y
que la suma por ID sea el número global. Los volúmenes por ID suman el global.

## Estudio de tres resoluciones

Origen fijo: mínimo exacto IFC ≈(-9.00000083,-9.00000083,0) m. Celdas cúbicas.
Las cantidades 19/37/73 en X/Y conservan la pequeña extensión real mayor que
18 m, como en Etapa 2. La referencia global es 636.775192693 m³.

| h [m] | Grilla XYZ | Celdas totales | Ocupadas | V_h [m³] | ΔV firmado [m³] | Error absoluto relativo [%] | Tiempo geometría [s] |
|---|---|---:|---:|---:|---:|---:|---:|
| 1.00 | 19×19×5 | 1805 | 600 | 600.000 | -36.775193 | 5.775224 | 0.0250 |
| 0.50 | 37×37×9 | 12321 | 5140 | 642.500 | +5.724807 | 0.899031 | 0.1651 |
| 0.25 | 73×73×18 | 95922 | 40536 | 633.375 | -3.400193 | 0.533971 | 1.2674 |

Tiempos de una ejecución local, medidos con perf_counter: voxelización,
atribución y tablas, sin lectura inicial IFC, importaciones ni gráficos.
Varían según el equipo/carga; no son garantías. No hizo falta modificar el
clasificador: se reutilizó el recorrido por planos y lotes y no se instaló nada.
La ocupación se calcula primero para verificar explícitamente que asignar IDs
no la altera. En las tres mallas, sum(N_por_ID)=N_ocupadas exactamente.

### Volúmenes por vertida

| h [m] | ID | N | V_h [m³] | V_IFC [m³] | Diferencia absoluta [m³] | Error [%] |
|---|---:|---:|---:|---:|---:|---:|
| 1.00 | 1 | 264 | 264.000000 | 147.625738 | 116.374262 | 78.830605 |
| 1.00 | 2 | 0 | 0.000000 | 147.625738 | 147.625738 | 100.000000 |
| 1.00 | 3 | 216 | 216.000000 | 214.224338 | 1.775662 | 0.828880 |
| 1.00 | 4 | 88 | 88.000000 | 88.924679 | 0.924679 | 1.039845 |
| 1.00 | 5 | 32 | 32.000000 | 38.374700 | 6.374700 | 16.611726 |
| 0.50 | 1 | 1076 | 134.500000 | 147.625738 | 13.125738 | 8.891226 |
| 0.50 | 2 | 1076 | 134.500000 | 147.625738 | 13.125738 | 8.891226 |
| 0.50 | 3 | 1696 | 212.000000 | 214.224338 | 2.224338 | 1.038322 |
| 0.50 | 4 | 980 | 122.500000 | 88.924679 | 33.575321 | 37.757034 |
| 0.50 | 5 | 312 | 39.000000 | 38.374700 | 0.625300 | 1.629458 |
| 0.25 | 1 | 8520 | 133.125000 | 147.625738 | 14.500738 | 9.822635 |
| 0.25 | 2 | 8520 | 133.125000 | 147.625738 | 14.500738 | 9.822635 |
| 0.25 | 3 | 15908 | 248.562500 | 214.224338 | 34.338162 | 16.029067 |
| 0.25 | 4 | 5124 | 80.062500 | 88.924679 | 8.862179 | 9.965939 |
| 0.25 | 5 | 2464 | 38.500000 | 38.374700 | 0.125300 | 0.326517 |

Los errores de las tablas se calcularon antes de redondear para mostrar.

## Hallazgos geométricos y límites

- h=1 m no tiene centros entre z=0.55 y z=1.10: la Vertida 02 recibe cero
  voxeles. No es una pérdida durante la atribución: la ocupación de Etapa 2
  no resuelve esa capa. La malla es inadecuada para representar las cinco capas.
- El error global disminuye en estas tres mallas, pero no debe generalizarse
  a todas las resoluciones. Las diferencias firmadas cambian de signo.
- Por vertida no hay disminución monótona: V01/V02 empeoran de 8.891 a 9.823 %
  entre 0.5 y 0.25 m; V03 de 1.038 a 16.029 %. V04 empeora al pasar de 1 a
  0.5 m y luego mejora. La alineación de centros con juntas/pendientes explica
  que reducir h no reparta el error uniformemente.
- El error global pequeño oculta cancelaciones. Con h=0.25 m las dos primeras
  vertidas suman aproximadamente -29.0015 m³ de diferencia mientras V03 aporta
  +34.3382 m³. No se declara convergencia suficiente de cada capa ni se recomienda
  usarla como discretización térmica final solo por el error total 0.534 %.
- La suma IFC es una referencia por sólidos, no una unión booleana comprobada.
  La detección de conflictos por centros no certifica ausencia de solapes de
  las superficies entre muestras. Las tolerancias no corrigen la geometría.

## Pruebas

**410 aprobadas = 389 anteriores + 21 nuevas.** Incluyen IDs y volúmenes de
cajas analíticas, voxeles anisótropos, juntas normales a X/Y/Z, junta inclinada,
aristas exteriores, tolerancia ±5e-8 m, orden e IDs intercambiados, prioridad de
interior único, solapes rechazados, conservación de ocupación, mallas reales de
tres tamaños, balances, capa no resuelta y preservación del IFC.

Los módulos térmicos no se modificaron. Las pruebas anteriores conservan sus
resultados después de compartir el recorrido geométrico de Etapa 2.

## Ejecución, gráficos y archivos

`casos/e07/identificar_vertidas.py` lee el IFC una vez y ejecuta el estudio.
Entradas en `vertidas_volumenes.json`; `--solo-datos` evita dibujar. Se imprime
la tabla completa y el diagnóstico antes de generar las figuras.

Tres PNG fijos en `resultados/e07/vertidas_volumenes/`:

1. `vertidas_y_corte.png`: h=0.5 m, cinco colores, vista separada y corte XZ.
2. `comparacion_resoluciones.png`: las tres mallas y sus cortes, con resolución
   y coordenada Y real de cada corte. No son cortes exactamente en Y=0.
3. `errores_volumen.png`: error global y por vertida frente al tamaño de voxel.

Las vistas separadas desplazan las piezas 3 m por nivel SOLO para dibujar;
los arrays originales y el IFC permanecen iguales. El renderizado utiliza
caras visibles para dibujar, pero no devuelve una clasificación de superficies
ni interfaces térmicas para el solver.

Nuevos: `vertidas_voxel.py`, `test_vertidas_voxel.py`, ejecutor/JSON, este documento
y tres PNG. Adaptados: recorrido compartido en `voxel.py`, README raíz/caso E07.

## Punto de detención

La estructura conserva grilla, ocupación, IDs, referencia IFC e informe. Permite
añadir otros arrays/propiedades en futuras etapas, pero aún no hay material,
estado activo, edad, temperaturas o interfaces por voxel. Leer `Inicio_h` desde
Etapa 1 no activa vertidas. `vertida_id` y `material_id` permanecen separados.

Para Etapa 4 falta clasificar caras exteriores, interiores y contactos según
ocupación/IDs, con sus áreas y pruebas. No se implementó esa funcionalidad,
activación temporal ni hidratación. Detener aquí para revisión.
