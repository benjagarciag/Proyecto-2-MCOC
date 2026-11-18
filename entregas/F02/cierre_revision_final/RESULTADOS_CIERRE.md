# Resultado del cierre técnico F02

La propuesta es una operación continua a60m³/h,12°C, once capas, nueve
circuitos con control19/18 y sin corte global. Madera hasta72h, primera
manta hasta240h y última hasta504h de edad local; después sombra solar
ideal90% en las caras expuestas. La cubierta permanece durante el estudio.
El10% solar residual se conserva. Agua18°C uniforme,Uv5 y tope15kW son
una transferencia equivalente, no un dimensionamiento físico validado.

## Comparación homogénea a672h

|Plan|Malla / paso máximo|D [h]|Mayor Tmax [°C]|MayorΔT [K]|P_T|P_Δ|P_f|Alarmas|
|---|---|---:|---:|---:|---:|---:|---:|---:|
|Única continua / propuesta60m³/h|0,40m /300s|10,6129|47,4941|16,5306|0%|0%|0%|0|
|Vecina más lenta55m³/h|0,40m /300s|11,5777|47,5128|16,6011|0%|0%|0%|0|
|Confirmación completa de la propuesta|0,20m /300s|10,6129|47,0322|15,7202|0%|0%|0%|0|

Cada fila tiene24pares completos y los mismos recursos disponibles, física,
clima y pesos. Los máximos de las columnas pueden ocurrir en distintos casos
y horas. Las dos ventanas336/672h conservan probabilidad conjunta0 en estas
matrices. Se muestra la confirmación fina como resolución de la misma
propuesta, no como un cambio constructivo que mejore el plan.

La alternativa55 agrega0,96481h,aproximadamente57,89min, y no aporta una
reducción de probabilidad en el catálogo. La diferencia del mayorΔT grueso
es+0,07054K, pequeña respecto de los cambios espaciales observados; no se
fundamenta la elección en que esa pequeña diferencia sea físicamente exacta.
Se elige60 porque alcanza la cota de tiempo bajo la capacidad adoptada.

## Cómo se cierra el punto5

La familia discreta esq∈{55,60}m³/h,paso5. Las tasas inferiores no pueden
superar la cotaD≥V/60; las superiores no son admisibles con estos recursos.
Se recorre completa esta familia y se confirma la propuesta con24pares
finos. No existe una desviación más rápida admisible que haya que hacer
fallar térmicamente. «Una vertida continua» y «propuesto» son el mismo caso
físico; la pauta permite no duplicar sus nombres.

La prueba temporal esD≥636,7751548866/60=10,6129192481h. No se optimiza
el tiempo de retiro de mantas ni se demuestra un óptimo con otros recursos.
La continuidad exige logística, unión y montaje compatibles; si agregan
esperas o postergación, deben incluirse enD y recalcular el clima relativo.

## Método y resolución

- Caso conocido: solución sinusoidal1D,error máximo0,00257143K. Pasaron
  los24tests de ese módulo y las verificaciones independientes de celda,
  control y superficie radiativa. El caso1D no valida toda la geometría3D.
- Conservación en las72piezas: mayor residuo absoluto0,000247955J y mayor
  relativo2,39×10⁻¹⁵. Las144filas de balance conservan los términos con signo:
  E_final=E_colocación+E_hidratación+E_aire+E_suelo+E_frío+residuo.
  E_frío es negativa cuando se extrae calor.
- Espacio:24pares emparejados0,40→0,20m a300s,0–672h;mayor cambio absoluto
  deΔT0,881712K. No se ha demostrado un orden asintótico de convergencia.
- Tiempo: dos contrastesM4_SS×2024/2025,0,40m,300→150s,con esta misma
  protección;mayor cambio absolutoΔT0,00136511K. Son contrastes temporales
  selectivos, no otra matriz temporal completa.
