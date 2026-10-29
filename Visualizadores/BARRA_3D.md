# Barra 3D solicitada para estudiar condiciones de borde

```powershell
.\.venv\Scripts\python.exe -B Visualizadores/visualizador.py
```

Abre sin ejecutar. En el menú unificado, seleccionar el caso de la barra, cambiar parámetros, pulsar **Ejecutar
test y calcular este caso**, leer el balance y después **Reproducir**.
Los controles están en una tabla desplazable; fuente, beta y observación
se encuentran más abajo. No se escriben figuras ni películas salvo petición
del usuario mediante **Guardar movie**.

## Geometría y condiciones iniciales

- Largo x=3 m, ancho y=3 m, altura z=6 m.
- Origen en el centro: x/y en [−1,5;1,5] m, z en [−3;3] m.
- T inicial=20 °C. k=2, rho=2400, cp=900 son valores didácticos heredados.
- Malla inicial 15×15×31: dx=dy=0,20 m, dz=6/31≈0,19355 m.
- dt inicial=300 s; horizonte 48 h. Todos estos valores son editables.

Ecuación: `rho cp dT/dt − k ∇²T = Q(x,y,z,t)`.
Se mantiene conducción explícita por balances cartesianos. La fuente se
integra analíticamente en cada paso, sin alterar la protección del solver.

## Fuente localizada y punto de observación

Las entradas se agrupan como vectores: **Dimensiones (x,y,z)**,
**Celdas (Nx,Ny,Nz)**, **Centro de la fuente (x,y,z)**,
**Tamaño de la fuente (x,y,z)** y **Observación (x,y,z)**.
Por ejemplo `(0, 0, 0)`, `(1, 1, 1)` y `(15, 15, 31)`.
Usar comas para separar componentes y punto decimal: `(0.5, 0, -1)`.
La tabla de parámetros también agrupa esas magnitudes. El archivo de entradas
y el solver conservan sus claves por componente, manteniendo compatibilidad.

La fuente se ubica en una caja, inicialmente de 1×1×1 m, centrada en (0,0,0).
Es una elección editable para visualizar una zona, no un dato calibrado.
Mover **Centro de la fuente x/y/z** cambia la posición real del aporte.
**Tamaño de fuente en x/y/z** cambia su volumen y por tanto la potencia total.
La caja debe permanecer completamente dentro de la barra.

Dentro de esa zona:

`Q(t)=Qmax/2*(1−cos(2 pi t/D))` para 0<=t<D, y cero después.

Fuera de la zona Q=0. Qmax inicial=5001 W/m³; D inicial=12 h, ambos editables.
No se afirma que ese valor produzca 70 °C en este caso: proviene del ejemplo
anterior y ahora cambian dimensión, fuente espacial y contorno.
Cada celda recibe el promedio volumétrico según su intersección con la caja,
de modo que mover la fuente no altera artificialmente su potencia por la malla.

**Observación x/y/z** es un control independiente: no mueve la fuente, mueve
el lugar donde se consulta Q y se aproxima T por interpolación trilineal.
La gráfica muestra Q dentro de la fuente y Q en el punto elegido; fuera de
la caja la segunda curva vale cero. La temperatura interpolada cerca de un
borde usa los centros extremos; para Dirichlet se devuelve el valor exacto
de la cara si el punto está sobre ella. La posible discontinuidad inicial
de Dirichlet a 30 °C se identifica como imposición del contorno.

## Cuatro casos

1. **Barra 3D · Dirichlet 20 °C**: todas las caras a 20 °C.
2. **Barra 3D · Dirichlet 30 °C**: todas las caras a 30 °C, interior inicialmente20 °C.
3. **Barra 3D · Neumann cero**: normal exterior, dT/dn=0 en todas las caras.
4. **Barra 3D · Robin beta editable**: se conserva literalmente la ecuación
   `dT/dn=beta*(T_superficie−20)` usando normal exterior, beta en 1/m.

### Interpretación de beta

- beta<0: enfriamiento cuando T_superficie>20; equivalente a h=−k beta>0.
- beta=0: aislamiento, equivalente a Neumann cero.
- beta>0: entra calor cuando T_superficie>20; la ley puede amplificar el calentamiento.

Valor inicial beta=−5 1/m, equivalente a h=10 W/(m² K) con k=2.
Puede probarse −1, 0 y +0,1, manteniendo los otros parámetros iguales.
Si la normal del ayudante es interior, la misma convección pasiva se expresa
con signo positivo: aclarar siempre la convención antes de comparar valores.

En la cara se calcula:

`P_entrante = k A beta/(1−beta*d/2) * (T_celda−20)`.

d es el tamaño de celda normal a la cara. Se exige beta*d/2<1 para esta
discretización; si se alcanza esa singularidad, refinar la malla o reducir beta.
La cota temporal usa el valor absoluto de los coeficientes de frontera.
No garantiza ausencia de crecimiento cuando la propia ley física beta>0 lo genera.

