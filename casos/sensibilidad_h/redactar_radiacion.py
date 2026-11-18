"""Informe de resultados radiativos: solo lectura de evidencia ya auditada."""
import json
from pathlib import Path

RAIZ=Path(__file__).resolve().parents[2]
S=RAIZ/'resultados/sensibilidad_radiacion'
D=RAIZ/'entregas/F02'


def leer(p):return json.loads(p.read_text(encoding='utf-8'))
def numero(x):return f'{x:.4f}'.replace('.',',')


def main():
    aud=leer(S/'auditoria.json');assert aud['estado']=='APROBADA'
    m=leer(S/'ambas/malla_0.4_paso300/matriz.json');rows=m['corridas']
    crit=max(rows,key=lambda r:r['DeltaTmax']['valor'])
    crit14=max(rows,key=lambda r:r['base_336h']['DeltaTmax']['valor'])
    todos=[leer(p) for p in S.glob('*/malla*/M*.json') if p.name.startswith('M')]
    texto=['# Sensibilidad a radiación — resultado del18/11/2026','',
        '**La omisión no es despreciable para esta propuesta.** Se conserva la evidencia anterior como modelo sin radiación. La radiación cambia temperaturas, diferenciales y el mecanismo que produce el máximo; el estudio extendido anterior no puede presentarse como confirmado al incluirla.','',
        '## Comparación aislada de mecanismos','',
        'M4_SS × ERA5-2024, misma malla0,40m y paso máximo300s. Los máximos de columnas distintas no necesariamente ocurren simultáneamente. ΔT siempre resta temperaturas del mismo instante.','',
        '| Intercambio exterior | Tmax14d [°C] | ΔT14d [K] | Tmax672h [°C] | ΔT672h [K] | Horizonte [h] | Alerta de pico pendiente |',
        '|---|---:|---:|---:|---:|---:|---|']
    nombres={'sin_radiacion':'Sin radiación','solar':'Solo solar','larga':'Solo onda larga','ambas':'Solar + onda larga'}
    for v in nombres:
        d=leer(S/'ventana_comun_672'/f'{v}.json');r=d['corrida'];a=r['base_336h']
        texto.append(f"| {nombres[v]} | {numero(a['Tmax']['valor'])} | {numero(a['DeltaTmax']['valor'])} | {numero(r['Tmax']['valor'])} | {numero(r['DeltaTmax']['valor'])} | {r['horizonte_h']} | {'Sí' if r['pico_no_resuelto'] else 'No'} |")
    texto+=['','![Evolución térmica](evidencia_radiacion/01_historias_comparadas.png)','',
        'La radiación solar puede calentar una cara descubierta hasta convertirla en el punto más caliente: Tmax ya no tiene por qué estar en el núcleo. La onda larga aumenta las pérdidas hacia el cielo y puede enfriar S25 durante la noche. Ambos efectos actúan juntos y no se suman linealmente, porque modifican las temperaturas, la conducción y el control de circuitos. Las mantas atenúan el flujo mientras permanecen instaladas; el efecto se intensifica al retirarlas. La última manta se retira a360h de edad de cada capa, después del horizonte docente336h: esto explica buena parte de la diferencia entre la conclusión a14d y el seguimiento posterior.','',
        '## Matriz combinada completa','',
        'Ocho fuentes × tres historiasERA5,24 pares, pesos iguales1/24. Solo se agregan solar y onda larga al plan original; no se optimizan parámetros para obtener cumplimiento.','',
        '| Ventana | Mayor Tmax [°C] | Mayor ΔT [K] | Pares con Tmax>70 | Pares con ΔT>20 | P(unión) del catálogo |',
        '|---|---:|---:|---:|---:|---:|']
    for corto in [True,False]:
        rr=[r['base_336h'] if corto else r for r in rows]
        pt=sum(r['excede_70'] for r in rr);pd=sum(r['excede_20'] for r in rr);pu=sum(r['excede_70'] or r['excede_20'] for r in rr)/24
        texto.append(f"| {'0–336h, exigencia docente' if corto else '0–600/672h, diagnóstico adicional'} | {numero(max(r['Tmax']['valor'] for r in rr))} | {numero(max(r['DeltaTmax']['valor'] for r in rr))} | {pt}/24 | {pd}/24 | {100*pu:.2f}% |")
    texto+=['',f"Caso de mayorΔT14d: **{crit14['curva']} × {crit14['clima']}**. Caso de mayorΔT extendido: **{crit['curva']} × {crit['clima']}**.",
        '',f"**{m['picos_no_resueltos']} pares conservan alerta de pico pendiente** al llegar a672h. Sus valores extendidos son máximos observados hasta ese horizonte, no máximos definitivos. Una excedencia ya observada es concluyente para esa ventana; ausencia de excedencia con alerta no certificaría el futuro.",
        '', '![Catálogo completo](evidencia_radiacion/02_catalogo_pareado.png)','',
        'El horizonte exigido sigue siendo14d desde la primera colocación. Una falla posterior no debe contarse como falla del requisito14d. Tampoco puede usarse el0/24 anterior sin indicar explícitamente que se omitió radiación. Las frecuencias son exactas únicamente dentro del catálogo discreto adoptado: no se estiman intervalos binomiales de24 ensayos aleatorios ni se demuestra riesgo real≤5%.','',
        '## Propiedades, orientación y resolución','',
        f"Contrastes en **{crit['curva']} × {crit['clima']}**, seleccionado por mayor diferencial nominal extendido. Estos contrastes no son una envolvente certificada de todos los posibles materiales, cielos u orientaciones.",'',
        '| Variante | Malla [m] | Paso máximo [s] | ΔT14d [K] | ΔT extendida [K] | Horizonte [h] |',
        '|---|---:|---:|---:|---:|---:|']
    for d in sorted(todos,key=lambda x:(x['procedencia']['variante'],x['procedencia']['lado_m'],x['procedencia']['paso_max_s'])):
        p=d['procedencia'];r=d['corrida']
        if (r['curva'],r['clima'])!=(crit['curva'],crit['clima']) or p['variante'] not in ['ambas','clara','oscura','despejado','giro90']:continue
        texto.append(f"| {p['variante']} | {p['lado_m']} | {p['paso_max_s']} | {numero(r['base_336h']['DeltaTmax']['valor'])} | {numero(r['DeltaTmax']['valor'])} | {r['horizonte_h']} |")
    texto+=['','![Contrastes](evidencia_radiacion/03_contrastes_y_refinamiento.png)','',
        'Absortancia solar0,6 y emisividad0,9 son hipótesis explícitas del acabado exterior equivalente, no propiedades medidas de las protecciones de obra. Se exploran absortancias0,2/0,9. Se estima cielo radiativo mediante punto de rocío y nubosidad total como proxy de nubosidad opaca; no hay medición de onda larga. Se suponen exposición sin sombras, difusa isotrópica y albedo0,2. Los refinamientos son selectivos: no constituyen una nueva matriz fina de24 pares.','',
        '### Confirmación del piloto crítico de14d','',
        '| Caso M4_SS × ERA5-2024 | Tmax14d [°C] | ΔT14d [K] | ΔT extendida [K] |',
        '|---|---:|---:|---:|']
    for d in sorted(todos,key=lambda x:(x['procedencia']['lado_m'],x['procedencia']['paso_max_s'])):
        p=d['procedencia'];r=d['corrida']
        if (r['curva'],r['clima'])!=('M4_SS','ERA5-2024') or p['variante'] not in ['ambas','clara','oscura']:continue
        a=r['base_336h']
        texto.append(f"| {p['variante']}, {p['lado_m']}m / {p['paso_max_s']}s | {numero(a['Tmax']['valor'])} | {numero(a['DeltaTmax']['valor'])} | {numero(r['DeltaTmax']['valor'])} |")
    oldfine=leer(RAIZ/'resultados/comparacion_circuitos/q60/malla_0.2/matriz.json')
    oldrow=next(r for r in oldfine['corridas'] if (r['curva'],r['clima'])==('M4_SS','ERA5-2024'))
    newrow=leer(S/'ambas/malla_0.2_paso300/M4_SS_ERA5-2024.json')['corrida']
    cambio=newrow['base_336h']['DeltaTmax']['valor']-oldrow['base_336h']['DeltaTmax']['valor']
    texto+=['',f"**Comparación pareada fina, únicamente0–336h:** sin radiación,ΔT={numero(oldrow['base_336h']['DeltaTmax']['valor'])}K; con radiación,ΔT={numero(newrow['base_336h']['DeltaTmax']['valor'])}K. Cambio **{numero(cambio)}K**. El incremento a14d es menor que en0,40m: no extrapolar el cambio grueso como efecto físico convergido. Ambos casos finos quedan bajo20K; no se ha repetido la matriz fina completa con radiación.",
        '','![Confirmación selectiva](evidencia_radiacion/04_confirmacion_selectiva.png)','',
        '## Verificaciones y trazabilidad','',
        f"Auditoría aprobada: **{aud['piezas']} piezas de resultados y {aud['transiciones']} registros de transiciones de circuitos**. Dos piezas de la ventana común reutilizan resultados672h existentes; no son simulaciones adicionales. Cada pieza incluye métricas336h y seguimiento extendido; algunas realizan también extensión672h. Se verificaron balance energético global, descomposición solar/convección/onda larga, residual superficial, potencia≤15kW, cobertura y umbrales19/18. Control sin radiación reproduce máximos originales con tolerancia1e-9. Pruebas independientes: sol–aire analítica, Newton contra bisección y balance con refrigeración.",'',
        'Los nuevos snapshots conservan exactamente el aire, viento yGHI originales. Se incorporaronDNI,DHI,punto de rocío y nubosidad con marcas temporales consistentes. La radiación se aplica al exterior de la protección, resolviendo su temperatura y atravesando su resistencia; no se inyecta directamente al hormigón a través de las mantas.','',
        'Método, ecuaciones, supuestos y fuentes: [protocolo](PROTOCOLO_RADIACION.md). '
        'Datos: `datos/clima/radiacion/manifiesto.json`. Resultados: `resultados/sensibilidad_radiacion/`. '
        'Tabla completa: [resultadosCSV](evidencia_radiacion/resultados.csv). '
        'Ejecutor: `casos/sensibilidad_h/sensibilidad_radiacion.py`; auditor: `auditar_radiacion.py`.','',
        '## Consecuencia para la entrega','',
        'Presentar la propuesta con sus resultados por horizonte e incorporar radiación al modelo que se use para defender la decisión, o justificar y definir una protección real que modifique su exposición y volver a simularla. Este estudio no redimensiona tubos, cambia retiros ni valida una solución nueva. La comparación60/55/50/45m³/h anterior sigue siendo una comparación sin radiación: no se ha repetido esa optimización completa con este intercambio.','',
        'Esta prueba de sensibilidad queda cerrada en el alcance descrito. En la presentación hay que distinguir el cumplimiento nominal observado a14d del diagnóstico posterior y declarar las propiedades superficiales supuestas. No se debe afirmar que la radiación es despreciable, que los refinamientos selectivos equivalen a una matriz fina completa con radiación o que los resultados garantizan riesgo real≤5%.']
    documento='\n'.join(texto)+'\n'
    for a,b in [('del18/11','del 18/11'),('malla0,40m','malla de 0,40 m'),('paso máximo300s','paso máximo de 300 s'),('Tmax14d','Tmax a 14 días'),('ΔT14d','ΔT a 14 días'),('Tmax672h','Tmax a 672 h'),('ΔT672h','ΔT a 672 h'),('horizonte docente336h','horizonte docente de 336 h'),('a360h','a 360 h'),('a14d','a 14 días'),('de14d','de 14 días'),('14d','14 días'),('336h','336 h'),('672h','672 h'),('historiasERA5,24','historias ERA5, 24'),('iguales1/24','iguales a 1/24'),('mayorΔT','mayor ΔT'),('el0/24','el 0/24'),('a672 h','a 672 h'),('únicamente0','únicamente 0'),('sin radiación,ΔT','sin radiación, ΔT'),('con radiación,ΔT','con radiación, ΔT'),('en0,40m','en 0,40 m'),('bajo20K','bajo 20 K'),('solar0,6','solar de 0,6'),('emisividad0,9','emisividad de 0,9'),('absortancias0,2/0,9','absortancias de 0,2/0,9'),('albedo0,2','albedo de 0,2'),('de24','de 24'),('a0,20m','a 0,20 m'),('datosCSV','datos CSV'),('resultadosCSV','resultados CSV'),('yGHI','y GHI'),('incorporaronDNI,DHI,punto','incorporaron DNI, DHI, punto'),('potencia≤15kW','potencia ≤ 15 kW'),('tolerancia1e-9','tolerancia 1e-9'),('riesgo real≤5%','riesgo real ≤ 5%'),('comparación60/55/50/45m³/h','comparación de 60/55/50/45 m³/h')]:
        documento=documento.replace(a,b)
    (D/'SENSIBILIDAD_RADIACION.md').write_text(documento,encoding='utf-8')
    print('Informe guardado:',D/'SENSIBILIDAD_RADIACION.md')


if __name__=='__main__':main()
