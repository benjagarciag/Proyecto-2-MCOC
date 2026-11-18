# Cambio de estrategia: sin tuberías interiores

## Decisión del usuario

Se descarta el enfriamiento por tuberías interiores. Se conserva como
objetivo la temperatura de colocación de 12 °C en todas las vertidas.
El sumidero volumétrico de hasta 15 kW deja de ser un control disponible
para esta propuesta. No se sustituye por una extracción superficial de
igual potencia sin modelar y justificar ese intercambio.

Los resultados anteriores a 12 °C/15 kW siguen siendo evidencia histórica:
no demuestran cumplimiento de la alternativa sin extracción interna.

## Primera comprobación propuesta, aún no ejecutada

Conservar geometría, fuentes, climas, h horario, propiedades, suelo,
cronograma único y protecciones del caso anterior; mantener 12 °C y
deshabilitar completamente el enfriamiento interior. Esto permite aislar
su efecto antes de modificar a la vez varios controles.

Se preparó `sin_extraccion_12c.py`: pasa `enfriamiento=None`, adapta
comprobaciones y metadatos y guarda resultados en otra ubicación.
Los ejecutores de controles anteriores exigen potencia positiva: no basta
con poner `tope_W=0` en sus JSON. Los scripts históricos se conservan.

Desde la raíz del proyecto, comprobar sin simular:

```powershell
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/sin_extraccion_12c.py --comprobar-insumos
```

Ejecutar personalmente los 24 escenarios:

```powershell
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/sin_extraccion_12c.py --ejecutar
```

Abrir el archivo con Run Python File sin argumentos solo muestra el diseño.
La salida es `resultados/sin_extraccion_12c/malla_0.5_paso900/`:
JSON por escenario, matriz `unica_12c_sin_extraccion.json` y `resumen.csv`.
Incluye historias horarias para diagnosticar retiros y máximos. Conserva
escenarios terminados con igual procedencia al reanudar. Si cambia el
script, elegir otro `--salida`.

Auditar que potencia y energía de extracción interna sean cero en toda la
historia. Se mantienen pérdidas por ambiente y suelo: ausencia de sumidero
interno no significa dominio adiabático.

Evaluar los 24 pares, 336 h y extensión para capturar máximos, balance,
Tmax, ΔTmax y unión de excedencias. No anticipar cumplimiento. Tras decidir
una variante prometedora, comprobar activación progresiva y resolución.

## Controles disponibles sin tuberías

| Control | Qué determinar | Qué debe comprobarse |
| --- | --- | --- |
| Preenfriamiento | Capacidad de planta y transporte para entregar 12 °C a60 m³/h | Temperatura real en recepción y continuidad del suministro; enfriar ingredientes antes de colocar es distinto del sumidero posterior. |
| Aislación y moldaje | Resistencia, caras, montaje y retiro escalonado | Conservar superficie más próxima al núcleo puede reducir diferencial, pero también retener calor y elevar Tmax; evaluar ambos límites. |
| Partición y secuencia | Tamaño de vertidas, inicios y esperas construibles | Puede modificar disipación y duración, pero esperar más no garantiza menor diferencial. Comparar recursos y controles comunes. |
| Horario de colocación | Si cambiar la hora es admisible en la familia de búsqueda | Mantener origen común de D y contabilizar postergación de la primera vertida. |
| Mezcla de menor generación | Solo si existe alternativa respaldada y admisible para el curso | No reducir arbitrariamente las fuentes del profesor ni excluir curvas para forzar cumplimiento. |

Orden recomendado: primero medir efecto de retirar sumidero; después
estudiar protecciones/retiro y cronogramas, y solo si es necesario otra
temperatura de colocación respaldada por capacidad de planta.

## Fundamento y coordinación

ACI reconoce preenfriamiento de ingredientes, aislación superficial y
gestión de dimensiones/secuencia como herramientas de control térmico:
[consulta técnica ACI](https://www.concrete.org/frequentlyaskedquestions.aspx?faqid=892).
Estos métodos justifican explorar la estrategia, no garantizan que cumpla
la geometría y fuentes particulares del proyecto.

- Benjamín: justificar 12 °C, protección, retiros y suministro; sin dimensionar circuito interior.
- Luis: preparar caso con `enfriamiento=None` y verificar balance/criterios; mantener resultados históricos.
- Matías: catálogo y comparación final con esta restricción común; los planes de15 kW quedan como referencia anterior.

Estado al preparar el ejecutor: entradas comprobadas sin simulaciones.
La corrida posterior del usuario se revisa a continuación.

## Resultado posterior: corrida ejecutada por el usuario

Se completaron los24 pares con pesos que suman1, 12 °C de colocación y
`enfriamiento.activo=false`, sin energía ni potencia de extracción interna.
Horizonte600 h, sin alertas de cola; residuo energético máximo absoluto
0,0000725 J. No se ejecutaron nuevas simulaciones al revisar esta evidencia.

| Métrica | Resultado |
| --- | --- |
| Tmax máxima | 51,2016 °C; M4_SS × ERA5-2025, a207 h |
| ΔT máximo | 39,1149 K; M4_SS × ERA5-2024, a428 h |
| Temperaturas simultáneas del peor diferencial | Tmax48,6068 °C; TminS25=9,4920 °C |
| Excedencias de70 °C | 0/24 |
| Excedencias de20 K / unión | 24/24: P_Δ=P_f=100% bajo este catálogo y pesos |
| Rango de máximos de diferencial entre escenarios | 22,0023–39,1149 K |

**No cumple esta configuración sin extracción.** A336 h ya hay15/24
excedencias (62,5%); truncar a14 días tampoco la vuelve factible.
El máximo registrado por paso puede diferir de la historia horaria, que
muestrea estados específicos. Usar las métricas de pico para clasificar.

### Diagnóstico antes de cambiar retiros

En el escenario del peor diferencial, la historia muestreada ya supera20 K
a161,5 h, antes de retirar la primera manta a240 h. A336 h el máximo
de diferencial es27,3956 K y el punto frío está a z=0,025 m, cerca de
la base y del perímetro. La base intercambia con suelo y no lleva las
mantas de las caras superiores/laterales.

Después del retiro final a360 h, el máximo global de428 h se asocia a
un punto S25 lateral (y≈−8,75 m, z=0,975 m); la superficie se enfría
mientras el interior permanece caliente. Por tanto, mantener aislación
más tiempo puede ayudar en caras expuestas, pero no demuestra resolver
el diferencial previo junto al suelo. Tampoco basta con postergar el retiro
fuera del horizonte para ocultar un máximo posterior.

Siguiente estudio propuesto, sin ejecutar: separar efecto de conservar
mantas/retiro gradual del efecto de partición y activación progresiva.
Se prepararon dos alternativas con comandos en
[retiros sin extracción](RETIROS_SIN_EXTRACCION.md):240/480 h y360/480 h.
Mantener el modelo de suelo respaldado o evaluar contacto/base como
alternativa constructiva explícita, sin ajustar su resistencia solo para
cumplir. Confirmar ambos indicadores y máximos tras cada retiro.

Siguiente comparación preparada, sin ejecutar:
[partición y colocación progresiva](PLANES_SIN_EXTRACCION.md), primero
única/rápida y después referencia/lenta.
