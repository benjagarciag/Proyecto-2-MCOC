# E04: generación térmica volumétrica en 2D y 3D

Etapa autorizada del 27 de octubre de 2026, exclusivamente en `E04_pruebas_2d`.
Complementa `e04_bordes.md`. Se extendió de forma compatible el solver común
con una fuente opcional que vale cero por defecto. No se reemplazaron los
solvers 1D, 2D o 3D ni los bordes. No se modificaron el proyecto original o
el BIM, ni hubo instalaciones, commits, merges, PR o publicaciones.

Consulta remota: main=4c4a1d3fe21ca5cb3b92d74de5d818f9a4991aa7 y
luis-entrega-fundacion=4e67a71a8e437df09867d8281e6a46d759edafc9, sin integrar.

## Significado físico y unidades

Una fuente volumétrica describe calor producido **dentro del material** por
unidad de tiempo y volumen. En hormigón masivo, el ejemplo físico es el calor
liberado durante la hidratación del cemento. Aquí se verifica una generación
constante prescrita; no se ha implementado su cinética, dependencia de edad
o temperatura ni calibración experimental. No interpretar los valores
didácticos como predicción de nuestra fundación.

| Unidad | Significado | Cómo convertir a potencia de una celda |
|---|---|---|
| W = J/s | Potencia total | Ya es energía por segundo |
| W/m² | Flujo superficial | Multiplicar por área de cara A [m²] |
| W/m³ | Generación volumétrica q''' | Multiplicar por volumen V [m³] |

Si q'''=600 W/m³ y una celda ocupa 0.001 m³, genera 0.6 W. En 0.01 m³
genera 6 W. Ambas tienen la misma tasa de calentamiento adiabático porque su
capacidad térmica también crece proporcionalmente con el volumen.

Recibir calor desde una superficie es un término de borde, localizado en
caras exteriores. Generarlo internamente es un término por volumen; puede
estar presente incluso si todas las caras son adiabáticas. No confundir esta
fuente en W/m³ con el parámetro Q0 de los scripts 1D docentes: sus escalas y
actualizaciones se explican por separado y no se modificaron.

## Balance implementado

    C_i = rho * cp * V_i                              [J/K]
    P_generada_i = q'''_i * V_i                        [W]
    C_i dT_i/dt = sum_j G_ij(T_j-T_i) + P_borde_i + P_generada_i

    T_i^(n+1) = T_i^n + dt/C_i *
                [sum_j G_ij(T_j^n-T_i^n) + P_borde_i^n + q'''_i V_i]

Se usa Euler explícito: conducción y bordes emplean el estado anterior; la
fuente constante agrega potencia en el mismo balance. En 2D, V=dx*dy*espesor;
en 3D, V=dx*dy*dz. El material continúa homogéneo, con rho, cp y k constantes.
Aunque el balance general permite C_i distinto por celda, esta etapa NO
implementa dos materiales ni conductividades/capacidades heterogéneas.

Con fuente uniforme, temperatura inicial uniforme y aislamiento total, no hay
diferencias entre vecinos y no hay flujo exterior. Entonces:

    dT/dt = q'''/(rho*cp)
    T(t) = T0 + q'''*t/(rho*cp)

El volumen se cancela. Por eso no se debe sumar directamente q''' como si
fuera W por celda: eso haría depender el calentamiento del tamaño de la malla.
Con q'''=600, rho=2400 y cp=900, la tasa es 1 K/h; desde 20 °C, a las 24 h
se llega a 44 °C. El ejemplo 2D y el 3D reproducen esa solución.

## Fuente localizada y refinamiento

