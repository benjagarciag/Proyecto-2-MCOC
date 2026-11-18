# Potencia de extracción y temperatura de colocación

Se estudian controles del plan, conservando los parámetros físicos de
referencia y sin ajustar h, k ni el suelo para alcanzar cumplimiento.

## Comparación fijada antes de las nuevas corridas

| Caso | Tope de extracción térmica | Temperatura de colocación |
| --- | ---: | ---: |
| Base existente | 12 kW | 12,231833… °C |
| potencia_15kw | 15 kW | Igual a la base |
| colocacion_10c | 12 kW | 10 °C |
| combinada_15kw_10c | 15 kW | 10 °C |

La temperatura base de la única es la media ponderada por volumen del
plan 13/12 °C; se conserva sin redondearla en el cálculo. Los 10 °C son
un objetivo exploratorio de control a confirmar con planta, no un dato
de suministro garantizado. El diseño compara cada cambio aisladamente
y su combinación, sin atribuir a la potencia un efecto debido al cambio
de temperatura. Los casos representan planes/controles alternativos, no
realizaciones aleatorias con probabilidad asignada.

Se mantienen U=5 W/(m³·K), referencia del sumidero 18 °C, máscara interior,
encendido a 6 h de edad, apagado a 432 h, aislación 80→40→0 mm, retiros
240/360 h y madera hasta 72 h. Subir el tope no modifica U. No confundir
estos 15 kW con la variante anterior de la rama que también cambiaba U a 6.
Si el tope deja de actuar como limitación, aumentarlo puede dejar de mejorar
la extracción: se conserva la ley U*V*max(T−18,0) y su límite global.

Se usa h horario con altura representativa 2 m y exponente 0,14, suelo
15 °C/R0, k_hormigón=2, rho=2476 y cp=1023. Misma geometría, ocho
fuentes, tres climas, pesos 1/24 y duración física de 10,613 h a 60 m³/h.
La fuente Q sigue prescrita por edad, sin retraso cinético por preenfriamiento:
esa limitación importa al interpretar temperaturas iniciales diferentes.
Se parte de malla 0,50 m y paso máximo 900 s, con horizontes 336/600 h y
extensión hasta 672 h si hay alerta de cola.

## Viabilidad constructiva pendiente

Los topes son potencias térmicas del sumidero equivalente, no consumo
eléctrico ni dimensionamiento de chiller/tuberías. Para compararlos bajo
recursos comunes, se postula un sistema capaz de alcanzar hasta 15 kW,
operado con límites 12 o 15 kW; su disponibilidad y transferencia real
deben fundamentarse. No se supone que un sistema dimensionado para 12
kW entregue automáticamente 15.

Reducir de 12,231833… a 10 °C a 60 m³/h añade aproximadamente 94,2 kW
de carga sensible de preenfriamiento, usando rho*cp*caudal*DeltaT, antes
de ganancias durante transporte. No equivale a 94,2 kW eléctricos. La
planta debe poder sostener temperatura y caudal para conservar D; si no,
el cronograma y las restricciones deben actualizarse. No se presupone
que el preenfriamiento adicional es gratuito o ilimitado.

## Ejecución personal

```powershell
# Solo lectura/importación, sin simulaciones.
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/controles_obra.py --comprobar-insumos
# Primero, efecto aislado de la potencia: 24 pares nuevos.
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/controles_obra.py --ejecutar --casos potencia_15kw
# Después, efecto aislado de colocación y combinación: 48 pares nuevos.
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/controles_obra.py --ejecutar --casos colocacion_10c combinada_15kw_10c
```

Sin argumentos solo describe el diseño. `--ejecutar` sin selección calcula
los tres casos nuevos (72 pares), reutilizando la base. Las verificaciones
sintéticas del adaptador preceden a la ejecución. En la preparación del
estudio el agente no ejecutó simulaciones.

Salidas fijas bajo `resultados/controles_obra/`: matriz por caso, JSON por
par, tabla agregada y diferencias respecto de la referencia. Cada matriz
incluye `estudio_controles` con controles efectivos y hashes. Se conservan
archivos existentes con igual procedencia. No se editan configuración,
solver ni insumos congelados; las configuraciones nuevas se construyen
en memoria usando los controles ya admitidos por el ejecutor.

La confirmación de candidatos se hace con `--lado 0.25` y sensibilidad
temporal independiente. Un resultado favorable en la malla exploratoria
no cierra por sí solo la recomendación ni la robustez a k, suelo, exposición
y pesos. Si ninguno cumple, explorar otra medida fundamentada; no ajustar
propiedades del material o bordes para forzar aprobación.

## Primer resultado: potencia de 15 kW

Tras preparar el diseño se ejecutó el efecto aislado de potencia, conforme
al inicio de estudio solicitado por el usuario. Los casos de 10 °C y su
combinación permanecen preparados, sin ejecutar en esta etapa.

Se comprobaron los 24 pares y pesos completos, coherencia de indicadores,
resta simultánea de temperaturas y tope de potencia. Las verificaciones
sintéticas iniciales aprobaron. Horizonte 600 h, sin alertas; residuo
energético máximo absoluto <0,000065 J.

