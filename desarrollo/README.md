# Desarrollo y verificación

Esta carpeta reúne los archivos técnicos. Para ejecutar los ejemplos y estudiar
su explicación, usar [casos/](../casos/README.md) y
[documentacion/](../documentacion/README.md).

| Ubicación | Contenido |
| --- | --- |
| [mcplan/difusion_1d.py](mcplan/difusion_1d.py) | Núcleo reutilizable de difusión 1D, sin fuente y con Dirichlet independientes. |
| [mcplan/ejemplos_1d.py](mcplan/ejemplos_1d.py) | Cálculo de los ejemplos Neumann, Robin y calor interno, sin IO. |
| [tests/](tests/README_TESTS.md) | Pruebas automatizadas del solver. |
| [ejecutar_notebook.py](ejecutar_notebook.py) | Ejecutar y guardar todas las celdas del notebook. |

Todos los comandos se ejecutan desde la raíz del proyecto:

```powershell
# Pruebas: la configuración raíz encuentra desarrollo/tests y desarrollo/mcplan.
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider

# Comprobar dependencias.
.\.venv\Scripts\python.exe -m pip check

# Ejecutar el notebook completo y guardar sus salidas.
.\.venv\Scripts\python.exe desarrollo/ejecutar_notebook.py
```

El script del caso `casos/1d/ejecutar.py` encuentra el paquete `mcplan` en esta
carpeta. No hace falta mover los archivos ni instalar otro solver.
El ejecutor incluye los cuatro ejemplos. Sus condiciones de borde y fuente
también se estudian en `casos/1d/codigos/` y en el notebook.
