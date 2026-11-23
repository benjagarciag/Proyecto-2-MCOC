# Proyecto 2 · Control térmico de hormigón masivo

**Grupo 6 · Benjamín García, Luis Noriega y Matías Stierling.** Planificación de la colocación de la fundación del Parque Eólico El Rosal, Los Ángeles, Biobío.

## Entrega final

- **F01 · Artículo y plan de control.** [PDF](entregas/F01/Articulo-Final/F01_Grupo6.pdf) · [Proyecto Overleaf](entregas/F01/Articulo-Final/F01_Grupo6_Overleaf.zip) · [Fuentes LaTeX](entregas/F01/articulo/README.md).
- **F02 · Defensa.** [PowerPoint final](entregas/F02/presentacion/F02_Grupo6_FINAL.pptx) · [Guion](entregas/F02/GUION_ORAL_F02.md) · [Evidencia y reproducción](entregas/F02/README.md).

La propuesta evaluada coloca **636,775 m³ en 10,61 h** a **60 m³/h y 12 °C**, en una operación continua de once capas. El modelo supone nueve circuitos de refrigeración, última manta hasta **504 h de edad local** y sombra solar del 90 % posterior. La confirmación de 24 escenarios a **0,20 m y 300 s** hasta 672 h obtuvo **47,03 °C**, **15,72 K** y **0/24 excedencias**. Es un resultado condicionado al catálogo, al modelo y a los controles simulados. [Cierre técnico](entregas/F02/cierre_revision_final/RESULTADOS_CIERRE.md)

## Trabajo por tema

| Área | Qué contiene | Acceso |
| --- | --- | --- |
| Geometría BIM y colocación | IFC, Blender, voxelización, caras e interfaces, activación y cronograma. | [Modelo BIM](desarrollo/fundacion/README.md) · [Métodos](documentacion/geometria_y_activacion/README.md) |
| Modelo térmico | Difusión, hidratación, conductancias, suelo, convección y radiación. | [Método](documentacion/modelo_termico/README.md) · [Bordes y clima](documentacion/entorno_termico/README.md) · [Solver](desarrollo/mcplan/termica_fundacion.py) |
| Escenarios y planes | Curvas de calor, reanálisis, colocación, controles y riesgo ponderado. | [Datos](datos/README.md) · [Ejecutores por propósito](casos/README.md) |
| Resultados y verificación | Matrices del cierre, sensibilidad numérica, cronogramas, curvas, cortes y pruebas. | [Resultados por tema](resultados/README.md) · [Pruebas](desarrollo/tests/) |
| Antecedentes | Entregas intermedias, reportes, demostraciones y estudios de configuraciones anteriores. | [Archivo del proyecto](archivo/README.md) |

## Reproducción

Desde la raíz de un clon Git con historial, usa Python 3.12 y las dependencias de [requirements.txt](requirements.txt). La comprobación de solo lectura revisa las piezas y el resumen publicado. El ejecutor de cierre, sin argumentos, muestra el resumen.

```sh
python -X utf8 -B casos/sensibilidad_h/verificar_resultados_publicados.py
python -X utf8 -B casos/sensibilidad_h/ejecutar_cierre_f02.py
python -B -m pytest -q
```

La [configuración final](entregas/F02/cierre_revision_final/CONFIGURACION_FINAL_REVISADA.json) identifica el protocolo del cálculo. La [pauta docente](Enunciados%20e%20Instrucciones/README.md) conserva los requisitos de entrega.
