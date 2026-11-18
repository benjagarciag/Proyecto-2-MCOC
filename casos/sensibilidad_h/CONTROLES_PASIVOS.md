# Colocación a10 °C y protección pasiva, sin tuberías

## Decisión y diseño

El usuario solicita estudiar10 °C y mejorar moldaje/aislación para reducir
el diferencial. Los10 °C son objetivo exploratorio de recepción, pendiente
de factibilidad de planta, no temperatura validada ni constante de curado.
Se mantiene única progresiva, geometría y materiales, h horario, suelo,
fuentes, climas y24 pesos1/24. No hay sumidero interior.

| Caso | T colocación | Aislación y edades de retiro por estrato |
| --- | ---: | --- |
| Referencia progresiva existente | 12 °C | 80→40→0 mm a240/480 h |
| t10_dos_capas | 10 °C | Igual a referencia |
| t12_tres_capas | 12 °C | 120→80→40→0 mm a240/360/480 h |
| t10_tres_capas | 10 °C | 120→80→40→0 mm a240/360/480 h |

La referencia12 °C ya calculada se conserva en
`resultados/planes_sin_extraccion/unica/malla_0.5_paso900/`.
Los otros tres casos separan efecto de preenfriamiento, de esquema de
protección y combinado. Añadir la tercera capa cambia espesor inicial
y escalonamiento; no atribuir sus resultados solo a uno de ambos.
No se asignan probabilidades a las tres decisiones alternativas.

## Propuesta de montaje a definir

- Laterales: madera18 mm, k0,158, con aislación exterior continua de
  tres capas40 mm, k0,042 de referencia para la alternativa reforzada.
- Cara superior expuesta: tres capas40 mm; no moldaje de madera sobre
  el hormigón. Coordinar instalación con terminación y curado. El modelo
  idealiza la cobertura desde activación del estrato: revisar demora real.
- Cubrir encuentros y juntas entre mantas sin huecos; proteger contra
  humedad, compresión y desplazamiento por viento mediante sistema de
  envoltura/fijación que confirme proveedor. No especificar producto sin ficha.
- Mantener la protección al retirar madera. El modelo conserva retiro
  de moldaje a72 h de edad como hipótesis: no es autorización estructural
  de desmolde. Debe existir soporte de aislación independiente del moldaje.
- Retirar una capa por etapa, según temperatura monitoreada, no solo
  por calendario. Los días10/15/20 son escenarios de simulación, no una
  recomendación universal. Verificar respuesta después de retirar todo.
- No colocar estas mantas entre hormigones que deben quedar unidos.
  La base permanece en contacto con el suelo equivalente y sin aislación.
  Un cambio bajo la fundación requeriría verificar compatibilidad estructural,
  transmisión de cargas y un detalle constructivo distinto: no se incluye.

El espesor total120 mm es una elección de sensibilidad con el mismo
material de referencia, no una solución recomendada por fabricante ni
un montaje temporal comprobado. Se conservan referencias documentadas en
`SUELO_PROTECCIONES.md`.

