# Primera etapa E04: difusión 2D con Dirichlet

> Versión publicada E04: ejecutar desde la raíz del repositorio con el entorno
> `.venv` preparado según el README principal. El total actual es 251 pruebas;
> los recuentos de cada etapa son históricos. [Índice E04](../../entregas/E04/README.md).

Trabajo experimental en la copia independiente `E04_pruebas_2d`, basada en
`4c4a1d3fe21ca5cb3b92d74de5d818f9a4991aa7`. Incluido en la rama E04 publicada;
la implementación ampliada se describe en el índice de la entrega.

El solver está en `desarrollo/mcplan/difusion_2d.py`. Las entradas de la demo
están en `parametros.json`. Se usan NumPy, Matplotlib y pytest ya instalados.
El solver 1D y el BIM existentes se conservan sin cambios.

Desde la raíz de ESTA copia, en PowerShell:

```powershell
$pythonE04 = ".\.venv\Scripts\python.exe"
& $pythonE04 -B casos/2d/ejecutar.py
& $pythonE04 -B -m pytest -q -p no:cacheprovider
```

Se reutiliza el intérprete existente sin instalar paquetes ni cambiarlo.
En otro computador se debe preparar el entorno descrito en el README raíz
y utilizar su propio ejecutable Python.

El ejemplo es una placa matemática de 1 x 1 m, de espesor uniforme 1 m,
con cuatro caras en el plano a 20 °C. No hay intercambio en la dirección del
espesor. El interior comienza con `20 + 50 sin(pi x/Lx) sin(pi y/Ly)` °C.
Los parámetros k=2 W/(m K), rho=2400 kg/m³ y cp=900 J/(kg K) son valores
didácticos, sin calibración para la fundación ni atribución a mediciones.
No es una simulación de hormigonado ni una comprobación del límite de 70 °C.

La ejecución guarda una sola figura, actualizando siempre:

`resultados/2d/base/perfiles_temperatura.png`

Sus cuatro paneles muestran temperatura inicial, temperatura final, error final
respecto de la solución exacta y evolución de las celdas centrales. No se
exportan CSV, archivos históricos ni modelos BIM adicionales.

Para refinar (reemplaza la figura del caso):

```powershell
& $pythonE04 -B casos/2d/ejecutar.py --celdas 60
```

También se puede proponer un paso con `--dt 100`. Un paso que exceda el límite
del balance se rechaza. Editar el JSON permite modificar dimensiones, material,
malla, duración, temperatura de borde y amplitud inicial de esta demo.
El solver admite temperaturas constantes independientes en las cuatro caras;
la demo usa cuatro iguales para poder compararse con la solución sinusoidal.

Este ejemplo conserva su alcance: 2D, un material homogéneo, sin fuente y
Dirichlet. Los demás casos E04 incorporan 3D, Neumann, Robin, fuente física
y dos materiales sin reemplazar este solver.
Ver la explicación en `documentacion/e04_2d.md`.
