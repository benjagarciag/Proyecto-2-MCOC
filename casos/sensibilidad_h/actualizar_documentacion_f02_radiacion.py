"""Actualiza guion, brief, comparación y contenido de diapositivas desde evidencia auditada."""
import json,re
from pathlib import Path
import familia_radiacion as motor

R=motor.RAIZ;S=motor.SALIDA;D=R/'entregas/F02'
CACHE=R/'.venv/cache/f02_radiacion_presentacion'


def n(v,d=2):return f'{v:.{d}f}'.replace('.',',')
def escribir(nombre,texto):(D/nombre).write_text(texto.strip()+'\n',encoding='utf-8')


def main():
    resumen=motor.leer(S/'resumen.json');assert resumen['estado']=='APROBADA' and resumen['piezas']==129
    datos=motor.leer(D/'evidencia_f02_radiacion/datos_presentacion.json')
    base=next(r for r in resumen['planes'] if r['q']==60 and r['h']==.4)
    fina=next(r for r in resumen['planes'] if r['q']==60 and r['h']==.2)
    esp=resumen['max_cambio_espacial_Delta'];temp=resumen['max_cambio_temporal_Delta']
    margen=20-fina['Delta'];evento=datos['evento']
    habla={
    'S1':'''Proponemos colocar toda la fundación de El Rosal en una operación continua, a sesenta metros cúbicos por hora y doce grados, con nueve circuitos de refrigeración idealizados. Eso requiere diez coma sesenta y una horas. Ahora incluimos radiación solar y de onda larga. Evaluamos temperatura máxima y diferencial durante catorce días desde la primera colocación. Ninguno de los veinticuatro escenarios nominales de la candidata excedió los límites. La conclusión depende de los supuestos que vamos a explicar.''',
    'S2':'''La hidratación genera calor dentro del hormigón y la conducción lo redistribuye. En las caras expuestas actúan convección por viento, radiación solar y emisión hacia el cielo. El sol puede calentar una cara más que el núcleo; durante la noche, la radiación puede enfriar la superficie. La madera y las mantas oponen resistencia a ese intercambio. Medimos la diferencia entre la máxima del hormigón y la mínima de S veinticinco en el mismo instante. S veinticinco es hormigón a unos veinticinco milímetros bajo sus superficies exteriores. El suelo conserva una representación equivalente a quince grados.''',
    'S3':'''Colocamos once capas de hasta cuarenta centímetros con dos frentes de treinta metros cúbicos por hora. No esperamos endurecimiento entre capas: su unión continua debe comprobarse con la mezcla y el recorrido real. Los nueve ramales se distribuyen en cuatro alturas y se habilitan después de quedar cubiertos. Abren cuando la mínima monitoreada alcanza diecinueve grados y cierran si algún tramo llega a dieciocho. El agua se idealiza uniforme a dieciocho grados. El cálculo usa una extracción equivalente con tope conjunto de quince kilowatts. La pared del tubo y el calentamiento del agua no están resueltos.''',
    'S4':f'''Resolvemos un balance de energía propio por celda, con activación progresiva según las capas. La radiación actúa sobre el exterior de la protección, cuya temperatura calculamos antes de obtener el flujo hacia el hormigón. Verificamos conservación de energía y soluciones independientes del balance superficial. Después separamos espacio y tiempo: comparamos cuarenta y veinte centímetros con los veinticuatro escenarios de la candidata, y trescientos y ciento cincuenta segundos en tres casos. El mayor cambio espacial del diferencial es {n(esp,2)} grados y el temporal es {n(temp,4)}. Estas comprobaciones mantienen la clasificación dentro de los catorce días y no calibran la transferencia real de los tubos.''',
    'S5':'''Esta figura corresponde a una misma fuente y clima, con radiación y malla de cuarenta centímetros. La temperatura máxima y la mínima en S veinticinco se comparan en cada instante. A las doscientas sesenta y siete horas, el punto caliente está a cuarenta y dos coma doce grados y S veinticinco a veinticinco coma cincuenta y nueve. Su diferencia es dieciséis coma cincuenta y tres. El punto caliente de ese evento es una cara reconstruida. La confirmación fina también cumple. El seguimiento posterior sí registra excedencias después de los catorce días, especialmente tras retirar la última manta. Por eso el cumplimiento de la ventana exigida no autoriza automáticamente los retiros posteriores.''',
    'S6':'''Conservamos ocho fuentes completas del profesor y tres historias climáticas de El Rosal, de dos mil veintitrés, veinticuatro y veinticinco. Cada par combina una fuente y una historia de aire, viento y radiación. Los veinticuatro pares pesan lo mismo, bajo independencia supuesta entre fuente y clima. Una corrida falla si supera cualquiera de los dos límites dentro de los catorce días. Sumamos sus pesos y obtenemos cero en el catálogo. Las propiedades radiativas nominales están fijadas. No representamos toda su incertidumbre ni demostramos riesgo real cero.''',
    'S7':'''Comparamos sesenta, cincuenta y cinco, cincuenta y cuarenta y cinco metros cúbicos por hora, ahora todos con radiación y la misma ventana de catorce días. Los cuatro cumplen en la malla común. A cuarenta y cinco, la duración sube a catorce coma quince horas y el peor diferencial aumenta ligeramente. Elegimos el plazo menor. Con seiscientos treinta y seis coma setenta y cinco metros cúbicos y una capacidad máxima adoptada de sesenta por hora, la cota es volumen dividido por caudal: diez coma sesenta y una horas. Una opción más rápida exigiría cambiar ese recurso. Los contrastes finos de las otras tasas son selectivos; la matriz fina completa corresponde a la candidata.''',
    'S8':'''Recomendamos sesenta metros cúbicos por hora, doce grados y el control idealizado de nueve circuitos, bajo el modelo con radiación. El plazo es de colocación; el control térmico continúa después. Debemos medir hormigón y agua, comprobar la transferencia real de los tubos y condicionar los retiros a monitoreo y predicción. Si cambian clima, exposición o refrigeración, debemos recalcular. El cumplimiento de los indicadores docentes no demuestra ausencia de fisuración.'''
    }
    responsables=['Benjamín','Benjamín','Benjamín','Luis','Luis','Matías','Matías','Matías']
    titulos=['Decisión y objetivo','Mecanismo físico con radiación','Colocación y refrigeración equivalente','Comprobación del cálculo','Temperaturas durante los14 días','Escenarios y probabilidad','Duración mínima bajo recursos','Recomendación y condiciones']
    tiempos=['0:00–0:30','0:30–1:25','1:25–2:20','2:20–3:20','3:20–4:35','4:35–5:20','5:20–6:25','6:25–7:00']
    for nombre in ['GUION_ORAL_F02.md','BRIEF_DIAPOSITIVAS_F02.md']:
        destino=CACHE/('anterior_'+nombre)
        if not destino.exists():destino.write_bytes((D/nombre).read_bytes())
    original=(CACHE/'anterior_GUION_ORAL_F02.md').read_text(encoding='utf-8')
    faq=original[original.index('## Preguntas físicas probables'):original.index('## Respuestas que conviene evitar')]
    nuevas={
    9:('¿Incluimos radiación y relleno?','Sí incluimos solar y onda larga en las caras expuestas. Se supone exposición sin sombras, absortancia0,6 y emisividad0,9 del acabado exterior equivalente. El cielo se estima con rocío y nubes. Los laterales siguen expuestos sin relleno; esa condición debe confirmarse. No se trata la radiación como parte del h convectivo.'),
    10:('¿Por qué el máximo diferencial puede ser posterior al máximo de temperatura?','El máximo depende de la evolución simultánea del punto caliente y S25. El interior conserva calor y las superficies responden al viento, sol, cielo y retiros. El sol también puede convertir una cara en el punto más caliente. Menor pico de hidratación no implica menor diferencial. El caso mostrado registraΔT16,5306K a267h, dentro de14 días.'),
    22:('¿Quince kilowatts se extraen siempre?','Son el tope global del sumidero equivalente Uv·V·max(T−18,0), con Uv=5W/(m³K) y celdas asignadas a circuitos abiertos. La potencia puede ser menor o cero. El control también evita cruzar18°C por extracción en un paso. No son15kW por tubo ni potencia eléctrica.'),
    23:('¿El caudal18L/min demuestra15kW?','No. El caudal se usa como dato operativo del anteproyecto y para registrar ramales/bypass. No interviene en la ley térmica del solver ni determina Uv. Faltan material y espesor de pared, convección interior, contacto y calentamiento axial del agua. Con9ramales abiertos,162L/min y15kW darían aproximadamente1,33K de aumento medio real del agua, solo como balance de referencia.'),
    24:('¿Qué interacción hormigón–tubería–agua se calculó?','Una representación equivalente de extracción en el hormigón. El solver no discretiza la pared del tubo ni resuelve una temperatura del agua a lo largo de su recorrido. El agua uniforme18°C representa un reservorio ideal. No equivale a afirmar que una red real mantenga entrada y salida18°C mientras extrae15kW.'),
    26:('¿Cuándo se apaga definitivamente?','No hay corte global432h ni fecha de desmantelamiento calculada. Los cierres por19/18 son reversibles. El requisito se evalúa a336h. El seguimiento600–672h encontró excedencias con radiación y varios picos pendientes, así que los retiros posteriores deben reevaluarse y no se presentan como liberación autorizada.'),
    32:('¿Por qué no una colocación más lenta?','Se repitieron los cuatro ritmos con solar y onda larga en336h. Todos cumplen en la malla común, pero el menor caudal prolonga colocación y aumenta ligeramente el mayor diferencial. La cotaV/60 y el recurso máximo adoptado sustentan la elección. Las pequeñas diferencias térmicas no prueban que60 sea un óptimo universal.'),
    }
    for i,(q,a) in nuevas.items():
        faq=re.sub(rf'\*\*{i}\. .*?(?=\n\*\*\d+\.|\n###|\Z)',f'**{i}. {q}** {a}\n',faq,flags=re.S)
    faq+='''
### Radiación e interacción con tubos

**36. ¿Dónde se aplica el sol si hay manta?** En el exterior de la última protección. Se resuelve su temperatura con convección, solar y onda larga. Solo el flujo que atraviesa la resistencia llega al hormigón. No se inyecta toda la energía solar al centro de una celda a través de la manta.

**37. ¿Por qué el efecto es más fuerte después de14 días?** La última manta se retira a360h de edad local, posterior a336h. Las caras descubiertas responden mucho más al intercambio radiativo. Con la configuración nominal, los24pares del seguimiento adicional superan20K;16mantienen alerta de pico pendiente. Eso no es falla del requisito14d ni un máximo definitivo del futuro.

**38. ¿Cómo entra la radiación en la ecuación?** q''=(Ts−Ti)/R=h(Ta−Ts)+αI+εσ(Trad,K⁴−Ts,K⁴). El flujo positivo entra al hormigón. Ts es exterior de protección y Ti centro de celda. R suma media celda y capas vigentes. Las temperaturas a la cuarta potencia están en kelvin.

**39. ¿Uv=5 es el coeficiente de convección dentro del tubo?** No. Uv tiene unidadesW/(m³K) y multiplica volumen de hormigón. Un coeficiente de película interior tieneW/(m²K) y multiplica superficie de tubo. La geometría de nueve ramales organiza cobertura, muestreo y asignación de celdas, pero no determina una resistencia térmica de pared en este solver.

**40. ¿Qué faltaría para acreditar refrigeración real?** Definir material, diámetros y espesor de tubo, contacto y resistencia hormigón–tubo, coeficiente interior y balance del agua a lo largo del ramal. Medir entrada/retorno y caudal permitiría contrastar Q=ṁcp(Tsal−Tent). También se requiere rechazo de calor en un equipo y comprobación hidráulica. No se sustituyó aquí la idealización docente por ese modelo.
'''
    guion=['# Guion oral F02 actualizado con radiación','',
        'Grupo6: Benjamín García, Luis Noriega y Matías Stierling. Defensa19/11/2026. Ocho diapositivas principales en siete minutos; los tiempos son objetivos, no ensayo realizado. El reparto sigue física/obra (Benjamín), método y resultados (Luis), incertidumbre y decisión (Matías).','',
        '**Versión vigente:** solar y onda larga activas, comparación homogénea0–336h. El enfriamiento sigue siendo equivalente y no resuelve la pared del tubo ni el agua axial. Los resultados posteriores se presentan como diagnóstico separado.','',
        '| Diapositiva | Responsable | Intervalo |','|---|---|---|']
    for i in range(8):guion.append(f'| S{i+1}: {titulos[i]} | {responsables[i]} | {tiempos[i]} |')
    for i in range(8):
        k=f'S{i+1}';guion+=['',f'## {k} — {responsables[i]}: {titulos[i]}','',f'<!-- habla:{k} -->',habla[k],f'<!-- fin:{k} -->']
    guion+=['','## Resultados para responder preguntas','',
        '| Evidencia con radiación | Tmax14d [°C] | ΔT14d [K] | Alcance |','|---|---:|---:|---|',
        f"|60m³/h,0,40m/300s |{n(base['Tmax'],4)} |{n(base['Delta'],4)} |24pares |",
        f"|60m³/h,0,20m/300s |{n(fina['Tmax'],4)} |{n(fina['Delta'],4)} |24pares completos |",'',
        f"Mayor cambio espacial emparejadoΔT={n(esp,4)}K; temporal={n(temp,4)}K en tres pares. Margen fino nominal={n(margen,4)}K hasta20K. Los seis contrastes finos de alternativas no son matrices finas completas.",'',
        'Evento ilustrado:267h, fase previa al cambio horario. Tmax simultánea42,1202°C (cara reconstruida), TminS25 25,5897°C yΔT16,5306K. No restar el pico histórico46,6574°C a esa mínima. El corte muestra centros de celdas, mientras el criterio incluye caras reconstruidas.','',faq,'',
        '## Fuentes','',
        '- [Comparación vigente](COMPARACION_CIRCUITOS_FINAL.md).\n- [Ecuaciones](ECUACIONES_MODELO_VIGENTE.md).\n- [Interacción con tuberías](INTERCAMBIO_TUBERIAS.md).\n- [Sensibilidad y seguimiento posterior](SENSIBILIDAD_RADIACION.md).\n- [Brief de diapositivas](BRIEF_DIAPOSITIVAS_F02.md).','',
        'Evitar afirmar: riesgo real cero; transferencia de tubos acreditada; resultados extendidos bajo20K; todas las alternativas con matriz fina; ausencia de fisuración demostrada.']
    escribir('GUION_ORAL_F02.md','\n'.join(guion))
    filas=['| Caudal [m³/h] | Malla [m] | D[h] | Tmax336h[°C] | ΔT336h[K] | P(unión) |','|---|---:|---:|---:|---:|---:|']
    for p in resumen['planes']:filas.append(f"|{p['q']}|{n(p['h'],2)}|{n(p['D_h'],4)}|{n(p['Tmax'],4)}|{n(p['Delta'],4)}|{n(100*p['riesgo']['P_union'])}%|")
    comparacion=f'''# Comparación final homogénea con radiación

Ventana obligatoria:336h desde la primera colocación. Solar y onda larga activas en todos los planes. Conservamos12°C, nueve circuitos, agua ideal18°C,Uv5 y tope15kW, control19/18, once capas y retiros72/240/360h de edad local. Cambia el caudal y los tiempos físicos de colocación y cobertura asociados.

{chr(10).join(filas)}

La candidata60m³/h alcanza la cotaV/Qmax=636,7752/60={n(base['D_h'],4)}h. Dos frentes de30m³/h y suministro continuo constituyen el recurso máximo idealizado adoptado. La capa mayor requiere107,4min a60 y143,2min a45, dentro de la condición de aceptación150min aún no ensayada. No se afirmó falla de una tasa mayor no admisible.

Las cuatro matrices gruesas tienen24pares completos. La candidata tiene además24pares finos completos, sin extrapolar ese riesgo fino a las otras tasas. Se realizaron seis contrastes finos de alternativas y tres temporales. El mayor cambio espacial deΔT es{n(esp,4)}K y el temporal{n(temp,4)}K. Dos mallas no demuestran convergencia asintótica. La zona refrigerable permanece414,016m³ y los tiempos físicos de las once capas se conservan.

La ley térmica de tubos continúa como extracción equivalente, sin pared ni calentamiento axial del agua. Ver [interacción](INTERCAMBIO_TUBERIAS.md). La radiación usaα0,6 yε0,9 supuestos, cielo estimado con rocío/nubes, albedo0,2 y exposición sin sombras. No se presentaP(unión) del catálogo como garantía de riesgo real≤5%.

La probabilidad es la suma de pesos1/24 de realizaciones que exceden70°C o20K en336h. Se conservan fuentes completas y clima compartido entre todas las capas de una realización. La reponderación de años y campañaSS aparece en las matrices. Son escenarios discretos enumerados y no24ensayos aleatorios para un intervalo binomial.

El seguimiento anterior con radiación600–672h registra24excedencias del diferencial, máximo observado33,0074K y16picos pendientes. Es diagnóstico posterior y no modifica la ventana exigida. La última manta se retira a360h de edad, por lo que el cumplimiento14d no acredita liberación térmica posterior.

Auditoría:5matrices completas,129piezas y{resumen['transiciones']}registros de transiciones. Se verifica procedencia, balance global y exterior, cobertura, control19/18 y tope15kW. Las piezas reutilizadas conservan hash de su origen y métricas336h exactas. No se inventa energía por ramal336h que no se había guardado en los estudios extensos.

Resultados: `resultados/familia_radiacion_336h/`. Resumen auditado: `resumen.json`. Tablas y siete figuras: [evidencia vigente](evidencia_f02_radiacion/). Históricos sin radiación conservados en `resultados/comparacion_circuitos/` y `evidencia_circuitos/`, sin usarlos como cifras actuales.

Ejecutores: `familia_radiacion.py`, `auditar_familia_radiacion.py` y `figuras_f02_radiacion.py` bajo `casos/sensibilidad_h/`. No cambiar scripts/config con hash para reanudar sus salidas. El IFC sigue intacto y12°C/cronograma son condiciones externas del plan. El respaldo final/SHA y ensayo oral no se realizaron en esta actualización.
'''
    escribir('COMPARACION_CIRCUITOS_FINAL.md',comparacion)
    # El brief conserva la dirección visual elegida y sustituye todos los resultados anteriores.
    original_brief=(CACHE/'anterior_BRIEF_DIAPOSITIVAS_F02.md').read_text(encoding='utf-8')
    diseno=original_brief[original_brief.index('## 4. Dirección visual'):original_brief.index('## 6. Guion visual')]
    slides={
    'S1':('Decisión y objetivo','10,61h de colocación,60m³/h,12°C, nueve circuitos y0/24excedencias EN14D. Malla fina0,20m/300s,24pares.','Conservar fundación oscura y revelar primero recursos, después resultado y horizonte. Añadir solar+onda larga en el rótulo del modelo.'),
    'S2':('Mecanismo físico con radiación','Hidratación en el volumen y tres intercambios en el exterior: convección, solar y onda larga. ΔT=Tmax,Ω−Tmin,S25 simultáneo.','Conservar corte editable. Revelar fuente, luego puntos, luego exterior. El sol actúa en la manta; el punto caliente puede ser una cara. No animar un máximo fijo como si siempre estuviera en el núcleo.'),
    'S3':('Colocación y extracción equivalente','Once capas≤0,40m, dos frentes×30m³/h, nueve ramales en cotas0,5/1,5/2,5/3,8m. Agua18°C ideal,18L/min por ramal abierto y162con bypass. Tope conjunto15kW.','Mostrar capas progresivamente, cuatro niveles3/3/2/1 y banda19/18. Texto explícito: Uv equivalente, sin pared ni agua axial resueltas. Movimiento del agua solo como esquema operativo.'),
    'S4':('Método y sensibilidad',f'Balance conservativo por celda. Solar+LW no lineal en superficie exterior. Espacio24pares, máximo cambioΔT{n(esp,3)}K; tiempo3pares,{n(temp,4)}K.','Mantener tabla editable y celda de balance. Animar aportes y después dos refinamientos separados. Conservar volumen refrigerable414,016m³ y tiempos físicos de capas; no confundir resolución con parámetros físicos.'),
    'S5':('Temperaturas dentro de14 días',f'M4_SS×ERA5-2024,0,40m/300s. Evento267h:42,12−25,59=16,53K. Pico46,6574°C a128,25h. Máximo del catálogo finoΔT{n(fina["Delta"],2)}K.','Curvas NATIVAS editables de0a336h con Tmax/S25 arriba yΔT abajo, límite20K y evento267h. El corte corresponde al evento267h y muestra centros, mientras el indicador incluye caras. Revelar primero temperaturas, después resta y corte. La nota del orador aclara excedencias posteriores al retirar mantas.'),
    'S6':('Escenarios y probabilidad','Ocho fuentes completas por tres historiasERA5, pesos1/24. Unión de los límites evaluada SOLO0–336h. α/ε nominales fijos.','Conservar gráfico nativo de fuentes y matriz8×3. Los climas incluyen aire, viento y radiación de cada año. No reducir fuentes a recetas seleccionables ni llamar el catálogo una muestraMonteCarlo.'),
    'S7':('Comparación y duración mínima','Tabla editable de los cuatro ritmos con las probabilidades CALCULADAS en336h. D≥V/60=10,61h.','Conservar Gantt y curva nativa duración–riesgo. Todos los planes usan misma física radiativa y resolución. La cota surge de la capacidad máxima supuesta; no de demostrar un fallo térmico de75m³/h.'),
    'S8':('Recomendación condicionada',f'Confirmación fina:{n(fina["Tmax"],2)}°C,{n(fina["Delta"],2)}K y0/24excedencias a14d. MargenΔ={n(margen,2)}K.','Mantener cierre oscuro y barra hasta20K calculada con el nuevo valor. Condicionar retiros y medir hormigón/agua. Explicitar transferencia equivalente sin validar y propiedades radiativas supuestas. La recomendación no autoriza automáticamente retirar la última manta después de14d.')
    }
    brief=['# Brief vigente de presentación F02 con radiación','',
        'Crear o actualizar PowerPoint académico en español para Benjamín García, Luis Noriega y Matías Stierling, grupo6. Defensa19/11/2026. Conservar ocho principales para siete minutos, índice de consulta y doce láminasB01–B12:21láminas totales. Usar estilo mixto oscuro/claro existente, texto mínimo, ecuaciones editables matemáticas y animaciones por clic. El PDF muestra el estado final completo de cada lámina.','',
        '**Fuentes vigentes:** COMPARACION_CIRCUITOS_FINAL.md, ECUACIONES_MODELO_VIGENTE.md, INTERCAMBIO_TUBERIAS.md, GUION_ORAL_F02.md y evidencia_f02_radiacion/. Sustituir todos los valores anteriores sin radiación. No mezclar el seguimiento600–672h con las métricas de la ventana exigida336h.','',
        '## Datos exactos','',*filas,'',
        f"Confirmación: cambio espacial máximoΔT{n(esp,4)}K; temporal{n(temp,4)}K. Seis contrastes finos de otras tasas son selectivos. Auditoría5matrices/129piezas/{resumen['transiciones']}registros. El criterio de S25 se reconstruye bajo las superficies del hormigón y la máxima incluye centros y caras.",'',
        'Constantes:ρ2476kg/m³,cp1023J/(kgK),k2W/(mK), suelo15°C conR=0,50/1,2m²K/W. Madera18mm/k0,158 hasta72h; mantas40mm/k0,042 hasta240/360h de edad local. No hay aislación entre capas. Fuente tabular por edad común a todas las capas de una realización. Cinco objetosIFC y once capas térmicas son conceptos distintos.','',
        'Radiación activa:α0,6 yε0,9 del acabado exterior equivalente, albedo0,2, orientación+xeste/+ynorte, sin sombras y difusa isotrópica. Cielo estimado mediante rocío y nubosidad total como proxy de opaca. Resolver q″=(Ts−Ti)/R=h(Ta−Ts)+αI+εσ(Trad,K⁴−Ts,K⁴), con R=Δx/(2k)+Σe/k. Definir cada símbolo en notas y kelvin en términosT⁴. No aplicar toda la solar al hormigón a través de las mantas ni añadir radiación otra vez al h.','',
        'Refrigeración:Uvol5W/(m³K) es equivalente, agua18°C uniforme, tope15kW conjunto y regla por circuito19/18 con cobertura. Caudal18L/min por ramal es un supuesto operativo y no determina Uvol ni Q en el solver. No se discretiza tubo, espesor, material, contacto ni película interior, ni se resuelve agua axial. Los nueve trazados sirven para cobertura, muestreo y asignación de celdas. No presentar un cálculo deΔTagua≈1,33K como retorno simulado.','',
        diseno,'','## Recorrido principal','']
    for i in range(8):
        k=f'S{i+1}';titulo,texto,visual=slides[k]
        brief += [f'### {k}: {titulo}',f'Responsable: {responsables[i]}. Intervalo: {tiempos[i]}.','',f'**Contenido visible:** {texto}','',f'**Composición y animación:** {visual}','',
            'Usar las notas exactas del guion oral para esta lámina. Revelaciones por clic con fundidos o barridos de300–700ms. Mantener unidades, ejes y fuente de cada cifra. Las figuras no se recalculan durante la exposición.','']
    respaldos=[
        ('B01','Geometría, capas y tubos','Conservar planta de los nueve ramales y tabla de cotas3/3/2/1, longitudes aproximadas639m y diámetro interior de cálculo25mm. Diferenciar cinco objetosIFC de once capas y mostrar que la geometría no acredita transferencia ni montaje.'),
        ('B02','Clima, viento y radiación','Mostrar aire, h yGHI en0–336h paraERA5 2023/24/25, coordenadas exactas−37.277929/−72.368271, fechas de snapshots y celda devuelta. h=5,7+3,8v2 y perfil10a2m con exponente0,14. hmedio17,09 es referencia, no constante. DHI/DNI, rocío y nubes se incorporan de snapshots complementarios coincidentes en aire/viento/GHI.'),
        ('B03','Balance exterior con radiación','PDE de hidratación y extracción, balance de la superficie de la protección y resistencia en serie. DefinirTs exterior,Ti centro, temperatura radiativa efectiva y kelvin. El suelo permanece reservorio equivalente sin inercia; caras cubiertas pasan a conducción interna. Tabla debe decir solar+LW explícitas, nunca radiación omitida.'),
        ('B04','Mantas y retiros','Conservar croquis de protecciones y edades72/240/360h. Añadir que360h queda después del requisito336h y el seguimiento muestra excedencias con radiación. Requiere resistencia, monitoreo y predicción; las edades no son autorizaciones automáticas.'),
        ('B05','Fuente y propiedades','Conservar ocho fuentes, identificación de probetas/campañas y tablaρ/cp/k. No elegir una supuesta mezcla favorable sin correspondencia de dosificaciones. Qpor edad no incluye cinética dependiente deT ni retraso de reacción por colocar a12°C.'),
        ('B06','Intercambio equivalente de tuberías','Ecuación de potencia sumada sobre celdas de circuitos abiertos, tope15kW y control. Rotular Uv[W/(m³K)] frente a h_interior[W/(m²K)]. Enumerar pared/contacto/convección interior/agua axial como pendientes de validación real. Conservar balance de referencia P=ṁcpΔTagua y ejemplo1,33K condicionado a162L/min y15kW, sin atribuirlo a salida del solver.'),
        ('B07','Colocación fría y unión','Conservar107,4/143,2min de capa mayor frente a ventana150min no ensayada y338kW sensibles aproximados para preenfriar20a12°C a60m³/h. Son cálculos constructivos distintos del frío embebido. No afirmar equipos contratados o tolerancias térmicas no simuladas.'),
        ('B08','Balance discreto y resolución','Fórmula conservativa, integración de hidratación y balance no lineal de caras. Mostrar los24 cambios pareados deΔT a336h con datos nuevos, ejes que permitan cambios negativos. Actualizar el máximo temporal de tres pares. El límite de estabilidad incorpora conductancias de contorno y frío, no solo vecinos internos.'),
        ('B09','Unión y pesos','Fila realM4_SS/ERA5-2024:46,6574°C y16,5306K en336h, peso1/24 e indicadores calculados. Reponderación de años/SS desde matrices nuevas. Conservar ejemplos aritméticos1/24y2/24 como ejemplos, no fallas observadas ni intervalos estadísticos binomiales.'),
        ('B10','Comparación completa','Tabla de los cuatro planes gruesos y la candidata fina, TODOS a336h. Sustituir columna antiguaΔT25d por margen hasta20K o quitarla. Cortes a336h de los cuatro ritmos, misma escala, plano y fuente/clima. No mostrar cortes428h sin radiación como actuales.'),
        ('B11','Medición y contingencias','Conservar sensores propuestos y umbrales operativos65/68°C y18/19K como propuestas, no normativa. Añadir medidas de caudal, entrada/retorno y condiciones de exposición solar. Cambios de frío, mantas o clima requieren nueva predicción y no heredan la matriz nominal.'),
        ('B12','Alcance físico y trazabilidad','Auditoría y sensibilidades nuevas. Radiación activa conα/ε y cielo supuestos, sombras no resueltas. Suelo sin inercia, fuente por edad, agua ideal y Uvol sin calibrar. No se resolvieron tensiones/fisuración. Incluir que el seguimiento posterior ya muestra excedencias y no hay liberación automática ni SHA final inventado.')]
    brief+=['## Consulta B01–B12','']
    for clave,titulo,texto in respaldos:brief += [f'### {clave}: {titulo}',texto,'']
    brief += ['## Evidencia y comprobación final','',
        'Los gráficos obligatorios son editables y sus libros embebidos contienen los valores actuales. Fuentes y climas conservados pueden reutilizar recursos originales porque no cambian, pero historias térmicas, sensibilidad, tabla de planes, evento y cortes se sustituyen. Mantener datos en evidencia_f02_radiacion/datos_presentacion.json y CSV junto a figuras01–07. El PPTX conserva navegación del índice y animaciones de las ocho principales.','',
        'Comprobar cada diapositiva a tamaño completo: sin recortes, ejes/unidades visibles, leyendas legibles, cifras consistentes con tablas auditadas y notas por responsable. Inspeccionar estado final estático y conservar vínculos de consulta. Repetir ecuaciones como texto matemático editable y verificar signos del flujo. El PDF es una versión estática completa, no una demostración de las animaciones.','',
        'El guion suma siete minutos como objetivo; no afirmar un ensayo realizado. No añadir citas de aprobación real, validación experimental o certeza de cumplimiento en obra. La conclusión se limita a los recursos y escenarios declarados.']
    escribir('BRIEF_DIAPOSITIVAS_F02.md','\n'.join(brief))
    payload=dict(habla=habla,responsables=responsables,titulos=titulos,tiempos=tiempos,resumen=resumen,
        base=base,fina=fina,evento=evento,datos=datos)
    (D/'presentacion/recursos/contenido_radiacion.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    palabras=sum(len(re.findall(r'\S+',t)) for t in habla.values())
    print('Actualizados guion,brief,comparación y notas. Palabras de diálogo:',palabras)


if __name__=='__main__':main()
