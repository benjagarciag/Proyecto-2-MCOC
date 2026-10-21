# E01: revisión oral de BIM, difusión y solver 1D

**Fecha:** miércoles 21 de octubre de 2026. **Puntaje:** 3 puntos.

Fuente: [enunciado oficial E01](../../Enunciados%20e%20Instrucciones/E01_Semana_1_Revision_oral_BIM_difusion_y_solver_1D.txt).

## Requisitos y estado

- [x] README mínimo con instalación y organización del proyecto.
- [x] Entorno inicial Python 3.12 con dependencias fijadas.
- [x] Primeros tests automatizados (31 casos comprobados).
- [x] Primer modelo IFC/Bonsai con cinco vertidas y propiedades leídas desde Python, incluido en esta entrega.
- [x] Implementación inicial del solver 1D.
- [ ] Preparación oral de cada integrante.

G00, G01, G02 y G05 ya están disponibles en
[el índice de material del profesor](../../Enunciados%20e%20Instrucciones/README.md).
Cada integrante debe completar su lectura; la disponibilidad no certifica que
el equipo las haya leído.

## Dónde está el trabajo

| Parte | Ubicación | Estado |
| --- | --- | --- |
| Instalación | [README principal](../../README.md#instalar-en-otro-computador) | Preparada |
| Dependencias | [requirements.txt](../../requirements.txt) | Versiones fijadas |
| Problema físico y solución exacta | [caso_1d.md](../../documentacion/caso_1d.md) | Definidos |
| Solver | [difusion_1d.py](../../desarrollo/mcplan/difusion_1d.py) | Implementado con Dirichlet y control de estabilidad |
| Caso ejecutable | [casos/1d/](../../casos/1d/README.md) | Ejecuta los cuatro casos; JSON para Dirichlet |
| Explicación para estudiar | [Notebook 1D](../../documentacion/explicacion_solver_1d.ipynb) | Cuatro scripts explicados y ejecutados: Dirichlet, Neumann, Robin y calor interno |
| Tests | [desarrollo/tests/](../../desarrollo/tests/README_TESTS.md) | 31 casos pasan, incluida reproducción de los 20 perfiles del video |
| BIM/IFC | [Fundación IFC](../../desarrollo/fundacion/README.md) | IFC4, cinco IfcFooting con propiedades y geometrías trianguladas desde Python |
| Caso base del video | `resultados/1d/base/` | Se genera al ejecutar; referencia previa del centro ≈ 5,22483 °C |
| Verificación exacta | `resultados/1d/verificacion_seno/` | Se genera al ejecutar; referencia previa del error final ≈ 0,00235449 K |

## Preparación oral

Cada integrante debe poder abrir y explicar el código real, además de responder
sobre BIM, IFC, Blender y Bonsai; independencia del solver respecto de Blender;
$k$, $\rho$, $c_p$ y $\alpha$; balance de energía; condición inicial;
Dirichlet, Neumann y Robin; discretización 1D y estabilidad explícita.

## Entrega en Canvas

Esta entrega incorpora el modelo BIM unificado y sus scripts en el commit
`Entrega E01`. Se conserva un único `fundacion.ifc` con propiedades y un único
`fundacion.blend` con materiales, terreno, iluminación y cámara.
Para consultar el SHA completo, ejecutar `git rev-parse HEAD`
desde ese commit. Declarar en Canvas el SHA de la versión que se evaluará.
Las 31 pruebas volvieron a pasar el 21 de octubre.

La demostración de modificar una pieza en Bonsai, guardar y detectar el cambio
desde Python, junto con variar Delta x/Delta t en la demo 1D, se exige
explícitamente en E02; sigue pendiente y conviene practicarla. E01 evalúa
comprensión oral y navegación por código real.

- Repositorio: https://github.com/benjagarciag/Proyecto-2-MCOC
- Commit de entrega: `Entrega E01`. Declarar su SHA completo en Canvas.
- Nota opcional: hasta 100 palabras indicando lo incompleto.

No se pide informe adicional. Este archivo sirve para organizar el trabajo del
equipo y no sustituye la revisión oral ni las evidencias pendientes.