## Qué se ve y qué se verifica

El panel inferior izquierdo tiene pestañas **Resultados**, **Parámetros** y
**Notas**. Resultados separa test numérico, error/residuo y criterios térmicos;
Parámetros muestra las entradas que realmente se calcularon, dx/dy/dz y dt;
Notas conserva las explicaciones completas. Un test numérico aprobado no
equivale a satisfacer los límites térmicos. No se recorta artificialmente T.

Se calculan en **cada paso numérico**, sin usar la interpolación de la película:

- Tmax del dominio, con centros y reconstrucción del contorno: límite70 °C.
- Delta T(t)=Tmax_Omega(t)−Tmin_S25(t), y su máximo temporal: límite20 °C.
- Instantes de ambos máximos y Tmin_S25 en el instante de Delta máximo.

S25 se estima en seis planos a25 mm de las caras, incluyendo aristas del cubo
interior. Se reconstruye linealmente entre caras físicas y centros de celda.
Con la malla inicial, el primer centro está a≈100 mm: el resultado se marca
como estimado y se exige estudiar refinamiento para una evaluación sólida.
Esto es distinto de restar la mínima de todo el dominio.

La tabla dice **EXCEDE (estim.)** o **Dentro (estim.)** para el horizonte
calculado. También muestra si se cubren los **336 h (14 días)** del proyecto;
las48 h de este ejercicio se marcan **PARCIAL**. Ni la reconstrucción gruesa
ni una corrida corta autorizan afirmar cumplimiento global del proyecto o
ausencia de grietas. Las probabilidades de excedencia aún no se calculan.

La vista inicial es **Cortes interiores**, para observar directamente el calentamiento.
La vista secundaria **Volumen 3D** dibuja el prisma completo en proporción 3×3×6,
con las seis caras coloreadas celda por celda y animadas. Arrastrar con el
ratón gira la cámara; **Ver caras opuestas** la gira 180 grados. Las caras
ocultas también se actualizan. La cámara elegida se conserva al reproducir.

El selector de caras distingue:

- **Superficies físicas**: Dirichlet20/30 son constantes por definición;
  Neumann cero extrapola el centro vecino; para Robin se reconstruye
  `T_superficie=20+(T_celda−20)/(1−beta*d/2)`.
- **Celdas exteriores**: temperaturas de los centros vecinos al contorno,
  proyectadas sobre las caras para observar la evolución interior cercana.
  No se presentan como temperaturas exactas de superficie.

**Cortes interiores** recupera los tres mapas previos. Cambiar de vista no
ejecuta de nuevo el solver. **Guardar movie** exporta la vista seleccionada,
con su cámara, modo de caras y escala de color fijos durante toda la película.
Los gráficos Q(t) y temperatura siguen acompañando la vista del volumen.
El volumen usa una paleta azul–rojo sin extremo negro, y declara por separado
el rango de temperatura de las caras mostradas y la máxima interior. Así se
distingue una superficie todavía fría de la zona fuente caliente oculta.

La reproducción intenta 25 cuadros/s y recorre la historia completa en unos12s.
Los cortes usan una caché de ejes/leyendas y actualizan solo imágenes/cursor.
Se interpola linealmente entre estados guardados únicamente para visualizar:
no cambia dt, campos calculados, balances ni tests. La movie exportada usa
25 cuadros/s e interpolación visual. Arrastrar el selector temporal pausa
la reproducción; la cámara 3D requiere un redibujo más costoso que los cortes.

- Tres cortes XY/XZ/YZ, a través de los centros de celda cercanos a la observación.
- Contorno cian de la zona fuente si intersecta el corte y cruz blanca del punto.
- Q(t) en la fuente y en el punto, T(t) en el punto y media/máxima/mínima del volumen.
- Balance `cambio de energía = calor por contorno + calor generado`.
- En Neumann cero y beta=0, cambio de energía igual a calor generado.

El resultado APROBADO se refiere a esos balances; no a una solución exacta
transiente general para una fuente localizada. La escala de cada simulación
permanece fija durante su animación; comparar también valores numéricos entre casos.

Las entradas se guardan al ejecutar en `Visualizadores/parametros.json`.
Para repetir el caso bajo pytest con esas entradas:

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q -s -p no:cacheprovider desarrollo/tests/test_e05_visualizador.py -k barra
```

Para estudiar comprobaciones independientes pequeñas de beta, equivalencia
con Robin pasivo, fuente temporal y movimiento de la caja:

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q -s -p no:cacheprovider desarrollo/tests/test_barra3d_fuente.py
```

Al preparar la ventana solo se comprobó sintaxis/importación; las simulaciones
y estas pruebas quedan para que las ejecute personalmente el usuario.
