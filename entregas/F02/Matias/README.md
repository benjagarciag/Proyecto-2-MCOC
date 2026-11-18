# F02 · Carpeta de trabajo de Matías Stierling

**Proyecto 2 MCOC, Grupo 6 · Parque Eólico El Rosal · evidencia al 18 de noviembre de 2026.**

**Luis y Benjamín**, aquí está el trabajo de Matías sobre fuentes, clima, escenarios, cronogramas, probabilidades y figuras de apoyo. La candidata auditada de vertida única a 12 °C y tope de 15 kW tiene **0/24 excedencias en la resolución publicada**. Las otras tres filas de la comparación quedan abiertas hasta que estén sus matrices y se confirmen los controles de obra. La presentación definitiva y el reparto oral siguen por acordar.

La evidencia corresponde a [`496dafa470afc9815d0451ee412d0a3e1fbb8dcd`](https://github.com/benjagarciag/Proyecto-2-MCOC/commit/496dafa470afc9815d0451ee412d0a3e1fbb8dcd), base de esta rama al publicarla. Se contrastaron las ramas remotas y el [estado integrado de F02](../README.md). Las configuraciones de cuatro planes estaban publicadas y la vertida única era la única matriz disponible a **12 °C, 15 kW y convección horaria**. Los cronogramas se identifican por ese corte de evidencia. El posproceso parte de las series y simulaciones ya publicadas. [Reparto del trabajo](../PENDIENTES_EQUIPO.md)

## Informes y estado

| Entrega | Verificado y disponible | Decisión pendiente |
|---|---|---|
| [M1 · Hidratación](M1_Hidratacion.md) | Adjunto idéntico a las copias oficiales, ocho integrales reproducidas, calidad 22A, β y cola documentados. | Confirmar dosificaciones, relación entre ensayos e hipótesis de ventana con el profesor. |
| [M2 · Escenarios](M2_Escenarios.md) | Tres años validados y alineados, 24 claves únicas, pesos y catálogo trazable. | Acordar fundamento y uso final de las curvas, los pesos y las hipótesis. |
| [M3 · Planes](M3_Planes.md) | Volúmenes, inicios y esperas reproducidos. Cota de caudal **10,613 h**. | Confirmación del suministro continuo, frío, protecciones y arranque. |
| [M4 · Probabilidad](M4_Probabilidad.md) | **24 filas de 15 kW** y **192 filas históricas de 12 kW** re-agregadas. Única actual: **46,284 °C**, **17,368 K**, **0/24** en la resolución disponible. | Matrices de rápida, referencia y lenta a 12 °C/15 kW, activación progresiva y confirmación de resolución. |
| [M5–M7 · Defensa](Pendientes_defensa.md) | Figuras, guion de contenidos a cubrir y decisiones con responsable. | Cerrar las figuras de 15 kW y ensayar la participación acordada. |

## Figuras listas para usar

PNG para insertar y SVG para exportar. Los archivos `H` conservan las condiciones históricas. No hay trazas núcleo/S25 ni campos de 15 kW publicados en la copia consultada. La figura 07 usa las dos temperaturas simultáneas almacenadas en el evento crítico de 15 kW.

| Origen | Figuras |
|---|---|
| Insumos y planes | [01 Hidratación](figuras/01_hidratacion.png) · [02 ERA5 y convección](figuras/02_clima_ERA5.png) · [03 Catálogo](figuras/03_catalogo.png) · [04 Gantt](figuras/04_gantt.png) |
| Candidata 12 °C/15 kW | [05 Duración–riesgo](figuras/05_duracion_riesgo_15kW.png) · [06 Máximos y umbrales](figuras/06_maximos_24_15kW.png) · [07 Diferencial a 380 h](figuras/07_diferencial_critico_15kW.png) |
| Antecedentes de 12 kW | [H01 Duración–riesgo](figuras/H01_duracion_riesgo_12kW.png) · [H02 Núcleo, S25 y ΔT en cuatro planes](figuras/H02_nucleo_S25_12kW.png) · [H03 Tres cortes del mismo campo, a 428 h](figuras/H03_cortes_12kW_428h.png) |

## Trazabilidad y comprobaciones

- [Curvas de hidratación](tablas/M1_curvas.csv), [catálogo de 24 escenarios](tablas/M2_catalogo_24.csv), [cronograma por vertida](tablas/M3_cronograma.csv), [resultados por escenario](tablas/M4_por_escenario.csv) y [comparación de planes](tablas/M4_comparacion.csv) son las tablas centrales. Son CSV UTF-8 con BOM, separados por coma y con punto decimal. Los campos térmicos vacíos significan matriz pendiente. Los riesgos se guardan como proporciones de 0 a 1.
- El [manifiesto](insumos/procedencia.json) registra **294 referencias** a archivos ya presentes en el commit auditado y la huella del adjunto, idéntica al [archivo oficial de hidratación](../../../datos/hidratacion/source_terms.txt). El [inventario](tablas/M4_inventario_matrices_GitHub.csv) lista 187 JSON con corridas o fragmentos. Los 24 fragmentos corroboran la matriz de la única.
- [`agregar.py`](scripts/agregar.py) reproduce las tablas de probabilidad con Python estándar. [`preparar.py`](scripts/preparar.py) regenera los análisis y SVG con NumPy. [`exportar_png.cjs`](scripts/exportar_png.cjs) convierte los SVG a PNG con Node y Sharp.
- [`verificar.py`](scripts/verificar.py) cubre huellas de insumos, los 24 fragmentos, conciliación con CSV oficial, catálogo, unión y umbral exacto, rechazo de matrices incompatibles, CSV reproducibles, SVG/PNG y enlaces relativos.

## Reproducir desde el clon

Desde la raíz del repositorio, entra a `entregas/F02/Matias`. Usa Git y Python 3.12 o posterior. Para regenerar las figuras se necesita además NumPy y, para convertir a PNG, Node con Sharp. Los scripts recuperan los bytes de los insumos desde el commit indicado en el manifiesto, mediante `git archive` en una carpeta temporal. Un clon con historial de esta rama ya contiene ese commit. El paquete funciona sin el adjunto original ni una carpeta de usuario de Windows.

```powershell
cd entregas/F02/Matias
python -B scripts/agregar.py
python -B scripts/preparar.py
node scripts/exportar_png.cjs
python -B scripts/verificar.py
```

Las figuras ya se incluyen y se pueden consultar sin ejecutar esas herramientas. Antes de sustituir una tabla, confirma con Luis controles, cronograma, hashes, resolución y catálogo. Repite la auditoría en una carpeta de salida nueva para conservar la evidencia de este corte.
