# E07 — Geometría, vertidas, superficies y construcción

Entrega E07 del Grupo 6, basada en main `e281ec4bc6d96f8e3481d08112cc94dcfff5f51c`.
Ejecutar desde la raíz del repositorio y con el entorno Python del proyecto activado.
La extracción de Etapa 1 se conserva; la Etapa 2 añade ocupación por centros
y la Etapa 3 asigna IDs geométricos y analiza volúmenes. La Etapa 5 incorpora
actividad temporal y etiqueta IFC de material, sin propiedades físicas inventadas.
No se modifica ni se completa ninguna propiedad del IFC.

## Etapa 6: hidratación didáctica por edad

```powershell
python -B casos/e07/hidratar_vertidas.py
```

`hidratacion.json` contiene la curva exponencial y los parámetros didácticos
de la guía: θ∞=45 K, τ=30 h, ρ=2400 kg/m³ y cp=900 J/(kg·K), sin calibración
experimental de M1. Se reutilizan calendario y edades de Etapa 5, con fuente
cero antes de activar e integral exacta por intervalo, incluso si cruza una colocación.

**528 tests aprobados: 481 anteriores + 47 nuevos.** Tres PNG y
`resumen_hidratacion.json` en `resultados/e07/hidratacion/`. `--solo-datos`
omite figuras. No se calcula la temperatura espacial de la fundación ni clima.
Ecuaciones, API, unidades, uso y pendientes en
[e07_hidratacion.md](../../documentacion/e07_hidratacion.md).

## Etapa 5: activación temporal

Desde la raíz del repositorio, con el entorno del proyecto activado:

```powershell
python -B casos/e07/activar_vertidas.py
```

`activacion.json` configura grilla e instantes de observación. El calendario y
las temperaturas se leen del IFC: 0/6/12/18/24 h y 19/18/18/18/18 °C.
Se inicializan solo las celdas nuevas y se conservan las temperaturas existentes.
`--solo-datos` omite las figuras. No hay difusión ni hidratación en este ejemplo.

Resultados en `resultados/e07/activacion_temporal/`: `secuencia_constructiva.png`,
`superficies_durante_construccion.png`, `volumen_y_areas_construidas.png` y
`resumen_construccion.json`. Se conservan los PNG anteriores.

**481 pruebas aprobadas: 434 anteriores + 47 nuevas.** Funciones, campos,
limitaciones y comandos en [e07_activacion_temporal.md](../../documentacion/e07_activacion_temporal.md).
M1 es una etiqueta; falta definir sus propiedades físicas. La resolución sigue
sin certificar y no se corrigen capas ausentes al activar.

## Etapa 4: superficies e interfaces

Desde la raíz del repositorio, con el entorno del proyecto activado:

```powershell
python -B casos/e07/clasificar_superficies.py
```

Entrada: `superficies.json`. Reutiliza ocupación e IDs y clasifica seis
vecinos como exterior, interna o interfaz, sin duplicar contactos.
`--solo-datos` omite gráficos. Las tablas de tres resoluciones se guardan en
`resultados/e07/superficies/areas_superficies.json`, junto con las figuras
`superficies_exteriores_y_corte.png` e `interfaces_y_caras_internas.png`.

**434 pruebas aprobadas: las 410 anteriores + 24 nuevas.** Las áreas, funciones,
comandos de prueba y limitaciones están en
[e07_superficies.md](../../documentacion/e07_superficies.md).
Con h=1 m desaparecen los contactos 01–02 y 02–03 y surge 01–03 artificial.
Ninguna resolución queda certificada. Estas superficies son geométricas del
modelo completo; no se implementa todavía exposición térmica temporal.

## Etapa 3: identificación y volúmenes

Desde la raíz del repositorio, con el entorno del proyecto activado:

```powershell
python -B casos/e07/identificar_vertidas.py
```

Entradas: `vertidas_volumenes.json` (h=1,0.5,0.25 m, mismo origen y tolerancia).
`--solo-datos` imprime tablas sin gráficos. Se leen las cinco mallas una sola
vez; cada ocupado recibe un ID 1..5 y los vacíos conservan 0. Los solapes de
interiores se rechazan con diagnóstico. El criterio de frontera y todas las
tablas están en [e07_vertidas_volumenes.md](../../documentacion/e07_vertidas_volumenes.md).

Figuras fijas en `resultados/e07/vertidas_volumenes/`: `vertidas_y_corte.png`,
`comparacion_resoluciones.png`, `errores_volumen.png`.
Con h=1 m la capa 02 no está resuelta. El error global pequeño no garantiza
que cada vertida tenga volumen suficientemente preciso.

Pruebas completas, en un directorio temporal exclusivo de esta copia:

