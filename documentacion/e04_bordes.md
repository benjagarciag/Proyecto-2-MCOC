# E04: condiciones de borde 2D y 3D

Etapa del 27 de octubre de 2026, solo en la copia `E04_pruebas_2d`.
Complementa los documentos históricos `e04_2d.md` y `e04_3d.md`: sus pendientes
Neumann/Robin quedan cubiertos por esta extensión. No se modificaron esos
solvers, el 1D, el proyecto original ni los modelos BIM. No hubo instalación,
commit, merge, PR ni publicación. Se consultó el remoto sin integrarlo:
main=4c4a1d3fe21ca5cb3b92d74de5d818f9a4991aa7;
luis-entrega-fundacion=4e67a71a8e437df09867d8281e6a46d759edafc9.

## Qué significa cada borde

| Condición | Qué prescribe | Ejemplo |
|---|---|---|
| Dirichlet | Temperatura en la superficie, °C | Cara mantenida a 20 °C |
| Neumann | Flujo superficial, W/m² | Entran 200 W por cada m² |
| Robin | Intercambio con ambiente mediante h y T∞ | Aire a 20 °C enfría un sólido caliente |

**Adiabático significa que no atraviesa calor la superficie.** Se representa
con Neumann q=0; no exige temperatura cero ni temperatura constante. El calor
puede seguir circulando entre celdas interiores. Un cuerpo aislado inicialmente
no uniforme tiende al equilibrio conservando su energía total.

La convención del programa es **positivo hacia dentro**, en TODAS las caras.
Con normal exterior n, q_entrante = k ∂T/∂n y q_saliente = -q_entrante.
No se debe cambiar el signo manualmente por estar en x_min o x_max.
Un flujo negativo extrae calor. Neumann se ingresa como flujo por área, no W
totales y no gradiente K/m: el programa multiplica por el área de cada cara.

## Balance y discretización

Cada celda almacena capacidad térmica C=ρ cp V [J/K], con ρ en kg/m³,
cp en J/(kg K), k en W/(m K). En 2D V=dx dy e; en 3D V=dx dy dz.

    C (T_i^(n+1)-T_i^n)/dt = Σ_j G_ij (T_j^n-T_i^n) + Σ_caras P_cara^n

    G_ij = k A / d                 [W/K]
    P_cara = B - H T_i             [W]
    T_i^(n+1) = T_i^n + dt*P_neta/C

Hay cuatro vecinos interiores en 2D y seis en 3D. Cada interfaz se evalúa una
sola vez: lo que gana una celda lo pierde su vecina. Todos los flujos utilizan
el estado anterior; ninguna celda usa la temperatura recién actualizada.
Las celdas de arista/esquina reciben la suma de sus distintas caras.

δ=d/2 es la distancia entre centro de celda y superficie física. A es el área
de UNA cara de celda, no el área total del dominio. En dirección x: A=dy e
en 2D y A=dy dz en 3D. Las diferencias en °C equivalen a diferencias en K.

### Dirichlet

    H_D = k A / δ = 2 k A / d
    P_entrante = H_D (T_borde-T_i)

Se prescribe la temperatura en la superficie; el centro de la celda de borde
puede tener otra temperatura. No se sobrescriben las celdas de borde.

### Neumann

    H_N = 0
    B_N = q_entrante A
    P_entrante = q_entrante A

El flujo no depende de T_i. Con q=0 la frontera no aporta ni extrae calor.
Una extracción constante puede seguir enfriando el dominio: no se corta
automáticamente al llegar a una temperatura ambiente, pues Neumann no la usa.

### Robin y media celda

La ley superficial de convección es q_saliente = h (T_s-T∞), con T_s la
temperatura de la superficie. El solver conoce T_i, en el centro, no T_s.
Por eso se suman las resistencias térmicas:

    R_cond = δ/(k A)                    [K/W]
    R_conv = 1/(h A)                    [K/W]
    H_R = 1/(R_cond+R_conv) = A/(δ/k+1/h) [W/K]
    P_entrante = H_R (T∞-T_i)             [W]

Si el ambiente está más frío, P<0 y el sólido pierde energía; si está más
caliente, P>0. El h debe ser no negativo. h=0 se trata sin dividir por cero
y equivale a aislamiento; h→∞ recupera Dirichlet a T∞. Aunque h sea muy
grande, la resistencia de conducción de media celda sigue presente.

Se puede reconstruir T_s = T_i + (P_entrante/A) δ/k. Para h>0 coincide con
T_s=T∞-(P_entrante/A)/h. No usar h A (T∞-T_i) ignorando la media celda,
salvo que se justifique como aproximación: puede sobreestimar el flujo.

## Estabilidad y precisión temporal

Sea S_i la suma de conductancias hacia vecinos más H de las caras exteriores:

    S_i = Σ_j G_ij + Σ_caras H_cara
    dt_max = min_i C_i/S_i = C/max_i(S_i), para este material homogéneo

