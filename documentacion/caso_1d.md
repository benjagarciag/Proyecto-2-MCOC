# Caso base 1D del profesor y verificación

## Qué caso usamos

Desde el 20 de octubre usamos como caso base el script del video:
[01_1d_dirichlet_verification.py](../casos/1d/codigos/01_1d_dirichlet_verification.py).
Se conserva sin modificar. Las entradas están en
[casos/1d/parametros.json](../casos/1d/parametros.json).

| Magnitud | Valor del script |
| --- | --- |
| Longitud $L$ | 1 m |
| Difusividad $\alpha$ | $10^{-4}$ m²/s |
| Temperatura interior inicial | 20 °C |
| Temperatura izquierda | 0 °C |
| Temperatura derecha | 10 °C |
| Amplitud sinusoidal $A$ | 0 K (el código dice `0*50.0`) |
| Nodos `nx` | 101: 100 intervalos |
| Paso espacial | 0,01 m |
| $r$ objetivo | 0,45 |
| Tiempo final | 4500 s = 75 min |
| Paso temporal propuesto y efectivo | 0,45 s |
| Pasos temporales | 10000 |
| Perfiles guardados en CSV | 20, como el script |

El script ingresa $\alpha$ directamente. No proporciona $k$, $\rho$ ni $c_p$
para este ejemplo; no les asignamos valores artificiales. En general
$\alpha=k/(\rho c_p)$. Este benchmark no es una calibración de hormigón.

## Física, condición inicial y bordes

Conducción en una sola dirección, material homogéneo, propiedades constantes,
sin fuente interna. Las caras laterales están aisladas; los extremos intercambian
calor con contactos ideales que mantienen su temperatura.

La ley de Fourier y el balance de energía dan:

$$
q_x''=-k\frac{\partial T}{\partial x},\qquad
\rho c_p\frac{\partial T}{\partial t}
=k\frac{\partial^2T}{\partial x^2},\qquad
\frac{\partial T}{\partial t}=\alpha\frac{\partial^2T}{\partial x^2}.
$$

La condición inicial interior es:

$$T(x,0)=20\ ^\circ\mathrm C,\qquad 0<x<L.$$

Los bordes de Dirichlet son:

$$T(0,t)=0\ ^\circ\mathrm C,\qquad T(L,t)=10\ ^\circ\mathrm C.$$

Desde $t=0$ se fijan ambos extremos. El perfil inicial tiene un salto respecto
del valor interior en los bordes; esa es la configuración del script del video.
No debe exigirse continuidad entre el perfil interior inicial y los contactos
impuestos en ese instante. Después del inicio el calor sale por los extremos.
Los extremos distintos producen una evolución asimétrica.

## Esquema numérico

Malla uniforme $x_i=i\Delta x$, con $N+1$ nodos y $\Delta x=L/N$.
Usamos FTCS: Euler hacia adelante en tiempo y diferencias centradas en espacio:

$$
T_i^{n+1}=T_i^n+r(T_{i+1}^n-2T_i^n+T_{i-1}^n),
\qquad r=\frac{\alpha\Delta t}{\Delta x^2}.
$$

Cada actualización interior puede obtenerse del balance de un volumen
$V=A_s\Delta x$ con conductancia $G=kA_s/\Delta x$. Todos los vecinos se
toman del estado anterior, sin sobrescribirlo. Los bordes se mantienen fijos.

Para este esquema de difusión pura 1D:

$$r\leq\frac12,\qquad\Delta t_{\max}=\frac{\Delta x^2}{2\alpha}.$$

Como el profesor, calculamos el paso propuesto desde $r_{objetivo}=0,45$ y luego:

$$
n_{pasos}=\left\lceil\frac{t_f}{\Delta t_{propuesto}}\right\rceil,
\qquad \Delta t=\frac{t_f}{n_{pasos}}.
$$

Así todos los pasos tienen la misma duración y se llega al tiempo final.
`paso_tiempo_s` permite proponer un paso explícito; un paso inestable se rechaza
antes del ajuste. Con `null` se calcula automáticamente desde el objetivo.
Reducir $\Delta x$ a la mitad reduce el paso máximo a la cuarta parte.

## Qué resultado esperamos del video

En equilibrio, $\partial^2T/\partial x^2=0$, por lo que:

$$T_{est}(x)=T_{izq}+(T_{der}-T_{izq})\frac{x}{L}=10\frac{x}{L}.$$

El centro tenderá a 5 °C. A los 4500 s obtenemos aproximadamente **5,22483 °C**;
todavía no se alcanza exactamente el equilibrio.
La distancia a esta recta mide cuánto falta para equilibrarse, **no el error
numérico transiente**. Los gráficos y métricas la identifican de esa forma.

## Verificación separada: el seno de la guía

La [guía extensa, §7](../Enunciados%20e%20Instrucciones/Guias/DIFUSION_DE_CALOR_1D_2D_3D.md)
usa otro ejemplo: extremos a 20 °C, amplitud 50 K, mismo $L$, $\alpha$ y 101
nodos, pero tiempo final de 1500 s. Sus entradas están en
[verificacion_seno.json](../casos/1d/verificacion_seno.json).

$$T(x,0)=20+50\sin(\pi x/L),\qquad T(0,t)=T(L,t)=20.$$

Su solución exacta es:

$$T_{exacta}(x,t)=20+50\sin(\pi x/L)e^{-\alpha(\pi/L)^2t}.$$

Evaluamos esta expresión en los mismos nodos y tiempos del cálculo numérico:

$$E_\infty(t)=\max_i|T_i^{num}(t)-T_{exacta}(x_i,t)|.$$

La solución sinusoidal no corresponde al caso uniforme del video. El propio
script del video tiene comentadas las comparaciones exactas, aunque su título y
su leyenda conservan referencias a otra versión. La adaptación sigue los valores
y operaciones activos, y corrige los rótulos en nuestros gráficos.

## Evidencia y límites

- [Solver propio](../desarrollo/mcplan/difusion_1d.py): mismo FTCS, con IO separado.
- [Tests](../desarrollo/tests/test_difusion_1d.py): reproducción de los 20 perfiles del video
  con tolerancia $10^{-12}$ °C, solución exacta sinusoidal, estados estacionarios,
  actualización manual, estabilidad, ajuste de tiempos e inputs inválidos.
- [Notebook ejecutado](explicacion_solver_1d.ipynb): explicación y experimentos.
- [Caso ejecutable y resultados](../casos/1d/README.md).

El refinamiento conjunto del caso sinusoidal mantiene $r$ casi constante
(puede disminuir por el ajuste temporal) y comprueba el comportamiento esperado
$O(\Delta t)+O(\Delta x^2)$. El estudio independiente de espacio y tiempo sigue
pendiente. Comparar con el script del profesor comprueba reproducción, mientras
que la solución exacta aporta una verificación independiente.

Neumann, Robin y calor interno también se ejecutan desde `ejecutar.py`, mediante
[ejemplos_1d.py](../desarrollo/mcplan/ejemplos_1d.py). Los bloques de Dirichlet
y la verificación exacta siguen en `difusion_1d.py`. No hay hidratación ni simulación
de la fundación real; este ejemplo no evalúa los límites docentes de 70 y 20 °C.

Los archivos de resultados anteriores fueron eliminados por petición del usuario.
Las siguientes ejecuciones generan los resultados en las carpetas fijas del caso.
