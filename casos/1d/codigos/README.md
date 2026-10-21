# Códigos del caso 1D

Cada archivo es un ejemplo ejecutable de difusión térmica unidimensional.

| Código | Fenómeno |
| --- | --- |
| [01_1d_dirichlet_verification.py](01_1d_dirichlet_verification.py) | Barra con temperaturas fijas de 0 y 10 °C en los extremos. |
| [03_1d_neumann.py](03_1d_neumann.py) | Temperatura fija a la izquierda y extremo derecho aislado. |
| [04_1d_robin.py](04_1d_robin.py) | Convección con ambiente variable. |
| [05_calor_interno.py](05_calor_interno.py) | Generación de calor dentro de una barra con extremos a 0 °C. |

## Ejecutar en Visual Studio Code

Abrir el archivo, seleccionar el intérprete `.venv/Scripts/python.exe` y utilizar
**Run Python File in Terminal**. El gráfico se abre en una ventana: cerrarla
cuando termine la revisión para finalizar la ejecución.

También se puede ejecutar desde PowerShell en la raíz del proyecto:

```powershell
.\.venv\Scripts\python.exe casos/1d/codigos/01_1d_dirichlet_verification.py
```

Cambiar el nombre del archivo para ejecutar otro ejemplo. Cada script guarda
su misma figura en `resultados/1d/<caso>/perfiles_temperatura.png` y también
la muestra en una ventana. Se reutilizan las carpetas `base/`, `neumann/`,
`robin/` y `calor_interno/`, sin carpetas con fecha.

El comando `ejecutar.py` sin opciones llama a estos cuatro archivos y guarda
sus figuras sin abrir ventanas. Robin conserva su figura completa de dos paneles.

Para estudiar las ecuaciones y cada bloque, abrir el
[notebook explicativo](../../../documentacion/explicacion_solver_1d.ipynb).
Para el ejecutor que actualiza los resultados en una carpeta fija, consultar
[el índice del caso 1D](../README.md).

Los cuatro archivos recibidos conservan su contenido numérico y
sus nombres se conservan; esta carpeta los agrupa por el problema que resuelven.
