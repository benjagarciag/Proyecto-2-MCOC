# Ejecutores por tarea

Ejecuta los comandos desde la raíz del repositorio. Las rutas internas se mantienen para que sigan funcionando los comandos históricos y las auditorías con manifiestos de huellas.

| Tarea | Entradas |
| --- | --- |
| Auditar y reproducir el cierre final | [Comprobación de solo lectura](sensibilidad_h/verificar_resultados_publicados.py) · [Auditor original](sensibilidad_h/auditar_cierre_f02.py) · [Ejecutor](sensibilidad_h/ejecutar_cierre_f02.py) · [Configuración](sensibilidad_h/cierre_f02.json) |
| Explorar controles de obra | [Circuitos](sensibilidad_h/confirmar_circuitos.py) · [Radiación](sensibilidad_h/sensibilidad_radiacion.py) · [Protección posterior](sensibilidad_h/proteccion_postdesmolde.py) |
| Construir y comparar escenarios | [Catálogo y parámetros](incertidumbre/parametros.json) · [Ejecutor de incertidumbre](incertidumbre/ejecutar.py) · [Verificaciones complementarias](f02_verificaciones/README.md) |
| Importar IFC y discretizar la fundación | [Extracción, voxelización, vertidas y activación](e07/README.md) |
| Visualizar simulaciones deterministas previas | [Ejecutor de 48 h y 14 días](semana4/ejecutar.py) · [Vista 3D](semana4/ver_3d.py) · [Dependencias de vista](semana4/requirements-vista.txt) |
| Comprobar difusión y balances básicos | [1D](1d/codigos/README.md) · [2D](2d/) · [3D](3d/) · [Bordes](bordes/) · [Fuentes](fuentes/) · [Materiales](materiales/) |
