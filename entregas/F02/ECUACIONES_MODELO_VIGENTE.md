# Modelo vigente F02: incorporación de radiación

Se adopta **solar y onda larga activas** en todas las caras expuestas al aire.
La entrada de ejecución es `casos/sensibilidad_h/modelo_f02.py` y la selección
explícita está en [MODELO_VIGENTE.json](MODELO_VIGENTE.json). Se usa el mismo
motor que produjo los resultados auditados de la sensibilidad; sus archivos
con hash permanecen intactos. Los modelos anteriores quedan como antecedentes.

## 1. Balance dentro del hormigón

\[
\rho c\frac{\partial T}{\partial t}
=\nabla\cdot(k\nabla T)+\dot q_{\mathrm{hid}}-\dot q_{\mathrm{frío}}.
\]

La hidratación agrega calor y la refrigeración lo extrae. Ambas fuentes están
en W/m³. El sol se incorpora como flujo en las caras exteriores, en W/m²;
no se distribuye como otra fuente volumétrica de hidratación. Las nuevas capas
se activan a 12 °C según el cronograma de once capas adoptado.

El sumidero sigue siendo equivalente: U = 5 W/(m³ K), agua uniforme a 18 °C,
tope global de 15 kW y control por circuito con umbrales 19/18 °C y cobertura.
La incorporación de radiación no representa una nueva validación de las tuberías.

## 2. Balance en el exterior de la protección

Se define flujo positivo **entrando hacia el hormigón**. En cada cara se resuelve:

\[
\underbrace{\frac{T_s-T_i}{R_i(t)}}_{q''_{\mathrm{hacia\ celda}}}
=\underbrace{h(t)[T_a(t)-T_s]}_{\mathrm{convección}}
+\underbrace{\alpha_s I_f(t)}_{\mathrm{solar}}
+\underbrace{\varepsilon\sigma
\left[F_{\mathrm{cielo}}T_{\mathrm{cielo},K}^{4}
+(1-F_{\mathrm{cielo}})T_{a,K}^{4}-T_{s,K}^{4}\right]}_{\mathrm{onda\ larga}}.
\]

- Tᵢ: temperatura del centro de la celda de hormigón.
- Tₛ: temperatura de la superficie **exterior de la última protección**. Si
  no quedan protecciones, coincide con la cara del hormigón.
- Tₐ: temperatura del aire; Iᶠ: irradiancia solar que llega a esa orientación.
- αₛ = 0,6: fracción solar absorbida; ε = 0,9: emisividad de onda larga.
  Son hipótesis del acabado exterior equivalente, no propiedades medidas.
- σ = 5,670374419 × 10⁻⁸ W/(m² K⁴). Las temperaturas de los términos a la
  cuarta potencia se convierten a kelvin: Tᴋ = T[°C] + 273,15.
- F_cielo = 1 arriba, 0,5 en vertical y 0 abajo; se aplica únicamente en
  caras expuestas al aire. El resto de la vista se idealiza a Tₐ.

Si el aire es más frío que la protección, la convección extrae calor. La
solar absorbida agrega calor. La onda larga extrae calor cuando el entorno
radiativo efectivo es más frío que la superficie; su signo se calcula,
no se impone siempre negativo. El balance permite que el sol caliente una
cara más que el núcleo y que el cielo enfríe la superficie durante la noche.

El coeficiente conserva el viento histórico y el perfil de altura adoptado:

\[
v_2(t)=v_{10}(t)\left(\frac{2}{10}\right)^{0.14},
\qquad h(t)=5.7+3.8v_2(t).
\]

h representa convección. No se incorpora la onda larga dentro de h además
de sumarla explícitamente en el balance.

## 3. Cómo actúan madera y mantas

\[
R_i(t)=\frac{d_i}{k_c}
+\sum_{\ell\ \mathrm{vigente}}\frac{e_\ell}{k_\ell}
\quad [\mathrm{m^2 K/W}],\qquad d_i=\frac{\Delta x}{2}.
\]

La resistencia incluye media celda y las protecciones que permanecen instaladas
en esa cara según la edad de su capa. La madera lateral de 18 mm y k = 0,158
se retira a 72 h. Cada manta tiene 40 mm y k = 0,042, con retiros a 240 y 360 h.
En caras superiores expuestas se usan las mantas; en las laterales, madera y
mantas mientras correspondan. Entre celdas de hormigón en contacto se aplica
conducción, no un contorno radiativo. El contacto con suelo conserva su modelo
de conducción al reservorio de 15 °C.

La radiación actúa sobre el exterior de las mantas y parte de esa energía
vuelve al ambiente. Solo el flujo neto transmitido por R entra al hormigón.
La resistencia cambia al retirar una protección; no se cambia su espesor
de forma gradual. Las protecciones conservan el supuesto previo de resistencia
sin almacenamiento de calor propio.

## 4. Datos solares y cielo radiativo

La horizontal superior recibe GHI. Para una cara vertical expuesta, con difusa
isotrópica y albedo del terreno a_g = 0,2:

\[
I_f=\mathrm{DNI}\max(0,\mathbf{s}\cdot\mathbf{n}_f)
+\frac{\mathrm{DHI}}2+\frac{a_g\,\mathrm{GHI}}2.
\]