```powershell
New-Item -ItemType Directory -Path '.venv/cache' -Force | Out-Null
$env:MPLCONFIGDIR = Join-Path (Get-Location) '.venv/cache/matplotlib'
python -B -m pytest -q -p no:cacheprovider --basetemp=.venv/cache/pytest_etapa3
```

Resultado actual: **410 aprobadas: 389 anteriores + 21 nuevas**.

## Etapa 2: voxelización

Desde la misma raíz e intérprete descritos abajo:

```powershell
python -B casos/e07/voxelizar_ifc.py
```

Editar `voxelizacion.json` para cambiar dx/dy/dz, tolerancia u origen.
También se admite `--pasos DX DY DZ` y `--solo-datos` para no dibujar.
Default: pasos de 0.5 m, grilla 37×37×9, 5140 celdas ocupadas, 642.5 m³.
La figura fija está en `resultados/e07/voxelizacion/geometria_y_voxeles.png`.
El color indica ocupación, no temperatura o vertida. El lector IFC sigue
siendo `mcplan.bim` y no se modificó para esta etapa.

Para verificar TODO, usar un directorio temporal propio de esta copia:

```powershell
New-Item -ItemType Directory -Path '.venv/cache' -Force | Out-Null
$env:MPLCONFIGDIR = Join-Path (Get-Location) '.venv/cache/matplotlib'
python -B -m pytest -q -p no:cacheprovider --basetemp=.venv/cache/pytest_etapa2
```

Resultado actual: **389 pruebas aprobadas: 353 anteriores y 36 nuevas**.
La tolerancia, política de frontera y limitaciones están en
[e07_voxelizacion.md](../../documentacion/e07_voxelizacion.md).

## Etapa 1: extracción conservada

## Ejecutar en este computador

Desde PowerShell:

```powershell
# Abrir la terminal en la raíz de la carpeta del proyecto
# Terminal con el entorno del proyecto activado
python -B casos/e07/extraer_ifc.py
```

Utiliza el Python y las dependencias ya instaladas; no los modifica ni instala
otro entorno. `.venv/cache` de ESTA copia solo almacena cachés y variantes
temporales para pruebas. En VS Code seleccionar ese intérprete y ejecutar
`casos/e07/extraer_ifc.py`. Desde otro computador usar su propio intérprete
con las dependencias declaradas en `requirements.txt`.

Se imprime el resumen y se actualiza una figura fija:

`resultados/e07/extraccion_ifc/geometria_ifc.png`

Izquierda: aristas de los triángulos en sus coordenadas originales.
Derecha: las mismas piezas, separadas 3 m adicionales por nivel únicamente
para distinguirlas en el gráfico. No se modifica la estructura devuelta ni
el archivo IFC. La imagen representa geometría, no temperaturas ni voxeles.

Añadir `--solo-datos` para no generar el gráfico. `--ifc ruta.ifc` permite
leer otra entrada, que debe cumplir las validaciones de las cinco vertidas.
El verificador anterior también continúa disponible:

```powershell
python -B desarrollo/fundacion/verificar_ifc.py
```

## Usar los datos desde Python

Los ejecutores agregan `desarrollo/` al path. Desde la raíz, en un script:

```python
import sys
sys.path.insert(0, 'desarrollo')
from mcplan.bim import extraer_fundacion_ifc

fundacion = extraer_fundacion_ifc('desarrollo/fundacion/fundacion.ifc')
vertida = fundacion.vertidas[0]
vertices = vertida.vertices_m        # matriz [n,3], XYZ en metros
triangulos = vertida.triangulos     # índices enteros [m,3], desde cero
superficie = vertices[triangulos]   # coordenadas de cada triángulo
print(vertida.guid, vertida.vertida_id, vertida.volumen_m3)
print(vertida.inicio_s, vertida.temperatura_colocacion_C)
```

La extracción no escribe ni imprime; su resultado contiene geometría y datos
ordinarios de Python/NumPy, sin depender de Blender o de objetos IFC vivos.

## Repetir pruebas

Desde la raíz, usando la variable de intérprete anterior:

```powershell
New-Item -ItemType Directory -Path '.venv/cache' -Force | Out-Null
$env:MPLCONFIGDIR = Join-Path (Get-Location) '.venv/cache/matplotlib'
python -B -m pytest -q -p no:cacheprovider --basetemp=.venv/cache/pytest_etapa1
```

El directorio de pruebas es exclusivo de esta copia y desechable. Las variantes
IFC inválidas se crean allí, nunca sobre `fundacion.ifc`. Resultado: **353 tests
aprobados: 320 anteriores + 33 nuevos**. No se generan gráficos durante pytest.

Validaciones, tolerancias, resultados y límites en
[e07_extraccion_ifc.md](../../documentacion/e07_extraccion_ifc.md).
