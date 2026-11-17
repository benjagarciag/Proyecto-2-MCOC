# F02 · Resultados con las ocho curvas de hidratación

**Grupo 6 · El Rosal, Los Ángeles.** Cuatro planes, ocho curvas y tres bloques
ERA5 congelados. El jueves 19 a las 10:00, hora de Chile, es el origen común.
La capacidad provisional es 60 m³/h con una cuadrilla y 0 h adicionales de
espera mínima. El dominio y la programación provienen del IFC. Véase el
[dossier de cronogramas y método](Revision_18_noviembre.md) para los inicios,
duraciones por vertida, bordes y la preparación de la defensa.

## Decisión

| Plan | D [h] | Peor Tmax [°C] | Peor ΔTmáx [K] | P_T [%] | P_Δ [%] | P_f [%] | Estado |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Vertida única | 10,61 | 56,96 | 41,30 | 0,00 | 100,00 | 100,00 | excede |
| Variante rápida | 15,64 | 56,94 | 41,42 | 0,00 | 100,00 | 100,00 | excede |
| Propuesta | 24,64 | 56,89 | 41,52 | 0,00 | 100,00 | 100,00 | excede |
| Variante lenta | 36,64 | 56,94 | 41,69 | 0,00 | 100,00 | 100,00 | excede |

Se cuentan las excedencias estrictas de 70 °C y 20 K en cada escenario, y
la unión cuenta una corrida una vez. Se usan las mismas ocho fuentes para
todos los planes, una realización común para todas las vertidas de un
escenario y el producto de pesos material–clima bajo independencia. Los
pesos 1/8 y 1/3 son hipótesis de escenarios de modelo. Con solo SS el
resultado también supera el criterio en todos los planes. La duración de la
vertida única es el límite inferior del cronograma con la capacidad supuesta,
pero esa alternativa también excede 20 K.

## Probetas y procesamiento

Se conservaron las ocho fuentes del [archivo original](../datos/hidratacion/source_terms.txt).
M1–M4 identifican probetas, con cuatro curvas por campaña. Falta confirmar
la identidad de la dosificación entre probetas y la independencia de las
repeticiones. El archivo registra fuentes volumétricas Q en W/m³ estimadas
por inversión térmica con beta de ensayo 2,5 W/(m²·K). Ese beta pertenece al
ensayo de probeta. Las corridas de fundación usan h convectivo de 5 W/(m²·K)
y sus propias resistencias de capas, moldaje y suelo.

Se aplicaron ρ = 2476 kg/m³ y cₚ = 1023 J/(kg·K), reportados para las
probetas, al convertir energía volumétrica en aumento de temperatura.
Se usó el inicio de la ventana como edad cero del modelo, dos horas
después del inicio del registro. Se integra Q por trapecios con paso de
600 s, se interpola el acumulado para obtener la energía de cada paso y
se reinicia la edad por vertida. SS termina a las 240,33 h y 22A a las
163 h. El acumulado se mantiene fijo después de cada registro y los NaN
marcan datos ausentes. Los ocho totales abarcan 61,21–100,17 MJ/m³ y
reproducen los valores redondeados de la cabecera. La incertidumbre por
el beta de inversión queda como limitación porque el archivo solo
contiene series completas para beta = 2,5.

## Verificación e inspección

Cada corrida se inicia con 336 h. Se aplicó la regla de extensión cuando
los indicadores se mantenían cerca del máximo al final de la ventana.
Cantidad de escenarios por horizonte efectivo: {336: 64, 504: 32}.
Quedaron 0 alertas al horizonte máximo. Se registran los máximos
a 336 h y los del horizonte efectivo. El pico térmico y el mínimo S25
se evalúan en el hormigón activo.

Se repitió la combinación M1_22A × ERA5-2025, de menor diferencial en el
ensayo, para la vertida única y la propuesta:

| Plan | Malla [m] | Paso máximo [s] | Tmax [°C] | ΔTmáx [K] |
| --- | ---: | ---: | ---: | ---: |
| Vertida única | 0,50 | 900 | 42,38 | 26,38 |
| Propuesta | 0,50 | 900 | 42,55 | 26,43 |
| Vertida única | 0,50 | 450 | 42,38 | 26,39 |
| Propuesta | 0,50 | 450 | 42,55 | 26,44 |
| Vertida única | 0,25 | 900 | 42,39 | 25,96 |
| Propuesta | 0,25 | 900 | 42,52 | 26,04 |

[Fuentes Q por campaña](../resultados/incertidumbre/curvas_reales/fuentes_q.png) ·
[Energía acumulada](../resultados/incertidumbre/curvas_reales/curvas_hidratacion.png) ·
[Curvas de vertida única, M1_SS × ERA5-2023](../resultados/incertidumbre/curvas_reales/vertida_unica.png) ·
[VTK del máximo diferencial de esa corrida](../resultados/incertidumbre/curvas_reales/unica_diferencial.vti)

[Tabla completa por escenario](../resultados/incertidumbre/curvas_reales/escenarios.csv) ·
[Resumen con clima, hashes, máximos y balance](../resultados/incertidumbre/curvas_reales/resumen.json) ·
[Sensibilidad espacial y temporal](../resultados/incertidumbre/curvas_reales/sensibilidad_malla_paso.json)

## Reproducir

~~~sh
python -B casos/incertidumbre/preparar_fuentes.py
python -B casos/incertidumbre/ejecutar.py --curvas datos/hidratacion/manifiesto.json --salida resultados/incertidumbre/curvas_reales
~~~

Para el respaldo de la defensa, mostrar también un plan de control en obra:
sensores interiores y cerca de caras expuestas, registro de aire, y revisión
del diferencial antes de retirar moldaje o aislación. Su ubicación y las
acciones ante resultados adversos requieren acuerdo del grupo. El PDF de
exposición y el SHA que se declare se cierran con la versión de la defensa.
