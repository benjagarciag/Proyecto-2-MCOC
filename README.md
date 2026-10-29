# Proyecto 2 - MCOC

**Grupo 6:** Benjamín García, Luis Noriega y Matias Stierling.

**Repositorio:** https://github.com/benjagarciag/Proyecto-2-MCOC

Planificación de vertidas de hormigón masivo mediante simulación térmica y
confiabilidad. Sitio: Los Ángeles, Biobío, Parque Eólico El Rosal.
Coordenadas meteorológicas: `-37.277929`, `-72.368271`.

## Empieza aquí

| Quiero… | Abrir |
| --- | --- |
| Modificar y visualizar los casos térmicos en una sola ventana | [Visualizadores: ejecución y funciones](Visualizadores/README.md) |
| Revisar E04: 2D/3D, bordes, fuentes y dos materiales | [E04: ejecución, pruebas y resultados](entregas/E04/README.md) |
| Practicar E05 y cambiar parámetros de los tests | [E05: batería y guía de estudio](entregas/E05/README.md) |
| Ejecutar los códigos 1D | [casos/1d/codigos/](casos/1d/codigos/README.md) |
| Entender el código y la física con gráficos | [Notebook explicativo](documentacion/explicacion_solver_1d.ipynb) |
| Agregar las propiedades de las vertidas al IFC | [Fundación: punto 23 de Bonsai](desarrollo/fundacion/README.md) |
| Saber qué falta para esta entrega | [E01: requisitos y estado](entregas/E01/README.md) |

## Carpetas del proyecto

| Carpeta | Contenido |
| --- | --- |
| [casos/](casos/README.md) | Ejemplos 1D, 2D, 3D, bordes, fuentes y dos materiales. |
| [documentacion/](documentacion/README.md) | Explicaciones físicas y notebook de estudio. |
| [entregas/](entregas/README.md) | Requisitos, pendientes y enlaces de cada evaluación. |
| [Enunciados e Instrucciones/](Enunciados%20e%20Instrucciones/README.md) | Enunciados, guías, calendario y archivos recibidos. |
| `resultados/` | Figuras de referencia de E04; los ejecutores actualizan las imágenes de su caso. |
| [desarrollo/](desarrollo/README.md) | Solver reutilizable, pruebas y herramientas de mantenimiento. |
| [Visualizadores/](Visualizadores/README.md) | Ventana unificada 1D/2D/3D, entradas editables y reproducción temporal. |

Guardar cada archivo en su carpeta y enlazarlo desde las entregas que lo usen.
Crear carpetas nuevas solo cuando exista contenido para ellas. El BIM existente
está en `desarrollo/fundacion/`; los ejemplos E04 son dominios didácticos independientes.

## Ejecutar E04

Con el entorno preparado según la sección de instalación, desde la raíz:

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe -B casos/2d/Ejecutar_2D.py
.\.venv\Scripts\python.exe -B casos/3d/Ejecutar_3D.py
.\.venv\Scripts\python.exe -B casos/bordes/Ejecutar_Bordes.py
.\.venv\Scripts\python.exe -B casos/fuentes/Ejecutar_Fuentes.py
.\.venv\Scripts\python.exe -B casos/materiales/ejecutar.py
```

**296 pruebas aprobadas en la última ejecución completa**, incluidas29 variantes
de práctica para E05. La versión actual recopila320 tests; los nuevos casos
del visualizador quedan para ejecución del usuario, por su preferencia de estudio.
Los tests no generan figuras; los ejecutores de ejemplos guardan sus figuras en `resultados/`.
El núcleo ampliado es `desarrollo/mcplan/difusion_bordes.py`; conserva los
solvers iniciales e incorpora bordes mixtos, generación W/m³ y dos materiales
opcionales con contacto perfecto. La interfaz material coincide con caras de
la malla. No se necesita Blender para ejecutar estas simulaciones.

La [guía E04](entregas/E04/README.md) enlaza las explicaciones y los 12 gráficos.
Los casos son verificaciones matemáticas; no incluyen hidratación calibrada,
clima, Monte Carlo ni una simulación de la fundación real.

## Ejecutar y estudiar el caso 1D

Abrir PowerShell en la raíz del proyecto.

Para abrir el gráfico del primer código:

```powershell
.\.venv\Scripts\python.exe casos/1d/codigos/01_1d_dirichlet_verification.py
```

Para abrir la explicación de los cuatro códigos:

```powershell
.\.venv\Scripts\python.exe -m jupyterlab documentacion/explicacion_solver_1d.ipynb
```

En Jupyter, seleccionar **Python 3.12 (Proyecto 2)**. Reiniciar el kernel y
ejecutar todas las celdas para repetir los cálculos y gráficos.

Para guardar únicamente las imágenes de perfiles de temperatura:

```powershell
.\.venv\Scripts\python.exe casos/1d/ejecutar.py
```

Los archivos de `resultados/1d/base/` se actualizan al repetir la ejecución.
El comando sin opciones también genera las imágenes de perfiles de Neumann, Robin
y calor interno en `resultados/1d/neumann/`, `robin/` y `calor_interno/`.
Se guardan las mismas figuras de `casos/1d/codigos/`, incluida la figura de Robin
con sus dos paneles. Ejecutar directamente uno de esos scripts también guarda
su imagen y la muestra en una ventana.
Para uno solo, añadir por ejemplo `--caso robin`.
El caso sinusoidal usa `resultados/1d/verificacion_seno/`. No se crean carpetas
nuevas por cada ejecución.

Los resultados anteriores fueron eliminados. La primera ejecución crea la
carpeta fija del caso; las siguientes actualizan sus archivos.

## Instalar en otro computador

Usar **Python 3.12**. Desde la raíz:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m ipykernel install --prefix .venv --name python3 --display-name "Python 3.12 (Proyecto 2)"
```

No es necesario activar el entorno para usar estos comandos.
`.venv/` contiene las dependencias y debe conservarse. Está oculta en el
Explorador de Windows para mantener limpia la vista; no se sube a Git.
Las cachés del notebook y los gráficos se guardan dentro de ese entorno.

## Archivos de configuración en la raíz

| Archivo | Para qué sirve |
| --- | --- |
| `requirements.txt` | Instalar las versiones de las dependencias. |
| `pytest.ini` | Encontrar y ejecutar las pruebas en `desarrollo/tests/`. |
| `.gitignore` | Evitar subir entornos y temporales a Git. |
| `AGENTS.md` | Instrucciones y contexto para trabajar con el asistente. |

## Estado actual

La preparación E04 está publicada en la rama `e04-difusion-2d-3d`, desarrollada
en la copia independiente `E04_pruebas_2d`. No integra la rama de compañeros ni
modifica el BIM. Los documentos por etapa conservan su contexto histórico;
el [índice E04](entregas/E04/README.md) describe el estado conjunto actual.

Hay códigos 1D, explicación ejecutada, pruebas automatizadas y un primer
[modelo IFC con propiedades de las cinco vertidas](desarrollo/fundacion/README.md).
La lectura desde Python comprueba identidades, propiedades y triangulación.
Para E01 queda la preparación individual y declarar el SHA evaluado.
Para E02 sigue pendiente demostrar cambios Bonsai → IFC → Python y variar
Delta x/Delta t en la demo 1D. La validación geométrica detallada sigue pendiente.
El [seguimiento de E01](entregas/E01/README.md) concentra la evidencia actual.

**SHA inicial E00:** `a901e91a5b4ce84cde37ba52c48251e97cffcc04`.
Cada evaluación declara su propio commit; el SHA inicial no identifica las
entregas posteriores.
