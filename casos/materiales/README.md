# Dos materiales: ejecución y parámetros

> Versión publicada E04: ejecutar desde la raíz del repositorio con el entorno
> `.venv` preparado según el README principal. El total actual es 251 pruebas;
> los recuentos de cada etapa son históricos. [Índice E04](../../entregas/E04/README.md).

Trabajar en la copia `E04_pruebas_2d`. Esta etapa no cambia el BIM ni el proyecto
original. Reutiliza el avance temporal y los bordes existentes con el argumento
opcional `materiales`; no crea otro solver numérico.

## Ejecutar

En PowerShell:

```powershell
.\.venv\Scripts\python.exe -B casos/materiales/ejecutar.py
```

Se reutiliza Python instalado, sin escribir en su entorno. Caché Matplotlib y
resultados se guardan dentro de esta copia. No se instaló nada. En VS Code,
abrir este ejecutor y seleccionar ese mismo intérprete antes de ejecutar.

El comando genera tres figuras fijas, actualizadas al repetir:

- `resultados/materiales/2d/perfiles_temperatura.png`
- `resultados/materiales/3d/perfiles_temperatura.png`
- `resultados/materiales/verificacion_interfaz/perfiles_temperatura.png`

Las dos primeras muestran materiales, temperatura inicial/final, perfiles,
media ponderada por capacidad y flujo en la interfaz. La tercera verifica un
estado estacionario inicializado con la solución exacta y compara el perfil
y el flujo con un dominio homogéneo. No es una simulación de llegada al estado
estacionario desde una condición uniforme.

## Editar

En [parametros.json](parametros.json) se declaran dos materiales con k, rho y cp,
la posición de la interfaz, la malla, las temperaturas y tf. Alpha se calcula
como k/(rho*cp); no se ingresa como cuarto valor independiente.

Los bloques ilustrativos tienen lados de 1 m; espesor 2D de 1 m. El ejecutor
muestra un plano normal a x. La API también admite interfaces normales a y/z
y mapas explícitos 0/1 de material por celda. Cada celda contiene UN material.

La interfaz debe coincidir con una cara: x=0.5 m requiere un número par de
celdas en x. Se rechaza una interfaz no alineada, sin desplazarla ni promediar
materiales dentro de la celda. `--celdas 32` cambia las celdas de ambos ejemplos;
`--dt 100` propone un paso en segundos, sujeto al control de estabilidad local.

Material 0/A ocupa la parte de menor coordenada (izquierda); material 1/B,
la parte de mayor coordenada. El contacto es perfecto, sin resistencia extra
ni almacenamiento de energía en la interfaz. La comparación homogénea usa
material A en TODO el dominio y las mismas temperaturas iniciales.

Los ejemplos transientes tienen todas las superficies adiabáticas y fuente
cero. La API conserva compatibilidad con los tres tipos de borde y fuentes
volumétricas prescritas de la etapa anterior. No incorpora hidratación.

## Repetir pruebas

Desde la raíz de la copia:

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider
```

Resultado: **251 pruebas aprobadas, 207 anteriores y 44 nuevas**. Las pruebas
no generan figuras. Otro computador debe usar su intérprete con dependencias
del `requirements.txt`; la ruta anterior corresponde a este computador.

Explicación física, ecuaciones y evidencia en
[e04_materiales.md](../../documentacion/e04_materiales.md).
