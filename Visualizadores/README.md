# Visualizador térmico unificado

Una sola ventana para configurar, verificar y observar la evolución de
temperatura de los casos 1D, 2D y 3D del proyecto. Reúne el visualizador de
estudio y la barra 3D con fuente localizada; no depende de una entrega E05.

## Abrir

Desde la raíz del repositorio:

```powershell
.\.venv\Scripts\python.exe -B Visualizadores/visualizador.py
```

Utiliza NumPy y Matplotlib del entorno del proyecto, y Tkinter incluido con
la instalación de Python. No necesita Blender para estos casos matemáticos.
Abrir la ventana **no ejecuta simulaciones ni pruebas**.

## Casos disponibles

| Caso | Qué permite estudiar |
| --- | --- |
| Solución exacta 1D | Perfil sinusoidal, difusión y error frente a solución analítica. |
| Seno 2D | Temperaturas en una placa y comparación con el seno exacto 2D. |
| Seno 3D | Difusión en volumen y comparación con el seno exacto 3D. |
| Conservación adiabática | Redistribución interior sin intercambio de calor con el exterior. |
| Fuente uniforme | Generación volumétrica constante con superficies aisladas. |
| Flujo Neumann | Flujo entrante/saliente prescrito en una cara. |
| Convección Robin | Intercambio con un ambiente mediante h y temperatura ambiente. |
| Barra 3D · Dirichlet 20 °C | Fuente localizada y seis caras a20 °C. |
| Barra 3D · Dirichlet 30 °C | Fuente localizada y seis caras a30 °C. |
| Barra 3D · Neumann cero | Fuente localizada y todas las caras aisladas. |
| Barra 3D · Robin beta editable | Fuente localizada y gradiente exterior dependiente de beta. |

Los casos no sinusoidales generales permiten 2D/3D. La barra específica
parte con largo x3m, ancho y3m y altura z6m, origen en el centro e inicio20 °C.
Ver [la explicación completa de esa barra](BARRA_3D.md).

## Uso paso a paso

1. Elegir un caso en el menú superior izquierdo.
2. Cambiar los parámetros activos y predecir qué debería ocurrir.
3. Pulsar **Ejecutar test y calcular este caso**.
4. Revisar las pestañas **Resultados**, **Parámetros** y **Notas**.
5. Pulsar **Reproducir**; usar **Pausa**, **Inicio** o el selector de tiempo.
6. Si se quiere un archivo, pulsar **Guardar movie**.

Los campos espaciales están agrupados como vectores:

| Entrada | Ejemplo | Significado |
| --- | --- | --- |
| Dimensiones (x,y,z) | `(3, 3, 6)` | Largo, ancho y altura en metros. |
| Celdas (Nx,Ny,Nz) | `(15, 15, 31)` | Cantidad de divisiones por dirección. |
| Centro de la fuente | `(0, 0, 0)` | Posición de la caja que genera calor. |
| Tamaño de la fuente | `(1, 1, 1)` | Dimensiones de esa caja en metros. |
| Observación | `(1.4, 0, 0)` | Punto donde se consulta Q(t) y se aproxima T(t). |

Usar **comas entre componentes y punto decimal**. Mover la observación no
mueve la fuente ni cambia el cálculo global. Cambiar el tamaño de fuente
manteniendo Qmax sí cambia el calor total generado, porque Q está en W/m³.
En 1D se ingresa alpha directamente; en 2D/3D se calcula alpha=k/(rho cp).

## Vistas y reproducción

- **1D:** perfil T(x,t), con referencia analítica.
- **2D:** mapa XY y curvas temporales.
- **3D:** cortes XY/XZ/YZ. En la barra siguen el punto de observación.
- **Volumen 3D:** vista secundaria de las seis caras, girable con el ratón.
  Permite elegir superficies físicas o celdas exteriores proyectadas.

Las superficies Dirichlet conservan la temperatura impuesta; para ver la
fuente interior se usan los cortes. Los colores mantienen escala fija durante
cada reproducción. Se intenta25 cuadros/s con caché en los cortes y una
duración de unos12s por historia. La interpolación entre estados es solo
visual: no modifica dt ni los resultados utilizados por los tests.

En la barra se grafican Q(t) dentro de la fuente, Q(t) en la observación,
temperatura observada y estadísticas del volumen. La fuente inicial es un
pulso cosenoidal de12h en una caja1×1×1m, con Qmax5001 W/m³ y horizonte48h;
son entradas editables, no propiedades calibradas del hormigón.

## Resultados y criterios térmicos

La tabla separa la **verificación numérica** de la **evaluación térmica**.
Un balance aprobado no implica cumplir los límites del proyecto.
En la barra se muestran Tmax<=70 °C y DeltaTmax<=20 °C, con
`DeltaT(t)=Tmax_Omega(t)−Tmin_S25(t)`. S25 se reconstruye a25mm de las caras.
Se evalúan todos los pasos del solver, no cuadros interpolados de la película.

La malla inicial tiene primeros centros a≈100mm: S25 se marca como estimado
y requiere refinamiento. El horizonte48h se marca parcial frente a los14días
del proyecto. No se calculan probabilidades de excedencia ni se afirma
ausencia de grietas. Los límites no recortan artificialmente la temperatura.

En la barra Robin se conserva la normal exterior y
`dT/dn=beta*(T_superficie−20)`, con beta en1/m. Por eso beta<0 enfría cuando
T>20, beta0 aísla y beta>0 puede introducir calor. Con beta<0, h=−k beta.
Esta convención es distinta de ingresar h positivo en el caso Robin general.

## Archivos y guardado

- `visualizador.py`: única entrada de la aplicación.
- `parametros.json`: entradas por caso, conservadas al trasladar el visualizador.
  Se actualizan al pulsar Ejecutar, no al abrir la ventana.
- `BARRA_3D.md`: detalles de geometría, fuente y condiciones de borde.

Las simulaciones quedan en memoria. **Guardar movie** escribe en la carpeta
fija `resultados/visualizadores/<caso>/evolucion.mp4`; si falta FFmpeg usa GIF.
La exportación conserva la vista elegida y usa25 cuadros/s.
Los resultados antiguos de `resultados/e05/`, si existen, se conservan.

El cálculo reutilizable está en `desarrollo/mcplan/visualizador_termico.py`
y `desarrollo/mcplan/barra_fuente_3d.py`. Las pruebas permanecen en
`desarrollo/tests/`; las que consultan configuraciones de la ventana leen
ahora `Visualizadores/parametros.json`.

Para ejecutarlas personalmente desde la raíz:

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q -s -p no:cacheprovider desarrollo/tests/test_e05_visualizador.py
```

Puede seleccionarse un caso con `-k seno_1d` o los de la barra con `-k barra`.
Se conservan los nombres históricos de estos tests porque forman parte de
la batería docente. La reorganización no ejecutó los casos numéricos.
