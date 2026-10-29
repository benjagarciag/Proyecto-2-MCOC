# Ejemplos Neumann y Robin, 2D y 3D

> Versión publicada E04: ejecutar desde la raíz del repositorio con el entorno
> `.venv` preparado según el README principal. El total actual es 251 pruebas;
> los recuentos de cada etapa son históricos. [Índice E04](../../entregas/E04/README.md).

Trabajar desde la raíz de **E04_pruebas_2d**, no desde el proyecto original.
Los módulos anteriores se conservan; estos ejemplos usan la extensión nueva
`mcplan.difusion_bordes`. No requieren Blender ni cambian el IFC.

## Ejecutar en este computador

En PowerShell, abrir la copia y usar el Python ya instalado (sin activar ni
instalar otro entorno):

```powershell
.\.venv\Scripts\python.exe -B casos/bordes/Ejecutar_Bordes.py
```

La ruta del intérprete reutiliza las dependencias instaladas; las escrituras
de esta ejecución son figuras y caché Matplotlib dentro de la copia.
No escribe en el entorno original (`-B` evita archivos bytecode).
En otro computador se debe usar su propio intérprete con las dependencias
del `requirements.txt` de esta copia; aquí no se hizo ninguna instalación.

Para un solo ejemplo, añadir `--caso 2d_adiabatico`, `--caso 2d_robin`,
`--caso 3d_neumann` o `--caso 3d_robin` al comando de ejecución.
También admite `--dt 200` (segundos) y `--celdas 20` (por dirección).
Un paso que excede el límite se rechaza antes de simular.
El paso efectivo puede ser algo menor para terminar exactamente en tf.

En VS Code: abrir `casos/bordes/Ejecutar_Bordes.py`, seleccionar el intérprete de
`.venv` ya utilizado y ejecutar el archivo Python. No hay que abrir el código
en Blender. Se guardan los gráficos; no se abre una ventana de Matplotlib.

## Editar los bordes

En el bloque `CASOS` al comienzo de [Ejecutar_Bordes.py](Ejecutar_Bordes.py),
cada caso declara todas sus caras. Las propiedades comunes están en `MATERIAL`:

- `x_min`: izquierda; `x_max`: derecha.
- `y_min`: abajo; `y_max`: arriba en el plano XY.
- En 3D también `z_min`: base y `z_max`: techo.

Cada cara usa uno de estos diccionarios de Python:

```python
{"tipo": "neumann", "flujo_entrante_W_m2": 0}
```

```python
{"tipo": "neumann", "flujo_entrante_W_m2": 200}
```

```python
{"tipo": "robin", "h_W_m2K": 10, "ambiente_C": 20}
```

```python
{"tipo": "dirichlet", "temperatura_C": 20}
```

Positivo significa calor **entrando**, en cualquier cara. Negativo significa
calor saliendo. Neumann cero y Robin con h=0 representan aislamiento ideal.
Se pueden mezclar los tres tipos, uno por cara. Los ejemplos predefinidos
usan propiedades constantes, lados de 1 m y espesor 2D de 1 m. En el modelo
2D las caras normales al espesor están aisladas y no se modelan gradientes z.

Para estudiar otras longitudes se usan los campos de `Parametros2D/3D` desde
Python; el ejecutor didáctico mantiene lados de 1 m y no expone esas entradas.
Los parámetros y títulos del caso deben corresponder a la demostración:
por ejemplo, el título `2d_adiabatico` supone que sus cuatro flujos siguen en cero.

## Resultados

Una única figura por ejemplo, actualizada al repetir la ejecución:

- `resultados/bordes/2d_adiabatico/perfiles_temperatura.png`
- `resultados/bordes/2d_robin/perfiles_temperatura.png`
- `resultados/bordes/3d_neumann/perfiles_temperatura.png`
- `resultados/bordes/3d_robin/perfiles_temperatura.png`

Arriba: campos de temperatura; los casos 3D muestran cortes XY y XZ.
Abajo: temperaturas media/máxima/mínima, potencia exterior entrante y balance
de energía. Las temperaturas resumen siete campos guardados; la potencia y
la energía se registran en todos los pasos. Cada figura usa una escala común
entre sus propios campos, pero las escalas pueden variar entre ejemplos.

## Repetir las pruebas

Desde la misma raíz:

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider
```

Resultado de esta etapa: **156 pruebas aprobadas**, 83 anteriores más 73 nuevas.
Las pruebas no generan figuras. Explicación y defensa oral en
[e04_bordes.md](../../documentacion/e04_bordes.md).