El peso de T_i en Euler explícito es 1-dt S_i/C. Exigir que sea no negativo
da un límite suficiente de estabilidad/monotonía para este problema lineal.
No se presenta como el límite espectral exacto. Robin y Dirichlet aportan H;
un Neumann constante aporta B, pero H=0. El control incluye esquinas y aristas.

Un Robin intenso puede hacer más restrictivo el paso que un borde adiabático.
No necesariamente lo hace: en nuestros cuatro ejemplos dominan las celdas
interiores y los límites Robin/Neumann coinciden para cada malla. Los tests
incluyen un h mayor que sí cambia el límite. No basta aplicar siempre el
criterio interior ni reutilizar un dt calculado para otros bordes.

El programa propone 0.9*dt_max por defecto, luego ajusta dt=tf/ceil(tf/dt)
para llegar exactamente al tiempo final. Si el usuario propone dt>dt_max,
lo rechaza ANTES de ajustarlo, incluso si tf es pequeño. Un paso estable
todavía puede dar error temporal; reducir dt sirve para estudiar precisión.

Un Neumann no nulo puede llevar T fuera del rango inicial por aporte/extracción
física: eso no basta para declarar inestabilidad. La monotonía entre mínimos
y máximos se comprueba para aislamiento sin fuentes y para Robin con ambiente
acotado. Los parámetros de cara son constantes en el tiempo y uniformes por
cara; clima variable y h espacial variable no están implementados.

## Conservación comprobada

Al sumar las ecuaciones de todas las celdas, los intercambios internos se
cancelan. Sin fuentes:

    E^(n+1)-E^n = dt * Σ_caras P_entrante^n

Se registra E=C ΣT con referencia arbitraria 0 °C; lo físicamente relevante
son sus diferencias. La integral temporal del calor usa el estado anterior,
igual que Euler: dt*sum(P_exterior[:-1]); el último valor de potencia no
corresponde a otro paso. No usar trapecios para comprobar este balance discreto.

Con todas las caras adiabáticas ΔE=0, hasta redondeo. Con Robin frío la energía
disminuye exactamente según la extracción exterior: eso también es conservar
el balance, aunque el cuerpo por sí solo sea un sistema abierto.

## Archivos y recorrido del código

1. `desarrollo/mcplan/bordes_termicos.py`: clases Dirichlet, Neumann y Robin.
   `coeficientes_cara` transforma cada condición en H y B; `preparar_operador`
   calcula áreas/conductancias y suma de extracción; `potencia_con_bordes_W`
   evalúa los intercambios internos y exteriores. Reutiliza `_caras` del
   balance cartesiano existente; no cambia su implementación.
2. `desarrollo/mcplan/difusion_bordes.py`: `geometria_y_bordes` adapta los
   Parametros2D/3D anteriores. Exige todas las caras, sin condiciones ocultas.
   `paso_maximo_bordes_s` calcula el límite; `_resolver` hace el avance
   explícito compartido y guarda energía/potencia. Las entradas públicas son
   `resolver_2d_bordes` y `resolver_3d_bordes`, con el mismo núcleo.
3. `desarrollo/tests/test_bordes_termicos.py`: evidencia reproducible.
4. `casos/bordes/parametros.json`: entradas editables y unidades.
5. `casos/bordes/ejecutar.py`: lectura de entradas, ejecución y gráficos.
6. `casos/bordes/README.md`: comandos para este computador.

Ejemplo de API 2D (cuatro caras explícitas; se admite mezcla de tipos):

```python
from mcplan.difusion_2d import Parametros2D
from mcplan.bordes_termicos import Neumann, Robin
from mcplan.difusion_bordes import resolver_2d_bordes

bordes = {cara: Neumann(0) for cara in ('x_min', 'x_max', 'y_min', 'y_max')}
bordes['x_max'] = Robin(h_W_m2K=10, ambiente_C=20)
resultado = resolver_2d_bordes(Parametros2D(tiempo_final_s=3600), bordes, 60)
```

Para 3D usar Parametros3D, agregar z_min/z_max y llamar resolver_3d_bordes.
Las coordenadas se entregan como (x,y,z), pero el arreglo T usa [z,y,x].
Se guardan hasta siete campos por defecto y un valor de energía/potencia por
paso; el solver no guarda toda la historia volumétrica ni depende de Blender.

## Pruebas ejecutadas

**156 aprobadas: 31 del 1D + 22 del 2D + 30 del 3D + 73 nuevas.**

Las nuevas cubren:

- Flujo positivo/negativo en cada cara 2D y 3D, áreas y un paso calculado a mano.
- Robin con ambiente caliente/frío en cada cara y resistencia de media celda.
- Conservación adiabática con campo no uniforme durante múltiples pasos.
- Balance mixto Dirichlet/Neumann/Robin con potencia exterior independiente.
- Estado estacionario lineal exacto para flujos Neumann opuestos.
- Estado estacionario lineal exacto Dirichlet-Robin, con resistencias en serie.
- Transiente Neumann exacto: T=30+5 Π cos(πx/L), decaimiento
  exp[-απ² Σ(1/L²)t], dominio unitario adiabático; error final <0.01 K.
