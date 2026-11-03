# E07 — Etapa 5: activación temporal de vertidas

Trabajo exclusivo de la copia `E07_pruebas`. Se verificó primero la base
funcional de Etapa 4: **434 pruebas aprobadas**. Se mantienen el IFC, los
solvers E04, la voxelización, la asignación final y los PNG anteriores.

## Calendario y material

Los datos se leen del IFC como parámetros del caso docente:

| Vertida | Inicio [h] | Temperatura al colocar [°C] | Material (etiqueta) |
| --- | ---: | ---: | --- |
| 01 | 0 | 19 | M1 |
| 02 | 6 | 18 | M1 |
| 03 | 12 | 18 | M1 |
| 04 | 18 | 18 | M1 |
| 05 | 24 | 18 | M1 |

t=0 es el origen docente de colocación, no una fecha meteorológica. El módulo
trabaja en segundos: 0, 21600, 43200, 64800 y 86400 s. No reescribe el IFC.

M1 es `TipoHormigon`, no un conjunto de propiedades físicas: el IFC no tiene
IfcMaterial asociado. No se inventan k, ρ o cp. Su definición física queda
pendiente antes del acoplamiento térmico de la fundación.

## Módulo reutilizable

Nuevo archivo: `desarrollo/mcplan/construccion.py`.

| API | Función |
| --- | --- |
| `preparar_construccion(fundacion, asignacion)` | Verifica SHA e IDs y relaciona cada voxel con el calendario IFC. |
| `ProgramaConstruccion` | Asignación final, eventos, material, inicio y temperatura de colocación por voxel. |
| `iniciar_construccion(programa)` | Estado previo t=−1 s, sin celdas activas. |
| `EstadoConstruccion` | Tiempo, activos, nuevos, temperatura actual y edad, en arrays ZYX. |
| `avanzar_construccion(estado, t, temperatura_actual_C=...)` | Incorpora nuevos voxeles sin reiniciar los existentes. |
| `proxima_colocacion_s(estado)` | Próximo evento estrictamente posterior. |
| `limitar_paso_por_colocacion_s(estado, dt)` | Recorta el paso hasta la siguiente colocación. |
| `mascaras_contactos_activos(estado)` | Enlaces Z/Y/X con ambos extremos activos, de las formas usadas en E04. |
| `superficies_construidas(estado)` | Reutiliza Etapa 4 con la ocupación construida. |

El estado conserva acceso a IDs y ocupación geométrica final. Los campos de
calendario y material existen también en voxeles futuros. En el espacio vacío
se usa etiqueta `''` y NaN para los campos numéricos sin significado.

```
activo_i(t) = ocupado_final_i AND (t >= inicio_i)
nuevo_i    = activo_i(t_nuevo) AND NOT activo_i(t_anterior)

T_i nueva = T_colocacion_i       si es nuevo
           T_actual_i anterior si ya estaba activo
           NaN                 si no está activo

edad_i = t-inicio_i si activo; NaN si aún no colocado o vacío
```

La comparación de tiempos es inclusiva, sin tolerancias que adelanten eventos.
Los tests usan `np.nextafter` inmediatamente antes y después. Se rechaza
retroceder el tiempo. Se admiten eventos simultáneos y orden por horario,
sin suponer que el número del ID determina cuándo se coloca.

Cada transición devuelve arrays nuevos de solo lectura. No altera el estado
previo ni el campo de temperaturas recibido. `temperatura_actual_C` debe ser
finita en voxeles ya activos; los valores de las celdas no colocadas se ignoran.
Las nuevas reciben siempre su T de colocación.

Sin un solver externo que actualice T, las temperaturas anteriores permanecen
constantes. Saltar varios eventos sirve para consultar construcción y edades,
pero no simula la historia térmica entre eventos.

### Uso desde Python

Con `desarrollo` en el path y los objetos de las etapas anteriores:

```python
from mcplan.construccion import (
    preparar_construccion, iniciar_construccion,
    avanzar_construccion, superficies_construidas,
)
programa = preparar_construccion(fundacion, asignacion)
estado = iniciar_construccion(programa)
estado = avanzar_construccion(estado, 0)         # 01 a 19 °C
estado = avanzar_construccion(estado, 6*3600)    # 02 a 18 °C, conserva 01
caras = superficies_construidas(estado)
```

Para recibir un campo calculado posteriormente, pasar
`temperatura_actual_C=T_calculada`. No reconstruir el estado desde cero
en cada paso: eso perdería la historia de temperaturas.

## Superficies construidas

Se crea una vista de IDs activos, con ID 0 en el resto, y se llama a
`clasificar_caras` de Etapa 4 sin modificarla ni cambiar la asignación final.

- Activo frente a vacío o no colocado: expuesto.
- Dos activos de igual ID: interna.
- Dos activos de distinto ID: interfaz activa.

Cada exterior mantiene `id_vecino_final`: 0 para vacío geométrico, o el ID
de la vertida no colocada. `expuestas_a_no_colocado` identifica estas últimas.
Se comprueban los límites antes de indexar vecinos; no hay envoltura periódica.

