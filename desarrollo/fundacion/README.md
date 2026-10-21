# Fundación IFC: propiedades de las vertidas

Esta carpeta contiene el modelo y el script del punto 23 de
[la guía de Bonsai](../../Enunciados%20e%20Instrucciones/Guias/GUIA_BONSAI_FUNDACION.md).

| Archivo | Uso |
| --- | --- |
| `fundacion.ifc` | Modelo original guardado desde Bonsai. |
| `fundacion.blend` | Sesión auxiliar de Blender. El modelo BIM se abre desde el IFC. |
| `agregar_propiedades.py` | Agrega las propiedades del ejemplo de §24 usando IfcOpenShell. |
| `fundacion_props.ifc` | Copia del modelo con las propiedades incorporadas. Abrir esta en Bonsai. |
| `verificar_ifc.py` | Punto 25: lee el IFC e imprime nombres, clases, GUID, propiedades y dimensiones. |

Desde PowerShell, en la raíz del proyecto:

```powershell
.\.venv\Scripts\python.exe desarrollo/fundacion/agregar_propiedades.py
```

El script abre el IFC, busca exactamente `Vertida_01` a `Vertida_05`, crea el
Property Set `UANDES_HormigonMasivo` en cada una y guarda `fundacion_props.ifc`.
Conserva el archivo original, la geometría, los nombres y los GUID. Si faltan
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
2. Elegir **File → Open IFC Project** y abrir `fundacion_props.ifc` de esta carpeta.
3. Seleccionar una vertida.
4. Ir a **Object Information → Property Sets** y desplegar `UANDES_HormigonMasivo`.
5. Para conservar las ediciones posteriores, usar **File → Save IFC Project**.

El comando sin argumentos vuelve a generar la misma copia desde `fundacion.ifc`;
por eso reemplaza las ediciones hechas únicamente en `fundacion_props.ifc`.
Para completar propiedades de un IFC ya editado, pasar su ruta como entrada y
otra ruta de salida: el script conserva sus valores existentes y completa los
campos faltantes, sin duplicar el set.

La guía contiene un error tipográfico en el nombre del comando del punto 23;
el script completo aparece en el punto 24. Aquí se utiliza el nombre español
`agregar_propiedades.py` y las rutas reales del proyecto.

## Punto 25: verificar desde Python

Ejecutar desde la raíz, después de guardar el IFC:

```powershell
.\.venv\Scripts\python.exe desarrollo/fundacion/verificar_ifc.py
```

El script lee `fundacion_props.ifc` sin modificarlo. Comprueba que existen
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
estanqueidad, todas las cotas ni validez térmica. La demostración de modificar
una pieza en Bonsai, guardar y detectar el cambio desde Python sigue pendiente.
