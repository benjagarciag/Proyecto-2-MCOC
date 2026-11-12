# E11 — Weather pipeline y visualización 3D

Avance para el laboratorio del 12 de noviembre de 2026. La referencia usa 48 h
del pronóstico GFS archivado para El Rosal, desde el 10 de noviembre de 2026
a las 17 h de Chile. En Canvas se declara repositorio y SHA evaluado.

## Abrir los resultados

- [Visualizador E11](../../resultados/e11/visualizador.html).
- [Visualizador E12](../../resultados/e12/visualizador.html).
- [Reporte determinista de E12](../../Reportes/Reporte_E12.md).

Descarga el repositorio y abre el HTML con doble clic en Chrome o Edge.
Cada archivo incorpora sus datos y funciona sin conexión. Recarga con Ctrl+F5
después de regenerarlo.

| Actividad | Objetivo | Caso implementado |
| --- | --- | --- |
| E10 | Explicar bordes, suelo, capas y trazabilidad | Demo oral y cliente meteorológico |
| E11 | Demostrar clima conectado al solver e inspección 3D | 48 h con GFS, HTML y VTI |
| E12 | Evaluar el plan durante 14 días | 336 h con ERA5 histórico y Markdown |

## Recorrido de la demo

1. Abrir el [snapshot GFS](../../datos/clima/forecasts/20261110T190042897941Z_44b1a950.json).
   Mostrar fuente, modelo, coordenadas, unidades y descarga del 10 de noviembre
   de 2026 a las 19:00:42 UTC, junto con la respuesta horaria.
2. Abrir Resultados y entorno en el HTML. La ficha separa los datos meteorológicos
   utilizados del calendario de la simulación y muestra hora de Chile.
3. Mostrar cómo el aire horario alimenta las condiciones de borde.
   [El solver](../../desarrollo/mcplan/termica_fundacion.py) interpola la serie.
   El coeficiente convectivo h permanece fijo en 5 W/(m²·K).
4. Ejecutar la corrida corta si el ayudante lo solicita. Con 0,50 m tiene
   192 pasos y alcanza 50,67 °C a las 48 h.
5. En Modelo y cortes, mover el slice XY/XZ/YZ o el clipping y consultar una celda.
   La marca roja es la sonda interior. Al abrir el máximo diferencial aparece
   la marca azul del punto S25.
6. Mostrar los VTI de esa misma corrida y abrir uno con PyVista para la evidencia
   VTK/PyVista.

Viento y radiación se conservan en el snapshot. El cálculo integrado utiliza
temperatura del aire. La demo E10 incluye un ejemplo separado de balance solar.

## Reproducir

En VS Code, **Run Python File** sobre `casos/semana4/ejecutar.py` pregunta
el caso (E11/E12) y la malla (0,50 m, 0,25 m o ambas). Al terminar, actualiza
los resultados del caso elegido; recargar el HTML con Ctrl+F5.
Una sola malla genera un HTML con esa resolución térmica; ambas reúne las dos.

Desde la raíz, con un entorno Python 3.12 preparado y activado,

~~~powershell
python -m pip install -r requirements.txt -r casos/semana4/requirements-vista.txt
python -X utf8 -B casos/semana4/ejecutar.py e11
python -X utf8 -B casos/semana4/ejecutar.py e12
~~~

En esta copia local de Windows se puede reutilizar el entorno existente,

~~~powershell
$python = '../Proyecto2/.venv/Scripts/python.exe'
$env:PYTHONPATH = Join-Path (Get-Location).Path '.venv/cache/visualizacion'
& $python -X utf8 -B casos/semana4/ejecutar.py e11
~~~

La ejecución normal genera corridas independientes de 0,50 y 0,25 m y las reúne
en el HTML principal. El selector cambia los campos, diagnósticos y tablas a
la corrida elegida. La opción de 1 m sirve para geometría y volúmenes y queda
sin resultados térmicos porque pierde V02.

