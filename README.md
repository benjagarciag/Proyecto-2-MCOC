# Proyecto 2 — Métodos Computacionales de Obras Civiles

**Grupo 6:** Benjamín García, Luis Noriega y Matias Stierling.

Planificación de vertidas de hormigón masivo mediante modelación BIM y cálculo
térmico. Sitio: **Los Ángeles, Biobío, Parque Eólico El Rosal**.
Coordenadas del caso: `-37.277929`, `-72.368271`.

[Repositorio oficial](https://github.com/benjagarciag/Proyecto-2-MCOC) ·
[Preparación E10](entregas/E10/README.md) ·
[Demo E11](entregas/E11/README.md) ·
[HTML E11](resultados/e11/visualizador.html) ·
[HTML E12](resultados/e12/visualizador.html) ·
[Informe E12](Reportes/Reporte_E12.md) ·
[Entrega E08 y demo](entregas/E08/README.md) ·
[Antecedentes E07](entregas/E07/README.md) ·
[Ejecutores E07](casos/e07/README.md) ·
[Visualizador HTML](Visualizadores/E07.html)

## Actualización E08

El HTML existente `Visualizadores/E07.html` incorpora controles de E08:
inicios y temperaturas de colocación editables, visibilidad individual y
escenarios JSON. La hidratación exponencial por edad, ingresada directamente
como q₀ [W/m³] y τ [h], está acoplada a conducción y bordes en el navegador.
No modifica el IFC; la integración Python anterior permanece separada.
Ver [demo, comprobaciones y limitaciones](entregas/E08/README.md).

## Base Python hasta E07

**Integración Python anterior: 528 pruebas aprobadas, 0 fallidas:** 320 de la base E04/E05/E06 y 208 E07.
La rama `e07-voxelizacion-vertidas-hidratacion` incorpora geometría IFC,
voxelización, IDs y volúmenes por vertida, superficies, activación e hidratación
por edad. Los solvers publicados y el BIM se conservan.

E04 aporta difusión 2D/3D, bordes, fuentes y materiales; E05, su batería de
verificación; el [dossier E06](Reportes/E06.md) conserva su evidencia histórica.
E07 diseña y verifica una fuente de hidratación, **todavía sin acoplarla a la
conducción y bordes de la fundación**. No hay clima real ni predicción de sus
máximas temperaturas. Los recuentos de documentos antiguos son históricos.

## Visualizador HTML: geometría y ecuación de calor

Abrir **[Visualizadores/E07.html](Visualizadores/E07.html)** con doble clic en
Chrome o Edge. Permite explorar los voxeles del IFC, errores por vertida,
contactos, construcción, temperaturas y condiciones Dirichlet/Neumann/Robin.
El cálculo térmico es propio, bajo botón, con una fuente interna ingresada en
W/m³ (exponencial por edad, constante o pulso) y parámetros didácticos editables. La conversión desde curva adiabática
no se presenta en el HTML, por indicación docente. No es una predicción calibrada.

La pestaña **Ecuación de calor** muestra máximas/mínimas por instante y de toda
la corrida, curvas temporales y aportes de conducción, borde y calor interno.
Se conserva la base Python de la rama E07; el laboratorio del navegador incorpora ahora una fuente exponencial por edad
equivalente al ejemplo didáctico Python, sin depender de ese módulo en ejecución. [Uso, método y comprobaciones](Visualizadores/README.md#laboratorio-html-de-e07).

## Organización y código

Se conservan las rutas e importaciones de la arquitectura existente.

| Carpeta / archivo | Contenido |
| --- | --- |
| `desarrollo/mcplan/difusion_*.py`, `bordes_termicos.py`, `materiales_termicos.py` | Solvers y balances térmicos anteriores. |
| [bim.py](desarrollo/mcplan/bim.py) | Lectura de cinco IfcFooting, propiedades y mallas SI. |
| [voxel.py](desarrollo/mcplan/voxel.py) | Grilla, centros y máscara geométrica de ocupación. |
| [vertidas_voxel.py](desarrollo/mcplan/vertidas_voxel.py) | IDs únicos, conflictos y comparación de volúmenes. |
| [superficies_voxel.py](desarrollo/mcplan/superficies_voxel.py) | Caras exteriores, internas e interfaces orientadas. |
| [construccion.py](desarrollo/mcplan/construccion.py) | Calendario IFC, actividad, T de colocación y edades. |
| [hidratacion.py](desarrollo/mcplan/hidratacion.py) | Curva adiabática, W/m³ y energía por intervalo. |
| `desarrollo/tests/` | Pruebas automatizadas. |
| `casos/` | Ejecutores y configuraciones JSON, separados del núcleo. |
| `resultados/` | PNG y datos producidos por los casos. |
| `documentacion/`, `entregas/`, `Reportes/` | Métodos, instrucciones y evidencias por entrega. |
| `desarrollo/fundacion/` | BIM e IFC existentes; no contienen el campo térmico. |
| `Enunciados e Instrucciones/` | Material docente de referencia. |
| [Visualizadores/](Visualizadores/README.md) | Herramientas anteriores de práctica térmica. |

## Programas y dependencias

Python **3.12**, NumPy, Matplotlib, pytest e IfcOpenShell permiten ejecutar E07;
las versiones y dependencias están declaradas en [requirements.txt](requirements.txt).
VS Code es el editor recomendado. Blender/Bonsai se usa para editar el BIM,
pero no necesita estar abierto para leer el IFC ni ejecutar los cálculos.

Usar una terminal con el entorno del proyecto activado, o seleccionar ese
intérprete en VS Code. En este computador se reutiliza el entorno numérico
existente; no se instalaron paquetes. En otro equipo se prepara su entorno
Python 3.12 y se instalan las dependencias declaradas antes de ejecutar.

Los componentes opcionales Jupyter/notebooks del entorno completo no están
instalados aquí ni se verificaron en esta entrega; las pruebas y casos E07 sí.
[Detalle del entorno comprobado](entregas/E07/README.md#dependencias-y-entorno).

## Ejecutar pruebas y ejemplos

Desde la raíz del repositorio, con el entorno correcto activado:

```powershell
python -B -m pytest -q -p no:cacheprovider --basetemp=.venv/cache/pytest_revision
python -B casos/e07/extraer_ifc.py
python -B casos/e07/voxelizar_ifc.py
python -B casos/e07/identificar_vertidas.py
python -B casos/e07/clasificar_superficies.py
python -B casos/e07/activar_vertidas.py
python -B casos/e07/hidratar_vertidas.py
```

[Casos E07](casos/e07/README.md) explica entradas, opciones y unidades. Los JSON
junto a los scripts configuran resolución y parámetros; horarios y temperaturas
de colocación se leen del IFC. Los scripts no escriben ni modifican ese IFC.

Para los ejemplos anteriores: [1D](casos/1d/codigos/README.md),
[E04](entregas/E04/README.md) y [E05](entregas/E05/README.md).

## Gráficos y limitaciones

`resultados/e07/` conserva **13 PNG y tres JSON**, agrupados en `extraccion_ifc`,
`voxelizacion`, `vertidas_volumenes`, `superficies`, `activacion_temporal` e
`hidratacion`. Los ejecutores regeneran sus salidas fijas. Se pueden abrir
los gráficos y el código directamente desde el explorador de VS Code.

| Paso de voxel | Error global de volumen | Problema local |
| --- | ---: | --- |
| 1 m | 5,775 % | V02 desaparece; contacto 01–03 artificial. |
| 0,5 m | 0,899 % | V04: 37,757 % de error. |
| 0,25 m | 0,534 % | V03: 16,029 % de error. |

**Ninguna resolución está validada para el cálculo térmico definitivo.** El
error global oculta compensaciones por vertida. Las áreas cartesianas escalonadas
no son áreas CAD exactas. [Estudio de volumen](documentacion/e07_vertidas_volumenes.md).

Los 636,775193 m³ de referencia proceden de las mallas del IFC. Por separado,
la hidratación de M1 usa valores **didácticos, sin calibración experimental**:
ρ=2400 kg/m³, cp=900 J/(kg·K), θ∞=45 K y τ=30 h, del ejemplo de la guía.
[Modelo y unidades](documentacion/e07_hidratacion.md).

El ejecutor de Semana 4 integra IFC, vertidas, hidratación, suelo, capas y
clima en Python. Genera un HTML autónomo por corrida que reutiliza la interfaz
E07/E08 para reproducción, cortes, clipping, curvas y consulta de máximos.
Los VTI se exportan desde la misma corrida. Uso en entregas/E11/README.md.

Quedan pendientes justificar la malla y los parámetros térmicos del caso real.
La incertidumbre y la confiabilidad corresponden a etapas posteriores.

Cada entrega identifica un commit explícito. El SHA inicial E00
`a901e91a5b4ce84cde37ba52c48251e97cffcc04` es histórico y no identifica E07.