En t=0, 01–02 está expuesto desde 01 hacia 02. En t=6 h pasa a interfaz activa,
manteniendo orientación y contando cada contacto una sola vez.
Expuesto no significa automáticamente convección: puede haber suelo, moldaje,
aislación o aire. Aquí no se asignan condiciones térmicas de borde.

## Compatibilidad con el balance E04

Se mantiene ZYX, float64 y segundos. Las máscaras de enlaces tienen las formas
de los contactos Z/Y/X del balance E04. Internas e interfaces construidas
contienen solo pares activo–activo. Un ensayo sintético compara sus intercambios
conservativos con el núcleo E04 para un dominio rectangular ya construido.

Para un futuro acoplamiento:

```
dt = min(dt_estabilidad_actual, dt_propuesto, t_siguiente_evento-t)
```

Tras cada evento habrá que actualizar capacidades, conductancias y estabilidad.
Recortar por colocación NO reemplaza el criterio de estabilidad térmica.

No se ha acoplado el solver rectangular E04 directamente a la fundación
irregular. No pasarle el campo con NaN sin un operador que excluya inactivos:
`0*NaN` también da NaN. El futuro operador debe indexar solo pares activos y
aplicar bordes en las caras construidas. Esta etapa prepara esos datos,
sin ejecutar una nueva simulación térmica.

## Resultados, grilla ilustrativa h=0,5 m

| Tiempo [h] | IDs activos | Voxeles | Volumen [m³] | Expuesto [m²] | Interfaces activas [m²] | Expuesto hacia no colocado [m²] |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Antes de 0 | Ninguno | 0 | 0 | 0 | 0 | 0 |
| 0 | 01 | 1076 | 134,5 | 574 | 0 | 269 |
| 6 | 01–02 | 2152 | 269 | 610 | 269 | 244 |
| 12 | 01–03 | 3848 | 481 | 674 | 513 | 123 |
| 18 | 01–04 | 4828 | 603,5 | 732 | 636 | 39 |
| 24 | 01–05 | 5140 | 642,5 | 760 | 675 | 0 |

En t=24 h se recuperan exactamente las caras de Etapa 4. Las edades son
24, 18, 12, 6 y 0 h. Los volúmenes son voxelizados, no exactos del IFC.

## Ejecutar y revisar en VS Code

Desde la raíz de E07_pruebas:

```powershell
# Terminal con el entorno del proyecto activado
python -B casos/e07/activar_vertidas.py
```

También se puede abrir ese script en VS Code y seleccionar ese intérprete.
Las rutas se calculan desde el archivo, no dependen de la carpeta de la terminal.
`--solo-datos` omite gráficos; `--parametros ruta.json` permite otra configuración.
`activacion.json` configura grilla e instantes; horarios y temperaturas se leen
del IFC. No requiere dependencias nuevas ni interfaz web.

Salidas nuevas en `resultados/e07/activacion_temporal/`:

- `secuencia_constructiva.png`: seis vistas 3D, colores por vertida activa.
- `superficies_durante_construccion.png`: cortes XZ; gris no colocado, rojo
  expuesto hacia futuras vertidas, naranja expuesto al vacío final y violeta
  interfaces activas. El corte omite caras normales a Y.
- `volumen_y_areas_construidas.png`: volumen y áreas por eventos.
- `resumen_construccion.json`: calendario, edades, conteos, áreas, pares y SHA.

Repetir actualiza solo estas salidas. Se conservan los resultados de Etapas 1–4.
Las figuras son estados constructivos, no temperaturas simuladas.

## Verificación y límites

**481 pruebas aprobadas: 434 anteriores + 47 nuevas** en
`desarrollo/tests/test_construccion.py`.

```powershell
python -B -m pytest -q -p no:cacheprovider --basetemp=.venv/cache/pytest_etapa5_01
```

Cubren los cinco eventos, persistencia de campos no uniformes, inicialización,
edades, repetición de instante, eventos simultáneos, superficies, enlaces activos,
comparación con E04, recuperación de Etapa 4, conservación del IFC/geometría,
resolución con capa ausente y rechazo de entradas incompatibles.

La activación no corrige la malla. h=1 m sigue sin representar V02 y puede crear
contactos artificiales; `ids_sin_voxeles` lo informa. h=0,5 m mantiene error
de volumen +37,757% en V04; h=0,25 m mantiene +16,029% en V03. Ninguna resolución
queda certificada. Las áreas siguen siendo caras cartesianas escalonadas.

La colocación es instantánea por vertida completa. No hay duración interna del
hormigonado, cálculo de energía por colocación, hidratación, clima o desmolde.

## Pendientes para Etapa 6

Revisar y autorizar la ley y parámetros de hidratación, definir propiedades
físicas justificadas para M1 y usar la edad de cada voxel construido. La fuente
deberá ser cero antes de colocar y comenzar con edad cero al activar. Habrá que
verificar W/m³, balance energético y acoplamiento del operador térmico para la
geometría irregular, además de resolver las limitaciones de malla. No se
implementa ninguna de estas funciones en esta etapa.
