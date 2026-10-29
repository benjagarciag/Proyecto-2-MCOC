# E05: práctica de la batería de verificación térmica

**Modo interactivo solicitado:** abrir el [visualizador unificado](../../Visualizadores/README.md)
para modificar parámetros, ejecutar personalmente cada test y reproducir la evolución.
La ventana abre sin calcular. Sus parámetros y verificaciones son compartidos con
`test_e05_visualizador.py`; la batería de variantes descrita abajo sigue disponible.

El enunciado pide ejecutar pruebas en vivo y explicar cambios de parámetros.
No requiere informe: se declara repositorio y SHA evaluado. Este documento
es una guía de estudio local, no una evidencia de haber aprobado la evaluación.

## Ejecutar y ver resultados numéricos

Desde la raíz del proyecto:

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q -s -p no:cacheprovider desarrollo/tests/test_e05_parametros.py
```

`-s` muestra los parámetros, errores y balances. Un punto indica un test
aprobado. Cada fila de `@pytest.mark.parametrize` es un caso independiente.
Editar esas tablas permite practicar sin modificar el solver ni sus ejemplos.
No se generan figuras ni archivos en resultados/.
Los materiales sintéticos de estos tests hacen que se ejecuten rápido;
no representan las propiedades del hormigón de la fundación.

Para un solo grupo, añadir al comando anterior uno de estos filtros:

| Grupo | Filtro | Variantes |
| --- | --- | ---: |
| Seno 1D | `-k test_e05_1d` | 3 |
| Seno 2D | `-k test_e05_2d` | 3 |
| Seno 3D | `-k test_e05_3d` | 3 |
| Energía adiabática | `-k test_e05_adiabatico` | 3 |
| Fuente uniforme | `-k test_e05_fuente` | 4 |
| Neumann | `-k test_e05_neumann` | 6 |
| Robin | `-k test_e05_robin` | 4 |
| Extra: paso rechazado | `-k test_e05_estabilidad` | 3 |

Total: 29 variantes de práctica. Las pruebas originales se conservan;
se ejecutaron además por separado los siete grupos del enunciado.

## 1. Solución 1D exacta

Referencia: `T=T0+A sin(pi x/L) exp[-alpha (pi/L)² t]`.
Se compara la temperatura numérica y exacta al final, en los mismos nodos.
Se exige `error_máximo/|A| < 0.002` para estas configuraciones.

- 40 intervalos: dx=0,025 m; dt≈2,809 s; error≈0,014701 K.
- 80 intervalos: dx=0,0125 m; dt≈0,703 s; error≈0,003679 K.
- También se cambia L a 2 m, alpha a 2e−4 m²/s y A a −30 K.

Pregunta: ¿por qué disminuye aproximadamente cuatro veces el error al refinar?
Se reducen dx y dt juntos, con dt proporcional a dx². Esto es convergencia
conjunta; no demuestra órdenes espacial y temporal independientes.
Una amplitud negativa representa un interior más frío que el borde.
Cambiar solo la geometría exige actualizar también el seno y su tasa de decaimiento.

## 2. Seno 2D

Referencia: `T=T0+A sin(pi x/Lx) sin(pi y/Ly) exp(-alpha lambda t)`;
`lambda=(pi/Lx)²+(pi/Ly)²`. Se evalúa en centros de celda.
Se exige `error_máximo/|A| < 0.005` en las variantes de práctica.

- Malla 12×10: error≈0,009474 K.
- Malla 24×20: error≈0,002392 K.
- Otra variante cambia dimensiones, conductividad y signo de A.

Pregunta: ¿qué hace aumentar k con rho y cp constantes?
Aumenta alpha=k/(rho cp), acelera el decaimiento del modo y reduce el paso
admisible. Las dimensiones intervienen en lambda y en la malla física.

## 3. Seno 3D

Se agrega `sin(pi z/Lz)` y `(pi/Lz)²` a lambda.
Los arreglos se almacenan en orden `[tiempo,z,y,x]`.
Se exige `error_máximo/|A| < 0.005` para estos parámetros.

- Malla 12×10×8: error≈0,011650 K.
- Malla 24×20×16: error≈0,003606 K.
- Otra variante cambia las tres longitudes, k y la amplitud.

Pregunta: ¿por qué no copiar sin cambios el dt de 2D?
La difusión en z agrega intercambios y endurece el límite de estabilidad.

## 4. Conservación de energía adiabática

Todas las caras tienen flujo Neumann cero y no hay fuente. Se parte de un
campo NO uniforme, de modo que sí existe transferencia interior.
Referencia: `E(t)=sum(rho cp V T)=E(0)`.

El máximo cambio de energía fue del orden de 1e−12 J; se exige <1e−9 J
para estas escalas sintéticas. Cambiar k o el tiempo cambia la distribución
de temperaturas, pero no debe cambiar la energía total.

Pregunta: ¿adiabático significa temperatura constante en todas las celdas?
No. Las celdas intercambian calor internamente; solo se impide el intercambio
con el exterior. Con k mayor, la distribución se uniformiza más rápido.

## 5. Fuente uniforme en dominio adiabático

Inicio uniforme y fuente constante q0 en W/m³. Referencia:
`T(t)=T0+q0*t/(rho cp)`.

| q0 [W/m³] | rho cp [J/(m³ K)] | Pendiente [K/s] | T a 0,08 s [°C] |
| ---: | ---: | ---: | ---: |
| 60 | 6 | 10 | 20,8 |
| 120 | 6 | 20 | 21,6 |
| 60 | 12 | 5 | 20,4 |

También se verifica el primer caso en 3D. Errores del orden de 1e−14 K;
se exige <1e−10 K. Duplicar q0 duplica la pendiente; duplicar rho cp la reduce
a la mitad. k no aparece en esta solución porque no hay gradientes.
No aplicar esta recta si hay pérdidas por el contorno.

## 6. Neumann

Se impone flujo en x_min y flujo cero en las otras caras. Convención de la API:
flujo positivo ENTRA al dominio. Referencia global `Delta E=q*A*t`.
La tasa de la primera celda es `q/(rho cp dx)`.

En 2D el área de la cara es 1,4 m² y tf=0,05 s:

- q=7 W/m² -> Delta E=+0,49 J.
- q=−7 W/m² -> Delta E=−0,49 J.
- q=14 W/m² -> Delta E=+0,98 J.

Se repiten los tres flujos en 3D, con área 3 m²: +1,05, −1,05 y +2,10 J.
Los residuos son del orden de 1e−13 J; se exige <1e−10 J.
Pregunta: ¿cuál es la diferencia con una fuente? Neumann aporta W/m² en
una superficie; una fuente volumétrica aporta W/m³ dentro del material.

## 7. Robin

Se impone convección en x_max; las demás caras son adiabáticas.
Desde el centro de la celda hasta el ambiente se usa:
`P=A*(Tamb−Tcelda)/(dx/(2k)+1/h)`.

Con T inicial=30 °C y área 1,4 m²:

- h=0 -> P=0: aislamiento, T constante en este inicio uniforme.
- h=5 y Tamb=20 °C -> P inicial≈−43,0769 W: enfría.
- h=20 y Tamb=20 °C -> P inicial=−80 W: extrae más calor.
- En 3D, h=5 y Tamb=40 °C -> P inicial≈+92,3077 W: calienta.

Se verifica la potencia inicial de forma independiente y el balance energético
en cada paso. El signo depende de Tamb−T, no de que el borde se llame Robin.
Multiplicar h por cuatro no multiplica necesariamente P por cuatro:
también existe la resistencia conductiva de media celda.

## Extra: estabilidad

Los tres tests proponen un dt un 1 % mayor que la cota admitida por el solver.
El resultado esperado es ValueError con texto 'inestable'; el test pasa
precisamente porque el solver rechaza ese paso.

Al cambiar malla o material, recalcular siempre el límite. Si dx se reduce
a la mitad en todas las direcciones, el dt admisible cae por un factor cuatro
para el mismo material y tipo de contorno.
En 2D/3D la cota usada incluye las celdas del contorno, aristas y esquinas;
es una condición suficiente conservadora.

## Cómo estudiar con un cambio propuesto por el ayudante

1. Identificar qué parámetro cambia y mantener unidades coherentes.
2. Predecir el efecto físico antes de ejecutar.
3. Actualizar la referencia analítica cuando corresponda.
4. Ejecutar el grupo y explicar su error, balance o excepción esperada.
5. Si falla, revisar hipótesis, estabilidad y resolución; no ampliar la tolerancia
   automáticamente para convertirlo en aprobado.

Un test aprobado verifica ese caso y esa tolerancia; no es validación experimental.
La batería completa se ejecuta sin `-s` con el comando habitual del README.
La entrega se prepara con el mensaje de commit **Entrega E05**. Para declarar
la evidencia, copiar el SHA exacto de ese commit; el nombre de la rama no
congela el estado evaluado. En la preparación se recopilaron320 tests sin
errores de importación, sin ejecutar los casos numéricos del usuario.
