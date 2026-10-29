# Tests

Las pruebas del primer solver están en [test_difusion_1d.py](test_difusion_1d.py).

Ejecutar desde la raíz del repositorio:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Se comparan los 20 perfiles del video con el bloque numérico original, sin abrir
gráficos ni escribir en las carpetas del profesor. La tolerancia es 10⁻¹² °C.
Se verifica de forma independiente el seno de la guía contra su solución exacta.
También se prueban bordes independientes, equilibrio lineal y uniforme, un paso
manual, refinamiento conjunto, estabilidad, ajuste temporal y entradas inválidas.

Las pruebas de [test_ejemplos_1d.py](test_ejemplos_1d.py) comprueban además
el calentamiento con Neumann, el balance superficial Robin, sus tiempos de
muestreo, el aporte `r*Q0` y el rechazo de pasos inestables.

El conjunto inicial 1D tiene 31 casos de prueba, incluidos los distintos valores de las pruebas
parametrizadas. Un código de salida cero indica que todas las pruebas pasaron.

En entornos que restrinjan la escritura de la caché, ejecutar:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
```

La desactivación de la caché no omite pruebas.

La última ejecución completa aprobó **296 tests**. La batería actual recopila
**320 tests**, incluyendo los añadidos del visualizador y criterios térmicos;
estos últimos no se ejecutaron al preparar el commit, por preferencia del usuario.
El conjunto incorpora soluciones 2D/3D,
Neumann, Robin, conservación adiabática, fuentes, materiales, barra y fuente
temporal, además de **29 variantes editables para E05** en
`test_e05_parametros.py`. Ver la [guía de estudio](../../entregas/E05/README.md).

Para imprimir parámetros y errores, sin generar archivos:

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q -s -p no:cacheprovider desarrollo/tests/test_e05_parametros.py
```