| Caso | Tmax peor [°C] | DeltaT peor [K] | Fallos conjuntos | P_f [%] |
| --- | ---: | ---: | --- | ---: |
| Base 12 kW, 12,231833… °C | 46,7954 | 21,0150 | 2/24 | 8,3333 |
| 15 kW, misma colocación | 46,4857 | 17,5348 | 0/24 | 0 |

Se conservó U=5; solo cambió el tope global de 12 a 15 kW. El nuevo
escenario de mayor diferencial es M4_SS × ERA5-2025 a 380 h: Tmax
simultánea 30,9592 °C, Tmin_S25 13,4244 °C, margen al umbral 2,4652 K.
La mayor extracción acumulada entre escenarios es 6,2031 MWh térmicos.
La duración constructiva permanece en 10,613 h por hipótesis de recursos.

Es un candidato factible en la resolución exploratoria bajo el catálogo,
pesos y parámetros fijados. No implica riesgo real cero, validación de
un circuito ni robustez ya comprobada frente a otras propiedades o bordes.
Antes de recomendarlo, confirmar malla y paso temporal, activación/encendido
constructivamente coherentes, capacidades de suministro y extracción,
y sensibilidades físicas relevantes. El modelo actual activa el bloque
completo al inicio y habilita enfriamiento a las 6 h, antes del término
constructivo de 10,613 h; no omitir esa aproximación en la defensa.

Confirmación espacial disponible para ejecución posterior:

```powershell
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/controles_obra.py --ejecutar --casos potencia_15kw --lado 0.25
```

## Decisión posterior: colocación uniforme a 12 °C

Por instrucción del usuario, las futuras comparaciones usan 12 °C en
todas las vertidas, incluidas V01–V05 y la operación de vertida única.
Se conserva la decisión en `colocacion_12c.json`. Es temperatura inicial
al colocar cada volumen: después evoluciona por generación e intercambio.
No representa una temperatura constante impuesta durante el curado ni
la temperatura del agua del circuito. La capacidad de planta para
entregar 12 °C a 60 m³/h sigue siendo un requisito constructivo pendiente.

Los resultados anteriores no cambian: la única de 15 kW que dio 0/24
usó 12,231833… °C; los planes de cinco vertidas anteriores usaron 13 °C
en V01 y 12 °C en las demás. No etiquetarlos como resultados de 12 °C
uniformes. No se modifican las propiedades IFC de práctica ni las fuentes.

Se preparó `colocacion_12c.py`, sin simulaciones por defecto y con salidas
separadas en `resultados/controles_12c/`. Para confirmar primero la única:

```powershell
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/colocacion_12c.py --ejecutar --casos unica_15kw_12c
```

El JSON declara los cuatro planes con temperatura uniforme y tope de
15 kW; el ejecutor permite comprobar y ejecutar los cuatro cronogramas.
Solo la única tiene resultados nuevos guardados; los otros tres están
pendientes de ejecución. Sin `--casos`, `--ejecutar` evalúa los cuatro.
Su tabla usa la única anterior a 12,231833 °C
como referencia. Los casos de 10 °C del estudio previo quedan como
alternativas exploratorias, no como la temperatura adoptada.

### Confirmación ejecutada a 12 °C exactos

El usuario solicitó ejecutar la única con 12 °C y tope de 15 kW. Se
completaron y comprobaron los 24 pares en malla 0,50 m y paso máximo
900 s, con pesos unitarios al sumar e indicadores coherentes. La
temperatura de colocación guardada es exactamente 12 °C. Horizonte
600 h sin alertas; residuo energético máximo <0,000054 J. Las
verificaciones sintéticas del adaptador aprobaron al iniciar.

| Colocación | Extracción máxima | Peor Tmax [°C] | Peor DeltaT [K] | Fallos conjuntos |
| --- | ---: | ---: | ---: | --- |
| 12,231833… °C | 15 kW | 46,4857 | 17,5348 | 0/24 |
| 12 °C | 15 kW | 46,2843 | 17,3681 | 0/24 |

P_T=P_delta=P_f=0 para el catálogo y pesos fijados. El peor diferencial
es M4_SS × ERA5-2025 a 380 h. La duración sigue siendo 10,613 h.
Se conservan U=5, reservorio de referencia 18 °C, encendido desde 6 h
de edad, apagado global a 432 h y máscara refrigerable de 366 m³.

Es un candidato factible en resolución exploratoria. Los otros planes
con 12 °C uniformes no se han recalculado todavía. No trasladar estas
métricas a colocación por estratos, otro encendido, malla/paso refinados
o distintas hipótesis de k/suelo sin las comprobaciones correspondientes.

Siguiente revisión: coherencia de activación y momento de encendido con
la colocación física; dimensionamiento del circuito y suministro; montaje
y retiros de protección; confirmación numérica del candidato y robustez
física/probabilística. La comparación final debe mantener comunes las
condiciones adoptadas y delimitar la optimalidad temporal.
