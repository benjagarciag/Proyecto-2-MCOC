# Verificaciones complementarias de F02

**Grupo 6 · Parque Eólico El Rosal, Los Ángeles.** Base de cálculo `3e56e69` de
`codex/revision-incertidumbre`. Inicio común **19-11-2026 a las 10:00**,
`America/Santiago` (UTC−03:00). Se reutilizan el IFC, el solver, las ocho
fuentes tabulares y los tres bloques históricos congelados de Luis.

## Comparación de cronogramas

Las cuatro filas usan la misma malla de 0,50 m, paso máximo de 900 s, S25 a
25 mm, 24 escenarios de peso 1/24 y horizonte de 600 h. El control usa tope
de 12 kW, `U = 5 W/(m³·K)`, referencia de 18 °C, habilitación a las 6 h de
edad y apagado a la hora global 432. La colocación es de 13 °C en V01 y
12 °C en las otras vertidas, o 12,2318 °C uniforme en la única. Madera de
18 mm hasta 72 h de edad. Dos mantas de 40 mm en laterales y caras superiores,
con retiros por edad a las 240 y 360 h.

| Plan | Inicios [h] | D [h] | Peor Tmax [°C] | Peor ΔT [K] | P_T | P_Δ | P_f | ¿P_f ≤ 5 %? | Procedencia |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| Única | 0 | 10,61 | 46,90 | 17,30 | 0 % | 0 % | 0 % | Sí | Publicado por Luis y reproducido |
| Rápida | 0 / 3 / 6 / 12 / 15 | 15,64 | 47,10 | 17,87 | 0 % | 0 % | 0 % | Sí | Publicado por Luis y reproducido |
| Referencia | 0 / 6 / 12 / 18 / 24 | 24,64 | 47,30 | 18,30 | 0 % | 0 % | 0 % | Sí | Publicado por Luis y reproducido |
| Lenta | 0 / 9 / 18 / 27 / 36 | 36,64 | 47,56 | 20,90 | 0 % | 16,67 % | 16,67 % | No | Matriz complementaria nueva |

Las cuatro excedencias de la lenta ocurren antes de 336 h. El caso crítico,
M2_22A × ERA5-2023, alcanza a 42 h 33,45 °C en V01 y un S25 de 12,55 °C
en V05, colocada a las 36 h. La peor Tmax de la lenta ocurre en otro par.
Al refinar las cuatro excedencias con 0,25 m y 450 s, la de 20,0007 K
desaparece y las tres de M2_22A se mantienen. Su peso de 12,50 % es una cota
inferior para la matriz fina. El refinamiento fue selectivo, por lo que no
estima el riesgo completo en esa malla.

La única minimiza la duración entre los planes evaluados que pasan el
criterio. Con una capacidad efectiva total limitada a 60 m³/h, el volumen IFC
de 636,775 m³ impone `D ≥ 636,775/60 = 10,613 h`. Alcanzar esa cota supone
continuidad del caudal. La familia evaluada usa los cronogramas publicados,
incluida la separación lenta de 9 h, y no agota las estrategias construibles.

[Resultados de Luis](../../entregas/Defensa_F02_cronogramas_12kW.md) ·
[Gráfico duración–riesgo](../../resultados/f02_verificaciones/figuras/F02-duracion-y-riesgo.png) ·
[Curvas del caso común](../../resultados/f02_verificaciones/figuras/F02-curvas-caso-lento.png)

## Activación y control térmico

El solver publicado activa cada bloque completo al inicio. El ensayo por
estratos divide cada bloque en capas horizontales de la malla y distribuye su
duración por fracción de voxeles. Cada estrato se activa al inicio de su
intervalo. Se conservan los horarios y temperaturas de los bloques, con
hidratación y retiros por edad del estrato. Es una aproximación para medir
sensibilidad, sin un frente de descarga y compactación validado en obra.

