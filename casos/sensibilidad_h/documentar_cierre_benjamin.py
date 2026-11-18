"""Consolida propuesta docente y dibuja montaje; no ejecuta el solver."""
import csv
from hashlib import sha256
import json
import os
from pathlib import Path

RAIZ=Path(__file__).resolve().parents[2]
os.environ.setdefault('MPLCONFIGDIR',str(RAIZ/'.venv/cache/matplotlib'))


def main():
    destino=RAIZ/'entregas/F02'
    esquema=json.loads((RAIZ/'resultados/diseno_circuitos_colocacion/esquema.json').read_text(encoding='utf-8'))
    matriz=json.loads((RAIZ/'resultados/circuitos_histeresis/matriz.json').read_text(encoding='utf-8'))
    filas=[
        ('Volumen IFC',esquema['volumen_ifc_m3'],'m3','IFC y esquema geométrico','Dato geométrico del modelo','Geometría oficial no completada'),
        ('Caudal total hormigón',60,'m3/h','Supuesto docente autorizado','Adoptado; dos frentes30','No rendimiento medido'),
        ('Temperatura colocación',12,'°C','Decisión del proyecto','Condición nominal exacta','Desviaciones requieren actualización'),
        ('Duración colocación',esquema['duracion_total_h'],'h','Integración de capas IFC /60','Calculada','Toda la fundación; no incluye control posterior'),
        ('Capas físicas',11,'capas','Esquema IFC','10x0.40m y última0.30m','No son juntas frías'),
        ('Espesor máximo capa',.4,'m','Decisión constructiva','Adoptado','Compatibilidad con vibrador y armadura'),
        ('Ventana local unión',150,'min','Condición propuesta de aceptación','Hipótesis a comprobar con mezcla','No ensayo ni fraguado medido'),
        ('Sitio','-37.277929 / -72.368271','latitud / longitud','Sitios del grupo6','Coordenadas exigidas','El Rosal; no sustituir por centro de ciudad'),
        ('Climas','ERA5 2023 / 2024 / 2025','historias horarias','Snapshots conservados','Alineación por hora relativa','No pronóstico de obra2026'),
        ('Densidad',2476,'kg/m3','Fuente docente de hidratación','Conservada','No calibrada en obra'),
        ('Calor específico',1023,'J/(kg K)','Fuente docente de hidratación','Conservado','Constante'),
        ('Conductividad hormigón',2,'W/(m K)','Supuesto con sensibilidad histórica','Conservada','No k óptimo ni calibrado'),
        ('Convección','5.7+3.8*v2','W/(m2 K)','Correlación documentada en VIENTO.md','Historia horaria','No radiación explícita ni apantallamiento'),
        ('Transformación viento','v2=v10*(2/10)^0.14','m/s','Perfil de exposición supuesto','Conservado','Campo abierto; altura2m representativa'),
        ('Temperatura suelo',15,'°C','Borde equivalente','Supuesto','Sin inercia ni medición local'),
        ('Conductividad suelo',1.2,'W/(m K)','Borde equivalente','Supuesto','No estudio geotécnico térmico'),
        ('Longitud suelo',.5,'m','Resistencia equivalente L/k','Supuesto','No profundidad de dominio simulado'),
        ('Exposición','Base a suelo; laterales abiertos sin relleno','—','Hipótesis declarada','Conservada','Cambio de relleno exige nuevos bordes'),
        ('Madera',.018,'m','Familia AraucoPly referencia previa','Adoptada','k0.158 W/(mK); resistencia mecánica aparte'),
        ('Aislación','2x0.040','m','Familia Aislanglass referencia previa','Adoptada','k0.042 W/(mK); seca y continua'),
        ('Retiro madera',72,'h de edad local','Calendario nominal','Condicionado a resistencia y revisión térmica','No certificado de desmolde'),
        ('Retiros mantas','240 / 360','h de edad local','Calendario nominal simulado','Condicionados a monitoreo y predicción','No retiro automático'),
        ('Circuitos',9,'ramales paralelos','Esquema geométrico','Adoptados','3/3/2/1 en cotas0.5/1.5/2.5/3.8m'),
        ('Diámetro interior cálculo',.025,'m','Decisión del proyecto','Idealización geométrica','Clase exterior/espesor no dimensionados'),
        ('Longitud interna',esquema['longitud_interior_esquema_m'],'m','Esquema de serpentines','Calculada','Sin acometidas ni colectores'),
        ('Caudal ramal abierto',18,'L/min','Decisión del proyecto','Constante','No calibra transferencia'),
        ('Caudal sistema con bypass',162,'L/min','9x18','Nominal constante','Embebido18*N; resto bypass'),
        ('Agua',18,'°C uniforme','Idealización autorizada','Conservada','No balance axial real'),
        ('U equivalente',5,'W/(m3 K)','Sumidero volumétrico','Hipótesis','No coeficiente pared ni calibración de tubo'),
        ('Tope extracción global',15,'kW térmicos','Control equivalente','Adoptado','No potencia constante ni eléctrica'),
        ('Zona refrigerable base',414.016,'m3','Máscara0.40m excluye contorno','Representación equivalente','No antigua máscara366m3'),
        ('Apertura',19,'°C mínima de tramos','Histéresis propuesta y simulada','Solo con cobertura','Cierre<=18; banda mantiene estado'),
        ('Apagado final','Sin hora fija','—','Decisión actual','Criterio de liberación en documento','No se adopta432h'),
        ('Advertencia','65 / 18','°C Tmax / K Delta','Decisión operativa propuesta','No umbral normativo','No optimizado'),
        ('Intervención','68 / 19','°C Tmax / K Delta','Decisión operativa propuesta','No umbral normativo','No optimizado'),
        ('Límites docentes','70 / 20','°C Tmax / K Delta','Pauta curso','Max temporal con resta simultánea','No garantía de ausencia de fisuración'),
        ('Registro','1 / <=5','min adquisición / archivo','Plan propuesto','Durante todo control','Brutos y extremos conservados'),
        ('Catálogo','8x3; peso1/24','—','Fuentes completas y ERA5 congelado','Modelo discreto explícito','No ensayos iid; curva común; independencia supuesta'),
        ('Horizontes','336 / 600','h desde primera colocación','Docente / diagnóstico','Resultados separados','Extensión si alertas; no fecha de liberación'),
        ('Malla base',.4,'m','Cálculo de nueve circuitos','Malla de comparación','Confirmación0.20m: candidata completa; alternativas selectivas'),
        ('Paso máximo base',300,'s','Cálculo de nueve circuitos','Sujeto a estabilidad y eventos','Confirmación temporal150s en tres pares'),
    ]
    with (destino/'PARAMETROS_BENJAMIN.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f);w.writerow(['parametro','valor','unidad','fuente','estado','alcance']);w.writerows(filas)
    entradas=['resultados/diseno_circuitos_colocacion/esquema.json','resultados/circuitos_histeresis/matriz.json',
        'casos/sensibilidad_h/simular_circuitos.py','casos/sensibilidad_h/control_circuitos.py']
    if (RAIZ/'resultados/circuitos_confirmacion/resumen.json').exists():
        entradas.append('resultados/circuitos_confirmacion/resumen.json')
    for q,h in [(q,.4) for q in [60,55,50,45]]+[(60,.2)]:
        ruta=f'resultados/comparacion_circuitos/q{q}/malla_{h:g}/matriz.json'
        if (RAIZ/ruta).exists():entradas.append(ruta)
    config=dict(version='benjamin-nueve-circuitos-2026-11-18',alcance='Docente idealizado; no proyecto ejecutivo',
        parametros=[dict(zip(['parametro','valor','unidad','fuente','estado','alcance'],f)) for f in filas],
        insumos_sha256={ruta:sha256((RAIZ/ruta).read_bytes()).hexdigest() for ruta in entradas},
        procedencia_simulacion=matriz['procedencia'],control=dict(cobertura_previa=True,abre_min_C=19,cierra_min_C=18,
        agua_uniforme_C=18,apagado_global_fijo=False,falla_medicion='cerrar ramal; actualizar predicción'),
        medidas_operativas='Propuestas; no incorporadas automáticamente a la matriz nominal',
        simulacion_base='resultados/circuitos_histeresis/matriz.json',
        confirmacion_selectiva='resultados/circuitos_confirmacion/resumen.json')
    if (RAIZ/'resultados/comparacion_circuitos/q60/malla_0.2/matriz.json').exists():
        config['confirmacion_espacial_completa']='resultados/comparacion_circuitos/q60/malla_0.2/matriz.json'
        config['comparacion_homogenea']='entregas/F02/COMPARACION_CIRCUITOS_FINAL.md'
    (destino/'CONFIGURACION_BENJAMIN.json').write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    fig,axes=plt.subplots(1,3,figsize=(12,4.6))
    etapas=[('Antes de 72 h',['Hormigón','Madera 18 mm','Manta 40 mm','Manta 40 mm']),
        ('Después del desmolde autorizado',['Hormigón','Manta 40 mm','Manta 40 mm']),
        ('Después de 240 h, si se autoriza',['Hormigón','Manta 40 mm'])]
    colores={'Hormigón':'#b1b7be','Madera 18 mm':'#c99c65','Manta 40 mm':'#e8d589'}
    for ax,(titulo,capas) in zip(axes,etapas):
        for j,c in enumerate(capas):
            ancho=1.4 if j==0 else .6
            x=0 if j==0 else 1.4+(j-1)*.6
            ax.add_patch(Rectangle((x,0),ancho,2,fc=colores[c],ec='white',lw=2))
            ax.text(x+ancho/2,1,c,rotation=90 if j else 0,ha='center',va='center',fontsize=10)
        ax.text(1.7,-.25,'Soporte de mantas independiente\n+ cubierta contra agua/viento',ha='center',va='top',fontsize=9)
        ax.set(xlim=(-.1,3.3),ylim=(-.8,2.5),title=titulo);ax.axis('off')
    fig.suptitle('Protección lateral adoptada · esquema sin escala',fontsize=15)
    fig.text(.04,.04,'Retiros por edad local: madera 72 h, mantas 240/360 h. Sujetos a resistencia, monitoreo y predicción.\n'
        'Coronación: dos mantas sin madera; base: suelo. No instalar aislación entre capas de hormigón.',fontsize=10)
    fig.tight_layout(rect=(0,.14,1,.9))
    fig.savefig(destino/'PROTECCIONES_BENJAMIN.png',dpi=150,facecolor='white');plt.close(fig)
    print('Generados: tabla única, configuración con hashes y croquis de protección.')


if __name__=='__main__':main()
