# E07 — Etapa 4: superficies e interfaces geométricas

Trabajo local en `E07_pruebas`, basado en main
`e281ec4bc6d96f8e3481d08112cc94dcfff5f51c`. Sin integración de compañeros,
commits, publicación, cambios del IFC o nuevos cálculos térmicos.
Las salidas y el análisis de errores de las etapas anteriores se conservan.

## Módulo reutilizable

`desarrollo/mcplan/superficies_voxel.py` recibe `AsignacionVertidas` de la
Etapa 3. `clasificar_caras(asignacion)` devuelve `SuperficiesVoxel`, con
tres colecciones `CarasVoxel`: `exteriores`, `internas`, `interfaces`.
No utiliza una caja como sustituto de la ocupación real.

Para cada voxel ocupado examina los vecinos ±X, ±Y, ±Z:

| Vecino | Clase |
| --- | --- |
| Vacío (ID 0) o fuera de la grilla | Exterior geométrica |
| Ocupado, mismo ID | Interna de una vertida |
| Ocupado, distinto ID | Interfaz entre vertidas |

Se almacenan índices de celda A y B en orden ZYX, sus IDs, normal XYZ,
área en m² y un indicador de vecino fuera de la grilla. El ID de B en las
exteriores es 0. Sus índices pueden ser negativos o superar la grilla:
**no deben usarse como índices NumPy sin verificar primero el indicador**.
Una cavidad vacía interior también tiene caras exteriores geométricas;
no se determina si está conectada con el aire exterior.

Las normales exteriores apuntan del hormigón al vacío. Internas e interfaces
se guardan solo en sentidos positivos X/Y/Z, desde la celda A a la B. Esto
evita almacenar dos veces A–B y B–A. La orientación NO depende del orden
numérico de los IDs. `contactos_por_par` agrupa por pares de IDs ordenados,
sin cambiar la orientación de las caras.

Áreas de caras perpendiculares a cada eje:

```
A_x = Δy Δz     A_y = Δx Δz     A_z = Δx Δy
```

También se admite grilla anisótropa. `centros_m(grilla)` y
`vertices_m(grilla)` devuelven centros y cuadriláteros en metros y en las
coordenadas del proyecto. El producto vectorial de sus aristas apunta
según la normal. Los arrays de caras se devuelven de solo lectura; la
asignación, máscara e IDs recibidos no se modifican.

Se verifica el balance de incidencias:

```
6 N_ocupados = N_exteriores + 2 (N_internas + N_interfaces)
```

Cada contacto compartido consume una cara de cada celda, aunque se almacene
una sola vez. En una grilla anisótropa el balance de áreas correspondiente
es `2 N_ocupados (A_x+A_y+A_z) = A_ext+2(A_int+A_interfaz)`.

## Resultados de la fundación

| h [m] | Voxeles ocupados | Caras exteriores | Área exterior [m²] | Caras internas | Área interna [m²] | Caras interfaz | Área interfaz [m²] |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 600 | 728 | 728 | 1100 | 1100 | 336 | 336 |
| 0,5 | 5140 | 3040 | 760 | 11200 | 2800 | 2700 | 675 |
| 0,25 | 40536 | 11976 | 748,5 | 104732 | 6545,75 | 10888 | 680,5 |

El área interna es la suma de particiones entre celdas, no una superficie
exterior física. Crece al refinar por existir más particiones.

### Contactos por par

La configuración declara explícitamente los contactos de referencia
01–02, 02–03, 03–04, 04–05 según la disposición apilada de las cinco piezas
IFC examinadas en Etapa 1. `diagnosticar_contactos` contrasta con esta lista;
**no calcula intersecciones CAD exactas ni supone que IDs consecutivos
siempre deban tocarse en otro modelo**.

| Par | Área h=1 m [m²] | Caras h=0,5 m | Área h=0,5 m [m²] | Área h=0,25 m [m²] |
| --- | ---: | ---: | ---: | ---: |
| 01–02 | 0 (perdido) | 1076 | 269 | 266,25 |
| 02–03 | 0 (perdido) | 976 | 244 | 266,25 |
| 03–04 | 88 | 492 | 123 | 109,5 |
| 04–05 | 32 | 156 | 39 | 38,5 |
| 01–03 | 216 (artificial) | 0 | 0 | 0 |
| **Total** | **336** | **2700** | **675** | **680,5** |

### Exterior por orientación, h=0,5 m

