# Caso 1D: difusión térmica

Esta carpeta contiene el caso ejecutable 1D y sus parámetros.

Para abrir directamente los ejemplos de Dirichlet, Neumann, Robin y calor
interno, entrar en [codigos/](codigos/README.md).

El caso base usa una barra de 1 m, interior a 20 °C, extremos a 0 y 10 °C,
alpha = 10⁻⁴ m²/s, 101 nodos y 4500 s. El caso sinusoidal de la guía se usa
por separado para verificación exacta. La física y las diferencias están en
[la documentación del caso 1D](../../documentacion/caso_1d.md).

## Archivos

- [codigos/](codigos/README.md): los cuatro scripts del caso 1D y cómo ejecutarlos en VS Code.
- [parametros.json](parametros.json): entradas del caso base del video.
- [verificacion_seno.json](verificacion_seno.json): entradas de la guía §7 para verificar.
- [ejecutar.py](ejecutar.py): carga las entradas, llama al solver y guarda resultados.
- [Notebook explicativo](../../documentacion/explicacion_solver_1d.ipynb): física y bloques de los cuatro scripts de clase, con resultados paso a paso.

## Ejecutar desde la raíz

```powershell
.\.venv\Scripts\python.exe casos/1d/ejecutar.py
.\.venv\Scripts\python.exe casos/1d/ejecutar.py --caso robin
.\.venv\Scripts\python.exe casos/1d/ejecutar.py --intervalos 200
.\.venv\Scripts\python.exe casos/1d/ejecutar.py --parametros casos/1d/verificacion_seno.json
```

Sin opciones, se ejecutan los cuatro casos: Dirichlet, Neumann, Robin y calor
interno. Para uno solo, usar `--caso dirichlet`, `--caso neumann`, `--caso robin`
o `--caso calor_interno`. `--caso todos` también ejecuta los cuatro.
Sin modificaciones de parámetros se ejecutan directamente los archivos de
`codigos/` y se guardan exactamente las figuras que muestran al abrirlos.
Al usar JSON o modificar malla/paso/tiempo, se utiliza el ejecutor parametrizable
y su gráfico de perfiles.
Si se especifica `--parametros` sin `--caso`, se ejecuta solo Dirichlet con ese JSON.
Los ejemplos adicionales usan las entradas de los scripts de clase; las opciones
`--intervalos`, `--dt` y `--tiempo-final` permiten modificarlas.

Se pueden editar los parámetros en JSON o sobrescribir `--intervalos`, `--dt`
y `--tiempo-final` en la línea de comandos. `--parametros <archivo.json>` permite
usar otro archivo. `--salida <carpeta>` permite indicar dónde guardar;
si la carpeta ya existe, se actualizan los archivos de resultados allí.

Con `paso_tiempo_s=null`, el paso se calcula desde r objetivo y la malla; después
se ajusta uniformemente al tiempo final, como el profesor. Con `--dt` se propone
un paso fijo, que se valida antes del ajuste. Para la malla base el límite es
0,5 s; para 200 intervalos, 0,125 s. `temperatura_inicial_C` se usa para el perfil
uniforme; el perfil `seno` usa la recta estacionaria más la amplitud sinusoidal.

El solver conserva el historial completo. Utilizar primero las resoluciones
pequeñas del ejemplo; aumentar mucho nodos y tiempos aumenta el uso de memoria.

## Resultados al ejecutar

Las salidas se guardan en carpetas fijas dentro de `resultados/1d/`:
`base/`, `neumann/`, `robin/` y `calor_interno/`. La verificación sinusoidal usa
`verificacion_seno/`. Cada ejecución actualiza los
mismos archivos; no se crean carpetas con fecha ni se acumulan corridas.
Se genera únicamente `perfiles_temperatura.png` en la carpeta fija de cada caso.
Con las entradas de clase, cada imagen es la misma figura del script correspondiente:
Dirichlet, Neumann y calor interno muestran perfiles; Robin muestra su figura
completa con historia temporal y perfiles en dos paneles.

Los parámetros de entrada permanecen en esta carpeta de casos; no se copian
a resultados. El historial completo se usa en memoria para calcular los gráficos.
Para los casos adicionales se conservan solo los perfiles e historias muestreados.
En Robin los perfiles cubren las primeras 10 h y la historia abarca las 48 h.
`--salida` señala la carpeta del caso seleccionado; con `todos`, señala la carpeta
madre y se reutiliza una subcarpeta por caso.

En calor interno se conserva el aporte `r*Q0` con `Q0=5/6000`: la tasa efectiva
es `alpha*Q0/dx**2`. Modificar la malla con Q0 fijo también modifica esa tasa.

Los archivos de ejecuciones anteriores fueron eliminados. Las carpetas y archivos
se generan cuando ejecutes el caso. Valores de referencia de las comprobaciones previas:

| Caso | Referencia |
| --- | --- |
| Base del video | 10000 pasos, r = 0,45, centro final ≈ 5,22483 °C. |
| Seno de la guía | Error máximo final ≈ 0,00235449 K. |

La distancia a la recta estacionaria del caso base no es error transiente.
La solución exacta solo se utiliza para el caso sinusoidal, que tiene esa referencia.

Evaluación que lo utiliza: [E01](../../entregas/E01/README.md).
