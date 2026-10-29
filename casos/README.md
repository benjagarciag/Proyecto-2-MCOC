# Casos para ejecutar

Cada subcarpeta reúne las entradas y el script de ejecución de un problema.
El código que pueda reutilizarse entre problemas se guarda en `desarrollo/mcplan/`.

| Caso | Contenido y estado |
| --- | --- |
| [1d/](1d/README.md) | Caso base del video (interior 20 °C y extremos 0/10 °C) y verificación sinusoidal de la guía. |
| [2d/](2d/README.md) | Difusión 2D con Dirichlet y solución sinusoidal exacta. |
| [3d/](3d/README.md) | Difusión 3D con Dirichlet y cortes del volumen. |
| [bordes/](bordes/README.md) | Neumann, aislamiento y Robin en 2D/3D. |
| [fuentes/](fuentes/README.md) | Generación volumétrica uniforme/localizada y convección. |
| [materiales/](materiales/README.md) | Dos materiales, contacto perfecto y comparación homogénea. |
| [Visualizador unificado](../Visualizadores/README.md) | Ventana común para modificar parámetros, ejecutar tests y reproducir casos 1D/2D/3D. |

Cada caso incluye README, parámetros y ejecutor. Las figuras se guardan en
`resultados/`, en carpetas fijas que se actualizan al ejecutar. Para el recorrido
completo, abrir [E04](../entregas/E04/README.md).
