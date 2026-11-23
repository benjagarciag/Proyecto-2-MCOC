# Artículo F01 en LaTeX

Revisión integral del 23 de noviembre de 2026. El artículo incorpora resumen, nueve secciones, referencias y dos anexos. La entrega debe acompañarse del SHA final de F01.

## Estructura vigente

- `main.tex`: documento principal y configuración tipográfica.
- `Portada.tex`: portada.
- `secciones/01_introduccion.tex`: introducción y objetivos.
- `secciones/02_caso_estudio_datos.tex`: caso de estudio, geometría, parámetros, hidratación y clima.
- `secciones/03_modelo_continuo.tex`: formulación física y condiciones de borde.
- `secciones/04_discretizacion_algoritmos.tex`: método implementado, sensibilidad, algoritmo y costo computacional.
- `secciones/05_verificacion_evaluacion.tex`: verificación, balance energético, sensibilidad, márgenes y limitaciones.
- `secciones/06_incertidumbre_optimizacion.tex`: restricciones, escenarios, evento conjunto, pesos, sensibilidad y alcance de la búsqueda.
- `secciones/07_resultados.tex`: cronogramas, probabilidades, extremos localizados, curvas, cortes y sensibilidades de la selección.
- `secciones/08_discusion_control.tex`: interpretación, alcance, instrumentación, funciones responsables, retiros, contingencias y liberación propuesta.
- `secciones/09_conclusiones.tex`: respuesta numérica, ahorro frente a la variante lenta, cumplimiento condicionado y comprobaciones pendientes.
- `Ref.bib`: bibliografía activa, autor–año con `natbib` y estilo `dcu`.
- `referencias.bib`: archivo anterior conservado; no está incluido en la compilación.
- `Imagenes/`: logo institucional, captura de Blender y figuras de datos.
- `datos/`: registros de trazabilidad y comprobaciones documentales.

La configuración del documento se conserva en `main.tex`, incluidos los ajustes de formato y distribución realizados por el usuario. Las figuras de hidratación y clima se generan con `generar_figura_hidratacion.py` y `generar_figuras_clima.py`, que trabajan con datos existentes y no ejecutan el solver.

## Evidencia del punto 5

Se reutilizan las comprobaciones ya archivadas, sin nuevas simulaciones:

- `casos/1d/verificacion_seno.json` y `desarrollo/tests/test_difusion_1d.py`: configuración y pruebas del caso analítico.
- `entregas/F02/cierre_revision_final/VERIFICACION.json` y `VERIFICACIONES_EJECUTADAS.txt`: errores y registro de pruebas ejecutadas.
- `entregas/F02/cierre_revision_final/BALANCES_144_FILAS.csv`: energía y residuos.
- `entregas/F02/cierre_revision_final/SENSIBILIDAD_ESPACIAL_24_PARES.csv`: comparación espacial pareada.
- `resultados/cierre_f02/resumen.json` y resultados del estudio de protección postdesmolde: matrices finales y contrastes temporales selectivos.
- `datos/comparacion_volumenes.json`: aproximación geométrica.

El capítulo distingue la matriz espacial completa de 24 escenarios de los dos contrastes temporales. No presenta estas comprobaciones como validación experimental de la fundación ni como una cota rigurosa del error. Se mantienen las protecciones finales de 504 h más sombra solar del 90 %, con seguimiento hasta 672 h.

Para el punto 6 se reagregaron los indicadores existentes con todas las curvas, solo SS y solo 22A. `datos/sensibilidad_pesos.json` conserva las 18 comprobaciones correspondientes a tres matrices, dos horizontes y tres selecciones de curvas. No se ejecutaron nuevas simulaciones. La familia final compara 55 y 60 m³/h; las exploraciones anteriores no se presentan como matrices finales homogéneas de otras tasas.

## Evidencia del punto 7

`generar_resultados.py` prepara las tablas de cronograma de ambas tasas y la tabla de localización de los seis extremos del conjunto. Copia cinco figuras verificadas del cierre F02 sin modificar sus originales. Solo lee datos existentes y no importa ni ejecuta el solver. `datos/resultados_trazabilidad.json` conserva las 22 filas de cronograma, los registros completos de los extremos y las procedencias y hashes de las imágenes.

La sección incluye `datos/tabla_cronograma_60.tex`, `datos/tabla_cronograma_55.tex` y `datos/tabla_localizacion_maximos.tex`. Estos archivos y las cinco imágenes cuyo nombre comienza con `resultados_` deben acompañar a las fuentes al copiar el proyecto a Overleaf. Las coordenadas reportadas corresponden a la malla, incluidas caras escalonadas a z=4,40 m; no se confunden con la altura oficial del IFC de aproximadamente 4,30 m. Las curvas y cortes muestran una realización; la tabla de extremos identifica por separado el escenario de cada máximo.

## Compilación

Seleccionar `main.tex` como documento principal. El PDF revisado y el paquete para Overleaf se encuentran en `../Articulo-Final/`, y la revisión punto por punto se conserva en la carpeta revision. El PDF se compiló con las figuras y se inspeccionaron las páginas renderizadas.

Los disparadores de 65/68 °C y 18/19 K, las frecuencias de registro, las funciones por asignar y los criterios de retiro/liberación del punto 8 son propuestas operativas del equipo; no se presentan como normas ni contingencias ya simuladas. El calendario nominal conserva 72/240/504 h más sombra, distinguiéndolo de las configuraciones históricas. La conclusión cuantifica un ahorro de 57,88865 min, equivalente al 8,33333 % de la duración del plan de 55 m³/h. No se ejecutaron simulaciones nuevas para esta redacción.

En Overleaf, subir la carpeta completa y elegir `main.tex`. Con una distribución TeX local, desde esta carpeta:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Las instrucciones del taller y de la pauta sirven como criterios de elaboración; los resultados y el alcance de las afirmaciones se contrastan con la evidencia del repositorio.
