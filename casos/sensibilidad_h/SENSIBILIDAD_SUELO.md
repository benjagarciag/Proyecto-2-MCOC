# Sensibilidad independiente del borde de suelo

Pregunta: ¿cuánto depende el diagnóstico del plan de la temperatura y
resistencia del reservorio de suelo? Este estudio no identifica propiedades
geotécnicas ni valida el supuesto de reservorio sin calentamiento.

Se mantienen la única, h horario derivado del viento, k_hormigón=2,
rho=2476, cp=1023, ocho fuentes y tres climas con pesos iguales,
protecciones 80→40→0 mm, retiros 240/360 h y extracción 12 kW/U=5
desde 6 h. Malla exploratoria 0,50 m, paso máximo 900 s, ventanas de
336 y 600 h con extensión hasta 672 h si se detecta alerta de cola.

## Variantes fijadas antes de calcular

| Variante | T_suelo [°C] | R_suelo [m²·K/W] | Qué cambia |
| --- | ---: | ---: | --- |
| Base existente | 15 | 0,4167 | Nada; reutiliza los 24 resultados |
| temperatura_12 | 12 | 0,4167 | Solo temperatura |
| temperatura_18 | 18 | 0,4167 | Solo temperatura |
| temperatura_22 | 22 | 0,4167 | Solo temperatura |
| resistencia_mitad | 15 | 0,2083 | Solo resistencia |
| resistencia_doble | 15 | 0,8333 | Solo resistencia |

Las temperaturas exploran el orden de magnitud observado en las medias
históricas de ERA5 a distintas profundidades. No son percentiles ni una
reconstrucción del suelo bajo la excavación y no abarcan todas las muestras
horarias. Se aplican como valores constantes, comunes a los 24 pares de
cada variante, sin modificar ni asignar probabilidades nuevas a los climas.

Las resistencias mitad/doble son perturbaciones exploratorias del borde
equivalente, sin pretender que representen una tolerancia medida. El código
mantiene k_suelo=1,2 y usa longitudes equivalentes 0,25 y 1,0 m para conseguir
esos valores; esas longitudes no se presentan como espesores geotécnicos
reales. R_suelo no incluye la media celda del hormigón, que el solver sigue
añadiendo. No se alteran a la vez temperatura y resistencia; las interacciones
entre ambas no quedan estudiadas con este diseño.

## Ejecución personal

```powershell
# Solo muestra el diseño.
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/suelo.py
# Solo lectura/importación y comprobación de parámetros, sin solver.
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/suelo.py --comprobar-insumos
# Calcula cinco variantes de 24 pares y reutiliza la base.
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/suelo.py --ejecutar
```

Son 120 pares nuevos; cada uno requiere varias integraciones temporales.
Se puede avanzar por variante mediante `--variantes temperatura_12`, etc.
La ejecución verifica primero el adaptador horario con los casos sintéticos
existentes. Durante la preparación el agente no ejecutó simulaciones;
posteriormente el usuario autorizó explícitamente la batería mediante
“ejecutemoslo”, y se completó en esta sesión.
La comprobación sin solver verifica que la sustitución de suelo deja intacto
k del hormigón y que las fuentes conservan rho/cp.

Salida fija: `resultados/sensibilidad_suelo/`, con JSON por variante y par,
matriz agregada, `comparacion_malla_0.5_paso900.csv` y diferencias por
escenario. Se conserva energía intercambiada con suelo, máximos, tiempos,
ubicaciones, alertas y balance energético. `estudio_suelo` identifica los
parámetros efectivos, referencia y hashes; los hashes originales del solver
describen el código congelado y deben interpretarse con esa procedencia.

No se sobrescriben resultados anteriores. `--lado 0.25` permite confirmar
variantes en la malla fina usando la referencia de esa resolución ya disponible.
`--paso-max 450` exige disponer primero de una referencia con ese mismo paso.

## Interpretación

