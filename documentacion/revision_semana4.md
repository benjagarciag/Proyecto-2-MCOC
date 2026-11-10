# Revisión de Semana 4 — E10, E11 y E12

## Versión y alcance

Branch recibido `codex/semana-4`, commit `0f165d801e06745ff3ee4d99a8278162787a06ad`.
Copia local `Proyecto2-Semana4-Revision`, branch `revision/semana-4`.
Código corregido y ejecutado en `195b797331c1ae0e50bebb1ac09a1561fa87008d`.
El SHA del paquete final de evidencia se obtiene con `git rev-parse HEAD`.

Se contrastaron los tres enunciados, las instrucciones generales, el IFC, los módulos añadidos, los snapshots, las pruebas, los VTI y el reporte. La batería inicial tuvo errores de permisos en el directorio temporal de Windows. Al usar un directorio accesible, las 542 pruebas recibidas pasaron. La batería corregida tiene 550 pruebas aprobadas. También pasaron las baterías Node E07/E08. Se renderizaron slice y clipping con PyVista/VTK en Windows.

## Trabajo recibido

- E10 incorpora suelo equivalente, convección con resistencias de moldaje y aislación, retiros independientes por edad, cliente GFS para El Rosal y snapshots exclusivos. Incluye demos y guía oral.
- E11 conecta 49 marcas horarias de aire a una corrida de 48 horas, con interpolación, activación por IFC e hidratación. Exporta campos de pico, diferencial y final a VTI, gráficos y resumen. PyVista permite slice y clipping.
- E12 ejecuta 336 horas con 337 marcas ERA5, suelo y capas. Evalúa Tmax y Tmax del dominio menos Tmin S25. Incluye Markdown menor que 1400 palabras con plan, bordes, curvas, ubicaciones y conclusión.

## Correcciones aplicadas

1. Los resúmenes identifican commit, cambios locales, fecha de ejecución, parámetros efectivos, hash del archivo de parámetros y plan completo de vertidas. Los VTI identifican commit, hash climático y fase.
2. Los lectores rechazan metadata incoherente en modelo, unidades, variables, cantidad de marcas, extremos temporales y fecha de descarga sin huso. El ejecutor rechaza tipos meteorológicos desconocidos.
3. La serialización ocurre antes de crear el snapshot exclusivo, para evitar archivos parciales por errores de serialización.
4. La entrada de hidratación usa q0 = 900 W/m³ y tau = 30 h, como E09. Se reutiliza la representación interna existente. La fuente numérica conserva su equivalencia con la recibida.
5. `--salida` permite corridas alternativas sin sobrescribir la evidencia. La captura fija respeta `--modo recorte`.
6. Ocho regresiones adicionales cubren metadata inconsistente, snapshot incompleto, suelo exclusivo en la base y retiro a una hora fraccionaria.
7. La guía incluye comandos Windows. El reporte identifica el código simulado y aclara la fecha provisional.
8. Se regeneraron las evidencias E11/E12 con el código corregido.

## Reproducción numérica

| Caso | Lado m | Paso máximo s | Tmax °C | Hora Tmax | DeltaTmax K | Hora DeltaTmax |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| E11 | 0,50 | 900 | 50,66815 | 48 | 21,51222 | 38 |
| E12 | 0,50 | 900 | 62,16718 | 154 | 43,29242 | 213 |
| E12 refinamiento espacial | 0,25 | 900 | 61,82086 | 154,5 | 43,17729 | 213 |
| E12 refinamiento temporal | 0,50 | 450 | 62,16217 | 154,125 | 43,29189 | 213 |

Los residuos absolutos de energía de las cuatro corridas son menores que 5e-5 J. Se reprodujeron los valores declarados por el compañero. La conclusión se mantiene con ambos refinamientos, ejecutados sin exportar.

## Estado por entrega

| Entrega | Requisitos técnicos | Evidencia | Cierre formal |
| --- | --- | --- | --- |
| E10 | Cubiertos para revisión oral | Módulos, snapshot real, demo y guía | Publicar y declarar repo/SHA en Canvas |
| E11 | Cubiertos para laboratorio | Snapshot, metadata, aire, BC variable, 48 h, VTI, slice y clipping | Publicar y declarar repo/SHA. Demostrar manipulación interactiva durante el laboratorio |
| E12 | Cubiertos para escenario determinista provisional | 14 días, bordes, vertidas, máximos, horas/ubicaciones, curvas, VTI y reporte | Publicar y declarar SHA del paquete con Markdown |

**E12 supera el diferencial de 20 K y queda bajo Tmax de 70 °C.** La entrega pide diagnosticar el desempeño. El incumplimiento del plan debe informarse.

## Hipótesis y límites

- El 27 de noviembre de 2026 a las 10 h es provisional. La instrucción general conserva la fecha de entrega/defensa final como TBD.
- El forecast del 10 de noviembre termina el 25 de noviembre y cubre cero horas del escenario E12. Se asignó por hora relativa un bloque ERA5 del 27 de noviembre al 11 de diciembre de 2025. Es un escenario histórico análogo.
- Suelo, capas y retiros son supuestos docentes del JSON. Los campos TBD del IFC siguen pendientes de definición.
- El solver integrado usa aire y h fijo de 5 W/(m² K). Viento y radiación se conservan en los snapshots. La demo E10 ilustra solar. E11/E12 omiten ese aporte y onda larga.
- S25 se reconstruye mediante el gradiente normal de las caras de la malla escalonada. La resolución de 500 mm limita la precisión espacial. El refinamiento a 250 mm mantiene la decisión.
- Las curvas usan una sonda interior fija y el mínimo móvil de S25. La sonda empieza a registrar al activarse su vertida.
- Se verificaron capturas fijas de slice y clipping. El arrastre manual interactivo queda para la demo.
- Los cambios anteriores de suelo del visualizador web están en Proyecto2. La implementación semanal revisada se ejecuta con `casos/semana4/ejecutar.py` y `ver_3d.py`.

## Comandos en esta copia local

```powershell
$python = '../Proyecto2/.venv/Scripts/python.exe'
$env:PYTHONPATH = Join-Path (Get-Location).Path '.venv/cache/visualizacion'
& $python -B casos/e10/ejecutar.py --demo
& $python -B casos/semana4/ejecutar.py e11
& $python -B casos/semana4/ver_3d.py resultados/e11/diferencial.vti
& $python -B casos/semana4/ejecutar.py e12
& $python -B casos/semana4/ver_3d.py resultados/e12/diferencial.vti
& $python -B casos/semana4/ejecutar.py e12 --lado 0.25 --sin-exportar
& $python -B casos/semana4/ejecutar.py e12 --paso-max 450 --sin-exportar
```

Las dependencias portables están en `requirements.txt` y `casos/semana4/requirements-vista.txt`.