| Normal XYZ | Caras | Área [m²] |
| --- | ---: | ---: |
| (−1,0,0) | 222 | 55,5 |
| (+1,0,0) | 222 | 55,5 |
| (0,−1,0) | 222 | 55,5 |
| (0,+1,0) | 222 | 55,5 |
| (0,0,−1) | 1076 | 269 |
| (0,0,+1) | 1076 | 269 |
| **Total** | **3040** | **760** |

## Resolución y límites

- h=1 m no representa la Vertida 02, de z=0,55 a 1,10 m: ningún centro
  cae en esa capa. Desaparecen 01–02 y 02–03, y la grilla crea 01–03.
  Ese contacto es un artefacto de discretización, no una modificación del IFC.
- h=0,5 y 0,25 m recuperan los cuatro pares esperados. Esto verifica su
  presencia en esas grillas; no demuestra precisión suficiente del área
  de cada contacto, de su cota ni de la forma de cada vertida.
- Se mantienen los errores de Etapa 3: a h=0,5 m la Vertida 04 tiene
  error de volumen +37,757%; a h=0,25 m la Vertida 03 tiene +16,029%.
  Errores globales de 0,899% y 0,534% ocultan compensaciones locales.
- Son áreas de caras cartesianas. Las superficies inclinadas o curvas
  quedan escalonadas; la suma de áreas ortogonales puede tener sesgo
  respecto del área euclídea de la malla IFC incluso al refinar. La serie
  exterior 728 → 760 → 748,5 m² no certifica convergencia al área CAD.
- No se ha corregido ni desplazado la grilla, asignado voxeles faltantes,
  modificado el IFC o elegido una resolución definitiva.
- Solo contactos por cara: aristas y vértices comunes no aportan área
  de intercambio entre celdas en este esquema de seis vecinos.

## Geometría completa y exposición durante la construcción

La clasificación describe la unión de **todas** las vertidas previstas.
No depende del tiempo. Una interfaz 01–02 pertenece al interior del modelo
completo; antes de colocar 02, la cara de 01 podría estar expuesta.
Eso se determinará con la máscara de actividad en una etapa posterior.

Exterior geométrica tampoco significa automáticamente convección con aire:
la base puede estar contra suelo y otras caras pueden tener moldaje o
aislación. Aquí no se asignan condiciones de borde ni conductancias.

## Ejecución y resultados visuales

Desde la raíz de esta copia, usando el Python ya instalado:

```powershell
# Terminal con el entorno del proyecto activado
python -B casos/e07/clasificar_superficies.py
```

`--solo-datos` omite las figuras. `--config ruta.json` permite usar otra
configuración. No se requieren dependencias nuevas.

`casos/e07/superficies.json` conserva las tres resoluciones, origen IFC,
tolerancia de 1e-7 m y contactos de referencia explícitos.

Salidas fijas en `resultados/e07/superficies/`:

- `superficies_exteriores_y_corte.png`: exterior 3D naranja y corte XZ,
  internas grises e interfaces magenta. El corte omite caras perpendiculares
  a Y; no altera sus conteos globales.
- `interfaces_y_caras_internas.png`: contactos 3D coloreados por par y una
  muestra de 291 caras internas de una franja, de las 11200 clasificadas.
  La muestra omite caras normales a Y para permitir observar el interior.
- `areas_superficies.json`: conteos, áreas por categoría/orientación/par,
  diagnósticos para las tres resoluciones y SHA256 del IFC leído.

Los gráficos mantienen coordenadas originales; colores indican clases
geométricas o pares de IDs, nunca temperatura ni actividad.

## Verificación y alcance

**434 pruebas aprobadas: 410 anteriores y 24 nuevas.** Ejecución verificada:

```powershell
python -B -m pytest -q -p no:cacheprovider --basetemp=.venv/cache/pytest_etapa4_02
```

`desarrollo/tests/test_superficies_voxel.py` cubre celda aislada, pares iguales
y distintos en tres ejes, caja anisótropa analítica, escalón, cavidad, ausencia
de contacto periódico, coordenadas/orientaciones, duplicaciones, tres grillas
reales, pérdida de capa, preservación de datos y entradas incompatibles.
Las pruebas no generan gráficos.

SHA256 de `fundacion.ifc` conservado:
`eba180b5cab9fe46a652c854fd8983f7b5d1175567762cf947b31b4bd1bb34e0`.

Para Etapa 5 se necesita revisar y autorizar la activación por `Inicio_h`,
definir su origen temporal y derivar caras expuestas de celdas activas frente
a vacías/inactivas. Habrá que verificar el cambio de exposición a contacto
cuando aparece la siguiente vertida y decidir cómo gestionar las limitaciones
de resolución antes de una simulación de la fundación. Nada de ello se
implementa aquí; tampoco hidratación ni nuevas simulaciones térmicas.