- Transiente Robin exacto de placa plana con ambos extremos convectivos:
  T=T∞+A cos[μ(x-L/2)/(L/2)] exp[-α(μ/(L/2))²t],
  μ tan μ = h(L/2)/k; otras caras adiabáticas; A positivo y negativo,
  en ambos solvers; error final <0.01 K. μ se obtiene por bisección.
- Límites h=0 y h muy grande, estabilidad calculada independientemente,
  rechazo de paso inestable y temperaturas acotadas con paso límite Robin.
- Regresión: Dirichlet por el núcleo nuevo reproduce los solvers anteriores.
- Validación de datos, cara faltante/desconocida, tiempo cero y memoria.

Las celdas de los tests de flujos tienen pasos distintos según el eje para
detectar errores de área. El ejemplo 3D Neumann es deliberadamente plano
(varía en x); las pruebas transientes Neumann también varían en x,y,z.
Estos tests verifican casos de referencia, no validan físicamente una obra.

## Resultados de los ejemplos predeterminados

k=2 W/(m K), ρ=2400 kg/m³, cp=900 J/(kg K), α=9.2592593e-7 m²/s.
Todos los lados miden 1 m; espesor 2D 1 m. Valores didácticos sin calibración.

| Ejemplo | Malla | tf | dt efectivo / máximo [s] | Temperatura media inicial → final | ΔE [MJ] |
|---|---|---|---|---|---|
| 2D adiabático | 25×25 | 24 h | 387.44395 / 432 | 40 → 40 °C | 0 |
| 2D Robin | 25×25 | 24 h | 387.44395 / 432 | 60 → 35.78193585 °C | -52.311019 |
| 3D Neumann | 15³ | 6 h | 720 / 800 | 20 → 22 °C | +4.32 |
| 3D Robin | 15³ | 24 h | 720 / 800 | 60 → 29.91501311 °C | -64.983572 |

Robin usa h=10 W/(m² K) y ambiente 20 °C en todas las caras consideradas.
El adiabático empieza con 40+20 cos(πx)cos(πy): las zonas calientes ceden calor
a las frías, sin cambiar la media. Neumann 3D introduce 200 W/m² por x_min,
con otras cinco caras adiabáticas. Su energía añadida exacta es
200 W/m² × 1 m² × 21600 s = 4.32 MJ; ΔT_media=4.32e6/(2400*900*1)=2 K.

El mayor residuo absoluto acumulado del balance en estos cuatro ejemplos es
3.73e-8 J, frente a intercambios del orden de millones de J. La figura
adiabática muestra una escala ±1 J para no exagerar el redondeo (~1.49e-8 J).
El 3D Robin enfría más que el 2D porque también intercambia por las caras z.
Ninguno incluye hidratación, fuentes internas ni interfaces entre materiales.

## Ensayo oral de dos minutos

1. «Dividimos el cuerpo en celdas. Cada una almacena calor y lo intercambia
   con cuatro vecinos en 2D o seis en 3D. El balance nos da cuánto cambia T».
2. «Dirichlet fija temperatura; Neumann fija flujo; Robin calcula intercambio
   con un ambiente. Nuestro signo positivo siempre significa calor entrante».
3. «Adiabático es flujo cero. No impide que el calor se redistribuya dentro.
   Lo demostramos porque la media se mantiene aunque cambien máximo y mínimo».
4. «Robin considera media celda más película de aire en serie. Si el ambiente
   está frío, el flujo entrante es negativo y disminuye la energía del sólido».
5. «Actualizamos todas las celdas desde el estado anterior. Limitamos dt usando
   capacidad dividida por suma de conductancias, incluidas las caras».
6. Abrir las figuras: mostrar potencia, cambio de energía y calor acumulado.
   Ejecutar pytest y señalar un test de conservación y uno exacto.

## Pendientes y límite de esta etapa

Para E04 (calendario: revisión oral 2D/3D + condiciones de borde), practicar
el recorrido anterior, modificar una cara y explicar el signo, y demostrar
qué pasa al variar dx/dt. Revisar el método de Schmidt según el material del
curso; no se afirma haber leído el Anexo 4 ICH completo. Confirmar con la
pauta docente el alcance exacto frente a E05 (laboratorio de verificación)
y E06 (dossier + BIM): no son la misma entrega.

Fuentes volumétricas físicas en W/m³ y dos materiales con interfaz siguen
pendientes y NO se implementaron. También siguen separados la validación
geométrica BIM, la voxelización/conexión al solver y el flujo completo de
vertidas/clima del proyecto final. Esta etapa verifica dominios cartesianos
didácticos; no constituye una simulación de la fundación real ni demuestra
cumplimiento de límites térmicos de obra. Integrar o publicar requiere una
autorización posterior. Detener aquí para revisión del usuario.
