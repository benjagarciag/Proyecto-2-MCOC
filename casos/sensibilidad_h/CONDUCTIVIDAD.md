# Sensibilidad de la conductividad del hormigón

Decisión del usuario: conservar rho=2476 kg/m³ y cp=1023 J/(kg·K),
asociados al archivo de fuentes del profesor. Mantener k=2 W/(m·K)
como referencia mientras se cuantifica su influencia.

## Diseño fijado antes de las corridas

| k [W/(m·K)] | Motivo |
| --- | --- |
| 1,6 | Perturbación exploratoria -20 % respecto de la referencia |
| 2,0 | Referencia docente; reutiliza resultados existentes |
| 8/3,6 = 2,222222… | Tabla 2 del artículo base de Ju y Lei (2019), k=8 kJ/(m·h·°C) |
| 2,4 | Perturbación exploratoria +20 % respecto de la referencia |

El intervalo ±20 % no es una distribución estadística, tolerancia medida
ni rango certificado de este hormigón. Se eligió para examinar la dependencia
del modelo de un parámetro sin medición propia. La referencia del artículo
aporta un contraste específico, pero pertenece a otro material: no sustituye
automáticamente el valor del hormigón de las probetas.

Se estudia inicialmente la vertida única con h horario, altura representativa
2 m y perfil de campo abierto con exponente 0,14. Malla 0,50 m, paso máximo
900 s, 24 combinaciones de ocho fuentes y tres climas. Mismos pesos,
geometría, temperaturas iniciales, mantas, retiros y extracción equivalente
de 12 kW/U=5 desde 6 h. Horizonte inicial 336 h y evaluación a 600 h,
con extensión hasta 672 h si hay alerta. Se conservan rho y cp y todas las
historias Q(t): cambiar k modifica la conducción, no el calor integrado.
No se recalcula la inversión de Q del ensayo con otros parámetros.

Por tanto es sensibilidad directa del modelo de fundación, no propagación
completa de la incertidumbre de identificación de las fuentes. Tampoco se
elige k para obtener cumplimiento. El objetivo es valorar si el resultado
y la recomendación dependen materialmente de su elección.

La matriz k=2 ya calculada contiene 24 pares. Hay 72 pares nuevos al
ejecutar los tres valores restantes. Cada par requiere varias integraciones
por las comprobaciones de horizonte. Las probabilidades se calculan por
separado para cada k; no se agregan distintos k como si fueran realizaciones
equiprobables. Una fila que conserve alerta de cola no permite cerrar el
cumplimiento. Si los cambios numéricos pueden alterar la clasificación,
confirmar con malla fina y sensibilidad temporal antes de concluir.

## Ejecución personal

Desde la raíz:

```powershell
# Describe el estudio sin simular ni generar resultados.
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/conductividad.py
# Lectura/importación y sustitución de k, sin solver.
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/conductividad.py --comprobar-insumos
# Calcula los valores nuevos y reutiliza la matriz k=2.
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/conductividad.py --ejecutar
```

El agente no ejecutó simulaciones de este estudio. El comando de ejecución
comprueba primero la adaptación de viento con los casos sintéticos ya
disponibles y luego simula la fundación. La modificación de k se hace
construyendo EntornoFundacion con la conductividad elegida. No se editan
el solver congelado, los CSV de las fuentes ni la configuración de referencia.
El paso sigue sujeto a la cota explícita de estabilidad: revisar el paso
efectivo si cambia k.

Salida fija bajo `resultados/sensibilidad_k/`: JSON por k y escenario,
matriz completa por k, tabla agregada `comparacion_malla_0.5_paso900.csv`
y diferencias por par en `escenarios_malla_0.5_paso900.csv`. Los JSON
incluyen `estudio_k` con valor efectivo, propiedades fijadas y hashes de
referencia y adaptación. Los hashes antiguos describen las fuentes originales,
no los parámetros modificados: consultar siempre `estudio_k`.

Se conservan archivos existentes con igual procedencia. No se sobrescriben
matrices publicadas del estudio de h. Es posible avanzar por valor con
`--k 1.6`, `--k 2.2222222222222223` o `--k 2.4`. Para confirmación fina:
`--lado 0.25`, con referencia k=2 de esa resolución ya disponible. El estudio
inicial evalúa sensibilidad de la propuesta; no demuestra robustez de todos
los cronogramas frente a k.

## Lectura prevista

Comparar Tmax, DeltaTmax, P_f, tiempos/ubicaciones críticas y cambios de
clasificación por par respecto de k=2. No suponer que aumentar k mejora
necesariamente ambos indicadores. Si la recomendación depende de k,
priorizar una medición/antecedente del material o una propuesta robusta al
intervalo estudiado. Incluso si no depende de k en estas pruebas, k=2
sigue siendo una aproximación docente, no una propiedad calibrada.

## Resultados de las corridas del usuario

Se comprobaron las tres matrices nuevas de 24 pares, sin duplicados,
pesos que suman uno e indicadores coherentes. La referencia k=2 se reutilizó.
Todos los pares alcanzan 600 h sin alertas de cola, con 2400 pasos; el mayor
residuo absoluto de las nuevas matrices es <0,00006 J.

| k [W/(m·K)] | Peor Tmax [°C] | Peor DeltaT [K] | Fallos | P_f [%] |
| --- | ---: | ---: | --- | ---: |
| 1,6 | 46,9068 | 21,7069 | 3/24 | 12,5000 |
| 2,0 | 46,7954 | 21,0150 | 2/24 | 8,3333 |
| 2,222222… | 46,7447 | 20,6572 | 2/24 | 8,3333 |
| 2,4 | 46,7083 | 20,3841 | 1/24 | 4,1667 |

P_T=0 en todos los valores, por lo que P_f=P_delta. En este estudio,
aumentar k reduce los peores indicadores. No generalizar esa monotonía a
otros planes, bordes o materiales. El máximo diferencial ocurre en
M4_SS × ERA5-2024 a 428 h para las tres matrices nuevas.

Con k=1,6 aparece un tercer fallo: M2_SS × ERA5-2024, con 20,1928 K.
Con k=2,222222… las clasificaciones individuales coinciden con k=2.
Con k=2,4, M4_SS × ERA5-2025 pasa a 19,9445 K: el cumplimiento agregado
en la malla base depende de un margen de apenas 0,0555 K en ese par.
No se debe adoptar k=2,4 porque produce P_f<=5 %: es una perturbación
exploratoria sin medición propia. Su clasificación requiere confirmación
numérica si se usa para sostener una recomendación.

Conclusión: k influye materialmente en la decisión dentro del intervalo
explorado; no se ha calibrado ni validado el valor. Se conserva k=2 como
referencia docente junto a rho y cp fijados. El valor del artículo no cambia
el incumplimiento en esta resolución. El siguiente avance de la revisión
física puede continuar con suelo y protecciones; la robustez del plan a k
debe permanecer identificada como pendiente al cerrar la decisión final.