`fuente_desde_config` admite tipo `uniforme` y tipo `caja` con límites en metros.
Para una celda parcialmente dentro de la caja se calcula:

    q'''_i = q'''_activo * V_interseccion_i/V_celda
    sum_i(q'''_i V_celda) = q'''_activo * V_caja

Así, la potencia total no cambia al mover límites respecto de la malla o al
refinar. Las franjas de color intermedio del mapa de fuente son celdas
parcialmente activas, no otro material ni una intensidad física distinta en
la caja. La distribución se promedia porque el solver tiene un valor por celda.

En 2D la región ocupa todo el espesor. En 3D se limita también en z. Los ejemplos
localizados tienen volúmenes activos diferentes: 0.25 m³ en 2D y 0.125 m³ en
3D. Con 2000 W/m³ generan 500 W y 250 W, respectivamente. No comparar sus
temperaturas atribuyendo toda la diferencia a la dimensión del solver.

La API también acepta un escalar, arreglo de promedios por celda o función
espacial f(X,Y[,Z]). Las funciones arbitrarias se muestrean en los centros y
su integral puede tener error de cuadratura. Para regiones discontinuas usar
la caja integrada o proporcionar promedios exactos por celda. No se promete
independencia exacta de la potencia con una máscara arbitraria de centros.

## Conservación y estabilidad

Al sumar todas las celdas se cancelan las potencias interiores:

    E^(n+1)-E^n = dt * [P_exterior^n + P_generada_total]
    P_generada_total = sum_i(q'''_i V_i)

E se registra con referencia arbitraria 0 °C; importan sus diferencias.
Con aislamiento y fuente, la energía del cuerpo NO es constante: aumenta
exactamente según la generación. Conservación significa cerrar este balance.
Con Robin puede salir calor y aun así aumentar T si se genera más de lo que
se extrae. El estado estacionario requiere igualar generación y pérdidas.

La generación registrada es constante en el tiempo. Su energía acumulada es
P_generada_total*t. El calor exterior acumulado usa la misma regla explícita
del solver: dt*sum(P_exterior[:-1]), no incluye el último valor de potencia.

El límite suficiente de estabilidad continúa siendo:

    dt_max = min_i C_i/[sum_j G_ij + sum_caras H_cara]

Una fuente prescrita independiente de T no modifica los coeficientes que
multiplican las temperaturas, por lo que no agrega otra restricción lineal.
Esto no significa precisión ilimitada: refinar dt sigue siendo útil. Una
futura fuente dependiente de T o del tiempo requerirá analizar estabilidad
y/o resolución temporal otra vez. No extrapolar este criterio a cinética
de hidratación no implementada. Los bordes siguen aportando sus H como antes.

## Código: dónde explicar cada paso

- `desarrollo/mcplan/fuentes_volumetricas.py` (nuevo):
  `fuente_desde_config` lee tipo/valor/región y calcula promedios conservativos;
  `preparar_fuente_W_m3` comprueba forma, finitud y valores >=0 y copia el campo.
- `desarrollo/mcplan/difusion_bordes.py` (extendido):
  `resolver_2d_bordes` y `resolver_3d_bordes` aceptan el argumento opcional
  `fuente_W_m3=0`. En `_resolver`, `volumen_m3` se obtiene de C/(rho cp),
  `potencia_fuente = fuente*volumen_m3` convierte a W y la actualización suma
  esa potencia al balance ya existente. No hay otro bucle numérico duplicado.
  `ResultadoBordes` agrega `fuente_W_m3` y `potencia_generada_W` conservando los
  campos anteriores. `potencia_exterior_W` sigue midiendo SOLO fronteras.
- `desarrollo/tests/test_fuentes_volumetricas.py` (nuevo): verificaciones.
- `casos/fuentes/Ejecutar_Fuentes.py` y `README.md`: parámetros del ejemplo,
  ejecución y gráficos reproducibles. Los comandos anteriores no necesitan cambios.

Ejemplo de API:

```python
from mcplan.difusion_2d import Parametros2D
from mcplan.bordes_termicos import Neumann
from mcplan.difusion_bordes import resolver_2d_bordes

p = Parametros2D(tiempo_final_s=86400)
b = {cara: Neumann(0) for cara in ('x_min', 'x_max', 'y_min', 'y_max')}
r = resolver_2d_bordes(p, b, 20, fuente_W_m3=600)
```

Para 3D, Parametros3D, agregar z_min/z_max y resolver_3d_bordes. Una fuente
negativa se rechaza: esta API implementa generación no negativa, no un sumidero
volumétrico. El enfriamiento superficial se representa con los bordes existentes.

## Verificaciones ejecutadas

**207 pruebas aprobadas: 156 anteriores + 51 nuevas.**

1. Solución adiabática uniforme exacta en 2D y 3D, con 4, 8 y 16 celdas por eje.
2. Variación del espesor 2D y longitud z 3D: potencia proporcional al volumen,
   tasa de calentamiento independiente del tamaño de celda.
3. Balance por paso con fuente espacial 10+3x y Dirichlet/Neumann/Robin.
4. Fuente localizada en un solo paso con fracciones calculadas a mano.
5. Caja no alineada, mallas de 5, 9 y 16 celdas: misma potencia y balance global.
6. Solución exacta transiente con fuente uniforme y modo coseno adiabático:
   T=T0+q'''t/(rho cp)+A product(cos(pi x)) exp(-alpha*dim*pi²*t).
   Refinamiento 8→16→32: cocientes de errores >3 y error final <0.003 K en
   ambos solvers. Es refinamiento conjunto espacial/temporal, no órdenes
   independientes en dx y dt.
7. Perfil parabólico estacionario exacto de placa con fuente y Robin en x:
   T=Tinf+q'''L/(2h)+q'''x(L-x)/(2k), otras caras adiabáticas.
   El error de borde discreto disminuye aproximadamente como dx²; no se exige
   que el perfil continuo sea estacionario exacto en una malla finita.
8. Robin con pérdida exterior pero calentamiento neto por generación mayor.
9. Fuente cero, mismo límite de estabilidad, rechazo de paso excesivo, tiempo
   cero, copia independiente del arreglo y validación de entradas.

## Resultados de los ejemplos a 24 horas

Todos usan k=2 W/(m K), rho=2400 kg/m³, cp=900 J/(kg K), T0=20 °C,
lados 1 m y espesor 2D 1 m. Mallas 25×25 y 15³. El dt efectivo es
387.44395 s (máximo 432 s) en 2D y 720 s (máximo 800 s) en 3D.

| Caso | Media final 2D / 3D [°C] | Máxima final 2D / 3D [°C] |
|---|---|---|
| Uniforme adiabático, 600 W/m³ | 44 / 44 | 44 / 44 |
| Localizado adiabático, 2000 W/m³ activos | 40 / 30 | 59.54864348 / 49.85106891 |
| Uniforme + Robin, 600 W/m³ | 35.20494738 / 32.46407489 | 40.68103838 / 39.35380386 |

Robin usa h=10 W/(m² K), Tinf=20 °C en todas las caras consideradas. En 2D
las caras normales al espesor no intercambian; en 3D sí intercambian las seis.
Ambos generan 51.84 MJ. Salen 18.99731366 MJ en 2D y 24.91759824 MJ en 3D;
el cambio de energía almacenada es 32.84268634 y 26.92240176 MJ.
El mayor residuo acumulado del balance de los seis casos es 7.30e-7 J,
frente a energías del orden de decenas de millones de J (redondeo numérico).

Las tres figuras están en `resultados/fuentes/{uniforme,localizada,robin}/`;
cada una se llama `perfiles_temperatura.png`. Una fila por dimensión, columnas:
mapa de fuente, temperatura final, evolución térmica y balance. El mapa 3D es
un corte XY central, pero las medias/energías usan TODO el volumen. La escala
de temperatura es común a las dos filas dentro de una figura. Las curvas
térmicas resumen trece campos; la energía se registra cada paso.

## Ensayo oral sencillo

«La hidratación libera calor dentro del hormigón. Representamos una tasa de
generación en W/m³. Cada celda genera q''' por su volumen, en W. Esa potencia
se suma a lo que entra por conducción y por las fronteras. Dividimos por la
capacidad térmica y multiplicamos por dt para obtener el cambio de temperatura.
Si aislamos el cuerpo y generamos uniformemente, la temperatura sube linealmente.
Refinar la malla reparte la misma potencia entre más celdas y no cambia esa
tasa. Con Robin, parte del calor generado sale al ambiente; la diferencia queda
almacenada. Verificamos ambas contribuciones en el balance de energía».

Mostrar el caso uniforme y calcular a mano 1 K/h; después la caja localizada;
por último, señalar generación positiva, pérdida exterior negativa y suma neta
en el gráfico Robin. Abrir la línea `potencia_fuente = fuente*volumen_m3` y la
actualización explícita. Ejecutar pytest y explicar un test de independencia
de malla y uno de balance.

## Pendientes y punto de detención

La base didáctica tiene ahora difusión 2D/3D, tres tipos de borde y generación
constante verificada. Dos materiales y sus interfaces siguen pendientes y NO
se implementaron. Antes de E04 practicar esta explicación, cambios de dx/dt,
el método de Schmidt y las hipótesis de cada ejemplo. Confirmar con la pauta
el alcance oral frente a E05 (batería de verificación) y E06 (dossier + BIM).

El proyecto final además requiere cinética/calibración de hidratación, conexión
IFC→voxelización→solver, secuencia de vertidas, interacción con suelo, moldajes,
clima y validación geométrica/docente. No se implementaron en esta etapa ni
se afirma cumplimiento de criterios térmicos de obra. Publicar o integrar
exige autorización posterior. Detener aquí para revisión del usuario.
