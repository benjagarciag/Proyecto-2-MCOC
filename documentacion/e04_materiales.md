# E04: dos materiales y contacto térmico perfecto

Etapa autorizada del 27 de octubre de 2026, exclusivamente en `E04_pruebas_2d`.
Se añadió el tratamiento de dos materiales al núcleo 2D/3D existente. Se conserva
la API homogénea por defecto y sus 207 pruebas. No se modificaron proyecto
original, BIM, solvers 1D/2D/3D originales ni la implementación de bordes.
No hubo instalaciones, commits, merges, PR o publicaciones.

Consulta remota sin integrar: main=4c4a1d3fe21ca5cb3b92d74de5d818f9a4991aa7;
luis-entrega-fundacion=4e67a71a8e437df09867d8281e6a46d759edafc9.
Este documento actualiza el pendiente «dos materiales» de las etapas anteriores.

## Qué cambia físicamente

Un material puede conducir calor con más facilidad y almacenar una cantidad
distinta de energía por grado. No basta una sola conductividad si los dos
materiales ofrecen resistencias diferentes al paso del calor.

- k [W/(m K)] controla la conducción.
- rho [kg/m³] y cp [J/(kg K)] determinan la capacidad térmica por volumen rho*cp.
- alpha=k/(rho*cp) [m²/s] relaciona conducción y almacenamiento.

Alpha se deriva de las otras tres propiedades. No se puede elegir alpha
independientemente de ellas sin perder consistencia. La ecuación de balance
usa k y C directamente; no se promedian alphas para definir la interfaz.

Las propiedades de cada material son positivas, constantes e isotrópicas.
Cada celda tiene ID 0 o 1 y pertenece a un solo material. La interfaz se
representa mediante caras de celdas; el constructor de bloques exige que su
plano coincida con la malla. Una posición no alineada se rechaza, no se mueve
silenciosamente. No hay mezclas subvoxel ni representación de curvas BIM.

## Contacto perfecto

Suponemos superficies completamente unidas, sin hueco, película o resistencia
de contacto adicional. La interfaz no almacena energía. En el contacto:

    T_s,A = T_s,B
    q_A→B = q que sale de A = q que entra en B

La temperatura superficial común NO exige que los centros de las dos celdas
tengan la misma T. Es normal que difieran: hay gradientes dentro de cada media
celda. En régimen estacionario cambia la pendiente del perfil al cambiar k,
pero la temperatura no presenta un salto de contacto y el flujo es continuo.

Durante un transiente puede variar el flujo de una cara a otra debido al
almacenamiento de las celdas. La continuidad exigida es en LA MISMA interfaz:
la potencia que sale por ella es la que entra al vecino. No exigir flujo
uniforme en todo el dominio mientras las temperaturas cambian.

## Resistencias y conductividad armónica

Sea A el área compartida y d_i/d_j las distancias desde cada centro a la cara:

    R_i = d_i/(k_i A)           [K/W]
    R_j = d_j/(k_j A)           [K/W]
    G_ij = 1/(R_i+R_j) = A/(d_i/k_i+d_j/k_j)  [W/K]

En nuestra malla regular d_i=d_j=d/2. Se puede escribir:

    k_armonica = 2/(1/k_i+1/k_j)
    G_ij = k_armonica*A/d
    P_i→j = G_ij*(T_i-T_j)      [W]
    q_i→j = P_i→j/A             [W/m²]

La media armónica aparece al sumar resistencias en serie. Da más peso al
material que dificulta la transferencia. No usar el promedio aritmético ni
escoger arbitrariamente k de uno de los vecinos.

El código calcula cada interfaz una sola vez. Para potencia entrante:

    potencia[i] += G_ij*(T_j-T_i)
    potencia[j] -= G_ij*(T_j-T_i)

Así se cancelan exactamente esas contribuciones al sumar el dominio, hasta
redondeo numérico. La función de potencias ya existente se reutiliza: admite
ahora conductancias por cara, además de los escalares del modo homogéneo.

## Balance, bordes y estabilidad local

    C_i = rho_i*cp_i*V_i
    C_i*dT_i/dt = sum_j G_ij*(T_j-T_i) + q'''_i*V_i + P_borde_i
    T_i^(n+1) = T_i^n + dt*P_neta_i^n/C_i

La forma del balance no cambia: cambian sus coeficientes locales. El mismo
dt es compartido por todas las celdas y todos los flujos usan el estado
anterior. El paso suficiente de estabilidad/monotonía es:

    S_i = sum_j G_ij + sum_caras H_borde
    dt_max = min_i(C_i/S_i)

No se usa C promedio ni C_global/max(S) con una capacidad arbitraria.
Dirichlet exterior usa H=k_i*A/(d/2); Robin usa
H=A/[(d/2)/k_i+1/h], con k_i de la celda exterior. Neumann constante no agrega
H. La fuente prescrita sigue sumando q'''V y no modifica estos coeficientes.
El paso se propone como 0.9*dt_max y luego se ajusta para terminar en tf;
un paso solicitado excesivo se rechaza antes de ajustar.

