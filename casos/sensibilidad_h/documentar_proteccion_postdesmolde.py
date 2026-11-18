"""Informe y figuras de las tres alternativas; requiere matrices completas auditadas."""
from pathlib import Path
import csv
import json
import os

RAIZ=Path(__file__).resolve().parents[2]
os.environ.setdefault('MPLCONFIGDIR',str(RAIZ/'.venv/cache/matplotlib'))
S=RAIZ/'resultados/proteccion_postdesmolde'
D=RAIZ/'entregas/F02/proteccion_postdesmolde'


def leer(p):return json.loads(p.read_text(encoding='utf8'))


def main():
    resumen=leer(S/'resumen.json')
    assert resumen['estado_auditoria']=='APROBADA' and resumen['matrices_completas']==3
    D.mkdir(parents=True,exist_ok=True)
    nombres={'retiro_504':'Solo retrasar última manta a 504 h',
        'sombra_90':'Retiro 360 h + sombra solar 90 %',
        'combinada_504_sombra_90':'Retiro 504 h + sombra solar 90 %'}
    filas=[]
    for v in nombres:
        m=leer(S/v/'matriz.json')
        for r in m['corridas']:
            filas.append(dict(variante=v,curva=r['curva'],clima=r['clima'],peso=r['peso'],
                Tmax_C=r['Tmax']['valor'],DeltaT_K=r['DeltaTmax']['valor'],
                t_Delta_h=r['DeltaTmax']['tiempo_h'],Tcaliente_evento_C=r['DeltaTmax']['Tmax_C'],
                Tmin_S25_evento_C=r['DeltaTmax']['Tmin_S25_C'],
                I_T=int(r['excede_70']),I_Delta=int(r['excede_20']),
                I_union=int(r['excede_70'] or r['excede_20']),alerta_cola=r['pico_no_resuelto']))
    with (D/'RESULTADOS_72_ESCENARIOS.csv').open('w',encoding='utf-8-sig',newline='') as out:
        w=csv.DictWriter(out,fieldnames=list(filas[0]));w.writeheader();w.writerows(filas)
    with (D/'CONFIRMACIONES_SELECTIVAS.csv').open('w',encoding='utf-8-sig',newline='') as out:
        rr=resumen['confirmaciones_selectivas']
        if rr:
            w=csv.DictWriter(out,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(2,1,figsize=(11,7),sharex=True,layout='constrained')
    rutas=[('Original',RAIZ/'resultados/sensibilidad_radiacion/ambas/malla_0.4_paso300/M4_SS_ERA5-2024.json','#999999')]
    colores=['#b54830','#1b74aa','#166c65']
    rutas += [(nombres[v],S/v/'malla_0.4_paso300/M4_SS_ERA5-2024.json',c) for v,c in zip(nombres,colores)]
    for etiqueta,p,c in rutas:
        d=leer(p);h=d['historia'];x=[r['tiempo_h'] for r in h]
        ax[0].plot(x,[r['Tmax_C'] for r in h],color=c,label=etiqueta)
        ax[1].plot(x,[r['DeltaT_K'] for r in h],color=c,label=etiqueta)
    for a in ax:
        a.axvline(336,color='black',ls=':',lw=1)
        a.axvline(360,color='#999999',ls='--',lw=.8)
        a.axvline(504,color='#166c65',ls='--',lw=.8)
        a.grid(alpha=.2)
    ax[0].set(title='M4_SS × ERA5-2024: mismo hormigón, clima y refrigeración',ylabel='Tmax [°C]')
    ax[0].legend(fontsize=8,loc='upper left',ncol=2)
    ax[1].axhline(20,color='black',ls='--',label='Límite20 K')
    ax[1].set(xlim=(0,672),xlabel='Tiempo desde primera colocación [h]',ylabel='ΔT simultáneo [K]')
    fig.savefig(D/'01_COMPARACION_HISTORIAS.png',dpi=170);plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,4.8),layout='constrained')
    ms=resumen['matrices'];ys=[m['Delta'] for m in ms]
    ax.bar(range(3),ys,color=colores)
    ax.axhline(20,color='black',ls='--',label='Límite20 K')
    for i,m in enumerate(ms):
        ax.text(i,m['Delta']+.35,f"{m['Delta']:.2f} K\nPf = {100*m['riesgo']['P_union']:.2f} %",ha='center',fontsize=10)
    ax.set(xticks=range(3),xticklabels=['Manta 504 h','Sombra 90 %\nretiro 360 h','Manta 504 h\n+ sombra 90 %'],
        ylabel='Mayor ΔT del catálogo [K]',title='24 escenarios por alternativa · 0,40 m / 300 s · 0–672 h',ylim=(0,max(ys)+5))
    ax.legend();ax.grid(axis='y',alpha=.2)
    fig.savefig(D/'02_CATALOGO_24_PARES.png',dpi=170);plt.close(fig)
    lineas=['# Protección después del desmolde: tres alternativas simuladas','',
        'Estudio autorizado por el usuario. No modifica PPT, PDF, guion, brief ni la entrada numérica vigente. Las variantes son nuevas salidas, conservando los estudios anteriores.',
        '', '## Qué se mantuvo y qué se cambió','',
        'Se mantienen60m³/h,12°C,11capas, nueve circuitos, agua ideal18°C,18L/min por ramal, bypass162L/min, Uv5W/(m³K), tope global15kW y control19/18sin corte global. Misma geometría, fuentes, clima, pesos y sitio. Madera18mm hasta72h y primera manta40mm hasta240h. Edades contadas desde activación de cada capa.',
        '',
        '1. **Retraso:** última manta40mm hasta504h (21días) en lugar de360h. Después se descubre la cara, sin sombra.',
        '2. **Sombra:** última manta hasta360h; luego transmitancia solar efectiva0,10 sobre todas las caras expuestas al aire de esa capa.',
        '3. **Combinación:** última manta hasta504h y la misma sombra posterior.',
        '',
        '**La sombra no es una manta adicional ni un cambio de absortancia del hormigón.** En el balance exterior se usa α·τ·I después del retiro local. Se mantienen convección y onda larga, incluido el cielo original; no se acredita una cubierta comercial ni se resuelven su temperatura, emisión infrarroja, influencia sobre viento o montaje. τ=0,10 es un supuesto de ensayo que necesitaría verificación para una instalación real. La cobertura se supone en caras superiores y laterales, no solamente un techo horizontal.',
        '',
        'La sombra permanece hasta el final del seguimiento. No se simuló su desmontaje a672h ni se afirma cumplimiento indefinido tras retirarla. Mantener tubos no es un cambio nuevo: las tres alternativas conservan el control reversible previo.',
        '', '## Resultados de los tres puntos','',
        '|Alternativa|Mayor Tmax [°C]|MayorΔT [K]|P_T|P_Δ|P_unión|Alertas de cola|',
        '|---|---:|---:|---:|---:|---:|---:|']
    for m in ms:
        lineas.append(f"|{nombres[m['variante']]}|{m['Tmax']:.4f}|{m['Delta']:.4f}|{100*m['riesgo']['P_T']:.2f}%|{100*m['riesgo']['P_delta']:.2f}%|{100*m['riesgo']['P_union']:.2f}%|{m['alertas']}|")
    lineas += ['',
        'Todas las filas contienen24pares completos (ocho fuentes×tres años), malla0,40m, paso máximo300s y ventana común0–672h. Pesos1/24. Los valores se deciden sin redondear. Máximos deT yΔpueden pertenecer a casos/horas distintos. Todas las variantes reproducen la historia previa y las métricas exactas0–336h del caso nominal, porque las medidas se activan después de esa ventana. No son24ensayos aleatorios ni probabilidad real garantizada.',
        '', '![Historias comparadas](01_COMPARACION_HISTORIAS.png)','',
        '![Catálogo completo](02_CATALOGO_24_PARES.png)','',
        '## Interpretación física','',
        'Retrasar la manta reduce exposición durante un tiempo, pero al descubrir la superficie sigue existiendo el calentamiento solar posterior. La sombra con retiro a360h evita gran parte de ese calentamiento, pero no elimina el enfriamiento superficial nocturno mientras el interior conserva calor. La combinación permite que el volumen se enfríe con mayor resistencia exterior antes de descubrirlo y atenúa después las ganancias solares.',
        '',
        'Ejemplo M4_SS×ERA5-2024: con sombra sola, a428h la máxima interior30,2942°C y la mínimaS25de6,8170°C producen23,4772K. El mecanismo no es el mismo que el pico de cara soleada del caso descubierto. Por eso no basta comparar únicamente Tmax o suponer que más enfriamiento siempre mejoraΔT.',
        '', '## Confirmaciones de resolución','',
        'Los refinamientos siguientes son **selectivos**; no constituyen una matriz fina completa de24pares ni una probabilidad fina global. Se conserva la zona refrigerable414,016m³ y los tiempos físicos de colocación.','',
        '|Variante / curva / clima|Malla [m]|Paso máximo [s]|Tmax [°C]|ΔT [K]|CambioΔT frente a0,40m/300s [K]|Alerta|',
        '|---|---:|---:|---:|---:|---:|---|']
    for r in resumen['confirmaciones_selectivas']:
        lineas.append(f"|{r['variante']} / {r['curva']}×{r['clima']}|{r['lado_m']}|{r['paso_max_s']}|{r['Tmax']:.4f}|{r['Delta']:.4f}|{r['cambio_Delta']:+.4f}|{r['alerta']}|")
    sombra_fina=[r for r in resumen['confirmaciones_selectivas'] if r['variante']=='sombra_90' and r['lado_m']==.2 and (r['Delta']>20 or r['Tmax']>70)]
    if sombra_fina:
        lineas += ['',f"En sombra sola se confirmaron {len(sombra_fina)}pares fallidos con0,20m. Bajo pesos1/24, su peso conjunto ya aporta una cota inferior de{100*len(sombra_fina)/24:.4f}%aP_unión en esa resolución. No es una estimación de la matriz fina completa; permite rechazarla si esa cota supera5%, sin depender del caso grueso marginal de20,028K."]
    comb=next(m for m in ms if m['variante']=='combinada_504_sombra_90')
    cumple=comb['riesgo']['P_union']<=.05
    lineas += ['', '## Conclusión y límites','',
        f"La combinación {'cumple' if cumple else 'no cumple'} el requisito probabilístico del catálogo en0–672h: P_unión={100*comb['riesgo']['P_union']:.4f}%. Margen del mayorΔT grueso respecto de20K: {20-comb['Delta']:.4f}K. Las confirmaciones se informan por separado y no eliminan incertidumbre de modelo.",
        '',
        f"Alarmas de cola de la combinación: {comb['alertas']}. Una ausencia de alarmas significa que el detector conservador no encontró indicadores de pico pendiente en esa historia climática; no demuestra un máximo universal bajo meteorología futura. Si hay alarmas, la captura de máximos sigue pendiente, aunque las excedencias ya observadas sean concluyentes.",
        '',
        'Si se adopta esta alternativa, cambia la programación de protección, no el plazo10,6129h de colocación. El retiro504h sigue sujeto a resistencia, monitoreo y predicción. La ventana de unión, la transferencia real de tubos, el equipo frigorífico y la cubierta de sombra continúan como hipótesis o verificaciones constructivas, no quedan validados por estos números. No se ha resuelto fisuración mecánica.',
        '',
        '504h es una edad ensayada favorable, no la edad mínima de retiro optimizada. Los tres ensayos corresponden a la candidata60m³/h; no se repitieron55/50/45m³/h con las nuevas protecciones. Si se incorpora una tabla de esos ritmos con protección revisada, deben calcularse sus filas de forma homogénea y no reutilizar las temperaturas antiguas como si fueran de esta configuración. La cota de duración V/60 conserva su significado bajo la capacidad máxima adoptada.',
        '', '## Auditoría y reproducción','',
        f"Auditoría aprobada: {resumen['piezas']}piezas, {resumen['matrices_completas']}matrices completas y {resumen['transiciones']}transiciones. Se comprobaron hashes, pesos, indicadores, balance energético global y radiativo, potencia máxima, cobertura, histéresis, caudal con bypass y equivalencia antes de336h.",
        '',
        'Configuración congelada del estudio: `casos/sensibilidad_h/proteccion_postdesmolde.json`. Motor: `proteccion_postdesmolde.py`. Auditor/agregador: `auditar_proteccion_postdesmolde.py`. Informe/figuras: `documentar_proteccion_postdesmolde.py`. Resultados originales en `resultados/proteccion_postdesmolde/`; resumen con confirmaciones y archivos por matriz. No editar scripts/config con hash para reanudar sus piezas.',
        '',
        'Tablas adjuntas: `RESULTADOS_72_ESCENARIOS.csv` y `CONFIRMACIONES_SELECTIVAS.csv`. Las fechas de calendario se obtienen desde t₀=19/11/2026a10:00UTC−03:00: los retiros de última manta se distribuyen entre504y514,4210h por capa (10/12/2026aprox.10:00–20:25). No se trata de esperar504h después de terminar toda la fundación.',
        '']
    (D/'RESULTADO_TRES_ALTERNATIVAS.md').write_text('\n'.join(lineas),encoding='utf8')
    print('Informe y figuras generados en',D)


if __name__=='__main__':main()