Con encendido a las 6 h de edad en ambos planes progresivos, los peores
diferenciales son **17,80 K** en la única y **17,91 K** en la rápida. Ambos
mantienen 0/24. La única obtiene menor diferencial en los 24 pares, pero
mayor Tmax que la rápida en 15 pares. La única progresiva también da
17,80 K y 0/24 si el enfriamiento de cada estrato se habilita al alcanzar una
edad igual a la duración total de la colocación. Esa regla garantiza que
ningún estrato se enfría durante la colocación y escalona el encendido
después de terminarla.

Las siguientes matrices alteran el caso de una sola vertida con encendido al
término físico, `U=5 W/(m³·K)`, temperatura de 12,2318 °C y tope de 12 kW
hasta 432 h. Cada fila indica los parámetros que cambian.

| Cambio | Peor ΔT [K] | Excedencias | P_f | ¿P_f ≤ 5 %? |
| --- | ---: | ---: | ---: | --- |
| Colocación a 16 °C | 20,13 | 1/24 | 4,17 % | Sí |
| Colocación a 18 °C | 21,70 | 3/24 | 12,50 % | No |
| Tope de 10 kW | 19,964 | 0/24 | 0 % | Sí |
| Apagado a las 360 h | 20,99 | 1/24 | 4,17 % | Sí |
| 16 °C y tope de 10 kW | 22,94 | 5/24 | 20,83 % | No |

La clasificación usa los extremos sin redondear. El tope de 10 kW mantiene U
en 5 y un margen de 0,036 K en la malla base. Su caso crítico dio 19,64 K en
el refinamiento selectivo. En el apagado a 360 h, seis casos se extendieron
a 672 h con los mismos snapshots. Todos resolvieron las alertas de cola y se
conservó un único fallo. Para estas sensibilidades, el resultado de 336 h
queda explícito en `base_336h`.

Una excedencia pesa 1/24 = 4,17 %. El evento conjunto es exceder 70 °C
**o** 20 K, con cada par contado una vez. P_f = 0 % significa cero
excedencias en los casos enumerados. Su alcance está condicionado a las ocho
curvas, los tres años históricos, los pesos, la independencia material–clima
asumida y la ejecución fijada. Faltan variabilidad entre camiones, fallas
temporales del equipo y climas/mezclas fuera del catálogo.

## Viabilidad constructiva

