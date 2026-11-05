# E08 — Lab BIM → grilla → activación → cálculo térmico

Abrir `Visualizadores/E07.html`. Se conserva el nombre de la entrada existente;
el encabezado del laboratorio ahora identifica E08. El HTML es autónomo.

## Demo para el laboratorio

1. En la barra lateral, cambiar Δx entre 1, 0,5 y 0,25 m. En **Volúmenes y
   error** se muestran el volumen IFC, el volumen voxelizado y los errores
   global y por vertida. Son tres grillas previamente exportadas del IFC.
2. En **Mostrar en la vista**, desmarcar una vertida y volver a marcarla.
   Cambia el dibujo 3D, los cortes y las aristas IFC; conserva el dominio físico,
   las métricas y el cálculo térmico. La selección permite aislar otra vertida.
3. En **Construcción → Entradas de la secuencia**, cambiar, por ejemplo,
   el inicio de V02 de 6 a 12 h y su temperatura de 18 a 25 °C.
   Pulsar **Aplicar secuencia**. La línea de tiempo, las activaciones y las
   edades se actualizan. Las temperaturas anteriores se invalidan.
4. En **Ecuación de calor**, usar **Hidratación exponencial por edad**.
   q₀ es la fuente inicial en W/m³ y τ su tiempo característico en horas.
   Cada vertida genera cero antes de colocarse; después su fuente disminuye
   exponencialmente con su propia edad. Los modos constante y pulso siguen
   disponibles. No se vuelve a presentar la derivación desde curva adiabática.
5. Pulsar **Calcular temperaturas** y luego **Ver temperatura en 3D**.
   Recorrer el tiempo para observar cuándo aparece la vertida modificada,
   su temperatura inicial y la evolución posterior. Las curvas muestran
   temperaturas, potencia de la fuente e intercambio por bordes.
   La vista **Calor interno configurado** colorea la fuente, no la temperatura.
6. **Guardar entradas JSON** descarga la secuencia aplicada, la resolución,
   el punto observado, la fuente y los bordes. **Cargar entradas JSON** restaura
   un escenario del mismo IFC. **Restaurar IFC** recupera únicamente los inicios
   y temperaturas originales. Los cambios no modifican el archivo IFC.

Los cambios de tabla requieren Aplicar secuencia. Guardar JSON usa los valores
ya aplicados. Recargar el HTML recupera los valores originales; cargar el JSON
permite repetir otro escenario. La simulación se ejecuta exclusivamente bajo botón.

## Método y comprobación

El solver recibe grilla, IDs, inicios, temperaturas y parámetros como entradas.
El calendario no está fijado dentro del núcleo numérico. Solo las celdas nuevas
reciben la temperatura de colocación; las antiguas conservan su estado.
Las caras hacia futuras vertidas intercambian con el exterior hasta que ambas
vertidas están colocadas. Las interfaces activas tienen contacto perfecto.

La fuente exponencial usa directamente q₀ y τ. Su energía por intervalo se
integra de forma exacta; conducción y bordes conservan Euler explícito con
limitación del paso y corte en eventos. Los valores iniciales q₀=900 W/m³,
τ=30 h coinciden con la fuente didáctica Python existente. No hay cinética
dependiente de la temperatura ni calibración experimental.

Verificación ejecutada el 5 de noviembre de 2026:

```powershell
node desarrollo/tests/test_e07_termico_web.cjs
node desarrollo/tests/test_e08_termico_web.cjs
```

Ambas comprobaciones aprobadas. La nueva contrasta una solución adiabática
independiente con dos pasos temporales, edades separadas, cambios de inicio y
temperatura, selección de fuente y balance de energía. También comprueba lógica
de aplicación e invalidación, visibilidad y validación JSON sin navegador.

El caso IFC de 0,5 m con hidratación, Robin a 10 °C y β=5 W/(m²·K), k=2,
ρ=2400 y cp=900, durante 336 h, da Tmax≈61,778214 °C y residuo energético
≈−2,136×10⁻⁴ J. Son resultados del ensayo didáctico; no validan la malla,
las propiedades reales, S25, fisuración ni confiabilidad.

La vista previa del archivo local fue bloqueada por la política del navegador
integrado. Se verificaron sintaxis y controladores, pero no se afirma una nueva
revisión visual en navegador. No se ejecutó la batería Python completa.

Para regenerar el HTML desde el IFC:

```powershell
.\.venv\Scripts\python.exe -B Visualizadores/exportar_e07.py
```

## Entrega en Canvas

Solo dos líneas, sin informe adicional:

```text
Repositorio: https://github.com/benjagarciag/Proyecto-2-MCOC
Commit evaluado: <SHA del commit E08 publicado>
```

El SHA base registrado dentro del HTML identifica la base de la exportación;
no sustituye al commit que contenga estos cambios. Publicar y declarar ese
commit antes de la revisión. El mensaje solicitado para esta entrega es
`Entrega E08`; consultar su SHA exacto con `git log -1 --format=%H`.
