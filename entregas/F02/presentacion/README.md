# Preentrega F02

Archivos vigentes: `F02_Grupo6_Pre_entrega.pptx` y `F02_Grupo6_Pre_entrega.pdf`.

Ocho láminas principales, índice y quince respaldos (24 en total). Se conservan las ocho secuencias de animación y los247efectos del PPT fuente, sus destinos y orden. Tablas, nueve gráficos y ecuaciones siguen editables. Los libros embebidos coinciden exactamente con las cachés de los gráficos. El PDF es estático, con24páginas y navegación; su texto está rasterizado a doble resolución.

El guion conserva los ocho intervalos personalizados, reparto y clics, con objetivo6:25. Se modificaron solo contenidos necesarios: manta504h/sombra90%, alcance14y28d, comparación60/55, sensibilidad y limitaciones. Las notas S1–S8 contienen ese mismo diálogo. No se afirma ensayo oral ni reproducción de animaciones en PowerPoint.

La propuesta fina tiene24pares completos a0,20m/300s hasta672h: Tmax47,0322°C,Δ15,7202K,Pf0 bajo el catálogo. Conservar el10%solar residual. Ni la cola cero de la fuente implica fin de hidratación ni cumplir estas métricas valida una instalación real.

Fuentes: [cierre final](../cierre_revision_final/RESULTADOS_CIERRE.md), [guion](../GUION_ORAL_F02.md), [brief](../BRIEF_DIAPOSITIVAS_F02.md), [puntos restantes](../CIERRE_PUNTOS_RESTANTES.md). Archivos con nombres anteriores son antecedentes, no la propuesta vigente.

## Reproducción documental

1. `preparar_pre_entrega.py` lee el guion actual y genera `recursos/contenido_pre_entrega.json`. El flag `--actualizar-guion` requiere la copia privada original y no debe ejecutarse sobre futuras ediciones del usuario.
2. `editar_pre_entrega.mjs` importa la copia fuente mediante Artifact Tool; realiza las ediciones de texto.
3. `postprocesar_pre_entrega.py` reintegra la autoría sin perder animaciones, actualiza datos nativos, respaldos y notas. Requiere Python documental con lxml/openpyxl.
4. `finalizar_pre_entrega.mjs` valida paquete, geometría, fuentes, tablas/gráficos y24láminas; exporta el PDF (alternativa ReportLab con renders2x si falta fuente del exportador nativo).

Intermedios privados en `.venv/cache/pre_entrega_f02/`. Los scripts numéricos con huellas no fueron alterados para esta edición. La identificación de la publicación se obtiene con `git log -1 -- entregas/F02/presentacion/F02_Grupo6_Pre_entrega.pptx`; no confundir el SHA base6718163 con el commit de preentrega.
