# Revisión del 18 de noviembre — planes e incertidumbre

Evidencia local sobre la Entrega E12 (`178ac5b`). Esta hoja conserva el piloto con la ley exponencial de E12. Las corridas con
las ocho probetas/campañas están en [Resultados F02](Defensa_F02_resultados.md).
La capacidad y espera siguen siendo supuestos provisionales.

## Decisión y recursos comunes

Se fija t₀ el **jueves 19-11-2026 a las 10:00, America/Santiago (UTC−03:00)**.
La ventana de 14 días termina el **03-12-2026 a las 10:00**. D es el tiempo
entre t₀ y el último término de colocación, en horas. El tiempo de enfriamiento
posterior se evalúa por separado dentro de la ventana térmica.

Se usa la misma fundación IFC de **636,78 m³**, una cuadrilla y una capacidad
efectiva provisional de **60 m³/h**. Espera mínima adicional provisional:
**0 h**; los inicios de la familia de cinco vertidas se redondean hacia arriba
en una grilla de **3 h**, respetando la separación nominal y el fin físico
de la colocación anterior. Cada duración es volumen IFC dividido por la
capacidad. Los recursos, la constructibilidad de la vertida única y la hora
común requieren ratificación del grupo. Los voxeles se activan térmicamente
todos al inicio de su vertida, mientras el calendario sí contabiliza toda
la duración de colocación. Esta aproximación es especialmente importante para
la vertida única, que requiere **10,61 h** de colocación.

| Plan | Inicios desde t₀ [h] | D [h] | Peor Tmáx [°C] | Peor ΔTmáx [K] | P(Tmáx > 70) | P(ΔTmáx > 20) | P(unión) |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Vertida única | 0 | 10,61 | 62,31 | 45,99 | 0/3 | 3/3 | 3/3 |
| Variante rápida | 0 / 3 / 6 / 12 / 15 | 15,64 | 62,33 | 46,04 | 0/3 | 3/3 | 3/3 |
| Propuesta de referencia | 0 / 6 / 12 / 18 / 24 | 24,64 | 62,23 | 46,04 | 0/3 | 3/3 | 3/3 |
| Variante lenta | 0 / 9 / 18 / 27 / 36 | 36,64 | 62,23 | 46,14 | 0/3 | 3/3 | 3/3 |

El peor valor de cada métrica se toma sobre los tres climas y puede provenir
de un día o de una historia diferente. Los cocientes representan el **peso
del conjunto discreto provisional**. En las alternativas evaluadas no se
encontró un plan factible: el diferencial controla. La variante lenta agrega
**12 h** a la propuesta sin ganar cumplimiento. En la rápida, V03 dura
**3,57 h** y se debe esperar hasta la hora 12 para iniciar V04. La vertida
única usa la máscara total del IFC y una temperatura de colocación uniforme
igual a la media de las cinco temperaturas ponderada por volumen.

[Resumen de todas las corridas](../resultados/incertidumbre/base/resumen.json) ·
[Curvas de la vertida única](../resultados/incertidumbre/base/vertida_unica.png) ·
[Campo al máximo diferencial](../resultados/incertidumbre/base/unica_diferencial.vti)

## Clima y pesos

Sitio El Rosal (−37,277929, −72,368271). Se descargó
[GFS Global vía Open-Meteo](../datos/clima/forecasts/20261117T013705171975Z_269ca9d8.json)
el **17-11-2026 01:37 UTC** (16-11 a las 22:37 en Chile). Desde t₀ entrega
**318 de 337 marcas** de temperatura requeridas, incluida la inicial.
Su última marca es **02-12 a las 15:00 en Chile**, 19 horas antes del fin
del horizonte. La cobertura contada por marcas incluye 318 de las 336
horas de la ventana semiabierta. A partir de la primera marca ausente,
cada control concatena la cola de uno de los tres ERA5 por hora relativa.
Se registra el salto en el empalme y se interpola entre marcas horarias.
Los controles GFS+cola son sensibilidades sin peso en la enumeración.

Para la enumeración se usan tres bloques **ERA5 de 2023, 2024 y 2025**
de las mismas fechas, sin empalmes internos, con peso provisional 1/3
cada uno. Temperatura en °C, viento en m/s, radiación de onda corta en W/m².
La física usa el aire horario; los snapshots conservan las tres variables.
Cada bloque conserva ciclo diario y persistencia. Los tres años se eligieron
como años consecutivos disponibles; esos pesos son una hipótesis y las
historias no representan percentiles observados. La sensibilidad duplica
el peso de cada bloque por turno y renormaliza; la decisión preliminar se
mantiene porque todos superan 20 K.

## Material y modelo probabilístico

La referencia provisional usa q₀ = 900 W/m³ y τ = 30 h, con generación
exponencial por edad. Para ingresar las ocho curvas, conservar los originales
junto a un manifiesto JSON. Declarar `mezcla`, `justificacion_comparabilidad_y_pesos`
y una lista `curvas`. Cada entrada requiere `id`, `peso`, `original`, `csv`,
`unidad`, `nota_ensayo_y_procesamiento`, `justificacion_cola_cero`.
El CSV procesado lleva `edad_h,acumulado`, desde cero, y puntos estrictamente
crecientes en edad. Unidades aceptadas: `K_adiabatico`, `J/kg_cementante`,
`J/g_cementante`. Las dos últimas requieren `cementante_kg_m3`.
Se pueden declarar `rho_kg_m3` y `cp_J_kgK` de cada curva.

