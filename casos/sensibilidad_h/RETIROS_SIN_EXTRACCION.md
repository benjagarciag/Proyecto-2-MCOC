# Estudio de retiro de aislación, sin extracción interna

## Pregunta y alcance

El usuario pide estudiar cuándo retirar la aislación y entender su efecto.
La única a12 °C sin extracción ya calculada supera20 K en24/24 escenarios;
Tmax máxima51,2016 °C y ΔTmax39,1149 K. No se recalcula esa referencia.
Los dos nuevos casos mantienen geometría, 12 °C, h horario, k, suelo,
fuentes, climas, pesos, moldaje y activación instantánea; solo cambian las
edades de retiro de las dos capas de lana de vidrio de40 mm.

| Caso | 80 mm hasta | 40 mm hasta | Qué permite distinguir |
| --- | ---: | ---: | --- |
| Referencia existente | 240 h (día10) | 360 h (día15) | Resultado ya disponible |
| Retiro10/20 | 240 h (día10) | 480 h (día20) | Efecto de retrasar solo el retiro final |
| Retiro15/20 | 360 h (día15) | 480 h (día20) | Efecto adicional de mantener80 mm cinco días más |

Son alternativas exploratorias, no edades ya recomendadas. La comparación
no incluye todas las fechas posibles ni demuestra retiro óptimo global.
Se usan24 escenarios por variante, 0,50 m/900 s y336/600 h, con extensión
hasta672 h si hay alertas. Hay120 h de observación tras el último retiro
en600 h; una alerta persistente impide concluir y requiere ampliar datos.
El moldaje de madera se sigue retirando a72 h y debe existir soporte para
mantener mantas. No se modifica IFC ni el suelo. No se ha simulado al
preparar el estudio.

## Por qué podría reducir ΔT

La hidratación calienta el núcleo. El aislamiento reduce las pérdidas de
la superficie al aire, por lo que puede mantener TminS25 más próxima a
Tmax. Retirar80 mm de una vez facilita un enfriamiento superficial rápido
mientras el núcleo responde lentamente. Pasar80→40→0 mm ofrece una
transición, pero cada retiro debe evaluarse porque aún puede generar picos.
Retener calor también puede elevar Tmax o retrasar el enfriamiento.

Ejemplo conceptual, no resultado: núcleo48 °C y superficie10 °C dan38 K;
si se logra superficie30 °C manteniendo núcleo48 °C, son18 K. El modelo
debe comprobar ambas temperaturas: no se supone núcleo constante.

ACI identifica aislación superficial como medida para reducir diferenciales:
[ACI, control térmico](https://www.concrete.org/frequentlyaskedquestions.aspx?faqid=892).
NRMCA recomienda planificar retiros según temperaturas monitoreadas y
evitar choque térmico:
[CIP42](https://www.nrmca.org/wp-content/uploads/2020/04/42p.pdf).
Estas referencias justifican el estudio, no las fechas10/15/20 días.

## Limitación importante del caso actual

El caso crítico ya excede20 K antes del primer retiro y su punto frío a336 h
está cerca de la base, a25 mm de profundidad. Las mantas laterales/superiores
no aíslan la base. Por ello los retiros podrían reducir el máximo lateral
tardío sin resolver el cumplimiento conjunto. Evaluar localizaciones antes
de recomendar prolongar protección o estudiar otra partición.

## Ejecución personal desde la raíz

Comprobar sin calcular:

```powershell
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/retiros_sin_extraccion.py --retiros 240 480 --comprobar-insumos
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/retiros_sin_extraccion.py --retiros 360 480 --comprobar-insumos
```

Ejecutar primero una variante y después la otra:

```powershell
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/retiros_sin_extraccion.py --retiros 240 480 --ejecutar
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/retiros_sin_extraccion.py --retiros 360 480 --ejecutar
```

Sin argumentos solo muestra el diseño. Las salidas están separadas en
`resultados/retiros_sin_extraccion/retiros_240_480/malla_0.5_paso900/`
y `retiros_360_480/malla_0.5_paso900/`. Cada una incluye matriz, piezas,
historias horarias y `resumen.csv`. Conserva resultados con igual procedencia.
Los retiros y hash del nuevo script se guardan en `estudio_sin_extraccion`;
`protecciones_estudio` también explicita las caras y fechas.

Comparar Tmax, ΔTmax, P_f, instante/superficie crítica, métricas antes y
después de cada retiro y alertas; no decidir solo por el menor ΔT global.
Un buen retiro requiere margen en ambos límites durante y después de
retirar, confirmación numérica y regla de campo condicionada a sensores.

## Resultados ejecutados por el usuario

Ambas variantes finalizaron sus24 escenarios con pesos que suman1,
sin extracción interna y sin alertas pendientes; hay filas extendidas
a672 h. Los balances presentan residuos absolutos inferiores a0,000096 J.
La revisión leyó matrices existentes y no lanzó simulaciones.

| Retiros [días] | Tmax peor [°C] | ΔT peor [K] | P_T | P_f |
| --- | ---: | ---: | ---: | ---: |
| 10/15, referencia | 51,2016 | 39,1149 | 0% | 100% |
| 10/20 | 51,2016 | 34,6484 | 0% | 100% |
| 15/20 | 51,2016 | 35,0314 | 0% | 100% |

Retrasar el retiro final mejora el peor diferencial4,4665 K frente a
la referencia. Mantener80 mm hasta día15, con igual retiro final día20,
no mejora adicionalmente el peor pico: lo incrementa0,3830 K.
El máximo absoluto de temperatura no cambia porque ocurre a207 h,
antes de los retiros modificados. Esto no significa historias idénticas:
en el escenario del peor diferencial nuevo, el núcleo conserva más calor
con la protección prolongada.

Ambas variantes alcanzan su peor diferencial a572 h (día23,83), en
M4_SS×ERA5-2023, tras el retiro final a480 h. El punto frío es lateral,
z=0,975 m, y≈−8,75 m. Con retiros10/20, Tmax simultánea45,7739 °C
y TminS25=11,1256 °C; con15/20,46,1884 °C y11,1570 °C.
La diferencia entre esas temperaturas explica que más tiempo con80 mm
no sea automáticamente mejor al final.

No se identifica un retiro factible con estos tres casos. El patrón
mejora el pico tardío pero no resuelve excedencias previas, incluidas
las de base. Siguiente paso recomendado: revisar partición y colocación
progresiva sin extracción, preservando recursos, fuentes y clima comunes;
si se continúa buscando fechas, ampliar el horizonte tras cada retiro y
no presentar una postergación del pico como cumplimiento.