La directa se anula cuando el sol está bajo el horizonte. La posición solar
usa las coordenadas exactas del grupo y el punto medio del intervalo horario.
Las medias radiativas de la hora precedente se asignan al intervalo que
representan. Se conserva la suposición +x este, +y norte y exposición sin
sombras. No es una validación del apantallamiento real ni de la geometría
solar de superficies inclinadas representadas por escalones cartesianos.

Se estima temperatura efectiva del cielo mediante:

\[
\varepsilon_{\mathrm{cielo}}=
\left[0.787+0.764\ln\left(\frac{T_{\mathrm{rocío},K}}{273}\right)\right]
\left(1+0.0224N-0.0035N^2+0.00028N^3\right),
\]
\[
T_{\mathrm{cielo},K}^{4}=\varepsilon_{\mathrm{cielo}}T_{a,K}^{4}.
\]

N es nubosidad en décimas de cielo (0–10); se usa nubosidad total ERA5 como
aproximación de nubosidad opaca. La implementación limita ε_cielo a [0,1].
Es una estimación con punto de rocío y nubes, no una observación infrarroja.
La ε_cielo atmosférica y la ε = 0,9 superficial son propiedades distintas.

## 5. Resolución y actualización de la celda

Para cada paso se conoce Tᵢ y se busca Tₛ con Newton, resolviendo el balance
no lineal por el término Tₛ⁴. Escribiendo F(Tₛ) como el lado izquierdo del
balance superficial menos el derecho, la iteración es:

\[
T_s^{(m+1)}=T_s^{(m)}-
\frac{F(T_s^{(m)})}{1/R_i+h+4\varepsilon\sigma(T_s^{(m)}+273.15)^3}.
\]

Luego se calcula P_f = A_f q''_f y se actualiza:

\[
\rho cV_i(T_i^{n+1}-T_i^n)
=\Delta t\left[\sum_jG_{ij}(T_j^n-T_i^n)
+\sum_{f\in\partial i}A_f q_f''-P_{\mathrm{frío},i}\right]
+E_{\mathrm{hid},i}^{n\to n+1}.
\]

Gᵢⱼ = kA/Δx entre vecinos. La energía de hidratación se integra en el
intervalo con las curvas tabulares; no se reemplaza por una fuente solar.
La conducción del suelo también entra en la suma de flujos de contorno.
Se conserva Euler explícito y un límite de estabilidad conservador para
la conductancia no lineal, además del paso máximo solicitado.

Para medir temperatura de cara del **hormigón**, se reconstruye:

\[
T_{f,c}=T_i+q''\frac{d_i}{k_c},\qquad
T_{S25}=T_i+q''\frac{d_i-0.025}{k_c}.
\]

Así se distinguen el exterior de la manta y los 25 mm bajo la superficie del
hormigón. El criterio sigue siendo:

\[
\Delta T(t)=T_{\max,\Omega}(t)-T_{\min,S25}(t),\qquad 0\le t\le336\ \mathrm{h}.
\]

Se resta en cada instante y después se maximiza en el tiempo. No se resta
la máxima histórica de una curva y la mínima histórica de otra.

## Ejecución y evidencia adoptada

Desde la raíz:

```powershell
# Estado y comprobación de integridad, sin simulaciones
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/modelo_f02.py
# Verificaciones físicas y numéricas pequeñas
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/modelo_f02.py --verificar
# Matriz nominal con radiación por defecto; reutiliza piezas compatibles
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/modelo_f02.py --ejecutar
# Un caso fino explícito
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/modelo_f02.py --ejecutar --escenario M4_SS ERA5-2024 --malla 0.2 --paso-max 300
```

Resultados vigentes: [comparacion completa](COMPARACION_CIRCUITOS_FINAL.md). Cuatro matrices gruesas y matriz fina completa de la candidata,24pares cada una, a336h. Candidata fina: Tmax47,0322C y DeltaT15,7202K. Los tres contrastes temporales y seis finos de otras tasas son selectivos. No se asigna riesgo fino global a otras tasas.

La refrigeracion conserva [el intercambio equivalente](INTERCAMBIO_TUBERIAS.md). La pared del tubo, pelicula interior y agua axial no estan resueltas. El seguimiento posterior conserva excedencias y picos pendientes y no acredita liberacion termica despues de14dias.

Para la comparacion de cuatro ritmos se usa la misma entrada con `--comparar-planes --ejecutar`. La matriz fina completa se consulta/reproduce con `--malla 0.2 --ejecutar`. El ejecutor `familia_radiacion.py` permite fases base/fina/temporal/alternativas para336h, sin ejecutar nada sin `--ejecutar`. Los resultados compatibles ya calculados se conservan.

Fuentes de formulación: [balance exterior de EnergyPlus](https://energyplus.readthedocs.io/en/stable/guides/engineering-reference/3.5-outside-surface-heat-balance.html),
[cielo radiativo](https://energyplus.readthedocs.io/en/stable/auxiliary-programs/auxiliary-programs.html#field-horizontal-infrared-radiation-intensity),
[NOAA](https://gml.noaa.gov/grad/solcalc/solareqns.PDF) y
[datos horarios Open-Meteo](https://open-meteo.com/en/docs/historical-weather-api).