Comparar máximos, probabilidades y diferencias por par, no solo peor caso.
Una variante con alerta de cola conserva clasificación indeterminada.
Si los cambios pueden alterar el cumplimiento, confirmar las variantes
relevantes con refinamiento espacial y temporal. No seleccionar T o R por
dar un resultado favorable. Si la decisión depende fuertemente del suelo,
se requiere mejor información local o evaluar un terreno transitorio.

Las protecciones y sus retiros se mantienen para aislar el efecto del suelo.
Su sensibilidad debe estudiarse aparte; no se consideran validados por
esta batería. Antes de cerrar el modelo físico se retomará también la
elección defendible de k del hormigón según lo acordado.

## Resultados de la ejecución autorizada

Completadas las cinco matrices nuevas: 120 pares más la referencia de 24.
Se comprobaron catálogos completos, ausencia de duplicados, suma de pesos,
indicadores estrictos, resta simultánea de Tmax y Tmin_S25 y agregación
de la unión. Las verificaciones sintéticas iniciales aprobaron. No quedaron
alertas de cola; una corrida de temperatura_22 (M1_22A × ERA5-2025) se
extendió a 672 h y las restantes quedaron en 600 h. El mayor residuo
absoluto de las nuevas matrices es <0,00008 J.

| Variante | Peor Tmax [°C] | Peor DeltaT [K] | Fallos | P_f [%] |
| --- | ---: | ---: | --- | ---: |
| Base 15 °C/R0 | 46,7954 | 21,0150 | 2/24 | 8,3333 |
| 12 °C/R0 | 46,7920 | 20,7074 | 2/24 | 8,3333 |
| 18 °C/R0 | 46,7988 | 21,3049 | 2/24 | 8,3333 |
| 22 °C/R0 | 46,8032 | 21,6673 | 3/24 | 12,5000 |
| 15 °C/R0/2 | 46,7888 | 20,4585 | 3/24 | 12,5000 |
| 15 °C/2R0 | 46,8004 | 21,9750 | 3/24 | 12,5000 |

P_T=0 en todos los casos: el diferencial determina las fallas. La
clasificación desfavorable persiste en las seis configuraciones de la
malla exploratoria, pero los pesos fallidos y los máximos son sensibles
al borde de suelo. Esto no valida T=15 °C ni R0 como valores reales.

El resultado no es monótono con la resistencia en términos de probabilidad:
reducirla a la mitad baja el peor diferencial global pero añade un fallo,
M4_SS × ERA5-2023, cuyo diferencial es 20,3713 K a 210,5 h con S25 a
z=0,025 m en la base. El escenario crítico de esa variante es
M4_SS × ERA5-2025, 20,4585 K a 213 h, también con S25 basal. En cambio,
con R0 y 2R0 el peor diferencial está controlado por M4_SS × ERA5-2024
a 428 h con S25 próximo a un lateral. No se pueden deducir probabilidades
solo del peor valor ni afirmar que más pérdida al suelo mejora siempre.

Temperatura_22 añade un fallo M2_SS × ERA5-2024 (20,2039 K); resistencia
doble añade el mismo par (20,4782 K). Hay escenarios cercanos al umbral,
por ejemplo el menor margen absoluto en resistencia_doble es 0,0731 K.
Las probabilidades son las calculadas en 0,50 m/900 s; no son una cota
del error numérico de las variantes nuevas. Si se usan para seleccionar
un plan, confirmar las variantes relevantes en resolución final.

Se conservan 15 °C/R0 como referencia declarada mientras se completa la
revisión de protecciones y extracción. Ninguna perturbación estudiada
resuelve el incumplimiento del plan actual en esta resolución. No se
busca un borde de suelo favorable para hacer pasar la propuesta.

Salidas de revisión: `comprobacion_matrices.json` registra las comprobaciones
y cambios por variante; `figuras/sensibilidad_suelo.png` muestra diferencial
y riesgo. `graficar_suelo.py` regenera esa figura desde la tabla existente,
sin solver.
