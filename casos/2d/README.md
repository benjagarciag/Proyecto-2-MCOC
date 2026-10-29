# Caso 2D original restaurado

`Ejecutar_2D.py` vuelve a los datos anteriores a los ejemplos de la barra:

- Placa 1 × 1 m, espesor uniforme 1 m y malla 30 × 30.
- Interior inicial `20 + 50 sin(pi x/Lx) sin(pi y/Ly)` °C.
- Cuatro caras a 20 °C, sin fuente interna.
- k=2 W/(m K), rho=2400 kg/m³, cp=900 J/(kg K), valores didácticos.
- Horizonte 24 h, dx=dy=1/30 m, paso automático de 180 s y límite de 200 s.
- Figura con inicio, final, error analítico y evolución central.

```powershell
.\.venv\Scripts\python.exe -B casos/2d/Ejecutar_2D.py
```

Actualiza únicamente `resultados/2d/base/perfiles_temperatura.png`.
La restauración del código no regenera los resultados: las imágenes y películas
existentes siguen correspondiendo a los ejemplos ejecutados anteriormente.
Los ejemplos posteriores se conservan por separado:

- `Barra_Enfriamiento_2D.py`: barra 4 × 2 m y contorno a 10 °C.
- `Demo_Inestabilidad_2D.py`: comparación de pasos estables e inestables.
- `Fuente_Temporal_2D.py`: generación de calor dependiente del tiempo.

## Barra 2D: enfriamiento de 4 × 2 m

Desde la raíz:

```powershell
.\.venv\Scripts\python.exe -B casos/2d/Barra_Enfriamiento_2D.py
```

El origen está en el centro: x entre −2 y 2 m, y entre −1 y 1 m.
El interior comienza uniformemente a 20 °C; para t > 0 las cuatro caras
se mantienen a 10 °C (Dirichlet). En el contorno hay un cambio instantáneo
respecto del estado previo a enfriar. No hay fuente interna ni intercambio
en la dirección del espesor. El equilibrio es uniforme a 10 °C.

Se conservan las propiedades didácticas del ejemplo anterior:
k=2 W/(m K), rho=2400 kg/m³, cp=900 J/(kg K), alpha=9.259259e−7 m²/s.
No son propiedades calibradas para la fundación. El tiempo de enfriamiento
depende de ellas; no se extrapola directamente a otro material.

La malla actual tiene 40 × 20 celdas: dx=dy=0,10 m. El paso temporal
explícito es 300 s (5 minutos), por debajo del límite de 1800 s de esta malla.
Al ser una malla par, se usa interpolación bilineal para aproximar la temperatura
central. El solver sigue en `desarrollo/mcplan/difusion_2d.py`, sin cambios.

## Tiempo suficiente para estabilizarse

El equilibrio exacto se alcanza asintóticamente. Se define estabilización práctica
como `max_celdas |T − 10 °C| <= 0.1 K`, evaluada en cada paso.
Se reporta el primer paso que cumple; la precisión temporal de esa detección
es el paso utilizado. No se confunde este criterio con error de discretización.
La temperatura máxima global es 20 °C al inicio y disminuye hacia 10 °C.

El horizonte se estima usando el primer modo de Fourier con un margen del 20 %;
después se comprueba numéricamente que alcanzó el criterio.
El paso respeta el límite de estabilidad, incluidas las esquinas, y se reduce
para que una hora contenga un número entero de pasos. Las muestras de la
película están en horas exactas, sin interpolación temporal. La última es
la primera hora entera que alcanza o supera la estabilización.

Resultado anterior, con 81 × 41 celdas: dt=360 s, estabilización a 495,0 h (20,625 días),
Tmáx final=10,099900 °C. El criterio se detecta entre 494,9 y 495,0 h.

## Salidas

Se actualizan los mismos archivos de `resultados/2d/base/`:

- `perfiles_temperatura.png`: inicio, final, máxima espacial y curva central.
- `temperatura_centro.png`: gráfico T(0,0,t) vs. tiempo en horas.
- `temperatura_punto_1_1.png`: T(1,1,t) en el borde superior, fijo a 10 °C
  para t > 0; se indica por separado el estado previo a imponer el contorno.
- `evolucion_temperatura.mp4`: película, un cuadro por hora desde t=0.

La película mantiene escala fija de 10 a 20 °C y proporción geométrica 2:1.
Se reproduce a 10 cuadros/s: cada segundo de video representa 10 horas físicas.
Para MP4 se necesita FFmpeg en PATH. Si no está disponible, se genera
`evolucion_temperatura.gif` con Pillow, incluido en los requisitos.
No se exportan CSV, historias numéricas ni nuevas carpetas por ejecución.

Las entradas están al inicio del script. Opciones:

```powershell
.\.venv\Scripts\python.exe -B casos/2d/Barra_Enfriamiento_2D.py --celdas 121 --dt 100 --tolerancia 0.05
```

`--celdas` fija Nx, y Ny es aproximadamente la mitad. Un paso propuesto
inestable se rechaza antes de ajustarlo. Las pruebas sinusoidales anteriores
se conservan en `desarrollo/tests/test_difusion_2d.py`; su solución exacta
de un solo modo no corresponde a esta condición inicial uniforme.
La explicación histórica está en `documentacion/e04_2d.md`.

## Demostración de pasos mayores que la cota de estabilidad

```powershell
.\.venv\Scripts\python.exe -B casos/2d/Demo_Inestabilidad_2D.py
```

Compara pasos de 300, 1800, 2000 y 3600 s, con dx=dy=0,10 m,
durante aproximadamente 24 h. Guarda `demostracion_inestabilidad.png`
en la misma carpeta de resultados. Solo esta demo omite deliberadamente
el rechazo de pasos; el solver y los parámetros principales se conservan.
El cálculo estable de la demo se comprueba contra el solver protegido.

1800 s es una cota suficiente conservadora: excederla ligeramente no obliga
a divergir. En esta ejecución, 2000 s no muestra crecimiento descontrolado;
3600 s produce oscilaciones y temperaturas artificiales de aproximadamente
−31044 a 34458 °C a las 24 h. El mapa inestable usa su propia escala,
indicada como desviación respecto a 10 °C. El punto junto a la esquina es
el centro de la celda interior (−1,95, −0,95) m; la cara física sigue a 10 °C.

También genera `movie_inestabilidad.mp4` (GIF si no hay FFmpeg): compara
300 s y 3600 s en 25 cuadros horarios, desde 0 hasta 24 h, a 2 cuadros/s.
Izquierda: temperatura de 10 a 20 °C. Derecha: desviación T−10 °C con
escala logarítmica simétrica fija para ver el inicio y la divergencia.
Las escalas de los paneles son distintas y permanecen fijas durante el video.

## Generación temporal: pulso de 12 h y simulación de 48 h

```powershell
.\.venv\Scripts\python.exe -B casos/2d/Fuente_Temporal_2D.py
```

Ejemplo solicitado con inicio y contorno a 20 °C y fuente espacialmente uniforme:
`rho cp dT/dt = k ∇²T + Q(t)`. Se interpreta ∇² como el laplaciano,
no como su aplicación repetida. Q está en W/m³. Para duración D:
`Q(t)=Qmax/2 (1−cos(2 pi t/D))` en 0<=t<D, y cero después.
Se usa D para distinguir duración del pulso y temperatura T.

Barra 4 × 2 m, propiedades didácticas anteriores, malla 40 × 20,
dx=dy=0,10 m, dt=300 s, horizonte 48 h. El módulo
`desarrollo/mcplan/fuente_temporal_2d.py` reutiliza el balance de conducción,
añadiendo `integral(Q dt)/(rho cp)` en cada paso. La integral temporal
de la fuente es analítica; la conducción sigue siendo Euler explícito.
Se conserva la protección de estabilidad. No es hidratación calibrada.

Por linealidad, se resuelve primero para Qmax=1 W/m³ y se escala la subida
respecto a 20 °C: `Qcrit=50/max(Tcentro_unidad−20)`.
El umbral significa alcanzar 70 °C en algún instante de las 48 h,
no necesariamente al terminar. La temperatura central se aproxima con
las cuatro celdas que rodean el origen, aprovechando la simetría.

| Duración cosenoidal | Qmax umbral [W/m³] | Hora del pico central |
| --- | ---: | ---: |
| 12 h | 5000,366742 | 11,9167 |
| 24 h | 2506,720004 | 23,2500 |
| 48 h | 1284,258767 | 44,0833 |

Para el principal se redondea hacia arriba a 5001 W/m³: pico 70,006332 °C
y 64,026879 °C a las 48 h. Refinando a 80 × 40 y dt=75 s,
el umbral es 5000,180237 W/m³ (cambio de 0,0037 %).
Es una verificación de sensibilidad conjunta, no una prueba de órdenes independientes.

Se actualizan dos figuras en `resultados/2d/fuente_temporal/`:

- `pulsos_y_temperatura.png`: Q(t) y temperatura central, variando amplitud
  para el pulso de 12 h y duración (12/24/48 h) a igual Qmax.
- `formas_y_campos.png`: coseno, triángulo y fuente constante Qmax/2,
  con duración de 48 h e igual energía Qmax D/2; campos en el pico del
  pulso principal de 12 h para Qmax=5001 y 6001,2 W/m³.

Comparar duraciones al mismo Qmax cambia la energía total; comparar formas
se hace a igual energía para distinguir el efecto del reparto temporal.
Las entradas se editan al inicio de `Fuente_Temporal_2D.py`.
