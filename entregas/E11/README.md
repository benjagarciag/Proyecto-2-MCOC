# E11 — Weather pipeline y visualización 3D

La demo usa 48 horas del pronóstico GFS guardado para el Parque Eólico El
Rosal. Empieza el 10 de noviembre de 2026 a las 17:00 (hora de Chile). El
mismo programa también ejecuta [el caso de 14 días de E12](../../Reportes/Reporte_E12.md).

## Demo

1. Abrir el [snapshot GFS](../../datos/clima/forecasts/20261110T190042897941Z_44b1a950.json).
   En `respuesta.hourly` están las marcas UTC y la serie `temperature_2m`.
2. Mostrar `metadata`: fuente, modelo, descarga **2026-11-10 19:00:42 UTC**,
   coordenadas pedidas **−37,277929; −72,368271**, unidades y horizonte. El
   JSON conserva también las coordenadas devueltas por el modelo.
3. Abrir [aire.png](../../resultados/e11/aire.png) y señalar el intervalo
   de 0 a 48 h y sus unidades en °C.
4. Mostrar [la entrada al solver](../../casos/semana4/ejecutar.py) y
   [el balance](../../desarrollo/mcplan/termica_fundacion.py).
   Se interpola la temperatura del aire entre marcas horarias. Para una cara
   expuesta, la potencia que entra a la celda es
   `P = H · (T_aire − T_celda)`, en W, con
   `H = A / (Δx/(2k) + Σ(e/k_capa) + 1/h)`, en W/K. El valor
   `h = 5 W/(m²·K)` es fijo. Viento y radiación están guardados en el
   snapshot y quedan fuera del cálculo.
5. Ejecutar el caso `e11`. La corrida de referencia tiene 192 pasos. El
   [resumen](../../resultados/e11/resumen.json) registra 50,67 °C de máximo a
   las 48 h.
6. Abrir [diferencial.vti](../../resultados/e11/diferencial.vti) con el
   visualizador. La escala de color es la temperatura de las celdas activas.
7. Arrastrar el plano con el mouse para mover el corte. Para clipping,
   agregar `--modo recorte`. En ParaView se puede aplicar **Threshold** con
   `activo = 1`, después **Slice** o **Clip**, y colorear por `T_C`.
8. Señalar la sonda de núcleo en `(0,25; 0,25; 1,25) m` y el punto
   **S25 mínima**, reconstruido a 25 mm bajo una cara exterior. El campo
   `superficie` identifica las celdas exteriores. `T_S25_min_C` indica la
   menor temperatura S25 de las caras exteriores de cada celda.

## Comandos desde la raíz

Instalar primero las dependencias de Python del proyecto y las de la vista 3D
en el mismo entorno, si todavía no están instaladas.

~~~sh
python -m pip install -r requirements.txt -r casos/semana4/requirements-vista.txt
python casos/semana4/ejecutar.py e11
python casos/semana4/ver_3d.py resultados/e11/diferencial.vti
~~~

En Windows se puede usar el Python del entorno del proyecto con las
dependencias instaladas. En esta copia de revisión, ejecutar en PowerShell:

~~~powershell
$env:PYTHONPATH = Join-Path (Get-Location).Path '.venv/cache/visualizacion'
$python = '../Proyecto2/.venv/Scripts/python.exe'
& $python casos/semana4/ver_3d.py resultados/e11/diferencial.vti
~~~

Para guardar una comprobación del corte sin abrir ventana, agregar
`--captura resultados/e11/corte.png`. Para guardar una corrida alternativa,
usar `ejecutar.py e12 --lado 0.25 --salida resultados/e12_malla025`.
El resumen identifica commit, modificaciones locales de código, parámetros
efectivos, plan de vertidas y hashes de entradas.

[Corte guardado](../../resultados/e11/corte.png) ·
[Curvas de la corrida](../../resultados/e11/temperaturas.png)

Para Canvas se declara el repositorio y el SHA del commit que contiene el
snapshot, el código y la evidencia de la demo.


