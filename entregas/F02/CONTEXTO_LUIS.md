# Contexto para Luis y su agente

## Encargo y base

Confirmar la implementación y confiabilidad numérica de la propuesta F02
del grupo 6. Benjamín cierra física/obra; Matías, escenarios y comparación.
El informe es conjunto. Leer `AGENTS.md`, la pauta
`Enunciados e Instrucciones/Enunciados/F02_DEFENSA_FINAL.txt` y
`entregas/F02/README.md` antes de modificar o calcular.

La rama hasta `6718163` está incorporada; avance publicado
`29c2fff608054b7cc91a7800b0586f3009547dd5`. Se conservan sus estudios de
estratos/encendido, verificaciones y resultados, pero corresponden a otra
configuración. La candidata nueva es única a 12 °C uniformes, h horario,
k=2, suelo 15 °C; sumidero U=5, referencia18 °C, tope15 kW, encendido
desde6 h de edad y apagado global432 h. D=10,613 h para colocar los
636,775 m³ a60 m³/h. Con 0,50 m/900 s y24 escenarios: Tmax46,2843 °C,
ΔTmax17,3681 K, P_f=0 hasta600 h, sin alertas. Solo esta única tiene
resultados de la familia nueva; no es todavía una confirmación fina.

## Qué falta determinar y por qué

| Tarea del reparto | Falta determinar | Por qué importa |
| --- | --- | --- |
| L1: activación | Efecto de pasar de bloque instantáneo a colocación progresiva con edades propias, usando ahora 12 °C/15 kW/h horario | La única tarda físicamente 10,613 h. Activarla completa al inicio cambia fuente, exposición y pérdidas durante la ejecución. Ya existen herramientas históricas para aprovechar, no se parte de cero. |
| L1/B2: encendido | Efecto de la regla construible de circulación acordada con Benjamín | El modelo permite refrigerar desde6 h de edad; no debe atribuir enfriamiento a hormigón todavía no colocado ni asumir un circuito viable sin revisión. |
| L2: espacio | Diferencia de métricas y clasificación entre0,50 y0,25 m manteniendo paso máximo900 s | La sensibilidad anterior corresponde a otras condiciones. La candidata debe tener su propia evidencia de resolución, especialmente para S25 a25 mm. |
| L2: tiempo | Diferencia entre pasos máximos900 y450 s con la misma malla y condiciones | Refinar malla y tiempo juntos no permite separar sus efectos. Informar también pasos efectivos limitados por estabilidad. No prometer orden de convergencia con solo dos niveles. |
| L3: algoritmo | Coherencia de balance, estabilidad, interfaces activas, edad de fuente/retiros y evaluación S25 | El dominio térmico incluye solo hormigón colocado. El diferencial usa Tmax y TminS25 del mismo instante; una interfaz cubierta deja de ser exterior. Una suma de energía coherente no prueba por sí sola exactitud espacial. |
| L4: robustez | Si rangos físicos defendibles de k/suelo/h/protecciones cambian la clasificación o la elección nueva | Los estudios históricos identifican hipótesis influyentes, pero sus probabilidades no se transfieren a esta candidata. No hace falta repetir indiscriminadamente todas las combinaciones. |
| L5: matriz final | Resultados completos de alternativas competitivas bajo controles, escenarios y pesos comunes | Comparar planes con distinta T inicial, h o capacidad de extracción atribuiría al cronograma efectos que no le corresponden. Coordinar selección y costo con Matías. |
| L5: horizonte | Si están capturados los máximos de todas las filas finales | El peor ΔT de la candidata ocurre a380 h, después de14 días. Evaluar336 h e informar extensión; resolver alertas antes de clasificar como cumplimiento. |
| L6: reproducción | Que otra máquina reconstruya insumos y ejecute el mismo caso con configuración y hashes identificables | La defensa debe ser reproducible sin depender del estado de Blender ni de una caché personal. Mantener IFC→geometría/propiedades→máscara→solver propio. |

## Archivos y precauciones

- Entrada nueva: `casos/sensibilidad_h/colocacion_12c.py` y su JSON.
  `--comprobar-insumos` solo lee; `--ejecutar` calcula. Los cuatro planes
  están habilitados; sin `--casos`, la ejecución solicita los cuatro.
- Matriz existente:
  `resultados/controles_12c/unica_15kw_12c/malla_0.5_paso900/unica_15kw_12c.json`.
- Estudiar `casos/f02_verificaciones/README.md` para estratos y encendido;
  `casos/sensibilidad_h/README.md`, `VIENTO.md` y `CONTROLES_OBRA.md` para
  adaptaciones, referencias previas y comandos.
- La base congelada6718163 se reconstruye por Git en
  `.venv/cache/f02_sensibilidad_h`. No editar la caché para crear una variante
  silenciosa. Los refinamientos requieren referencias compatibles antes de
  lanzar; una opción CLI no garantiza que todas las referencias ya existan.
- `.gitattributes` preserva bytes de scripts/JSON con hashes. Si se modifica
  un script o configuración con procedencia distinta, elegir salida nueva;
  no editar métricas ni hashes para forzar reanudación.

## Entrega y coordinación

Entregar tabla de resolución/costo/cambios/clasificación, evidencia de
balance y caso conocido, matrices completas, configuraciones y comandos.
Guardar máximos con ubicación/instante y campos/trazas necesarios para
Matías. Benjamín debe fijar controles construibles y rangos; Matías, la
familia y pesos antes de las matrices finales. Mientras tanto se puede
auditar código y preparar verificaciones.

Rama sugerida: `codex/luis-verificacion-numerica`. Coordinar cambios a
ejecutores compartidos; conservar resultados originales e IFC de práctica.
El usuario prefiere ejecutar personalmente variantes: preparar comandos
y estimar costo antes de correr salvo autorización expresa.