ACI incluye preenfriamiento y aislación en el control térmico:
[consulta técnica](https://www.concrete.org/frequentlyaskedquestions.aspx?faqid=892).
Más aislación puede retener calor y no resolver el punto frío junto al
suelo. Clasificar Tmax≤70 °C y ΔT≤20 K simultáneamente, con horizontes
336/600 h y extensión a672 h ante alertas; no ocultar máximos posteriores.

Reducir12→10 °C a60 m³/h requiere aproximadamente84,4 kW térmicos
adicionales de preenfriamiento sensible (ρ2476, cp1023), antes de ganancias
de transporte. No es consumo eléctrico ni extracción interior posterior.
La fuente prescrita por edad no cambia cinética al reducir T inicial:
conservar esta limitación al interpretar resultados.

## Ejecución personal

Se comprobaron fuentes, climas, máscara, construcción de capas y compilación
sin nuevas simulaciones térmicas. Desde la raíz, ejecutar los tres casos
(72 escenarios nuevos, referencia existente sin recalcular):

```powershell
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/controles_pasivos.py --ejecutar
```

Para partir solo por la combinación solicitada (24 escenarios):

```powershell
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/controles_pasivos.py --casos t10_tres_capas --ejecutar
```

Luego completar efectos aislados:

```powershell
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/controles_pasivos.py --casos t10_dos_capas t12_tres_capas --ejecutar
```

Sin argumentos solo imprime diseño; `--comprobar-insumos` no simula.
Parámetros en `controles_pasivos.json`. Las salidas están separadas en
`resultados/controles_pasivos/<caso>/malla_0.5_paso900/`, con matriz,
trazas y resumen. La procedencia registra configuración y capas; si
cambian, elegir nueva salida. Conservar archivos históricos.
Las diferencias heredadas contra comparadores publicados usan otras
condiciones; comparar aquí las métricas absolutas de cada caso.

## Cómo decidir después

Comparar ambos máximos, P_f a336 h y extendido, superficie crítica y
respuesta antes/después de retiros. Si domina la base, no seguir añadiendo
aislación lateral suponiendo que resolverá ese contacto. Confirmar malla,
tiempo y construcción real antes de recomendar una alternativa favorable.

## Resultado posterior: combinación10 °C y tres capas

El usuario ejecutó `t10_tres_capas`. Se verificaron24 pares únicos,
pesos que suman1, todas las vertidas a10 °C, retiro de las tres capas
a240/360/480 h, activación progresiva y extracción interior desactivada.
Hay horizontes600/672 h, sin alertas pendientes; residuo absoluto máximo
0,000157 J. Esta revisión no ejecutó simulaciones térmicas adicionales.

| Métrica | Referencia12 °C / dos capas | 10 °C / tres capas |
| --- | ---: | ---: |
| Tmax peor [°C] | 51,3334 | 49,4266 |
| ΔT peor hasta336 h [K] | 27,7584 | 24,5331 |
| P_f hasta336 h | 16/24=66,67% | 12/24=50% |
| ΔT peor extendido [K] | 34,8552 | 34,0111 |
| P_f extendido | 24/24=100% | 23/24=95,83% |

La combinación mejora, pero no cumple ni en14 días ni en el horizonte
extendido. No separar efectos de temperatura y protección sin los otros
dos casos preparados, todavía no ejecutados. Las probabilidades se
refieren al catálogo discreto y pesos asumidos, no a riesgo real medido.

El peor diferencial a336 h es M4_SS×ERA5-2023: Tmax48,6204 °C,
TminS25=24,0873 °C, punto frío próximo a la base en z=0,025 m.
La base no tiene mantas; reforzar solo laterales/superior no modifica
directamente su resistencia de contacto con el suelo. Esto identifica
un mecanismo que debe revisarse antes de seguir añadiendo protección.

El máximo extendido ocurre en el mismo escenario a572 h, tras retiro
final: Tmax45,1770 °C, TminS25=11,1660 °C, punto lateral z=0,975 m.
La máxima Tmax ocurre en M4_SS×ERA5-2025 a218,25 h. Una fila pasa
con ΔT19,9516 K, margen≈0,0484 K: no declarar clasificación robusta
sin refinamiento; la conclusión global de incumplimiento no depende de ella.

Siguiente decisión: completar efectos aislados si se necesita atribución;
revisar físicamente borde de suelo/base y limitaciones del reservorio,
sin elevar su temperatura ni resistencia solo para cumplir. Cualquier
aislación bajo una fundación requeriría solución estructural y constructiva
admisible, no la colocación arbitraria de mantas compresibles bajo cargas.

Revisión posterior del mecanismo y balance del borde:
[auditoría de base y suelo](AUDITORIA_BASE_SUELO.md).