## Visualizador HTML con resultados Python

El ejecutor genera también resultados/e11/visualizador.html y
resultados/e12/visualizador.html. Cada archivo es autónomo y se puede abrir con
doble clic, sin conexión ni servidor. Reutiliza la interfaz y el renderizador
del laboratorio E07/E08.

Python resuelve la física y exporta campos temporales, diagnósticos por paso y
estados de máximos. El HTML permite reproducción, cortes XY/XZ/YZ, clipping por
eje, consulta de celdas, visibilidad por vertida y colores de bordes según suelo,
aire y capas. Incluye clima, retiros, curvas de núcleo/S25, diferencial y balance.

El intervalo se configura con --intervalo-html 1 en horas. Se guarda el primer
paso calculado que alcanza cada intervalo, además de eventos de construcción y
el final. La exportación observa la corrida sin cambiar su paso. Los extremos
se calculan en todos los pasos. Los colores entre campos se interpolan solo
para reproducción y respetan las activaciones.

Los botones de máximos abren campos guardados con su fase previa o posterior
al evento. La tabla por vertida distingue el máximo actual de centros y el máximo
de toda la corrida, que incluye caras. La marca roja corresponde a la sonda
interior. La azul aparece al seleccionar el máximo diferencial y corresponde
al punto S25 de ese estado.

Para cambiar parámetros se descarga el JSON desde Modelo y supuestos y se
ejecuta otra corrida en Python. La exportación VTI sigue disponible para E11.

~~~powershell
& $python -X utf8 -B casos/semana4/ejecutar.py e12 --intervalo-html 1
Start-Process 'resultados/e12/visualizador.html'
~~~


### Selector de resolución

La ejecución normal genera corridas Python de 0,50 y 0,25 m y las reúne en el
HTML principal. El selector cambia los campos, diagnósticos y tablas a la
corrida correspondiente. La opción de 1 m permite explorar geometría y
volúmenes. Esa malla pierde V02 y se presenta sin resultados térmicos.

La malla de 0,50 m conserva la salida visual horaria. Para limitar el tamaño del
archivo combinado, la corrida alternativa de 0,25 m guarda campos visuales cada
cuatro horas y en los eventos de construcción. Su solver mantiene el mismo paso
y calcula diagnósticos y extremos en cada paso. La metadata de cada malla
identifica el intervalo utilizado.

Una ejecución con --lado 0.25 genera solamente esa resolución y permite elegir
otro intervalo mediante --intervalo-html. Los VTI de la malla alternativa
se guardan bajo resultados/e11/malla_025 o resultados/e12/malla_025.

Las pestañas son enlaces de sección. Al cambiar de pestaña se ocultan los
resúmenes generales para mostrar directamente el contenido seleccionado.


### Lectura de resultados y presentación

La ficha de clima separa el origen de los datos, el momento de descarga, el
período meteorológico usado y el calendario del escenario. Los horarios se
presentan en hora de Chile continental. La tabla de bordes identifica Robin
convectiva, Robin con capas, la condición conductiva equivalente del suelo
y la continuidad térmica de las interfaces.

Los extremos localizan los estados más exigentes de toda la corrida y permiten
revisar los criterios de 70 °C y 20 K. Las explicaciones de cada gráfico se
limitan a dos líneas y sus leyendas se presentan fuera del área de trazado.
Las ecuaciones se renderizan con MathML nativo, disponible sin conexión.

El gráfico de generación volumétrica usa la fuente en la sonda interior,
obtenida de los diagnósticos de Python. La casilla de comparación agrega un
pulso cosenoidal de referencia con duración de 12 h y pico igual a la fuente
inicial de la corrida. Esa comparación es didáctica. Las corridas existentes
conservan su fuente de hidratación exponencial.

Datos de la corrida explica la función de cada entrada y agrupa los
identificadores de integridad en un detalle desplegable. El JSON descargable
contiene los parámetros efectivos; el identificador SHA-256 corresponde al
archivo original de parámetros usado al calcular.
