# Artículo F01 en LaTeX

Estado al 23 de noviembre de 2026: borradores de las secciones 1 a 5 integrados. El punto 5 queda preparado para la revisión del equipo. El artículo todavía no es una versión final de entrega: faltan los apartados posteriores y la revisión conjunta.

## Estructura vigente

- `main.tex`: documento principal y configuración tipográfica.
- `Portada.tex`: portada.
- `secciones/01_introduccion.tex`: introducción y objetivos.
- `secciones/02_caso_estudio_datos.tex`: caso de estudio, geometría, parámetros, hidratación y clima.
- `secciones/03_modelo_continuo.tex`: formulación física y condiciones de borde.
- `secciones/04_discretizacion_algoritmos.tex`: método implementado, sensibilidad, algoritmo y costo computacional.
- `secciones/05_verificacion_evaluacion.tex`: verificación, balance energético, sensibilidad, márgenes y limitaciones.
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

## Compilación

Seleccionar `main.tex` como documento principal. El proyecto completo compiló correctamente con el compilador integrado del editor el 23 de noviembre de 2026, después de incorporar el punto 5. Esa comprobación no equivale a una revisión visual completa de todas las páginas.

En Overleaf, subir la carpeta completa y elegir `main.tex`. Con una distribución TeX local, desde esta carpeta:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Las instrucciones del taller y de la pauta sirven como criterios de elaboración; los resultados y el alcance de las afirmaciones se contrastan con la evidencia del repositorio.
