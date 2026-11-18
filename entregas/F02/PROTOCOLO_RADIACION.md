> Actualizacion posterior: la [comparacion vigente](COMPARACION_CIRCUITOS_FINAL.md) contiene cuatro planes con radiacion y matriz fina completa de24pares a336h. Este documento conserva el estudio inicial y su alcance original.

# Sensibilidad a radiación: protocolo

Solicitud del usuario del18/11/2026: comprobar mediante simulaciones si es
defendible omitir radiación. Los resultados anteriores permanecen conservados.
Este estudio no cambia la estrategia para obtener cumplimiento.

## Comparación controlada

Se mantienen12°C de colocación,60m³/h, once capas, nueve circuitos con agua
ideal18°C, control19/18°C, U5 y tope15kW; mismos retiros72/240/360h, suelo,
fuentes y viento horario. Malla0,40m y paso máximo300s para comparaciones
pareadas. Horizonte docente336h desde la primera capa;600h complementarias,
con extensión672h si el detector anterior identifica pico pendiente.

Se separan solar, onda larga y ambas en M4_SS con las tres historias.
Después se enumeran las ocho fuentes por las tres historias para ambas.
El caso crítico combinado se contrasta con absortancias0,2/0,9, cielo despejado,
rotación90°. Los refinamientos espacial0,20m y temporal150s por separado
se aplican aM4_SS × ERA5-2024, caso crítico de14d en los pilotos y en
la matriz nominal, para distinguir resolución de efectos físicos. No se
ha refinado el casoM1_22A que controla el diferencial nominal extendido.
Se repiten también absortancias0,2/0,9 en ese par: el caso crítico extendido
no tiene por qué ser el que controla los14d.
Estos contrastes son sensibilidad determinista, sin probabilidades asignadas.

## Balance físico

Con flujo positivo entrando al hormigón, se resuelve por cara:

`q = (Ts - Tc)/R = h(Taire - Ts) + alpha I + epsilon sigma (Tenv^4 - TsK^4)`.

Ts es la temperatura exterior de la última protección; R incluye media celda
de hormigón y las resistencias vigentes de madera y mantas. No se aplica
directamente toda la radiación al centro de la celda atravesando la aislación.
El contorno físico del hormigón y S25 se reconstruyen con el flujo neto.
Las temperaturas a la cuarta potencia están en kelvin. El h previo representa
convección; no se añade otro coeficiente convectivo.

Solar: GHI en horizontales superiores; directa normal proyectada con posición
solarNOAA, difusa isotrópica y reflexión del terreno con albedo0,2 en verticales.
Sin sombras ni apantallamiento; los ejes geográficos se suponen y se contrastan
con giro90°. Las caras escalonadas conservan la representación cartesiana.

Onda larga: emisividad superficial0,9; vista al cielo1 en cara superior,
0,5 en vertical y0 en inferior; resto del entorno a temperatura del aire.
Emisividad de cielo Clark–Allen con corrección Walton, punto de rocío y
nubosidad totalERA5 como aproximación de nubosidad opaca. No hay mediciónIR.
Absortancia0,6 nominal y0,2/0,9 como contrastes de acabado exterior equivalente;
no son propiedades medidas ni calibradas de las mantas específicas.

## Datos y verificaciones

Tres nuevos snapshotsERA5 contienenDNI,DHI,punto de rocío y nubosidad, en las
coordenadas exactas del grupo. Taire, viento y GHI coinciden exactamente con
los snapshots anteriores en los tres años. Las irradiancias son medias de la
hora precedente: se aplican al intervalo correspondiente, con posición solar
en su punto medio; aire y punto de rocío se interpolan, h se conserva horario.

Se verifica solución sol–aire analítica sin onda larga, equilibrio radiativo,
Newton frente a bisección independiente, atenuación por aislación, vector
solar unitario y balance de celda con refrigeración. Un control conalpha=eps=0
reproduce los máximos anteriores a tolerancia1e-9. Cada corrida comprueba
balance global, balance exterior solar+convección+onda larga y tope15kW.

Las probabilidades del catálogo se calculan únicamente para la matriz
combinada completa24 pares con pesos1/24. No representan riesgo real de obra.
Los máximos a336h se reportan separados de los extendidos; superar solo el
horizonte extendido no equivale a incumplir el horizonte docente14d.
Para comparar los cuatro mecanismos enM4_SS/ERA5-2024 se completa además
una ventana común672h (`radiacion_ventana_comun.py --ejecutar`). La figura
del catálogo compara las dos alternativas solo a336h; su panel extendido
muestra únicamente radiación, con horizontes600–672h declarados por pieza.
No se atribuyen a la radiación diferencias causadas por ventanas distintas.

## Fuentes de formulación

- [Balance exterior de EnergyPlus](https://energyplus.readthedocs.io/en/stable/guides/engineering-reference/3.5-outside-surface-heat-balance.html).
- [Modelo de radiación atmosférica de EnergyPlus](https://energyplus.readthedocs.io/en/stable/auxiliary-programs/auxiliary-programs.html#field-horizontal-infrared-radiation-intensity).
- [Posición solar NOAA](https://gml.noaa.gov/grad/solcalc/solareqns.PDF).
- [Variables y marcas temporales Open-Meteo](https://open-meteo.com/en/docs/historical-weather-api).

La pautaF01 exige fundamentar la importancia relativa si se omite radiación;
la introducción general yG07 permiten incluirla cuando sea relevante. El
resultado de esta prueba debe definir cómo se presenta esa simplificación.

## Reproducción

Desde la raíz, con `.venv/Scripts/python.exe -X utf8 -B` seguido de
`casos/sensibilidad_h/sensibilidad_radiacion.py --ejecutar --fase FASE`.
Fases usadas: `verificar`, `control`, `piloto`, `matriz`, `cotas`.
Para agregar los24 pares se usa `agregar_radiacion.py` (solo lectura y
escritura de la matriz). El agregador interno original carece del campo
clima al calcular riesgo336h; se conservó el ejecutor con su hash y se
corrigió la agregación en ese archivo separado, sin repetir simulaciones.
Usar lotes en `cotas` evita invocar al final ese agregador interno.
La fase opcional`fina` permite refinar el caso crítico extendido,
pero no se ejecutó en este estudio. `--lote 0`, `1` y `2` reparte una fase entre procesos
independientes; se debe esperar su término antes de agregar la matriz.
Sin`--ejecutar` no se simula. Las piezas existentes solo se reutilizan si
su procedencia coincide; cambiar scripts/config exige conservarlas y usar
otra carpeta de salida.

La confirmación adicional del casoM4_SS/ERA5-2024 se ejecutó llamando
`resolver` del mismo módulo con `ambas,.2,300` y `ambas,.4,150`; sus
contrastes de acabado con `clara,.4,300` y `oscura,.4,300`. Se conservan
los mismos hashes del ejecutor, física y configuración, y cada pieza
registra explícitamente sus parámetros.

Al terminar: `casos/sensibilidad_h/auditar_radiacion.py`, después
`figuras_radiacion.py` y `redactar_radiacion.py` con el mismo intérprete.
Estos tres solo leen evidencia, sin nuevas simulaciones.