La energía se calcula como E=sum_i(C_i*T_i), con referencia arbitraria 0 °C.
Con aislamiento y sin fuente, E es constante. Si hay bordes/fuentes:

    E^(n+1)-E^n = dt*(P_exterior^n + sum_i q'''_i V_i)

La media aritmética de T no representa la energía cuando C varía. En un
dominio aislado, el equilibrio final es:

    T_equilibrio = sum_i(C_i*T_i,inicial)/sum_i(C_i)

## Dónde está implementado

1. `desarrollo/mcplan/materiales_termicos.py` (nuevo):
   - `MaterialTermico`: valida k, rho, cp y calcula alpha.
   - `DosMateriales.campos`: transforma IDs 0/1 en campos locales y los copia.
   - `materiales_desde_config`: dos bloques separados por plano x/y/z alineado.
   - `preparar_operador_materiales`: resistencias de medias celdas, G compartida,
     coeficientes de borde locales y suma S por celda.
2. `desarrollo/mcplan/difusion_bordes.py` (extendido):
   - `_preparar_balance`: elige modo homogéneo o dos materiales y calcula C_i.
   - `paso_maximo_bordes_s(..., materiales=...)`: mínimo local C_i/S_i.
   - `resolver_2d_bordes`/`resolver_3d_bordes`: argumento opcional materiales;
     se conserva el bucle temporal, fuentes y potencias interiores/exteriores.
   - Resultado: `capacidad_J_K` y `materiales` con IDs, k, rho, cp y alpha.
3. `desarrollo/tests/test_materiales_termicos.py`: 44 pruebas nuevas.
4. `casos/materiales/{parametros.json,ejecutar.py,README.md}`: ejemplos.

Si `materiales=None`, se usan las propiedades homogéneas de Parametros2D/3D
como antes. Si se pasa DosMateriales, sus propiedades locales prevalecen; los
parámetros siguen definiendo geometría y tiempos. No interpretar el alpha
homogéneo de Parametros como alpha de las dos regiones.

## Propiedades y resultados de los ejemplos

| Material | k [W/(m K)] | rho [kg/m³] | cp [J/(kg K)] | alpha [m²/s] |
|---|---|---|---|---|
| A, izquierda | 2 | 2400 | 900 | 9.2592593e-7 |
| B, derecha | 0.5 | 1600 | 800 | 3.90625e-7 |

Valores didácticos; no calibrados para nuestra fundación. Dominios de lados
1 m, espesor 2D de 1 m, interfaz x=0.5 m, inicialmente A a 60 °C y B a 20 °C.
Exterior adiabático, fuente cero, tf=24 h. La comparación homogénea usa todo A.

| Resultado | 2D (24×24) | 3D (16³) |
|---|---|---|
| dt efectivo / máximo [s] | 421.46341 / 468.75 | 630.65693 / 703.125 |
| Pasos | 205 | 137 |
| Flujo final en interfaz [W/m²], hacia +x | 43.28083003 | 43.40548321 |
| Temperatura superficial común final [°C] | 48.68626547 | 48.68530813 |
| Máximo cambio de energía absoluto [J] | 2.98e-8 | 2.98e-8 |

El equilibrio energético esperado es 45.11627907 °C para ambos dominios:
(2.16e6*60+1.28e6*20)/(2.16e6+1.28e6). Esta es también la media ponderada
constante durante el transiente; NO significa que todas las celdas hayan
llegado al equilibrio a las 24 h. El control homogéneo tiene equilibrio 40 °C.
La comparación cambia tanto conducción como capacidad térmica; no atribuir
todo el efecto a k. Los ejemplos varían solo en x, deliberadamente, para poder
explicar la interfaz; los tests también verifican transferencias en y y z y
un mapa alternado con temperaturas diferentes en todos los ejes.

Una condición inicial escalonada tiene un contacto inicialmente no equilibrado;
el flujo reconstruido en t=0 depende del tamaño de la celda. La convergencia
se verifica con una solución transiente suave compatible en la interfaz.

## Verificación estacionaria y comparación homogénea

La tercera figura usa caras x_min=60 °C y x_max=20 °C, otras adiabáticas, sin
fuentes. Se inicializa con el perfil exacto por tramos y se comprueba que no
cambie. La solución es:

    q = (60-20)/[0.5/2+0.5/0.5] = 32 W/m²
    T_interfaz = 60-q*0.5/2 = 52 °C
    T(x) = 60-32*x/2                       para x<=0.5
           52-32*(x-0.5)/0.5               para x>=0.5

Pendiente izquierda -16 K/m, derecha -64 K/m: B necesita un gradiente cuatro
veces mayor para transmitir el mismo flujo. En contacto perfecto no hay salto
de T en x=0.5. Si todo es material A, T es lineal y q=80 W/m².
El solver conserva el perfil exacto con error 0 K en estos ejemplos; el error
de flujo es <=2.27e-13 W/m². Esto es una prueba de preservación de equilibrio,
no demuestra por sí sola convergencia transiente desde cualquier estado.

Figuras fijas (únicamente PNG):

- `resultados/materiales/2d/perfiles_temperatura.png`
- `resultados/materiales/3d/perfiles_temperatura.png`
- `resultados/materiales/verificacion_interfaz/perfiles_temperatura.png`

## Pruebas y refinamiento

**251 aprobadas: 207 anteriores + 44 nuevas.** Las nuevas comprueban:

- Un paso manual con k/capacidades distintas en x/y y x/y/z.
- Conservación adiabática y equilibrio ponderado por capacidad.
- Perfil exacto por tramos, flujo continuo y T superficial común en cada eje.
- Contrastes de k y conductancia armónica calculada independientemente.
- Recuperación homogénea con Dirichlet, Neumann y Robin más fuente.
- Coeficientes de borde que usan k local; fuente y capacidad local.
- Balance abierto con generación y Robin.
- Límite temporal local mediante recorrido independiente de vecinos; rechazo
  de paso excesivo y temperaturas acotadas con paso límite.
- Mapa alternado, intercambio en todos los ejes, independencia de copias,
  tiempo cero y validación de propiedades, IDs e interfaz alineada.

Referencia transiente adiabática en x∈[0,1], interfaz x=0.5:
k_A=1, rho_A*cp_A=1; k_B=4, rho_B*cp_B=4; alpha=1 en ambos.

    T=30+10*phi(x)*exp(-pi²*t)
    phi(x)=cos(pi*x) para x<0.5; 0.25*cos(pi*x) para x>0.5

T es continua en la interfaz y k*dT/dx también, con flujo de contacto no
nulo. No hay variación transversal. Al refinar x y mantener dt/dx²=0.05:

| Nx | Error máximo final [K], ambos solvers |
|---|---|
| 8 | 0.0196089018 |
| 16 | 0.00493737676 |
| 32 | 0.00123731998 |

Cocientes de error 3.9715 y 3.9904, compatibles con convergencia de orden dos
en este refinamiento conjunto. No son mediciones independientes del orden
espacial y del temporal. Se fijó esa relación temporal porque el dt automático
también depende de los ejes transversales y no mantiene dt/dx² constante.

## Explicación oral de esta etapa

«Cada celda almacena calor según su densidad y calor específico. Entre dos
materiales, sumamos la resistencia de media celda de cada uno. Su inversa es
la conductancia compartida. Calculamos una sola potencia: sale de una celda
y entra en la otra. Eso conserva energía. Contacto perfecto significa que no
agregamos resistencia extra ni un salto de temperatura en la superficie.
Las temperaturas de los centros sí pueden ser distintas. La conductividad
armónica resulta de esas resistencias en serie. El balance sigue teniendo
la misma forma, pero ahora usamos capacidades y conductancias locales, también
para limitar dt. En equilibrio, el material menos conductor necesita una
pendiente de temperatura mayor para transmitir el mismo flujo».

Mostrar primero los colores y la interfaz; después el perfil exacto con su
cambio de pendiente; señalar que el flujo continúa en 32 W/m². Abrir
`preparar_operador_materiales` y la actualización del núcleo compartido.
Cerrar con conservación y el test de recuperación homogénea. La revisión
oral completa de TODAS las etapas se prepara después de revisar esta entrega.

## Estado frente a E04 y punto de detención

El calendario disponible declara E04: «W2 — Revisión oral: 2D/3D + condiciones
de borde», miércoles 28, 4 puntos. No se encontró una rúbrica E04 desglosada
en los archivos disponibles; no asignamos puntajes ni certificamos cobertura
de criterios que no estén publicados aquí. E05 y E06 son actividades separadas.

| Tema desarrollado para la preparación | Evidencia | Pendiente |
|---|---|---|
| Difusión 2D/3D y stencil | Solvers y pruebas de etapas anteriores | Explicación individual |
| Dirichlet/Neumann/Robin | Bordes y tests, incluidos k locales | Demostrar cambios de cara y signos |
| Balance y fuente W/m³ | Fuentes y pruebas exactas | Explicar unidades |
| Dos materiales/contacto perfecto | Esta etapa y perfil exacto | Defender hipótesis y media armónica |
| Estabilidad/refinamiento | dt local y solución transiente exacta | Variar dx/dt y explicar el efecto |
| Conservación y regresión | 251 pruebas | Ejecutar y explicar pruebas elegidas |
| Schmidt y referencias del curso | Guías y documentos disponibles | Lectura/defensa; no se afirma lectura completa del Anexo 4 ICH |

Falta ensayar la revisión oral completa y contrastar cualquier rúbrica E04
adicional del profesor. No se identificó aquí otro pendiente de implementación
dentro de las etapas didácticas autorizadas. Hidratación, clima, Monte Carlo,
conexión/validación BIM y proyecto final quedan fuera de esta etapa y no se
desarrollaron. No se afirma cumplimiento de criterios térmicos de una obra.
Detener aquí antes de integrar o pasar a la revisión oral completa.
