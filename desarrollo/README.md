# Código y verificación

El paquete [mcplan](mcplan/) implementa el cálculo de la fundación. Los [ejecutores y sus configuraciones](../casos/README.md) indican qué datos consume cada caso. El [cierre final](../entregas/F02/README.md) enlaza las matrices y su reproducción.

| Área | Módulos principales |
| --- | --- |
| BIM y geometría | [Lectura IFC](mcplan/bim.py) · [Grilla y ocupación](mcplan/voxel.py) · [Identificación de vertidas](mcplan/vertidas_voxel.py) · [Caras e interfaces](mcplan/superficies_voxel.py) |
| Colocación e hidratación | [Activación por edad](mcplan/construccion.py) · [Fuentes de calor tabulares](mcplan/hidratacion_tabular.py) |
| Balance térmico | [Solver de la fundación](mcplan/termica_fundacion.py) · [Suelo, moldajes y aire](mcplan/entorno_termico.py) · [Conductancias y capacidades](mcplan/materiales_termicos.py) |
| Clima y escenarios | [Reanálisis](mcplan/clima_historico.py) · [Pronósticos](mcplan/clima.py) · [Adaptador de radiación del cierre](../casos/sensibilidad_h/radiacion_borde.py) |
| Exportación y visualización | [Exportación HTML](mcplan/exportacion_html.py) · [Visualizadores](../Visualizadores/README.md) |
| Verificación | [Pruebas automatizadas](tests/README_TESTS.md) · [Ejecutores de difusión, bordes y fuentes](../casos/README.md) |

El IFC, el modelo de Blender y sus herramientas están en [fundacion](fundacion/README.md). Para estudiar la formulación, consulta la [documentación técnica por tema](../documentacion/README.md).
