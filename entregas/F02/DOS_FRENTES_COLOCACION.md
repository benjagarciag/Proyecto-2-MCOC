# Suministro y colocación con dos frentes

El usuario aclaró que busca ambas cosas: ritmo prudente por frente y menor
duración total mediante operación paralela. Se propone el siguiente esquema
condicional; no se afirma que los recursos estén contratados ni que el
rendimiento se haya medido en El Rosal.

## 1. Transporte respaldado y flota propuesta

Se adopta carga útil7,5 m³ por mixer. Polpaico la declara como máximo en
sus condiciones de entrega, sujeto a reducciones por producto/obra:
[condiciones§2.1](https://www.comprapolpaico.cl/assets/docs/T%C3%A9rminos_y_Condiciones.pdf).
No confundirlo con volumen geométrico de tambor ni extrapolar a toda flota.

Flota propuesta16 activos+2 reserva, ciclo completo supuesto2 h.
`q_transporte=16*7,5/2=60 m³/h`. Las2 h deben incluir carga, ida, control,
descarga, retorno y actividades de ciclo; no representan2 h con hormigón
en el camión. No se midieron rutas. Dos camiones descargando no bastan
para suministro continuo: el resto de la flota carga, viaja o retorna.

## 2. Atención de mixers y operación paralela

Melón publica tiempos **óptimos** de descarga de1,3 y2,0 min/m³ para
distintos rangos de cono en su ficha de mixer tradicional, p39 del PDF.
Para7,5 m³ equivalen a9,75 y15 min. No son tiempos completos de atención
ni prueba del comportamiento de nuestra mezcla:
[protocolo Melón](https://www.melon.cl/wp-content/uploads/2022/10/Protocolo-atencion-op.mixer-camion-mixer_compressed.pdf).

Se plantean presupuestos de atención15 y20 min por mixer. El primero
redondea descarga favorable a10 min y añade5 min de relevo/maniobra;
el segundo toma15 min y añade5. Esos5 min son hipótesis de organización,
no medición del proveedor. No se cambia dosificación ni añade agua para
forzar cono: confirmar compatibilidad de la mezcla especificada con bombeo.

Con dos frentes independientes, la recepción sería:
`q_recepción=2*7,5*60/t_atención`:60 m³/h con15 min y45 con20 min.
Contabilizar una sola vez atención dentro del ciclo de flota; la condición
de recepción es otro cuello de botella, no una espera que se sume de nuevo.

Dos camiones alimentando una sola tolva pueden facilitar continuidad, pero
la bomba sigue teniendo su capacidad total. Aquí «dos frentes» significa
dos líneas de bombeo/colocación independientes (por ejemplo dos equipos),
con zonas coordinadas y cuadrillas capaces de compactar cada flujo.

## 3. Planta y preenfriamiento

Opción de estudio: proveedor local o combinación de plantas asignadas que
puedan entregar≥60 m³/h **a12 °C de recepción**, con reserva de producción
por acordar. Es un requisito del escenario, no capacidad verificada de
Polpaico u otro proveedor. Si son dos plantas, confirmar misma mezcla y
control de calidad: no suponer identidad ni sumar sus capacidades nominales.
La oferta local identificada se conserva en `SUMINISTRO_EL_ROSAL.md`.

Quedan por confirmar capacidad a baja temperatura, logística y atención
continua. Si planta solo puede asignar40, dos frentes no dan60: manda40.
No asignar por defecto80% a una planta sin conocer operación o fuente.

## 4. Bombeo, compactación y secuencia

Se especifica como requisito30 m³/h efectivos por frente para bombeo y
compactación. No se deduce de una bomba nominal ni de tener un vibrador.
Definir cuadrilla independiente, operadores de manguera/vibrado y apoyo,
coordinación común, equipos de reserva y turnos, confirmando rendimiento
con área, congestión de armadura, espesor de tongada y mezcla.

Propuesta: avanzar coordinadamente por capas de espesor acordado con el
procedimiento de consolidación; ambos frentes contribuyen a una misma
operación continua, evitando acumular toda la altura en un extremo. No
crear una junta fría o dos cuerpos independientes por dividir el suministro.
El espesor/recorrido real y los tiempos admisibles entre capas siguen
pendientes de definición técnica, no los decide solo el solver térmico.

El modelo térmico por estratos puede representar el llenado vertical total
según caudal combinado, pero no el frente horizontal de dos bombas ni el
vibrado. No presentarlo como reproducción espacial de su movimiento.

## Resultado del modelo logístico condicional

Misma flota16+2 y planta asignable supuesta60, con límite30 por frente:

| Alternativa | Atención por mixer | Caudal efectivo [m³/h] | D=636,775/q [h] |
| --- | ---: | ---: | ---: |
| Un frente objetivo | 15 min | 30 | 21,226 |
| Dos frentes, ritmo prudente | 20 min | 45 | 14,151 |
| Dos frentes, objetivo | 15 min | 60 | 10,613 |
| Dos frentes, ciclo de flota2,5 h | 15 min | 48 | 13,266 |

En45, cada frente recibe un camión cada20 min; despacho global cada10 min,
con12 activos mínimos ideales a ciclo2 h. En60, cada frente cada15 min,
despacho global cada7,5 min y16 activos. Pueden mantenerse todos disponibles
en escenario45; no suponer que los18 producen nominalmente.

El caso prudente45 es más lento que el objetivo60, pero más rápido que
un frente30. Esa es la combinación de prudencia y paralelismo solicitada.
Ninguna cifra es aún rendimiento local garantizado ni resultado térmico.
El margen con16 activos a60 y ciclo2 h es nulo para demoras adicionales:
la reserva y/o capacidad extra requieren organización explícita.

Comparar inicialmente45 y60 con iguales recursos disponibles y los mismos
controles térmicos; usar30 para mostrar efecto de operar solo un frente.
Más de60 requiere cambiar al menos un límite de recursos. No afirmar
menor D factible antes de calcular riesgo y confirmar constructibilidad.

## Cálculo editable, sin solver

Configuración en `casos/sensibilidad_h/suministro_paralelo.json`:

```powershell
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/suministro_paralelo.py
```

El script solo calcula el mínimo entre capacidades de planta, transporte,
recepción, bombeo y compactación. No exporta ni altera resultados térmicos.
Estado: aritmética comprobada; recursos y ciclos locales pendientes de
confirmación. No se envió consulta a terceros.
