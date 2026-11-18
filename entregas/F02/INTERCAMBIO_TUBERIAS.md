# Qué intercambio hormigón–tubería–agua representa el modelo

La refrigeración tiene una interacción térmica **equivalente** con el hormigón.
Se conserva la idealización docente autorizada de agua uniforme a18°C.
No se calculó una red térmica explícita de hormigón, pared de tubo y agua.

Para una celda asignada a un ramal abierto:

\[
P_i^{\mathrm{bruta}}=U_vV_i\max(T_i-18,0),\qquad U_v=5\ \mathrm{W/(m^3K)}.
\]

El controlador limita además la extracción de cada paso para impedir que
por sí sola cruce18°C. Si la suma supera15kW, reduce proporcionalmente
todas las potencias. La potencia total puede ser menor o cero. El balance
del hormigón descuenta esa energía en cada actualización.

Los nueve trazados determinan cobertura previa, puntos de muestreo y
asignación de la zona interior refrigerable414,016m³. Cada circuito abre
con mínima monitoreada≥19°C y cierra si un tramo llega≤18°C. Es un control
sobre celdas de hormigón próximas al trazado; no una temperatura de pared
o del agua calculada a lo largo de cada tubo.

## Lo que el caudal no determina

Los18L/min por ramal abierto y162L/min con bypass son datos operativos
del anteproyecto y se registran en la historia. No entran en la fórmula
de extracción ni calibran Uv. Cambiar solo ese dato no produce en este
solver el cambio de transferencia que tendría una red real.

Uv no es un coeficiente de película interior: este último tendría unidades
W/(m²K) y multiplicaría superficie de tubo. Tampoco se deduce Uv del
diámetro interior de cálculo25mm o de los aproximadamente639m de trazado.

## Qué requeriría una representación física detallada

Se necesitarían material, diámetros y espesor de pared, contacto con el
hormigón, resistencia térmica circundante, coeficiente de convección
interior y balance del agua entre tramos. La transferencia tendría que ser
compatible simultáneamente con esas resistencias y con la capacidad de
transportar energía del agua:

\[
P_{\mathrm{agua}}=\dot m c_{p,w}(T_{\mathrm{salida}}-T_{\mathrm{entrada}}).
\]

Con los nueve ramales abiertos,162L/min≈2,7kg/s y15kW darían un aumento
medio de aproximadamente1,33K usando cp del agua≈4186J/(kgK). Este balance
de referencia no prueba que los tubos transfieran15kW ni es una salida
del solver. El agua uniforme18°C corresponde a un reservorio ideal, no
a afirmar entrada18°C/salida18°C con extracción finita en una red real.
Faltan comprobación hidráulica y rechazo de calor en un equipo.

## Cómo se acopla con radiación

La convección, solar y onda larga cambian el campo del hormigón. Eso cambia
las diferenciasT−18 y las temperaturas muestreadas por el controlador, por
lo que los circuitos pueden abrir/cerrar en momentos distintos y extraer
otra energía. El balance incluye ambos efectos simultáneamente. No se
añadió radiación a una historia térmica ya terminada.

Las matrices nuevas mantienen Uv y el tope para aislar el cambio de borde.
No se sustituyó el supuesto equivalente por una transferencia de tubos
calibrada. Cumplimiento de criterios térmicos dentro del catálogo y
validación de una instalación real son conclusiones distintas.

Implementación: `casos/sensibilidad_h/control_circuitos.py`, método
`ControlCircuitos.extraer`; acoplamiento en cada paso del solver por
`adaptar`. El ejecutor actualizado es `familia_radiacion.py` y las
[ecuaciones del modelo](ECUACIONES_MODELO_VIGENTE.md) definen el balance.
