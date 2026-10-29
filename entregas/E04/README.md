# E04 — Difusión 2D/3D y condiciones de borde

Grupo 6. Preparación de la revisión oral del 28 de octubre de 2026.
Rama: **e04-difusion-2d-3d**. Base: `4c4a1d3fe21ca5cb3b92d74de5d818f9a4991aa7`.
Desarrollado y verificado en la copia independiente `E04_pruebas_2d`; publicación
autorizada por el usuario. No se alteró el proyecto original ni el BIM y no se
integraron las otras ramas. El commit exacto se consulta en el historial de
esta rama; al evaluar se debe usar su enlace permanente, no un SHA de E01.

## Ejecutar desde una copia del repositorio

Python 3.12. Preparar el entorno con el `requirements.txt` raíz si aún no existe;
las dependencias ya instaladas no necesitan reinstalarse. No requiere Blender
para el cálculo. Desde la raíz, en PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider
```

Resultado verificado: **251 pruebas aprobadas** (31 de 1D, 22 de 2D, 30 de 3D,
73 de bordes, 51 de fuentes y 44 de materiales). Para ejecutar los ejemplos:

```powershell
.\.venv\Scripts\python.exe -B casos/2d/Ejecutar_2D.py
.\.venv\Scripts\python.exe -B casos/3d/Ejecutar_3D.py
.\.venv\Scripts\python.exe -B casos/bordes/Ejecutar_Bordes.py
.\.venv\Scripts\python.exe -B casos/fuentes/Ejecutar_Fuentes.py
.\.venv\Scripts\python.exe -B casos/materiales/ejecutar.py
```

Los casos 2D y 3D se configuran al comienzo de `casos/2d/Ejecutar_2D.py`
y `casos/3d/Ejecutar_3D.py`. Los bordes se configuran en `casos/bordes/Ejecutar_Bordes.py`.
Las fuentes se configuran en `casos/fuentes/Ejecutar_Fuentes.py`.
Materiales conserva su `parametros.json` editable. Cada README explica las opciones. Los
comandos actualizan las figuras de su caso, sin exportar historias ni CSV.
No ejecutar los módulos de `desarrollo/mcplan/` como scripts: se usan desde
los ejecutores. En Linux/macOS usar `.venv/bin/python` en lugar de la ruta
Windows. No se incluyen el entorno `.venv`, cachés ni configuración personal.

## Organización y evidencia

| Etapa | Código/ejemplo | Explicación |
|---|---|---|
| 2D Dirichlet | [Caso 2D](../../casos/2d/README.md) | [Balance 2D](../../documentacion/e04_2d.md) |
| 3D Dirichlet | [Caso 3D](../../casos/3d/README.md) | [Balance 3D](../../documentacion/e04_3d.md) |
| Neumann/Robin | [Bordes](../../casos/bordes/README.md) | [Bordes y estabilidad](../../documentacion/e04_bordes.md) |
| Generación W/m³ | [Fuentes](../../casos/fuentes/README.md) | [Unidades y energía](../../documentacion/e04_fuentes.md) |
| Dos materiales | [Materiales](../../casos/materiales/README.md) | [Interfaz y conductividad armónica](../../documentacion/e04_materiales.md) |

El núcleo ampliado es [difusion_bordes.py](../../desarrollo/mcplan/difusion_bordes.py).
Reutiliza el avance explícito, bordes y fuentes con argumentos opcionales. Los
solvers iniciales y sus pruebas permanecen disponibles. Las explicaciones por
etapa conservan el estado histórico local; este índice resume la versión publicada.

Balance: `C_i*dT_i/dt = sum G_ij*(T_j-T_i) + q'''_i*V_i + P_borde_i`, con
`C_i=rho_i*cp_i*V_i`. En contacto perfecto,
`G_ij=A/[(d/2)/k_i+(d/2)/k_j]`. Paso suficiente:
`dt_max=min_i C_i/(sum G_ij+sum H_borde_i)`. Todas las potencias usan el estado
anterior y los intercambios interiores se calculan una vez con signos opuestos.

## Figuras de referencia publicadas

Las imágenes son las verificadas en el computador de desarrollo; al ejecutar
se recalculan. Propiedades didácticas, sin calibración de la fundación.

| Ejemplo | Figura |
|---|---|
| 2D Dirichlet | [Temperaturas y error](../../resultados/2d/base/perfiles_temperatura.png) |
| 3D Dirichlet | [Cortes del volumen](../../resultados/3d/base/perfiles_temperatura.png) |
| 2D adiabático | [Conservación](../../resultados/bordes/2d_adiabatico/perfiles_temperatura.png) |
| 2D Robin | [Enfriamiento](../../resultados/bordes/2d_robin/perfiles_temperatura.png) |
| 3D Neumann | [Flujo impuesto](../../resultados/bordes/3d_neumann/perfiles_temperatura.png) |
| 3D Robin | [Convección](../../resultados/bordes/3d_robin/perfiles_temperatura.png) |
| Fuente uniforme | [Solución adiabática exacta](../../resultados/fuentes/uniforme/perfiles_temperatura.png) |
| Fuente localizada | [Distribución espacial](../../resultados/fuentes/localizada/perfiles_temperatura.png) |
| Fuente y Robin | [Generación y pérdidas](../../resultados/fuentes/robin/perfiles_temperatura.png) |
| Dos materiales 2D | [Contacto y comparación](../../resultados/materiales/2d/perfiles_temperatura.png) |
| Dos materiales 3D | [Bloques y cortes](../../resultados/materiales/3d/perfiles_temperatura.png) |
| Interfaz estacionaria | [Perfil exacto y continuidad del flujo](../../resultados/materiales/verificacion_interfaz/perfiles_temperatura.png) |

## Alcance y preparación oral

Listos para demostrar: grillas 2D/3D, balance energético, Dirichlet/Neumann/Robin,
generación prescrita constante, contacto perfecto entre dos materiales,
estabilidad local, conservación, soluciones exactas y refinamiento. La interfaz
de materiales debe coincidir con caras de la malla; no hay mezclas subvoxel.
La fuente no depende de temperatura ni representa una curva de hidratación.

Pendiente: practicar la defensa individual, demostrar cambios de dx/dt y
contrastar cualquier rúbrica E04 adicional. El calendario disponible indica
«revisión oral: 2D/3D + condiciones de borde»; no se dispone aquí de una rúbrica
desglosada. E05 y E06 son actividades separadas. Hidratación, clima, Monte Carlo
y conexión de estos ejemplos al BIM están fuera de esta entrega. No se afirma
cumplimiento de límites térmicos de obra ni lectura completa del Anexo 4 ICH.