La malla de 0,50 m guarda campos visuales cada hora y la alternativa de 0,25 m
cada cuatro horas, además de eventos. Los extremos se evalúan en cada paso.
Entre campos se interpolan los colores para reproducción.

Para una sola resolución o un intervalo de salida diferente,

~~~powershell
python -X utf8 -B casos/semana4/ejecutar.py e12 --lado 0.25 --intervalo-html 1 --salida resultados/e12_malla025
python -X utf8 -B casos/semana4/ejecutar.py e12 --paso-max 450 --sin-exportar
~~~

La opción --sin-exportar imprime el resumen sin modificar resultados.

## Archivos 3D y PyVista

Con **Run Python File** sobre `casos/semana4/ver_3d.py`, elegir en la terminal
primero el caso, luego la malla y finalmente el resultado. El visor ofrece
solo archivos existentes y no recalcula la física. Ambos scripts reconocen
automáticamente las dependencias locales de `.venv/cache/visualizacion`
si esa carpeta existe.

Cada corrida exporta pico.vti, diferencial.vti y final.vti. Contienen temperatura,
ID de vertida, máscara activa, identificación de superficie y S25 reconstruida.
La malla alternativa se guarda en la subcarpeta malla_025.

~~~powershell
python -X utf8 -B casos/semana4/ver_3d.py resultados/e11/diferencial.vti
python -X utf8 -B casos/semana4/ver_3d.py resultados/e11/diferencial.vti --modo recorte
~~~

Para una captura fija se agrega --captura resultados/e11/corte.png.
En ParaView se puede seleccionar activo mediante Threshold y aplicar Slice o Clip.

## Leer el HTML

- Los extremos localizan los estados más exigentes para evaluar 70 °C y 20 K.
- Los bordes identifican Robin convectiva, Robin con capas, la condición
  conductiva equivalente del suelo y la continuidad térmica de las interfaces.
- La tabla de capas muestra presencia y resistencia activa según la edad de cada vertida.
- Las curvas muestran temperaturas, entorno, diferencial, generación, tasas y potencias.
  Cada gráfico tiene una explicación breve y una leyenda independiente.
- El cosenoidal es una referencia de 12 h con pico igual a la fuente inicial.
  La corrida conserva su hidratación exponencial por edad.
- Modelo y supuestos presenta ecuaciones MathML y trazabilidad. El JSON descargable
  contiene los parámetros efectivos.

Cambiar parámetros físicos requiere descargar el JSON y ejecutar otra corrida
en Python. Los controles del HTML recorren los resultados guardados.

## Hipótesis y comprobaciones

Suelo, capas, retiros y propiedades son supuestos docentes. S25 se reconstruye
a 25 mm de las caras de una malla escalonada. E12 usa ERA5 de 2025 asignado por
hora relativa a una fecha hipotética de 2026.

La batería registrada tiene 554 pruebas Python aprobadas. Las pruebas Node
verifican campos, activaciones, gráficos, cortes, clipping y navegación con un
DOM real. Se revisó visualmente la presentación en el navegador integrado.

~~~powershell
node desarrollo/tests/test_semana4_html.cjs resultados/e11/visualizador.html
node desarrollo/tests/test_semana4_dom.cjs resultados/e11/visualizador.html
~~~

La regresión DOM requiere jsdom como dependencia de pruebas. Se puede instalar
con npm install --no-save --package-lock=false --prefix .venv/cache/html-dom jsdom.
El HTML autónomo se abre sin Node ni jsdom.

Para Canvas se declara el SHA del commit con el mensaje
Entrega E11. Identificar su SHA completo con `git log -1 --format=%H --grep="^Entrega E11$"`.
Los resúmenes conservan la procedencia real de cada corrida: commit base,
modificaciones locales al ejecutar y hashes de entradas. El commit evaluado
incluye los archivos guardados, aunque su cálculo sea anterior a ese commit.
