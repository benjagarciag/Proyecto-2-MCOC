# E07 — Voxelización, vertidas e hidratación

Grupo 6. Evaluación: miércoles 4 de noviembre de 2026.

Base: `main` publicado en `e281ec4bc6d96f8e3481d08112cc94dcfff5f51c`
(Entrega E06). La entrega se prepara en `E07_integracion` y se publica en la rama
`e07-voxelizacion-vertidas-hidratacion`, conservando main y los archivos de los
compañeros. El SHA base no contiene E07: para Canvas se utiliza el commit de
esta rama publicado en su historial. El PR queda pendiente de autorización para fusionar.

## Alcance preparado

| Requisito | Implementación |
| --- | --- |
| Geometría IFC | `bim.extraer_fundacion_ifc`: cinco IfcFooting, propiedades, mallas y unidades. |
| Voxelización | `voxel.voxelizar_fundacion`: ocupación por centros en coordenadas IFC. |
| Vertidas y volúmenes | `vertidas_voxel.asignar_vertidas` y `comparar_volumenes`: IDs, conflictos y errores. |
| Superficies | `superficies_voxel.clasificar_caras`: exterior, internas e interfaces únicas y orientadas. |
| Activación | `construccion.avanzar_construccion`: horario IFC, nuevos voxeles, T persistente y edades. |
| Hidratación | `hidratacion.CurvaAdiabatica` y `HidratacionVertidas`: curva, W/m³ y energía exacta por intervalo. |

Los horarios IFC son 0/6/12/18/24 h; T de colocación 19/18/18/18/18 °C. El IFC
no se modifica. El estado final recupera las superficies de la fundación completa.

## Pruebas y ejemplos

**528 pruebas aprobadas, 0 fallidas** (320 anteriores y 208 E07).

```powershell
# Terminal con el entorno del proyecto activado
python -B -m pytest -q -p no:cacheprovider --basetemp=.venv/cache/pytest_integracion_01
```

Se comprueban geometrías analíticas, unidades y coordenadas, conservación de
ocupación/IDs, conflictos, áreas y orientación, activaciones inmediatamente
antes/después de eventos, persistencia de temperaturas no uniformes, edades,
integración de hidratación y recuperación adiabática con el solver existente.

También se ejecutan los casos publicados 1D, 2D, 3D, bordes, fuentes y dos
materiales, y el bloque reproducible del dossier `Reportes/E06.md`. Este último
verifica convergencia espacial/temporal, conservación, fuente y Robin. Los
tests de E05 forman parte de la batería completa. No se automatizan botones
de las ventanas gráficas ni se cambia el dossier histórico.

Para no reemplazar PNG publicados de E04, sus figuras de comprobación se guardan
en `.venv/cache/validacion_anteriores/`, redirigiendo solo la escritura de imágenes
durante la ejecución. No se alteran parámetros ni fórmulas. En 1D se utiliza
el argumento existente `--salida`. Esas figuras y logs no forman parte de la entrega.

Los seis ejecutores E07 se prueban con sus parámetros completos, incluidos
gráficos, en la copia nueva. Solo actualizan `resultados/e07/`. Los resultados
de `E07_pruebas` permanecen intactos.

Comprobación final: los trece PNG regenerados son idénticos byte a byte a
los de `E07_pruebas`; los tres JSON conservan exactamente sus datos. La
comparación de archivos de proyecto mediante SHA256 confirma que tanto
`E07_pruebas` como la carpeta original del proyecto permanecen
sin cambios (excluyendo metadatos Git, el entorno y las cachés del inventario).
Respecto del main base, los únicos archivos existentes modificados son el
README principal y el verificador IFC autorizado. El BIM, IFC, solvers y
`Reportes/E06.md` son idénticos a la base publicada.

## Limitaciones numéricas conservadas

