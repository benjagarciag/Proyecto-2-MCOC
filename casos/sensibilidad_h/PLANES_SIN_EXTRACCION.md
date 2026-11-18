# Partición y colocación progresiva, sin extracción interna

Pregunta: ¿separar la colocación en las cinco vertidas existentes reduce
ΔT? No se presupone mejora: una vertida fría también puede aumentar
el diferencial con hormigón ya caliente. No se cambia la geometría IFC.

| Caso | Inicios [h] | D físico [h] |
| --- | --- | ---: |
| Única progresiva | 0 | 10,613 |
| Rápida progresiva | 0/3/6/12/15 | 15,640 |
| Referencia progresiva | 0/6/12/18/24 | 24,640 |
| Lenta progresiva | 0/9/18/27/36 | 36,640 |

Todos conservan12 °C, ausencia de extracción, h horario, k=2, suelo15 °C,
madera18 mm retirada a72 h y dos capas40 mm retiradas a240/480 h.
Este retiro10/20 días dio menor peor diferencial entre los ensayados,
pero no cumple ni se considera óptimo. Mantenerlo común permite comparar.

Se reutiliza la colocación por estratos del compañero: cada bloque se
divide en capas horizontales de la malla. Su duración V/60 se distribuye
por volumen de voxel; cada estrato se activa al inicio de su intervalo,
con edad propia de hidratación y retiros. Las caras cubiertas pasan a
interfaces interiores. No es un frente de descarga validado.

Comparar única progresiva contra única instantánea10/20 días permite
estudiar activación; comparar planes progresivos entre sí estudia secuencia.
El retiro por edad del estrato introduce escalonamiento local y debe
traducirse después a un montaje construible.

Cada plan:24 escenarios, 0,50 m/900 s,336/600 h y extensión a672 h si
hay alertas. Revisar máximos después de los últimos retiros. Una alerta
sin resolver impide concluir. Confirmar numéricamente toda variante decisiva.

## Ejecución personal desde la raíz

Primero única y rápida:48 pares en total.

```powershell
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/planes_sin_extraccion.py --planes unica rapida --ejecutar
```

Después referencia y lenta:otros48 pares.

```powershell
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/planes_sin_extraccion.py --planes referencia lenta --ejecutar
```

Sustituir `--ejecutar` por `--comprobar-insumos` para lectura sin simulación.
Sin argumentos solo imprime diseño. Los resultados están en
`resultados/planes_sin_extraccion/<plan>/malla_0.5_paso900/`, con matriz,
trazas horarias y `resumen.csv`. Las tablas superiores identifican en el
nombre qué subconjunto de planes fue solicitado. Reanuda archivos con
procedencia compatible; usar otra `--salida` si cambia el código.

`estudio_planes` registra cronograma, activación, retiros y hashes. Las
columnas heredadas `diferencia_delta_con_publicada_K` usan un comparador
histórico con otras condiciones: para decidir aquí, comparar métricas
absolutas de los planes nuevos bajo condiciones comunes.

Estado: lectura, geometría y activación comprobadas para cuatro planes;
sin nuevas simulaciones térmicas durante la preparación.

## Primera etapa ejecutada por el usuario: única y rápida

Ambas matrices contienen24 pares completos, pesos que suman1, colocación
a12 °C y ausencia de extracción interna. Conservan retiros240/480 h de
edad por estrato y9 grupos de activación. Hay horizontes600/672 h, sin
alertas pendientes; residuo máximo absoluto0,000226 J. Se revisaron
archivos guardados, sin ejecutar nuevos cálculos térmicos.

| Caso | D [h] | Tmax peor [°C] | ΔT peor [K] | P_f |
| --- | ---: | ---: | ---: | ---: |
| Única instantánea, retiros10/20 días | 10,613 | 51,2016 | 34,6484 | 100% |
| Única progresiva | 10,613 | 51,3334 | 34,8552 | 100% |
| Rápida progresiva | 15,640 | 51,3811 | 34,9824 | 100% |

Ninguna excede70 °C y todas las filas exceden20 K. Modelar colocación
progresiva incrementa el peor diferencial0,2068 K respecto de la única
instantánea. La rápida incrementa0,1272 K respecto de la única progresiva
y tarda5,027 h más. En esta primera etapa no se observa mejora de la
decisión por dividir la operación en ese cronograma.

Los peores diferenciales de ambos planes son M4_SS×ERA5-2023 a572 h,
con puntoS25 lateral en(-3,75,-8,75,0,975) m aproximadamente.
En la única progresiva, Tmax simultánea45,9884 °C y TminS25=11,1332 °C;
en la rápida,46,1173 °C y11,1349 °C. El mecanismo crítico sigue siendo
interior caliente frente a lateral frío después del retiro de aislación.
La máxima Tmax corresponde a M4_SS×ERA5-2025:214,75 h para única y
218,25 h para rápida. No confundir identificadores de estratos del solver
con los cinco identificadores originales de vertida del IFC.

Referencia y lenta siguen pendientes. Se pueden ejecutar con el segundo
comando anterior para cerrar esta familia, sin suponer que serán mejores.
Si ninguna cumple, estos resultados delimitan lo ensayado; no demuestran
imposibilidad de cualquier solución sin tuberías. Revisar controles y
restricciones físicas antes de ampliar búsqueda a otras particiones,
temperaturas o protección/base, y no ajustar propiedades para aprobar.