- **Suministro.** El ritmo supuesto implica 85 despachos si el mixer lleva
  7,5 m³, con uno cada 7,5 min a régimen. Para ciclos de 90–120 min, el orden
  de magnitud es 12–16 mixers en rotación, más reserva. Se necesita confirmar
  planta, ruta, rendimiento efectivo de bombeo, cuadrilla y contingencia.
  [Capacidad nominal documentada por un proveedor](https://hcb.cl/terminos-y-condiciones/)
- **Juntas frías.** Falta definir el frente, el tiempo de retorno a un punto
  de la capa anterior, la trabajabilidad de la mezcla y la capacidad de
  vibrado. El cronograma y la activación térmica no certifican continuidad
  física. [Manual de hormigonado de Polpaico](https://manualdelconstructor.polpaico.cl/3-el-hormigon/3-7-hormigonado/)
- **Preenfriamiento.** Remover 6 K a 60 m³/h con `ρ=2476 kg/m³` y
  `cp=1023 J/(kg·K)` equivale a unos 253 kW térmicos de carga sensible, antes
  de ganancias durante transporte y bombeo. Los 12,23 °C son un objetivo
  modelado. Faltan mediciones por carga y capacidad de planta confirmada.
- **Postenfriamiento.** Los 12 kW representan un sumidero equivalente, no el
  tamaño de un chiller. El crítico de la única con encendido tardío extrae
  5,00 MWh térmicos en la ventana hasta 432 h. Con agua y un salto de 5 K,
  12 kW corresponden a unos 34,4 L/min en el balance del fluido. Faltan
  temperatura de ida y retorno, trazado, pérdidas de carga, conductancia hacia
  el agua y redundancia. [ACI 207.4R-20](https://www.concrete.org/Portals/0/Files/PDF/Previews/207.4R-20_preview.pdf)

## Reproducción y comprobación

Desde la raíz, con Python 3.12 y NumPy:

```powershell
python -X utf8 -B casos/f02_verificaciones/verificar.py
python -X utf8 -B casos/f02_verificaciones/ejecutar.py lenta_12kw --salida salida_f02
python -X utf8 -B casos/f02_verificaciones/verificar.py --regenerado salida_f02/lenta_12kw.json
```

El valor por defecto usa las máscaras del HTML E12 **en este mismo
repositorio**, con verificación del hash del IFC. El ejecutor comprueba
también las huellas guardadas del solver, configuraciones, manifiesto, ocho
CSV, fuente original y tres snapshots. Si falta IfcOpenShell, esa modalidad
permite importar el solver y bloquea cualquier llamada de lectura IFC.
`--geometria ifc` usa el flujo directo cuando IfcOpenShell está disponible.

- Los nueve experimentos nuevos y las cuatro referencias reproducibles se
  declaran en [configuraciones.json](configuraciones.json).
- `--modo colas` repite los casos marcados al final de 600 h hasta 672 h.
  `--modo refinar` recalcula las excedencias y el peor par a 0,25 m/450 s,
  conservando el peso original y dejando el riesgo agregado nulo. Para los
  resultados publicados aquí, usar `unica_apagado_360h` con `colas`, y
  `lenta_12kw` o `unica_10kw` con `refinar`.
- Para una verificación breve, agregar `--escenario M2_22A ERA5-2023`. Con
  `--traza` se guarda la serie, y con `--lado 0.25` o `--paso-max 450`
  se pueden separar los efectos espacial y temporal. El subconjunto no se
  usa para estimar probabilidades.
- El ejecutor escribe en un directorio explícito y rechaza reemplazar un
  archivo existente. `verificar.py --regenerado` contrasta máximos, tiempos,
  ubicaciones y pasos con la evidencia de la misma configuración.

El [registro de reproducción](../../resultados/f02_verificaciones/reproduccion_publicada.json)
contiene **96 corridas previas** contra las salidas de Luis, incluidas las 24
de la única con encendido tardío. En la
[sensibilidad numérica](../../resultados/f02_verificaciones/sensibilidad_numerica.json)
del par M4_SS × ERA5-2024, los primeros tres registros reproducen a Luis: la
única pasa de 17,3036 K a 17,3052 K al reducir el paso a 450 s y a
17,0080 K al refinar la malla a 0,25 m por separado. Al reducir ambos, los
tres cronogramas dan 17,01 / 17,64 / 18,17 K en ese par. Es evidencia de
sensibilidad y conserva el orden en el caso estudiado.

Las
[matrices complementarias](../../resultados/f02_verificaciones/matrices)
contienen **216 pares nuevos** en nueve configuraciones, una extensión de
seis colas y cinco refinamientos selectivos. Cada fila conserva los extremos,
sus ubicaciones, las métricas a 336 h y el balance en J. Las
[trazas C6](../../resultados/f02_verificaciones/trazas_c6.json) usan un
mismo escenario para los cuatro cronogramas. Los PNG se prepararon a partir
de esas salidas y sirven de apoyo para la defensa.

Antes de publicar se regeneraron las nueve matrices, las seis colas y los
cinco refinamientos con Python 3.12.14 y NumPy 2.3.5. Se verificaron sus
extremos, tiempos, ubicaciones y pasos. También pasaron seis invocaciones
Node de E07, E08 y del HTML E11/E12. La suite Python y la prueba DOM del
repositorio quedaron bloqueadas por faltas de `pytest` y `jsdom`,
respectivamente. La alternativa que vuelve a leer el IFC requiere
IfcOpenShell, que no estaba disponible.
