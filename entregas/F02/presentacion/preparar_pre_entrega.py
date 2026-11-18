"""Integra contenido final conservando guion personalizado; no ejecuta solver."""
from pathlib import Path
import argparse,json,re

R=Path.cwd();F=R/'entregas/F02';W=R/'.venv/cache/pre_entrega_f02'


def main():
    p=argparse.ArgumentParser();p.add_argument('--actualizar-guion',action='store_true');a=p.parse_args()
    guion=F/'GUION_ORAL_F02.md'
    if a.actualizar_guion:
        texto=(W/guion.name).read_text(encoding='utf8')
        cambios={
            'comparación homogénea0–336h.':'comparación homogénea0–672h con métricas también a336h.',
            'Los resultados posteriores se presentan como diagnóstico separado.':'La protección revisada mantiene la última manta hasta504h de edad local y después sombra solar90%; se conserva10% de incidencia. No se validó retirar esa sombra.',
            'Revisamos 24 escenarios, con sol y radiación incluidos, y ninguno supera los límites durante los 14 días. Ahora les contamos cómo llegamos a eso y bajo qué supuestos.':'Revisamos 24 escenarios con radiación: ninguno supera los límites en los 14 días ni hasta los 28 simulados. Les contamos los supuestos.',
            'el centro queda caliente':'el interior conserva calor',
            'Dentro van nueve circuitos en paralelo, en cuatro alturas, de 18 litros por minuto cada uno, con un tope total de 15 kilowatts.':'Dentro van nueve circuitos en cuatro alturas, a 18 litros por minuto por ramal. El cálculo usa un tope equivalente de 15 kilowatts.',
            'Cada circuito se abre cuando está cubierto y llega a 19 grados, y se cierra si baja a 18. Esa banda evita que se abra y se cierre a cada rato. El agua la suponemos ideal a 18 grados. Luis les cuenta cómo lo comprobamos.':'Cada circuito abre cubierto y con mínima de 19 grados; cierra a 18, con agua ideal a 18. La última manta queda hasta 504 horas de edad local; después, sombra del 90 %. Luis sigue con el cálculo.',
            'al decir «cada circuito se abre»':'al decir «cada circuito abre»',
            'gráfico de la regla 19/18 °C y el rótulo de supuesto.':'gráfico de la regla 19/18 °C y protección 504 h + sombra 90 %.',
            'Después afinamos la malla a 20 centímetros y el paso de tiempo a la mitad. El diferencial cambió como máximo 1,17 grados con la malla, y apenas una milésima con el paso. Todo sigue cumpliendo. Eso muestra un cálculo estable, no una refrigeración calibrada.':'Después afinamos por separado la malla a 20 centímetros y el paso de tiempo a la mitad. El diferencial cambió como máximo 0,88 grados con la malla y 0,0014 con el paso. Mantiene el cumplimiento, sin calibrar los tubos.',
            'Ojo: después de los 14 días, al retirar la última manta, sí aparecen excedencias, así que hay que seguir midiendo.':'Con manta hasta 504 horas y sombra posterior, también cumple hasta el día 28.',
            'tabla de los cuatro ritmos':'tabla de los dos ritmos y la exclusión por capacidad',
            'Probamos cuatro ritmos, de 60 a 45 metros cúbicos por hora. Los cuatro cumplen.':'Comparamos 60 y 55 metros cúbicos por hora con la misma protección. Ambos cumplen.',
            'La diferencia es el tiempo: 10,61 horas a 60 y 14,15 a 45, sin mejora térmica.':'La diferencia es el tiempo: a 55 tardamos 11,58 horas, unos 58 minutos más.',
            'Y más rápido no se puede:':'Y más rápido, con estos recursos, no se puede:',
            'Recomendamos 60 metros cúbicos por hora, 12 grados y nueve circuitos. El control térmico sigue después de colocar.':'Recomendamos 60 metros cúbicos por hora, 12 grados y nueve circuitos, con manta hasta 21 días y sombra posterior. El control continúa.',
            'La limitación: refrigeración y radiación son supuestas, no calibradas en obra. Muchas gracias.':'La limitación: refrigeración y sombra idealizadas; falta validarlas en obra. Muchas gracias.',
        }
        for viejo,nuevo in cambios.items():
            if viejo not in texto:raise ValueError('No coincide la edición personalizada: '+viejo[:70])
            texto=texto.replace(viejo,nuevo)
        texto=texto.replace('S5: Temperaturas durante los14 días','S5: Temperaturas y seguimiento')
        ini=texto.index('## Resultados para responder preguntas');fin=texto.index('## Preguntas físicas probables')
        texto=texto[:ini]+'''## Resultados para responder preguntas

Todas las filas siguientes usan última manta hasta504h de edad local y sombra solar90% posterior, con radiación y control de tubos19/18. Cada fila contiene24pares completos hasta672h. También cumplen las métricas336h.

| Plan y resolución | D [h] | Tmax672h [°C] | ΔT672h [K] | P conjunta |
|---|---:|---:|---:|---:|
|60m³/h,0,40m/300s|10,6129|47,4941|16,5306|0%|
|55m³/h,0,40m/300s|11,5777|47,5128|16,6011|0%|
|60m³/h,0,20m/300s|10,6129|47,0322|15,7202|0%|

Mayor cambio espacial emparejadoΔT=0,881712K en0–672h; temporal0,001365K en dos pares separados. Margen fino=4,2798K hasta20K. No confundir con1,174621K del estudio anterior a336h. El plan55 cuesta57,89min adicionales; la pequeña diferencia térmica no sustenta por sí sola la elección.

Evento ilustrado: M4_SS×ERA5-2024,0,40m/300s,267h, fase previa al cambio horario:42,1202°C−25,5897°C=16,5306K. El punto caliente es una cara reconstruida; el corte muestra centros. No restar el pico histórico46,6574°C a esa mínima.

Tres medidas: retrasar solo última manta a504h produce24/24fallas; sombra90%con retiro360h produce5/24; combinación produce0/24hasta672h. La sombra es una hipótesis de transmisión solar0,10 en todas las caras al aire, conservando h y onda larga; no se ha validado su instalación o retiro.

''' +texto[fin:]
        respuestas={
            9:'Sí incluimos solar y onda larga. Antes del retiro local de la última manta usamos exposición completa; después de504h se transmite10% de la solar. Se conserva el intercambio infrarrojo y h originales como idealización. Laterales sin relleno,α0,6 yε0,9 supuestas; la radiación no se incluye otra vez en h.',
            13:'Es una condición propuesta de aceptación, no espera obligatoria o fraguado medido. La capa mayor tarda107,4min a60 y117,1min a55m³/h, frente a150min exigidos disponibles. La mezcla, recorrido y vibración deben demostrar unión real.',
            15:'La manta limita el enfriamiento superficial mientras el interior conserva calor. No se necesita mantenerla indefinidamente en el modelo: última manta504h y sombra posterior dieron0/24fallas hasta672h.504h es una edad ensayada, no un retiro mínimo optimizado.',
            16:'Madera72h, primera manta240h y última504h de edad local por capa; después sombra90%. Son edades nominales condicionadas a resistencia, monitoreo y predicción. No son un único retiro simultáneo de toda la fundación.',
            26:'No se calculó fecha definitiva de apagado. El control19/18 sigue después de los retiros y puede reabrir. La combinación cumple672h, pero la sombra permanece instalada; retirar sombra o desmantelar tubos exige otra predicción. El caso antiguo360h sin sombra sí excedía posteriormente.',
            32:'Con la misma protección revisada se completaron60/55m³/h a672h. Ambos danP_f0 en el catálogo grueso;55tarda11,5777h,57,89min más. La propuesta60 además tiene24pares finos completos. La selección usa la cotaV/60, no una diferencia térmica pequeña menor que la sensibilidad espacial.',
            37:'El retiro antiguo360h sin sombra descubría caras que podían calentarse por sol o enfriarse de noche;24/24fallaban después de14d. Se corrigió con última manta504h y sombra posterior90%:24/24pasan hasta672h en ambas mallas, sin alertas. Esto no acredita retirar después la sombra.',
            38:"q''=(Ts−Ti)/R=h(Ta−Ts)+ατI+εσ(Trad,K⁴−Ts,K⁴). τ=1 antes del retiro de última manta y0,10 después de504h de edad local. Flujo positivo hacia el hormigón, Ts exterior de protección, Ti centro. R suma media celda y capas; las potencias cuartas usan kelvin.",
        }
        for num,resp in respuestas.items():
            patron=rf'(\*\*{num}\. [^\n]*?\?\*\*).*?(?=\n\n\*\*\d+\.|\n\n### |\n\n## |\Z)'
            texto,n=re.subn(patron,lambda m:m[1]+' '+resp,texto,flags=re.S)
            if n!=1:raise ValueError(('Pregunta no encontrada',num,n))
        agregado='''### Cierre de la pauta y protección nueva

**41. ¿El10% solar residual se despreció?** No. Está incluido comoτI=0,10I. No comparamos0%contra10% de transmisión para llamarlo despreciable. «90% de sombra» comercial puede medir otra banda; debe acreditarse transmisión solar efectiva y cobertura superior/lateral.

**42. ¿El hormigón deja de hidratarse a los21días?** No. El retiro se justifica por la respuesta térmica simulada, no por una edad universal de fin de hidratación. Nuestro archivo adopta cola nula al terminar su registro240,333hSS/163h22A; es una hipótesis, no el fin físico de reacción.

**43. ¿Qué significa una vertida única si hay11capas?** Una sola operación continua de todo el volumen, con capas sin esperas de endurecimiento. Coincide con la propuesta. El solver activa cada capa al inicio, pero D conserva su duración física: última activación10,4210h y término10,6129h.

**44. ¿Cómo se actualizaS25?** Solo se muestrean caras exteriores del hormigón activo. Al cubrir una cara con la siguiente capa pasa a interfaz interna y sale deS25. Reconstruimos a25mm desde el centro y el flujo de cara; no resolvemos celdas de25mm ni usamos el exterior de la manta.

**45. ¿Dónde empieza el reloj?** t₀=19/11/2026a10:00UTC−03:00,America/Santiago, común a todos los planes. D incluye esperas y cualquier postergación; no se reinicia al comenzar una primera capa tardía. Preparativos y continuidad de suministro son condiciones declaradas.

**46. ¿Qué caso conocido y balance tenemos?** Seno1D exacto con error máximo0,00257143K y24tests de ese módulo, además de celda/control/superficie por cálculos independientes. Mayor residuo global0,000247955J. Son verificaciones numéricas, no validación experimental de fundación o tubos.

'''
        texto=texto.replace('## Fuentes',agregado+'## Fuentes')
        texto=texto.replace('- [Comparación vigente](COMPARACION_CIRCUITOS_FINAL.md).','- [Cierre vigente](cierre_revision_final/RESULTADOS_CIERRE.md).')
        texto=texto.replace('Evitar afirmar: riesgo real cero; transferencia de tubos acreditada; resultados extendidos bajo20K; todas las alternativas con matriz fina; ausencia de fisuración demostrada.','Evitar afirmar: riesgo real cero; transferencia real de tubos acreditada; transmisión solar de un producto validada; retiro de sombra simulado; fecha definitiva de apagado; todas las alternativas con matriz fina; ausencia de fisuración demostrada.')
        guion.write_text(texto,encoding='utf8')
    texto=guion.read_text(encoding='utf8')
    antiguo=(W/guion.name).read_text(encoding='utf8')
    tiempos=re.findall(r'\| S\d:.*?\|.*?\| (.*?) \|',texto)
    assert tiempos==re.findall(r'\| S\d:.*?\|.*?\| (.*?) \|',antiguo)
    habla={}
    for i in range(1,9):
        cuerpo=re.search(rf'<!-- habla:S{i} -->(.*?)<!-- fin:S{i} -->',texto,re.S)[1].strip()
        habla[f'S{i}']=cuerpo
        viejo=re.search(rf'<!-- habla:S{i} -->(.*?)<!-- fin:S{i} -->',antiguo,re.S)[1]
        assert len(re.findall('▶ CLIC',cuerpo))==len(re.findall('▶ CLIC',viejo))
    datos=dict(tiempos=tiempos,habla=habla,responsables=['Benjamín']*3+['Luis']*2+['Matías']*3)
    (F/'presentacion/recursos/contenido_pre_entrega.json').write_text(json.dumps(datos,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    def palabras(t):
        t=re.sub(r'^>.*$','',t,flags=re.M)
        return len(re.findall(r'\S+',t))
    counts={f'S{i}':dict(antes=palabras(re.search(rf'<!-- habla:S{i} -->(.*?)<!-- fin:S{i} -->',antiguo,re.S)[1]),despues=palabras(habla[f'S{i}'])) for i in range(1,9)}
    (W/'conservacion_guion.json').write_text(json.dumps(dict(intervalos=tiempos,palabras=counts),ensure_ascii=False,indent=2),encoding='utf8')
    print('Conservados8intervalos y todos los clics. Palabras:',counts)


if __name__=='__main__':main()
