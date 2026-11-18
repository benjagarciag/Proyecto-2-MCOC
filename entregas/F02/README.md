# F02 — estado integrado y siguiente trabajo

Grupo 6: Benjamín García, Luis Noriega y Matías Stierling. Actualizado el
18-11-2026. [Pendientes y reparto entre los tres](PENDIENTES_EQUIPO.md).
[Pauta oficial F02](../../Enunciados%20e%20Instrucciones/Enunciados/F02_DEFENSA_FINAL.txt)
· [Pauta E13](../../Enunciados%20e%20Instrucciones/Enunciados/E13_W5_MIERCOLES_INCERTIDUMBRE.txt).

## Qué se incorporó

Se integró la rama `f02-verificaciones-complementarias`, hasta
`6718163118123c4b05667b91ad5b4d50124dcf2d`, conservando sus verificaciones,
resultados y documentos. Encima se incorporaron las sensibilidades y decisiones
de la revisión conjunta. La [evidencia del compañero](../../casos/f02_verificaciones/README.md)
describe su configuración original, con h constante y tope 12 kW.
No reemplaza las comprobaciones pendientes del nuevo caso.

Publicación de este avance: mensaje **Avance miercoles entrega final**.
Identificar su SHA con:

```powershell
git log -1 --format=%H --grep="^Avance miercoles entrega final$"
```

Ese SHA identifica el avance integrado, no una defensa terminada.

## Candidata actual y alcance

Una operación continua; **12 °C de colocación en todo el hormigón**;
enfriamiento volumétrico equivalente U=5 W/(m³ K), referencia 18 °C,
tope 15 kW, activación desde 6 h de edad y apagado global a 432 h.
Se conserva k=2 W/(m K), suelo a 15 °C con resistencia equivalente,
protecciones y retiros descritos en los documentos físicos.
Se usa h horario calculado del viento; su media 17,09 W/(m² K) es una
referencia y no sustituye la historia horaria en esta candidata.

| Resolución / catálogo | Peor Tmax | Peor ΔT | P_T / P_Δ / P_f | Horizonte |
| --- | ---: | ---: | --- | --- |
| 0,50 m / paso máximo 900 s; 8 curvas × 3 climas, pesos 1/24 | 46,2843 °C | 17,3681 K | 0 / 0 / 0 % | 600 h, sin alertas |

[Matriz de la candidata](../../resultados/controles_12c/unica_15kw_12c/malla_0.5_paso900/unica_15kw_12c.json).
El peor diferencial ocurre en M4_SS × ERA5-2025 a 380 h, después de las
336 h iniciales; no truncar ahí la evaluación. Cumple el modelo discreto en
esta resolución. **Faltan confirmación numérica de esta configuración,
constructibilidad del control y comparación final con condiciones comunes.**
No implica riesgo real cero ni ausencia demostrada de fisuras.

Inicio común: 19-11-2026 a las 10:00, America/Santiago (UTC−03).
ERA5 2023/24/25 se alinea por hora relativa; son historias del sitio,
no pronósticos de la obra. Pesos y admisibilidad de las fuentes siguen
siendo hipótesis que se deben defender.

## Qué significan las 10,61 horas

El volumen geométrico IFC es 636,775 m³. Con capacidad total efectiva de
60 m³/h y sin interrupciones, **toda la fundación tarda 10,613 h** si se
ejecuta como una sola operación continua. No son 10,61 h por vertida ni
el tiempo de enfriamiento posterior. La capacidad de suministro es un
supuesto constructivo pendiente de confirmación.

| Plan | Inicios relativos [h] | Fin de colocación D [h] |
| --- | --- | ---: |
| Única | 0 | 10,613 |
| Rápida | 0 / 3 / 6 / 12 / 15 | 15,640 |
| Referencia | 0 / 6 / 12 / 18 / 24 | 24,640 |
| Lenta | 0 / 9 / 18 / 27 / 36 | 36,640 |

En los planes de cinco vertidas, las duraciones V/60 son aproximadamente
2,460 / 2,460 / 3,570 / 1,482 / 0,640 h. D incluye los intervalos
entre inicios. El solver activa bloques instantáneamente en la candidata
actual; se debe contrastar con la activación progresiva ya disponible.

## Documentos y evidencias de revisión

| Tema | Documento | Resultados guardados |
| --- | --- | --- |
| h y refinamiento previo | [Diseño y comandos](../../casos/sensibilidad_h/README.md) | [Sensibilidad h](../../resultados/sensibilidad_h/) |
| Viento y h horario | [Fundamento](../../casos/sensibilidad_h/VIENTO.md) | [Comparación](../../resultados/sensibilidad_h/viento/) |
| k y propiedades | [Conductividad](../../casos/sensibilidad_h/CONDUCTIVIDAD.md) | [Sensibilidad k](../../resultados/sensibilidad_k/) |
| Modelo físico | [Balance e hipótesis](../../casos/sensibilidad_h/MODELO_FISICO.md) | — |
| Suelo y protecciones | [Revisión](../../casos/sensibilidad_h/SUELO_PROTECCIONES.md), [sensibilidad](../../casos/sensibilidad_h/SENSIBILIDAD_SUELO.md) | [Suelo](../../resultados/sensibilidad_suelo/), [contraste ERA5](../../resultados/revision_suelo_protecciones/) |
| 15 kW y 12 °C | [Controles de obra](../../casos/sensibilidad_h/CONTROLES_OBRA.md) | [15 kW previo](../../resultados/controles_obra/), [12 °C exactos](../../resultados/controles_12c/) |

Los estudios anteriores conservan 12 kW o temperatura 12,231833 °C en la
única, según su procedencia. No trasladar sus riesgos/refinamientos a la
candidata nueva. Los cuatro planes a 12 °C/15 kW están configurados;
solo la única ha sido ejecutada en esa familia.

## Reproducción desde la raíz

Usar un clon Git con historial y las dependencias de `requirements.txt`.
Los estudios reconstruyen automáticamente su base congelada mediante
`git archive 6718163` en `.venv/cache/f02_sensibilidad_h`; no hay que compartir
la caché personal. El solver original y las propiedades IFC no se sobrescriben.
La adaptación horaria, parámetros y hashes se registran junto a los resultados.
`.gitattributes` conserva los bytes de scripts y JSON de estos estudios:
la conversión automática de finales de línea invalidaría los hashes de reanudación.

Lectura/verificación sin simulaciones:

```powershell
.\.venv\Scripts\python.exe -X utf8 -B casos/f02_verificaciones/verificar.py
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/colocacion_12c.py --comprobar-insumos
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/colocacion_12c.py
```

Ejecución explícita de un plan (24 escenarios; conserva resultados compatibles):

```powershell
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/colocacion_12c.py --ejecutar --casos unica_15kw_12c
```

Comparación de los cuatro planes con los mismos 12 °C/15 kW:

```powershell
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/colocacion_12c.py --ejecutar
```

La tabla generada usa como referencia histórica la única de 12 kW a
12,231833 °C: los cambios respecto de ella pueden incluir temperatura,
control y cronograma. Para comparar planes nuevos, usar sus columnas
absolutas y sus configuraciones, sin atribuir todo el cambio a una sola causa.
Los comandos de ejecución se dejan al equipo; la integración no requiere
nuevas corridas. El [reparto](PENDIENTES_EQUIPO.md) contiene los cierres
que faltan para preparar la defensa del 19 de noviembre, 10:30–12:30.
