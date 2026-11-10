# E10 — Entorno, moldaje y clima

Revisión oral del miércoles 11 de noviembre, 10:30–13:20. Canvas: solo repositorio
y SHA completo del commit publicado y acordado por el grupo. Esta guía es para
preparar la demo, no es un informe para subir.

## Recorrido de la demo

Desde la raíz de la rama Semana 4, con el entorno Python del proyecto activado:

~~~bash
python -B casos/e10/ejecutar.py --demo
python -B casos/e10/ejecutar.py --snapshot datos/clima/forecasts/20261110T190042897941Z_44b1a950.json --inicio 2026-11-27T10:00:00-03:00
~~~

La primera ejecución compara la misma celda y el mismo aire antes y después de
los retiros. La segunda reabre un pronóstico real sin internet, informa la
cobertura de 14 días y usa la temperatura de una hora disponible como entrada
de Robin. Para una descarga nueva, sustituir `--snapshot <archivo>` por
`--descargar`. No se instala nada. Si aún usas el entorno WSL de la carpeta
original, cambia `python` por `../Proyecto-2-MCOC/.venv/bin/python`.

| Mostrar | Archivo y función |
|---|---|
| Bordes clásicos | [bordes_termicos.py](../../desarrollo/mcplan/bordes_termicos.py), `coeficientes_cara` |
| Suelo, capas y onda corta | [entorno_termico.py](../../desarrollo/mcplan/entorno_termico.py), `borde_suelo`, `borde_aire`, `Capa` |
| Cliente y trazabilidad | [clima.py](../../desarrollo/mcplan/clima.py), `url_pronostico`, `guardar_snapshot`, `cargar_snapshot`, `cobertura` |
| Clima → potencia en la cara | [ejecutar.py](../../casos/e10/ejecutar.py), `comparar_bordes` |
| Evidencia reproducible | [Snapshot real del 10 de noviembre](../../datos/clima/forecasts/20261110T190042897941Z_44b1a950.json) y [pruebas](../../desarrollo/tests/test_e10.py) |

## Qué explicar

- **¿Dónde entra el aire?** En Robin. Con signo positivo hacia el hormigón:
  `P = H (T_aire - T_celda)`. El solver cartesiano recibe potencias en W,
  no temperaturas del aire impuestas al centro de la celda. Para aire frío,
  esta potencia es negativa si el hormigón está más caliente.
- **¿Qué hace el viento?** Se descarga a 10 m en m/s. Puede alimentar una
  correlación de convección `h(v)` con altura, orientación y exposición
  justificadas. En esta primera demo se deja `h=5 W/(m²·K)` constante;
  se conserva el viento sin fingir que ya modifica `h`.
- **¿Cómo se modela moldaje y aislación?** Cada capa aporta `R=d/k` en m²·K/W.
  Se suma media celda, las capas activas y la película exterior:
  `H=A/(δ/k_hormigón + Σ d/k + 1/h)`. Sin capa se recupera el Robin anterior.
- **¿Qué cambia al desmoldar?** Se quita solo la resistencia de la capa retirada.
  Si queda aislación, su resistencia sigue. Con la misma diferencia térmica,
  el flujo aumenta en magnitud; si el aire está frío, aumenta la pérdida.
  En la demo, a **71,999 / 72 / 96 h** de edad, la potencia de aire pasa de
  **−5,086 → −5,814 → −19,231 W** por cara. Las edades 72 y 96 son supuestos
  didácticos desde la colocación de cada vertida; no se interpretó ni cambió
  `RetiroMoldaje_h` del IFC.
- **¿Cómo entra el suelo?** En la base se usa conducción hasta un reservorio de
  suelo de temperatura prescrita a una profundidad dada. La resistencia
  por área es `δ/k_hormigón + R_contacto + L_suelo/k_suelo`. No hay película de
  aire ni solar en esa cara. No es un modelo transitorio del suelo.
- **¿Qué es el flujo solar?** Irradiancia incidente en W/m². La parte absorbida
  es `absortancia × irradiancia`, que entra al balance de la superficie.
  La GHI del snapshot es horizontal y promediada sobre la hora que termina
  en la marca UTC. En la demo se usa solo en la cara superior horizontal;
  no se copia a paredes o al suelo.
- **¿Cómo se evita contar dos veces?** Se usa aire real con un `h` convectivo
  (sin radiación incluida) y se suma la onda corta absorbida **una vez** en
  la cara exterior. El balance reparte ese calor entre la celda y el aire.
  No se aplica además una temperatura de aire equivalente que ya incluya
  la misma radiación. Onda larga no implementada.
- **Forecast / reanálisis / observación:** un forecast predice el futuro desde
  una corrida; un reanálisis reconstruye el pasado con un modelo que asimila
  observaciones; una observación es una medición de estación o sensor. No se
  mezclan esas procedencias bajo la etiqueta de pronóstico.
- **¿Por qué guardar los pronósticos anteriores?** Se actualizan con nueva
  información. Un snapshot permite repetir la decisión con los datos
  disponibles en ese momento, comparar plazos y evaluar el error a futuro.
  El archivo conserva respuesta, proveedor, modelo solicitado, fecha/hora de
  descarga, coordenadas pedidas, unidades, variables y marcas cubiertas.
  Fecha de descarga no equivale a hora de inicialización del modelo.
- **¿Qué pasa si aún no cubre los 14 días posteriores al 27?** La fecha/hora
  del comando es solo la ventana de la pregunta, no una fecha de obra aprobada.
  La descarga del 10 de noviembre trae marcas del **10 al 25 de noviembre UTC**:
  cubre **0 de 336 horas** de la ventana. La política propuesta es descargar de
  nuevo al acercarse la fecha y, si queda una cola sin cubrir, usar bloques
  horarios de reanálisis de fechas análogas de la misma estación del año,
  conservando juntas T, viento y solar y etiquetando la procedencia y el empalme.
  Si no hay cobertura desde el inicio, el escenario es totalmente histórico
  y provisional. El cliente de E10 **reporta** el faltante; la demo de E10 no implementa
  ese relleno. [E12](../../Reportes/Reporte_E12.md) ejecuta el escenario histórico completo.

## Fuente y alcance

[Open-Meteo Forecast API](https://open-meteo.com/en/docs), modelo solicitado
`gfs_global` (NCEP GFS), sitio del grupo 6 Parque Eólico El Rosal
(**−37,277929; −72,368271**). El primer snapshot conserva 384 marcas horarias
en UTC. La API devuelve también las coordenadas de la celda del modelo; no se
confunden con las pedidas. El código no sobrescribe snapshots previos.

La demo usa propiedades y capas didácticas y calcula la potencia de una cara
con los datos del pronóstico. [E11](../E11/README.md) conecta la serie
meteorológica y los cambios de contorno al solver 3D de la fundación.

Comprobación: **550 pruebas Python aprobadas** en la revisión, incluidas 15 de E10 y siete del solver integrado de Semana 4. También se
ejecutó el caso sintético y se descargó y releyó el snapshot real sin errores.
