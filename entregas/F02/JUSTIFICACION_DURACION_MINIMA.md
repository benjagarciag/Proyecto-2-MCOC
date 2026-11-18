# Justificación de duración mínima y cambios de rendimiento

## Alcance

Supuesto autorizado por el profesor, según informó el usuario: capacidad
efectiva total máxima60 m³/h, suministro continuo, dos frentes30 m³/h,
bombeo/compactación compatibles. Se conserva volumen IFC636,7751927 m³.
La temperatura de colocación12 °C y extracción equivalente hasta15 kW
son controles de la candidata, no la explicación algebraica de la cota.

## Demostración de la cota

SeaD el plazo desde inicio común t0 hasta terminar toda la colocación,
yq(t) el caudal efectivamente colocado, sumado sobre ambos frentes.
Con interrupciones o postergación, q(t)=0 durante esas esperas. Entonces:

```
V = integral desde0 hastaD de q(t) dt
q(t) ≤ q_max = 60 m³/h
⇒ V ≤ 60 D
⇒ D ≥ V/60 = 10,6129199 h
```

La igualdad solo se alcanza si se coloca a60 durante todo el intervalo,
sin esperas. Una secuencia por zonas puede ser continua si mantiene ese
caudal y la continuidad constructiva; una etiqueta de «vertida» en IFC
no obliga por sí sola a introducir una espera. El procedimiento de capas
y consolidación debe ser compatible con la mezcla y armaduras.

La cota no es resultado de ajustar temperaturas ni de encontrar un mínimo
en una curva térmica. Es el menor tiempo constructivo del conjunto de
recursos declarado; para convertirlo en recomendación falta comprobar
cumplimiento térmico y ejecución. No abarca preparación previa común ni
enfriamiento posterior; las esperas desde t0 sí forman parte deD.

## Mayor o menor rendimiento

| q total [m³/h] | D continua [h] | Diferencia frente a60 [h] | Alcance |
| --- | ---: | ---: | --- |
| 30 | 21,226 | +10,613 | Menor utilización; puede representar un frente30 |
| 45 | 14,151 | +3,538 | Ritmo menor dentro de recursos disponibles |
| 60 | 10,613 | 0 | Capacidad máxima supuesta de la familia |
| 75 | 8,490 | −2,123 | Requiere capacidad adicional |
| 90 | 7,075 | −3,538 | Requiere capacidad adicional; dos frentes45 |

Para caudal constante, D(q)=V/q y su derivada es−V/q²: aumentarq reduce
tiempo de manera no lineal. Pasar45→60 aumenta caudal33,3% y reduce
duración25%; duplicar30→60 reduce duración a la mitad.
La curva continúa bajo10,61 al permitir más de60, por lo que no existe
un mínimo universal en10,61 independiente de los recursos.

Con igualq durante colocación, añadir por ejemplo2 h de espera da
D=V/q+2 h: las esperas no mejoran el objetivo temporal, aunque podrían
ser necesarias por restricciones constructivas o para estudiar otra
respuesta térmica. No afirmar que una espera de horas garantiza resistencia.

## Qué cambia térmicamente y qué aún no sabemos

Cambiarq altera las horas de activación de las capas, sus edades simultáneas,
exposición e interfaces y el momento de operación del frío según su regla.
Un ritmo mayor concentra la colocación en el tiempo; uno menor separa las
edades y prolonga la exposición. Con una fuente por edad, bordes variables
y frío limitado, la respuesta de Tmax yΔT debe calcularse: no se deduce
del signo de la derivada deD. Una colocación más lenta puede introducir
zonas frías junto a hormigón caliente; no es automáticamente más segura.

Los valores deq75 y90 de la tabla son sensibilidad de recursos, no planes
admisibles conq_max60. Si se simulan, identificar el cambio de recurso y
mantener explícitos los controles y restricciones correspondientes.

No están calculadas las curvas de riesgo por caudal para12 °C/15 kW con
activación progresiva. El caso instantáneo previo favorable no demuestra
por sí solo cumplimiento de la operación continua representada por capas.
Para cada alternativa admisible se necesitan las24 realizaciones, máximos
a336 h y extendidos yP_f conjunto≤5%, con resolución confirmada.

## Gráfico y reproducción

![Caudal y cota de duración](../../resultados/controles_12c/figuras/caudal_duracion_cota_minima.png)

Verde: caudales dentro de la capacidad supuesta. Naranja discontinuo:
duraciones menores que requieren recursos adicionales. Punto azul:
cota constructiva10,613 h, sin atribuirle validación térmica definitiva.
Solo se graficaD=V/q; no hay puntos de riesgo inventados.

```powershell
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/graficar_caudal_duracion.py
```

GeneraPNG ySVG de evidencia analítica existente, sin solver ni simulaciones.

Texto para defensa: «Con capacidad efectiva total limitada a60 m³/h,
el volumen636,775 m³ imponeD≥10,613 h. La colocación continua puede
alcanzar esa cota si no hay esperas. Ritmos menores aumentanD y deben
compararse térmicamente. Ritmos mayores permiten menos tiempo, pero quedan
fuera de los recursos declarados. La recomendación requiere demostrar
ademásP_f≤5% y coherencia de la ejecución».
