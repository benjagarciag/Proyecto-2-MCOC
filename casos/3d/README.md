# E04: difusión 3D con seis caras Dirichlet

> Versión publicada E04: ejecutar desde la raíz del repositorio con el entorno
> `.venv` preparado según el README principal. El total actual es 251 pruebas;
> los recuentos de cada etapa son históricos. [Índice E04](../../entregas/E04/README.md).

Etapa experimental autorizada, exclusivamente en `E04_pruebas_2d`.
La referencia de partida es `4c4a1d3`; esta etapa forma parte de la rama E04
publicada, sin integrar las ramas de compañeros.

Desde la raíz de esta copia, en PowerShell:

```powershell
$pythonE04 = ".\.venv\Scripts\python.exe"
& $pythonE04 -B casos/3d/Ejecutar_3D.py
& $pythonE04 -B -m pytest -q -p no:cacheprovider
```

Se usa el intérprete ya instalado, sin instalar paquetes ni alterar el entorno.
En otro computador, utilizar el entorno propio preparado con requirements.txt.

La demo utiliza un cubo matemático de 1 m por lado, 21 celdas por eje,
seis caras a 20 °C y un perfil inicial sinusoidal de amplitud 50 K.
k=2 W/(m K), rho=2400 kg/m³ y cp=900 J/(kg K) son valores didácticos;
no son datos medidos del hormigón del Grupo 6. El cubo NO es la fundación.

Se genera una sola imagen, actualizada siempre en:

`resultados/3d/base/perfiles_temperatura.png`

Incluye los tres cortes centrales XY, XZ y YZ al inicio y a las 24 h,
la evolución central y el error final frente a la solución exacta. Los seis
mapas de temperatura comparten límites de color; el error tiene escala propia.

El bloque de parámetros al comienzo de `Ejecutar_3D.py` permite modificar
dimensiones, propiedades del material, tamaño de
malla, duración, paso, temperatura de las caras y amplitud del ejemplo.
También pueden usarse `--celdas 31` y `--dt 100`. Estas opciones reemplazan
la figura del mismo caso. La API del solver admite seis temperaturas de cara
independientes; la demo usa caras iguales para verificar el seno exacto.

Se guardan siete instantáneas en memoria y una curva central con un valor por
paso. No se exportan historias numéricas, CSV, volúmenes VTK ni copias del BIM.
No contiene Neumann, Robin, fuentes ni interfaces entre materiales.

Implementación: `desarrollo/mcplan/difusion_3d.py`.
Balance común por ejes: `desarrollo/mcplan/balance_cartesiano.py`.
Pruebas: `desarrollo/tests/test_difusion_3d.py`.
Explicación oral y resultados: `documentacion/e04_3d.md`.