| h [m] | Voxeles | Volumen [m³] | Error global | Limitación local |
| --- | ---: | ---: | ---: | --- |
| 1 | 600 | 600 | 5,775 % | V02: 0 voxeles, 100 % de error; interfaz 01–03 artificial. |
| 0,5 | 5140 | 642,5 | 0,899 % | V04: 37,757 % de error. |
| 0,25 | 40536 | 633,375 | 0,534 % | V03: 16,029 % de error. |

Referencia IFC: 636,775193 m³. Ninguna resolución queda completamente validada:
el error global pequeño no garantiza precisión por vertida. Las caras de voxel
son escalonadas; sus áreas no certifican el área euclídea CAD. No se cambió el
criterio de centros ni se ajustó la geometría para mejorar métricas.

La mezcla M1 utiliza parámetros externos **didácticos**, procedentes del ejemplo
exponencial de la guía: ρ=2400 kg/m³, cp=900 J/(kg·K), θ∞=45 K y τ=30 h.
No es una calibración experimental y no se añaden propiedades al IFC. No hay
acoplamiento de hidratación con conducción/bordes en la fundación, clima real
ni predicción de Tmax. Esos desarrollos quedan para autorización posterior.

En el caso didáctico se obtiene q inicial=900 W/m³ y energía acumulada
0–24 h=22,049599 GJ con los volúmenes voxelizados. La fuente es cero antes
de cada colocación; la energía de intervalos cruzados se integra desde el evento.

## Dependencias y entorno

Se reutiliza el Python existente, sin instalar paquetes ni copiar `.venv`.
NumPy 2.5.4, Matplotlib 3.11.2, pytest 9.1.1, IfcOpenShell 0.9.0.post1,
Pillow 13.0.0 y Shapely 2.2.0 están disponibles y coinciden con requirements.
Tkinter también está disponible. `pip check`: sin requisitos instalados rotos.

El entorno no contiene 83 paquetes del conjunto completo declarado, principalmente
Jupyter/notebooks y sus dependencias. Por tanto **la ejecución del notebook y el
entorno completo de requirements no están verificados aquí**. Esto no bloquea
los tests ni los ejecutores E04–E07 probados. Se conserva requirements.txt;
no se instalan paquetes ni se elimina la funcionalidad de notebooks.

La ruta `$pythonE07` anterior es propia de este computador. En otro equipo se
usa su intérprete y el entorno declarado; no se ha realizado una instalación
limpia adicional durante esta preparación.

## Archivos de incorporación

Respecto del main base: 47 archivos nuevos y dos modificados, sin incluir cachés.

- Seis módulos nuevos `desarrollo/mcplan/{bim,voxel,vertidas_voxel,superficies_voxel,construccion,hidratacion}.py`.
- Seis tests nuevos `desarrollo/tests/test_*.py` con esos mismos nombres.
- Doce archivos de `casos/e07/`: seis ejecutores, cinco JSON y su README.
- Seis documentos `documentacion/e07_*.md` de las etapas originales.
- Dieciséis resultados E07: trece PNG y tres JSON.
- Este documento `entregas/E07/README.md`.
- Modificados: README principal y `desarrollo/fundacion/verificar_ifc.py`,
  que delega en el lector reutilizable conservando su comando anterior.

Las notas históricas de los documentos por etapa mencionan `E07_pruebas`, donde
se desarrollaron. Para ejecutar esta integración, seguir el README principal
y `casos/e07/README.md`, que apuntan a esta copia.

Quedan fuera del paquete: `.git/`, `.venv/`, cachés, logs de verificación,
scripts auxiliares temporales, videos y copias completas del proyecto. No se incorporan interfaces web. No se copian ni reemplazan BIM, IFC, Reportes/E06,
solvers o archivos de compañeros.

## Publicación y revisión de main

La rama de entrega se publica con autorización del equipo. El historial de
GitHub proporciona el SHA exacto para Canvas. El PR permite revisar los cambios
sin modificar main. No se realiza force push ni fusión automática.

Antes de una futura incorporación a main se debe comprobar si cambió desde la
base, revisar únicamente estos archivos, repetir verificaciones y obtener
la autorización correspondiente. Las rutas y solvers existentes se conservan.
