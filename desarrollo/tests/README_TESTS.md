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

Hay 31 casos de prueba, incluidos los distintos valores de las pruebas
parametrizadas. Un código de salida cero indica que todas las pruebas pasaron.

En entornos que restrinjan la escritura de la caché, ejecutar:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
```

La desactivación de la caché no omite pruebas. Este conjunto inicial no sustituye
la futura batería completa de fuentes, flujos, dominios adiabáticos y 2D/3D.
