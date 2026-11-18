# Contraste con suelo transitorio: diseño y ejecución

## Objetivo

Contrastar el reservorio fijo15 °C con un terreno que almacena calor,
para la candidata única progresiva a10 °C, tres capas40 mm retiradas
a240/360/480 h, sin extracción interior. No se eleva T inicial del suelo
para obtener cumplimiento. Referencia existente:
`resultados/controles_pasivos/t10_tres_capas/malla_0.5_paso900/t10_tres_capas.json`.

## Modelo propio implementado

Debajo de cada celda basal se coloca una columna1D de suelo, sin intercambio
horizontal entre columnas. Se resuelve conducción cartesiana por volúmenes
finitos y Euler explícito al mismo paso que el hormigón; se aplica la cota
de estabilidad de ambos materiales. El suelo tiene k1,2 W/(m K), temperatura
inicial uniforme15 °C y15 °C en el límite inferior del dominio. Las columnas
antes de cubrirse se consideran adiabáticas en su cima: no se modela la
exposición al aire de la excavación antes de colocar.

La conductancia de contacto suma medias celdas de hormigón y suelo:
`H=A/[Δz_h/(2k_h)+Δz_s/(2k_s)]`. Un único flujo se suma con signos
opuestos a ambos balances. No se conserva además la resistencia equivalente
0,5/1,2: se sustituye por suelo discretizado, sin doble contar. Suelo
y hormigón siguen siendo estados diferentes. Tmax/S25 y riesgo se calculan
solo en hormigón; no incorporar temperaturas de suelo a sus métricas.

No se modifica el solver histórico ni se usa un solver externo. Se adapta
en memoria su fuente congelada y se guardan hashes de esa adaptación,
módulo de columnas, configuración y scripts.

## Parámetros e incertidumbre explícita

| Variante | Capacidad volumétrica [MJ/(m³ K)] | Profundidad [m] | Celda suelo [m] |
| --- | ---: | ---: | ---: |
| nominal | 1,8 | 4 | 0,25 |
| capacidad_baja | 1,2 | 4 | 0,25 |
| capacidad_alta | 2,4 | 4 | 0,25 |
| malla_suelo_fina | 1,8 | 4 | 0,125 |
| dominio_profundo | 1,8 | 8 | 0,25 |

La capacidadρc nominal y su rango son hipótesis exploratorias, sin mediciones
locales ni probabilidades asignadas. No son valores geotécnicos validados
ni percentiles. Se parametrizaρc directamente porque es lo que entra en el
balance;1,8 MJ/(m³ K) equivale, por ejemplo, al producto hipotético1800 kg/m³
por1000 J/(kg K), no a dos mediciones independientes. k y T inicial se
mantienen para aislar el cambio de modelo. Falta incertidumbre de humedad,
perfil térmico, estratigrafía y contacto real.

Fundamento general: modelos de terreno requieren conductividad, densidad
y calor específico, y resuelven la evolución térmica mediante conducción.
Consultar [EnergyPlus, dominio de suelo](https://bigladdersoftware.com/epx/docs/23-2/engineering-reference/ground-heat-transfer-calculations-using-site.html)
y [LBL, propiedades con almacenamiento](https://simulationresearch.lbl.gov/modelica/releases/v12.1.0/help/Buildings_HeatTransfer_Data_Soil.html).
Estas fuentes respaldan la formulación, no certifican nuestro rango local.

La longitud difusiva `sqrt(k*t/ρc)` nominal a672 h es aproximadamente1,27 m.
La profundidad4 m es una elección inicial; contrastar8 m evita asumir que
el límite inferior ya es suficientemente lejano. También comprobar malla
y tiempo: el balance no sustituye una comprobación de resolución.

## Verificación realizada

Solo casos sintéticos pequeños, sin correr las24 realizaciones de la fundación:

- signo y conservación del flujo impuesto a una columna;
- perfil lineal estacionario con flujo conocido y fondo aT prescrita;
- cubo de hormigón acoplado al suelo, sin fuente ni convección, comparado
  contra una matriz Euler construida independientemente;
- balance de hormigón, suelo y conjunto.

Estas comprobaciones aprobaron. No equivalen a validación experimental,
estudio de convergencia ni verificación de un suelo3D. La omisión del flujo
horizontal/perimetral es especialmente relevante porque el punto crítico
se encuentra próximo al borde. No afirmar que columnas1D corrigen por
completo la física ni que el resultado será más favorable.

## Ejecución personal desde la raíz

Comprobar entradas o repetir verificaciones pequeñas:

```powershell
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/suelo_transitorio.py --comprobar-insumos
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/suelo_transitorio.py --verificar
```

Primero evaluar nominal:24 escenarios con336/600 h y extensión hasta672 h
si se detectan alertas. El horizonte se mide desde la primera vertida.

```powershell
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/suelo_transitorio.py --variante nominal --ejecutar
```

Las otras variantes se ejecutan por separado sustituyendo `nominal` por
su nombre. No mezclarlas en una sola probabilidad. Sin argumentos solo
imprime diseño; no simula. Se conservan resultados con procedencia compatible.

Salidas:
`resultados/suelo_transitorio/nominal/t10_tres_capas/malla_0.5_paso900/`,
con matriz, piezas, historias y resumen. `estudio_pasivo.suelo_transitorio`
identifica propiedades/dominio. Los balances añaden almacenamiento del
suelo, energía del fondo, temperaturas extremas de celdas superiores y
residuos de suelo y conjunto. `suelo` conserva el flujo integrado hacia
el hormigón, con el signo histórico. No confundirlo con energía del fondo.

Antes de recomendar: comparar Tmax, ΔT y P_f a336 h y extendidos, punto
crítico y calor intercambiado; comprobar capacidad/malla/dominio y límites
del perímetro. Si hay alertas de cola, ampliar horizonte/datos antes de
concluir. El modelo anterior puede seguir siendo referencia equivalente;
no llamarlo erróneo solo porque difiera del transitorio.