- El margen del mayorΔT fino es4,27977K. Ninguna de estas comprobaciones
  acredita la transferencia real del tubo, propiedades de la cubierta o
  ausencia de fisuración mecánica.

No mezclar0,881712K de la comparación nueva a672h con1,174621K del estudio
anterior a336h: cambiar la ventana puede cambiar el máximo de cada par y
su diferencia. Las336h de las corridas nuevas se comprobaron contra la
evidencia anterior de idéntica resolución y tasa.

## Evidencia lista para el punto6

- `COMPARACION_PLANES.csv`:D,indicadores y probabilidades agregadas.
- `METRICAS_144_FILAS.csv`:plan,curva,clima,peso,métricas,indicadores,
  instantes,fases y coordenadas de máximos en336/672h.
- `BALANCES_144_FILAS.csv`:energías firmadas y residuo por caso/horizonte.
- `PARAMETROS_FINAL.csv` y `CONFIGURACION_FINAL_REVISADA.json`:condiciones
  de construcción, material, ambiente, protección, frío y método.
- `SENSIBILIDAD_ESPACIAL_24_PARES.csv`,`VERIFICACION.json` y
  `VERIFICACIONES_EJECUTADAS.txt`:comprobaciones cuantitativas.
- Figuras01–07:duración–probabilidad con línea5%,cronogramas,curvas de
  Tmax/sonda/S25/ΔT con umbrales,cortes a267/672h,refinamiento24pares,
  ocho fuentes y tres climas completos. En las curvas se añadieron los
  eventos exactos de máximo para no perderlos por muestreo horario.

Se revisaron visualmente las siete figuras. Las horas, plano y escala de
colores son comunes entre los cortes de la misma fila; los mapas muestran
centros,mientras el criterio deTmax incluye caras reconstruidas.

La [explicación completa de §§5–6](../CIERRE_PUNTOS_RESTANTES.md) incluye
ecuaciones,unidades,bordes por etapa,estabilidad,limitaciones,plan de sensores
y contingencias,ejemplo de falla y la organización sugerida de ocho láminas
en siete minutos. Se preservó el guion personalizado con sus marcas de clic;
no se sobrescribieron sus notas ni el PPT/PDF durante este cierre técnico.

## Reproducción sin internet

Desde la raíz del repositorio,con el entorno instalado:

```powershell
# Consultar resultados, sin simular
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/ejecutar_cierre_f02.py
# Reproducir o reutilizar un caso fino individual
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/ejecutar_cierre_f02.py --ejecutar --escenario M4_SS ERA5-2024
# Reproducir o reutilizar las tres matrices
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/ejecutar_cierre_f02.py --comparar --ejecutar
# Auditar sin solver
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/ejecutar_cierre_f02.py --auditar
# Regenerar tablas y figuras sin solver
.\.venv\Scripts\python.exe -X utf8 -B casos/sensibilidad_h/documentar_cierre_f02.py
```

La configuración y scripts numéricos conservan sus hashes. Auditoría final
aprobada:72piezas,3matrices,2045transiciones;26piezas reutilizadas con origen
verificado y46corridas nuevas. Las repeticiones usan el mismo archivo si
coincide la procedencia. Las fuentes y snapshots quedan locales.

## Qué significa y qué falta trasladar a la entrega

La probabilidad es exacta en el catálogo discreto;no es una garantía de
riesgo real≤5%. La comparabilidad de las curvas,pesos,cola de hidratación,
transferencia de tubos,sombra y demás simplificaciones permanecen declarados.
La cubierta y los tubos no tienen fecha de desmontaje o apagado definitivo
validada. La ausencia de alertas no demuestra un máximo universal futuro.

Quedan la integración coordinada aPPT/guion,exportación delPDF final,
congelación delSHA de defensa y ensayo oral con el equipo de exposición.
No se presentan esas actividades como realizadas. El ensayo y comprensión
individual no se pueden sustituir por los archivos generados.
