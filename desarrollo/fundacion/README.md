# Fundación IFC: propiedades de las vertidas

Esta carpeta contiene el modelo y el script del punto 23 de
[la guía de Bonsai](../../Enunciados%20e%20Instrucciones/Guias/GUIA_BONSAI_FUNDACION.md).

| Archivo | Uso |
| --- | --- |
| `fundacion.ifc` | Único modelo BIM de trabajo: geometría, identidad y propiedades de las cinco vertidas. |
| `fundacion.blend` | Única sesión Blender: fundación, materiales de hormigón, terreno con pasto, iluminación y cámara. Vinculada a `fundacion.ifc`. |
| `agregar_propiedades.py` | Agrega las propiedades del ejemplo de §24 usando IfcOpenShell. |
| `verificar_ifc.py` | Punto 25: lee el IFC e imprime nombres, clases, GUID, propiedades y dimensiones. |

Desde PowerShell, en la raíz del proyecto:

```powershell
.\.venv\Scripts\python.exe desarrollo/fundacion/agregar_propiedades.py
```

El script abre el IFC, busca exactamente `Vertida_01` a `Vertida_05`, crea el
Property Set `UANDES_HormigonMasivo` en cada una y actualiza el mismo `fundacion.ifc`.
Conserva la geometría, los nombres, los GUID y los valores de propiedades ya existentes. Si faltan
vertidas o sus nombres están duplicados, se detiene antes de escribir.

Los valores proceden del ejemplo docente:

| Propiedad | Valor inicial |
| --- | --- |
| `VertidaID` | 1, 2, 3, 4 y 5 |
| `Inicio_h` | 0, 6, 12, 18 y 24 h desde la primera vertida |
| `TemperaturaColocacion_C` | 18 °C |
| `TipoHormigon` | M1, identificador de ejemplo |
| `Moldaje` y `Aislacion` | TBD: pendiente de definir |
| `RetiroMoldaje_h` | 72 h, según el ejemplo de la guía |

Estos valores permiten practicar el flujo BIM; aún no constituyen un plan de
vertidas validado ni definen las propiedades térmicas del hormigón.
`Inicio_h` representa el inicio planificado relativo, en horas; no es una fecha.
La referencia temporal del retiro de moldaje deberá aclararse al definir el plan.

Para ver las propiedades en Blender con Bonsai:

1. Guardar primero cualquier cambio pendiente del modelo abierto.
2. Elegir **File → Open IFC Project** y abrir `fundacion.ifc` de esta carpeta.
3. Seleccionar una vertida.
4. Ir a **Object Information → Property Sets** y desplegar `UANDES_HormigonMasivo`.
5. Para conservar las ediciones posteriores, usar **File → Save IFC Project**.

El comando sin argumentos completa los campos faltantes en `fundacion.ifc`, sin
duplicar el set ni reemplazar sus valores existentes. Guarda primero cualquier
edición pendiente en Bonsai y vuelve a abrir el IFC después de ejecutar el script,
para que Bonsai cargue los cambios externos. Para trabajar sobre otra entrada,
pasar su ruta como argumento. Una segunda ruta permite elegir otra salida si se
necesita explícitamente. La escritura usa un temporal y reemplaza el destino
solo cuando termina correctamente; el temporal se elimina al finalizar.

La guía contiene un error tipográfico en el nombre del comando del punto 23;
el script completo aparece en el punto 24. Aquí se utiliza el nombre español
`agregar_propiedades.py` y las rutas reales del proyecto.

## Punto 25: verificar desde Python

Ejecutar desde la raíz, después de guardar el IFC:

```powershell
.\.venv\Scripts\python.exe desarrollo/fundacion/verificar_ifc.py
```

El script lee `fundacion.ifc` sin modificarlo. Comprueba que existen
exactamente las cinco vertidas con clase IfcFooting y las siete propiedades,
triangula sus geometrías e imprime sus límites en coordenadas globales, en metros.
Los límites forman una caja envolvente (bounding box), no son el volumen de la pieza.
Se puede pasar otra ruta IFC como argumento.

Resultado comprobado el 21 de octubre de 2026: IFC4, unidades en metros, cinco
vertidas leídas y trianguladas correctamente, cada una con su GUID y propiedades.

| Vertida | Dimensiones X × Y × Z [m] | Desde z hasta z [m] |
| --- | --- | --- |
| 01 | 18 × 18 × 0.55 | 0–0.55 |
| 02 | 18 × 18 × 0.55 | 0.55–1.10 |
| 03 | 18 × 18 × 1.10 | 1.10–2.20 |
| 04 | 12.50 × 12.50 × 1.10 | 2.20–3.30 |
| 05 | 7 × 7 × 1 | 3.30–4.30 |
| Conjunto | 18 × 18 × 4.30 | 0–4.30 |

Esto reproduce la comprobación básica de los puntos 25–26. No comprueba solapes,
estanqueidad, todas las cotas ni validez térmica.

## Práctica E02: cambio de propiedad detectado desde Python

Demostración realizada el 21 de octubre de 2026 sobre `Vertida_01`:

1. Python leyó `TemperaturaColocacion_C = 18.0` desde el IFC guardado.
2. Se editó esa propiedad en el proyecto activo de Bonsai a `19.0`.
3. Antes de guardar, Bonsai mostraba `19.0` y el archivo seguía conteniendo `18.0`.
4. Se guardó mediante **Save IFC Project**.
5. Otro proceso Python abrió el archivo y leyó `19.0`, con el mismo GUID
   `31Auww6L95uPtdfMwkzuh4` y nombre `Vertida_01`.

El IFC queda con **19 °C en Vertida_01** como dato de práctica, sin validación
como temperatura definitiva del plan. Las otras vertidas conservan 18 °C.
Para mostrar el valor guardado, ejecutar `verificar_ifc.py` con el comando anterior.
Esto demuestra el flujo Bonsai → IFC → Python sin depender del estado de Blender.