La energía acumulada es ρcₚΔTₐd, o bH después de convertir la masa. Se
interpola linealmente el acumulado y se usa su incremento exacto en cada
intervalo. La pendiente entrega la potencia volumétrica, por segundos.
La curva procesada debe conservar el total, incluir una cola físicamente
justificada y ser monótona. El ejecutor mantiene constante el acumulado
tras su última marca. Para ensayos no adiabáticos hay que obtener primero
la generación mediante un balance del ensayo. En la revisión, mostrar los
originales, el gráfico de curvas completas, el calor integrado y las notas de
procesamiento. La cinética usa edad y reinicia en cada vertida.

El producto de pesos material × clima supone independencia. Una misma
realización del material se usa en todas las vertidas de un escenario,
como hipótesis común de mezcla. Con ocho curvas admisibles y tres ERA5
se ejecutan 24 escenarios por plan; una falla pesa 4,17 % si son
equiprobables y dos pesan 8,33 %. La unión cuenta cada escenario que
excede alguno de los límites una vez. La enumeración ponderada no tiene
error Monte Carlo. Publicar una recomendación requiere curvas compatibles,
recursos ratificados y una sensibilidad del conjunto final.

## Comprobaciones numéricas y tiempo de cálculo

| Comprobación | Rango de ΔTmáx en los 12 casos [K] |
| --- | ---: |
| Base, 0,50 m y paso máximo 900 s | 44,24–46,14 |
| Malla 0,25 m, paso máximo 900 s | 43,60–46,24 |
| Malla 0,50 m, paso máximo 450 s | 44,24–46,13 |
| Profundidad alternativa de 50 mm, malla 0,50 m | 43,83–45,67 |

Las cuatro condiciones numéricas conservan la clasificación. Los 12 controles
de GFS con cola histórica dieron diferenciales **43,13–44,49 K** y Tmax
menor que **62,27 °C**. Los saltos registrados al empalmar el aire fueron
−7,7, −4,0 y +0,9 °C según la cola. Todos los máximos de decisión de las
corridas base quedaron dentro de las 336 h sin activar la regla de extensión.
El residuo energético máximo de la base fue 0,00012 J en valor absoluto.

La base tomó aproximadamente 1,3–2,2 segundos por corrida histórica en
este equipo durante la ejecución concurrente. Con los ocho materiales serían
96 corridas históricas para cuatro planes; reservar unos minutos a 0,50 m
y presupuestar más tiempo al refinar. El resumen guarda tiempos medidos,
extremos, ubicación, eventos y residuos por corrida.

[Refinamiento espacial](../resultados/incertidumbre/malla_025/resumen.json) ·
[Refinamiento temporal](../resultados/incertidumbre/paso_450/resumen.json) ·
[Sensibilidad de profundidad](../resultados/incertidumbre/s25_050/resumen.json)

## Qué mostrar en el oral

1. **Balance físico**. ρcₚ∂T/∂t = ∇·(k∇T) + q̇. Cada lado está en W/m³.
   ρ es 2400 kg/m³, cₚ es 900 J/(kg K) y k es 2 W/(m K) para el caso provisional.
   El dominio incorpora solo voxeles de vertidas activas. Las interfaces
   entre celdas activas transfieren calor de forma conservativa.
2. **Bordes**. En aire, P = H(Tₐᵢᵣₑ − T꜀ₑₗdₐ), con h = 5 W/(m² K)
   fijo y resistencias por área de media celda, capas y película convectiva.
   La base usa conducción hacia el suelo equivalente a 15 °C. Las caras
   laterales usan ARAUCOPLY de 18 mm y Aislanglass de 40 mm, retirados a
   72 y 96 h de edad respectivamente. Una cara expuesta puede pasar a
   interfaz al activar la vertida vecina.
3. **Euler y S25**. C = ρcₚV y G = kA/Δx. El paso se limita con el
   cociente C/suma de conductancias y se divide en eventos. La temperatura
   a 25 mm se reconstruye por gradiente normal. Se evalúan Tmax y
   Tmax−Tmin,S25 en cada paso con el dominio activo. Revisar balance,
   malla 0,25 m, paso 450 s y profundidad alternativa de 50 mm como
   sensibilidad, conservando 25 mm para la decisión.
4. **Verificación y límites**. Mostrar el ensayo adiabático analítico,
   el test nuevo de integración tabular y los residuos del balance.
   La comparación de mallas y el ajuste del material evalúan partes
   del modelo; la validación de la fundación necesitaría observaciones
   térmicas independientes de la obra.

**Tres consultas prioritarias**. (1) ¿Son comparables las ocho curvas y
qué midió cada ensayo? (2) ¿Qué capacidad efectiva, espera mínima y
controles de colocación se pueden justificar? (3) ¿Cómo representar la
colocación progresiva y mejorar S25 en la malla escalonada?

## Ejecutar

Desde la raíz con Python 3.12 y el entorno del proyecto, incluidas las
dependencias de visualización para VTK:

~~~sh
python -B casos/incertidumbre/ejecutar.py
python -B casos/incertidumbre/ejecutar.py --curvas datos/hidratacion/manifiesto.json
python -B casos/incertidumbre/ejecutar.py --lado 0.25 --sin-figuras --salida resultados/incertidumbre/malla_025
python -B casos/incertidumbre/ejecutar.py --paso-max 450 --sin-figuras --salida resultados/incertidumbre/paso_450
python -B casos/incertidumbre/ejecutar.py --profundidad-s25 0.05 --sin-figuras --salida resultados/incertidumbre/s25_050
python -B casos/semana4/ver_3d.py resultados/incertidumbre/base/unica_diferencial.vti
~~~

En este equipo, ejecutar desde la copia Semana 4 en Ubuntu con
`/home/luis/Proyecto-2-MCOC/.venv/bin/python` y, para exportar o ver VTK,
`PYTHONPATH=.venv/cache/visualizacion`. El resumen registra la revisión
base y las huellas de entradas y código ejecutado. Para identificar el
paquete local de evidencia usar `git rev-parse HEAD`.
