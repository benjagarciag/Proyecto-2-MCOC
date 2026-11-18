"""Redacta la comparación final a partir de matrices y auditorías terminadas."""
from pathlib import Path
import re
import comparar_circuitos as f


def main():
    leer=f.base.viento.leer
    ms={q:leer(f.SALIDA/f'q{q}/malla_0.4/matriz.json') for q in [60,55,50,45]}
    fina=leer(f.SALIDA/'q60/malla_0.2/matriz.json')
    audit=leer(f.SALIDA/'auditoria.json')
    if fina['riesgo']['P_union']>.05 or fina['picos_no_resueltos']:
        raise ValueError('La candidata fina no tiene cumplimiento confirmado: revisar recomendación antes de redactar.')
    esquema=leer(f.RAIZ/'resultados/diseno_circuitos_colocacion/esquema.json')
    texto='''# Comparación final homogénea — nueve circuitos

Se recomienda colocar todo el volumen en una operación continua a60 m³/h,
dos frentes coordinados,12 °C y11capas de hasta0,40 m, con nuestros nueve
circuitos y el control19/18 °C. La recomendación está condicionada al
modelo discreto de incertidumbre y a los recursos y controles idealizados
declarados; no acredita riesgo real ni diseño ejecutivo de las tuberías.

## 1. Familia recorrida y comparación

Se enumeraron60/55/50/45 m³/h, paso5 m³/h. Cada plan usa los mismos24
pares de ocho fuentes completas y tres bloques climáticos, pesos1/24,
t₀19-11-2026 10:00UTC−03, geometría, temperatura, suelo, viento horario,
protecciones, nueve ramales y potencia disponible. Solo cambia el ritmo
de colocación y los tiempos de activación/cobertura que determina.
Ambos frentes reciben la mitad del caudal total; no se duplica el recurso.
El solver activa cada capa completa al inicio de su intervalo físico;
no resuelve el movimiento de la banda de descarga. D sí conserva el
tiempo de colocar todo el volumen. Refinar la malla no elimina esta
aproximación de activación de las11capas.
Se suponen armaduras, tubos fijados, moldajes, suministro y equipos listos
en t₀ para los cuatro planes. No se calculó el montaje previo. Si esa
preparación retrasa la primera colocación, la espera se suma aD y la
cota deja de alcanzarse con el cronograma nominal.

La candidata es también la vertida única. No se inventan planes diferentes
para llenar nombres: la pauta admite esta coincidencia si se justifica la
cota de duración. Las alternativas mantienen una operación continua con
la misma partición física; no incluyen esperas de resistencia entre capas.

| Plan | D [h] | Tmax336 [°C] | ΔT336 [K] | Tmax extendido [°C] | ΔT extendido [K] | P_T / P_Δ / P_f extendido [%] |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
'''
    for q,m in ms.items():
        fs=m['corridas'];ries=m['riesgo']
        texto+=f"| {'Única/propuesta' if q==60 else 'Alternativa'} {q} m³/h | {m['D_h']:.4f} | "
        texto+=f"{max(x['base_336h']['Tmax']['valor'] for x in fs):.4f} | {max(x['base_336h']['DeltaTmax']['valor'] for x in fs):.4f} | "
        texto+=f"{max(x['Tmax']['valor'] for x in fs):.4f} | {max(x['DeltaTmax']['valor'] for x in fs):.4f} | "
        texto+=' / '.join(f'{100*ries[k]:.4f}' for k in ['P_T','P_delta','P_union'])+' |\n'
    texto+='''
Son cuatro matrices completas de24 escenarios a0,40 m/paso máximo300 s.
La extensión captura máximos tardíos; las métricas336 h se conservan
separadas. No se obtiene ventaja truncando en14 días. Para clasificar se
usan valores completos y unión lógica de excedencias, no cifras redondeadas.
La tabla y todas las filas están en
[comparacion_planes.csv](evidencia_circuitos/comparacion_planes.csv) y
[escenarios.csv](evidencia_circuitos/escenarios.csv).

![Duración y riesgo](evidencia_circuitos/figuras/04_duracion_riesgo.png)

## 2. Por qué10,613 h es el mínimo de la familia de recursos

Con V_IFC=636,7751927 m³ y caudal total disponible≤60 m³/h,
**D≥V_IFC/60=10,6129199 h**. Las esperas o postergar el inicio solo aumentanD.
La operación continua alcanza aproximadamente esa cota. D se refiere
al fin de colocación, no al fin de curado, apagado del
frío o autorización de carga. La disponibilidad del sistema se simula
hasta el horizonte extendido; no se calculó una fecha de liberación.
La integración
geométrica de capas difiere del volumen IFC en menos0,00004 m³, unos
milisegundos enD; se conserva esa tolerancia y no se interpreta como una
ganancia constructiva. Menos10,61 h requeriría cambiar el recurso máximo.

Por ejemplo75 m³/h daría una cota8,49 h, pero excede60 m³/h disponibles;
no es candidato admisible y no se afirma que falle térmicamente. Una
opción aún más lenta tampoco puede mejorar la cota temporal. Los caudales
menores45 quedan fuera de la vecindad recorrida, sin atribuirles resultados
térmicos no calculados. No se exige fabricar una falla de una opción rápida.

Las capas mayores tienen107,364 m³: los ciclos a60/55/50/45 son
107,36/117,12/128,84/143,15 min, respectivamente. Los cuatro están dentro
de la **condición de suministro de unión150 min** propuesta, si el patrón
de bandas mantiene ese retorno local. Es una condición a demostrar con
la mezcla, no una resistencia ni un tiempo de fraguado medido. Los
resultados no prueban consolidación ni ausencia de juntas frías.

![Cronogramas](evidencia_circuitos/figuras/03_cronogramas.png)

## 3. Confirmación numérica de la candidata

Se completó el catálogo de24 pares también a0,20 m/300 s, manteniendo
las11capas físicas y la zona refrigerable414,016 m³ por pertenencia a los
voxeles de referencia0,40 m. No se vuelve a erosionar una sola celda fina,
porque eso ampliaría artificialmente la zona refrigerada. El volumen del
dominio pasa de640,704 a638,944 m³ frente a636,775 m³ delIFC.

| Malla / paso máximo | Pares | Tmax extendido [°C] | ΔT extendido [K] | P_f extendido [%] |
| --- | ---: | ---: | ---: | ---: |
'''
    for m in [ms[60],fina]:
        texto+=f"| {m['lado_m']:.2f} m /300 s |24 | {max(x['Tmax']['valor'] for x in m['corridas']):.4f} | "
        texto+=f"{max(x['DeltaTmax']['valor'] for x in m['corridas']):.4f} | {100*m['riesgo']['P_union']:.4f} |\n"
    b={(r['curva'],r['clima']):r for r in ms[60]['corridas']}
    fi={(r['curva'],r['clima']):r for r in fina['corridas']}
    dT=max(abs(fi[k]['Tmax']['valor']-b[k]['Tmax']['valor']) for k in b)
    dD=max(abs(fi[k]['DeltaTmax']['valor']-b[k]['DeltaTmax']['valor']) for k in b)
    texto+=f'\nMayor cambio absoluto al emparejar escenarios: Tmax{dT:.4f} K yΔT{dD:.4f} K.\n'
    texto+='''El refino temporal separado0,40 m/150 s en tres pares decisivos
produjo cambios deΔT de hasta0,0038 K y conservó clasificación. Ver
[confirmación selectiva temporal](CONFIRMACION_CIRCUITOS.md). Dos mallas
permiten sensibilidad, no orden asintótico ni calibración física.

![Catálogo completo en ambas mallas](evidencia_circuitos/figuras/08_sensibilidad_espacial.png)

Las alternativas55/50/45 tienen refinos selectivos deM4_SS×2024 y×2025,
elegidos por máximo base y cambio espacial alto observado en la candidata.
No se presenta ese subconjunto como probabilidad fina completa. Sus
probabilidades de comparación son las matrices base comunes, con alcance
numérico declarado. El menorD recomendado depende de que la candidata
sea factible; una alternativa más lenta no puede superar su cota temporal.

| Alternativa | Par refinado | ΔT base [K] | ΔT fino [K] | Cambio [K] |
| --- | --- | ---: | ---: | ---: |
'''
    for r in audit['refinos_alternativas']:
        q=int(r['plan'][1:]);anterior=next(x for x in ms[q]['corridas'] if x['curva']=='M4_SS' and x['clima']==r['clima'])
        valor=anterior['DeltaTmax']['valor']
        texto+=f"| {q} m³/h | M4_SS × {r['clima']} | {valor:.4f} | {r['DeltaTmax_K']:.4f} | {r['DeltaTmax_K']-valor:+.4f} |\n"
    texto+='''
Estos contrastes permiten comprobar cambios de caso dominante; no se
mezclan sus resultados con filas gruesas para inventar una matriz fina
homogénea de las alternativas.

## 4. Mecanismo térmico y desviaciones

La diferencia relevante es Tmax del hormigón colocado menos Tmin,S25
**al mismo instante**, maximizada después en el tiempo. No se resta el
máximo global de una hora del mínimo de otra. El calentamiento por
hidratación y la disipación son diferentes en núcleo y contorno. Tras
retirar protección, un episodio frío puede reducirS25 más rápido que el
interior. Por eso el máximo diferencial aparece mucho después del pico
absoluto de temperatura y también después del día14.

| Caudal [m³/h] | Hora del peorΔT [h] | T caliente simultánea [°C] | Tmin,S25 [°C] | ΔT [K] | Par |
| --- | ---: | ---: | ---: | ---: | --- |
'''
    for q,m in ms.items():
        x=max(m['corridas'],key=lambda r:r['DeltaTmax']['valor']);ev=x['DeltaTmax']
        texto+=f"| {q} | {ev['tiempo_h']:.3f} | {ev['Tmax_C']:.4f} | {ev['Tmin_S25_C']:.4f} | {ev['valor']:.4f} | {x['curva']} × {x['clima']} |\n"
    texto+='''
Al variar el ritmo se desplazan edades, activación, cobertura y retiros
respecto del mismo clima. Por eso no se presupone monotonicidad. En esta
familia, bajar60→45 agrega aproximadamente3,54 h sin mejorar el máximo
del catálogo; las diferencias de ese máximo son pequeñas frente a la
sensibilidad espacial observada. La decisión temporal no se basa en una
supuesta mejora térmica significativa de unas centésimas de grado.

![Curvas por cada escenario](evidencia_circuitos/figuras/05_curvas_por_escenario.png)

![Historias comparables](evidencia_circuitos/figuras/06_historias_comunes.png)

Las curvas usan el mismoM4_SS×ERA5-2024 y escala temporal. La sonda interior
puntual no se confunde conTmax global. Los cortes siguientes muestran
temperaturas de centros a428 h, con el mismo escenario, planos y escala;
S25 se reconstruye aparte en las caras exteriores. No son cortes históricos
de12 kW ni de otra regla de refrigeración.

![Cortes de la configuración actual](evidencia_circuitos/figuras/07_cortes_comunes.png)

## 5. Probabilidad, sensibilidad y conclusión defendible

Los24 pares son una enumeración del modelo discreto: curva completa con
peso1/8, clima completo con peso1/3 e independencia supuesta. La curva se
comparte entre todas las capas de cada realización. Una corrida que excede
ambos límites cuenta una sola vez. Se reportan ambas marginales y unión.
Las reponderaciones duplicando cada año y reteniendo soloSS se recalculan
en [sensibilidad_pesos.csv](evidencia_circuitos/sensibilidad_pesos.csv).
Con cero excedencias, reponderar el mismo catálogo conserva cero: no
representa climas omitidos, fallas de obra ni incertidumbre deU.

La recomendación se limita al escenario docente con suministro12 °C,
60 m³/h y enfriamiento ideal18 °C/U5/tope15 kW. El caudal de agua no
calibraU ni prueba15 kW reales; no se resolvieron transferencia de pared,
agua axial, pérdidas de carga, trabajabilidad o resistencia estructural.
El control y la instrumentación están en
[cierre de Benjamín](CIERRE_BENJAMIN.md). El cumplimiento térmico no
demuestra ausencia de fisuración mediante análisis mecánico.

**Texto para la decisión:** «Recomendamos una operación continua a60 m³/h,
en11capas y a12 °C, con nueve circuitos idealizados y control por temperatura.
Es la más rápida entre los planes evaluados y alcanza la cota volumen/caudal
del recurso adoptado. El riesgo conjunto informado corresponde al catálogo
discreto y al modelo, no a una garantía de obra. Cambios de suministro,
clima o refrigeración requieren actualizar la predicción».

## 6. Integración y evidencia utilizable en la presentación

Los fundamentos de fuentes/clima/probabilidad deMatías y las verificaciones
y explicaciones del método deLuis se integran con procedencia en
[INTEGRACION_EQUIPO_CIRCUITOS.md](INTEGRACION_EQUIPO_CIRCUITOS.md).
Las tablas de otras configuraciones se conservan como antecedentes y
no se usan como resultados de esta familia. Las ocho fuentes y los tres
climas se verificaron numéricamente contra los mismos insumos.

![Fuentes originales](evidencia_circuitos/figuras/01_fuentes.png)

![Clima y convección](evidencia_circuitos/figuras/02_clima.png)

Para exponer: decisión y tabla; datos/fuentes; modelo y bordes; método y
verificación; ejemplo de una fila probabilística; duración–riesgo;
mecanismo mediante curvas/cortes; límites y contingencias. La explicación
del balance explícito y las reglas de operación están en los documentos
de cierre y simulación, no ocultas detrás de una figura.
El [modelo y balance implementado](MODELO_NUEVE_CIRCUITOS.md) reúne
ecuaciones, bordes, fuente por edad, extracción, estabilidad yS25 para
conectar los aportes del equipo con esta configuración.
'''
    texto+=f"\nAuditoría de{len(audit['matrices'])} matrices completas y{audit['transiciones_auditadas']} transiciones aprobada.\n"
    texto+='''Se comprobaron insumos comunes, pares/pesos, métricas simultáneas,
balance, topes, cobertura, histéresis y probabilidades por cálculo
independiente. Las matrices conservan las huellas de sus24 archivos.

**Fuera de esta tarea:** PDF final, respaldo final sin internet, publicación
del commit/SHA de defensa y ensayo. No se declaran terminados ni se
confunden los commits de aportes consultados con unSHA final.
'''
    texto=re.sub(r'\b(a|de|en|con|hasta|desde|son|por|paso|peso|pesos|mismos|máximo|menos|enumeraron|alternativas)(?=\d)',r'\1 ',texto)
    texto=re.sub(r'(?<=\d)(?=capas\b|pares\b|matrices\b|transiciones\b)', ' ',texto)
    texto=texto.replace('t₀19','t₀ 19').replace('10:00UTC','10:00 UTC').replace('deMatías','de Matías').replace('deLuis','de Luis')
    (f.RAIZ/'entregas/F02/COMPARACION_CIRCUITOS_FINAL.md').write_text(texto,encoding='utf-8')
    print('Comparación final redactada. P_f fina candidata:',fina['riesgo']['P_union'])


if __name__=='__main__':main()
