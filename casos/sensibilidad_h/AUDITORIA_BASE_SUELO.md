# Revisión del borde base–suelo en la candidata sin tuberías

## Qué se revisó

Lectura de la implementación y de los resultados existentes de
`t10_tres_capas`, sin nuevas simulaciones. Las adaptaciones horarias y
de ausencia de extracción preservan el borde original. Sus parámetros
proceden de la configuración congelada6718163, no de un estudio geotécnico.

## Condición realmente aplicada

`desarrollo/mcplan/termica_fundacion.py` identifica suelo solo en caras
inferiores cuyo plano coincide con z=0. Las demás superficies exteriores
se tratan como expuestas al aire según orientación/capas. Los laterales
no están en contacto con suelo en este escenario de excavación abierta.

`desarrollo/mcplan/entorno_termico.py:borde_suelo` usa:

```
H = A / [(Δz/2)/k_hormigón + R_contacto + L_equivalente/k_suelo]
potencia hacia el hormigón = H (T_reservorio − T_celda)
```

Parámetros: T_reservorio15 °C, k_suelo1,2 W/(m K), L_equivalente0,5 m,
contacto adicional0. La media celda de hormigón sí se incluye. En
Δz0,50 m, k_hormigón2: R_suelo0,4167 m² K/W, R_total0,5417 m² K/W,
conductancia por área1,8462 W/(m² K). No se impone la cara del hormigón
a15 °C: la resistencia permite que su temperatura sea mayor o menor.
TminS25 es hormigón a25 mm, no la temperatura del reservorio.

No se encontró en esta revisión un error de signo o ausencia de media
celda en la fórmula. Eso no valida los valores elegidos ni la reconstrucción
S25 en malla gruesa. La auditoría no es una validación experimental.

## Qué muestran los resultados a336 h

Escenario M4_SS×ERA5-2023, peor diferencial a14 días de esta candidata:

| Magnitud | Valor |
| --- | ---: |
| Tmax simultánea | 48,6204 °C |
| TminS25 | 24,0873 °C |
| ΔT | 24,5331 K |
| PuntoS25 crítico | aproximadamente(-3,75,-8,75,0,025) m |
| Energía neta cedida al suelo | 3,2228 MWh térmicos |
| Energía neta cedida al aire | 1,3959 MWh térmicos |
| Fracción del suelo entre esas pérdidas netas | 69,78% |

Estas energías son integrales de toda la fundación y no de un punto.
Inicialmente el hormigón se coloca a10 °C y el reservorio a15 °C:
el suelo aporta calor al principio. Posteriormente el signo se invierte.
El balance contabiliza ambos sentidos. No confundir esos intercambios
con extracción artificial interior, que está desactivada.

El pequeño residuo energético (≈0,000132 J a336 h) indica cierre del
balance numérico implementado; no certifica la física del borde.

## Limitación física identificada

El reservorio permanece a15 °C aunque absorbe calor. No hay celdas de
suelo, capacidad térmica ni temperatura de interfaz resuelta como estado
del terreno. L=0,5 m es longitud equivalente de transferencia, no un
espesor real de suelo modelado ni profundidad geotécnica confirmada.

En un terreno transitorio, el suelo próximo a la fundación puede
calentarse y redistribuir el calor. La importancia y sentido del error
del borde equivalente dependen de tiempos, propiedades, geometría y
condiciones lejanas. No se ha demostrado que el reservorio sobreestime
siempre la pérdida, ni que corregirlo haga cumplir el plan.

Referencia de modelos transitorios del terreno por diferencias finitas:
[EnergyPlus, Engineering Reference](https://bigladdersoftware.com/epx/docs/23-2/engineering-reference/ground-heat-transfer-calculations-using-site.html).
Se consulta como fundamento, sin sustituir el solver propio del curso.

## Qué está respaldado y qué falta

- Temperatura inicial15 °C: supuesto de referencia. ERA5 conservado
  muestra órdenes de magnitud dependientes de profundidad y año; no
  identifica la temperatura bajo la excavación, cuya profundidad respecto
  del terreno original no está confirmada.
- k_suelo1,2 y contacto: no hay datos geotécnicos térmicos locales que
  validen estos valores. Emplantillado, humedad o membrana reales deben
  identificarse antes de asignarles una resistencia adicional.
- Las mantas no cubren la base. No colocar lana de vidrio de edificación
  bajo una fundación cargada como simple cambio térmico; cualquier capa
  requiere compatibilidad estructural y constructiva demostrada.
- Existe sensibilidad de T_suelo/R en `SENSIBILIDAD_SUELO.md`, pero usó
  una configuración anterior con extracción. No transfiere sus riesgos
  a10 °C y tres capas sin extracción.

## Siguiente comprobación recomendada

Contrastar reservorio fijo con suelo transitorio, manteniendo la candidata,
fuentes, clima y controles comunes. Un primer modelo propio por columnas
1D verticales bajo cada cara basal permitiría almacenar calor en el
terreno y conservar flujos iguales/opuestos; omitiría difusión horizontal
y efectos tridimensionales del perímetro, limitación relevante aquí.

Antes de implementarlo, fijar k, capacidad volumétricaρc, perfil térmico
inicial, profundidad y condición inferior como datos o hipótesis explícitas.
Comprobar sensibilidad de dominio/malla/tiempo y balance conjunto suelo+
hormigón; verificar un caso conocido de conducción/contacto. No introducir
ρ y cp silenciosamente ni ajustar una nueva T hasta obtener cumplimiento.

Otra opción preliminar de menor costo es repetir la sensibilidad de suelo
en la candidata actual; cuantifica dependencia de supuestos pero no valida
ni sustituye el modelo transitorio. Aún no se implementó ni ejecutó este
contraste como parte de la auditoría.

Actualización: se implementó el contraste y se verificó con casos sintéticos,
sin lanzar la fundación. Diseño, limitaciones y comandos en
[suelo transitorio](SUELO_TRANSITORIO.md).
