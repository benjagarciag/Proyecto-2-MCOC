# Fuentes volumétricas: ejecutar y editar

> Versión publicada E04: ejecutar desde la raíz del repositorio con el entorno
> `.venv` preparado según el README principal. El total actual es 251 pruebas;
> los recuentos de cada etapa son históricos. [Índice E04](../../entregas/E04/README.md).

Esta etapa usa los solvers 2D/3D con bordes existentes y el nuevo argumento
opcional `fuente_W_m3`. La fuente predeterminada es cero; los comandos anteriores
siguen funcionando. No se requieren aplicaciones o dependencias nuevas.

## Ejecutar en este computador

En PowerShell:

```powershell
.\.venv\Scripts\python.exe -B casos/fuentes/ejecutar.py
```

Se reutiliza el intérprete instalado sin modificar el entorno original.
El código, la caché Matplotlib y los resultados se escriben en esta copia.
También puedes abrir `ejecutar.py` en VS Code, seleccionar ese intérprete y
ejecutarlo. Las figuras se guardan sin abrir ventanas.

Para un solo ejemplo, añadir `--caso uniforme`, `--caso localizada` o
`--caso robin`. Cada ejemplo ejecuta 2D y 3D y guarda UNA figura comparativa:

- `resultados/fuentes/uniforme/perfiles_temperatura.png`
- `resultados/fuentes/localizada/perfiles_temperatura.png`
- `resultados/fuentes/robin/perfiles_temperatura.png`

Se actualizan esas mismas figuras al repetir; no se exportan CSV u otros datos.
La primera fila es 2D, la segunda 3D (corte XY central). Columnas: fuente en
W/m³, temperatura final, evolución térmica y balance energético. La escala de
temperatura es común a ambas filas de cada figura; varía entre ejemplos.

## Parámetros editables

En [parametros.json](parametros.json) se declaran material, temperatura inicial,
tiempo final, número de celdas, fuentes y todos los bordes de cada ejemplo.
El ejecutor mantiene lados de 1 m y espesor 2D de 1 m. Para otras longitudes
se usa la API Python con `Parametros2D/3D`; no están expuestas en este ejecutor.

Fuente uniforme:

```json
{"tipo": "uniforme", "valor_W_m3": 600.0}
```

Fuente localizada 2D (ocupa todo el espesor):

```json
{"tipo": "caja", "valor_W_m3": 2000.0,
 "limites_m": {"x": [0.25, 0.75], "y": [0.25, 0.75]}}
```

En 3D añadir `"z": [0.25, 0.75]` dentro de `limites_m`.
Los límites son posiciones físicas en metros, no índices de celdas. Se calcula
la fracción activa de cada celda, para conservar la potencia total al refinar.
La fuente es constante en el tiempo, no negativa e independiente de T.
No representa todavía una curva de hidratación calibrada.

Cada cara sigue admitiendo Dirichlet, Neumann o Robin como en la etapa anterior.
En los JSON se pueden elegir distintos tipos por cara. Robin usa media celda
más película convectiva en serie; no cambió esa implementación.

El ejecutor también admite `--celdas 30` y `--dt 100` (segundos). Al refinar
debe reducirse el paso estable. Si se omite `--dt`, se calcula automáticamente.
No es necesario activar el entorno ni cambiar la configuración del sistema.

## Pruebas

Desde la misma raíz:

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider
```

**207 pruebas aprobadas: 156 anteriores + 51 nuevas.** Las pruebas no generan
figuras. Para otro computador, usar su intérprete y las dependencias fijadas en
`requirements.txt`; no copiar la ruta del intérprete de Matías.

Explicación del balance y recorrido oral en
[e04_fuentes.md](../../documentacion/e04_fuentes.md).
