"""Exporta resultados Python reutilizando la interfaz y el renderizador E07/E08."""
import base64
from dataclasses import asdict
from html import escape
from itertools import groupby
import json

import numpy as np

from .superficies_voxel import clasificar_caras, diagnosticar_contactos
from .vertidas_voxel import comparar_volumenes


def _float32(valores):
    return base64.b64encode(np.asarray(valores, dtype="<f4").tobytes()).decode("ascii")


def _panel(titulo, contenido):
    return ('<div class="panel"><div class="panel-head"><h2>' + escape(titulo)
            + '</h2></div><div class="panel-content">' + contenido + '</div></div>')


def _reemplazar(texto, anterior, nuevo):
    if texto.count(anterior) != 1:
        raise ValueError("Revisar la plantilla del visualizador en " + anterior[:65])
    return texto.replace(anterior, nuevo)


def exportar_html(raiz, fundacion, asignacion, corrida, fotogramas, resumen, salida):
    """Publica la misma corrida, sin ejecutar nuevamente la física."""
    if not fotogramas:
        raise ValueError("Se requieren campos temporales para el HTML.")
    ids = asignacion.vertida_id
    ocupados = np.flatnonzero(ids)
    tiempos = [float(t) for t, _ in fotogramas]
    if tiempos[0] != 0 or tiempos[-1] != resumen["horizonte_h"] or any(
            b <= a for a, b in zip(tiempos, tiempos[1:])):
        raise ValueError("La secuencia debe cubrir el horizonte en orden estricto.")
    if any(np.asarray(t).shape != (len(ocupados),) for _, t in fotogramas):
        raise ValueError("El campo térmico no corresponde a la grilla.")
    grilla = asignacion.voxelizacion.grilla
    superficies = clasificar_caras(asignacion)
    contactos = json.loads((raiz / "casos/e07/superficies.json").read_text(
        encoding="utf-8-sig"))["contactos_ifc_esperados"]
    h = resumen["lado_m"]
    fuente = resumen["parametros_efectivos"]["hidratacion"]
    q0 = fuente.get("q0_W_m3")
    if q0 is None:
        q0 = (fuente["theta_infinito_K"] * fuente["densidad_kg_m3"]
              * fuente["calor_especifico_J_kgK"] / fuente["tau_s"])
    especiales = {}
    for nombre, campo in corrida.campos.items():
        temperatura = campo.temperatura_C.ravel()[ocupados]
        s25 = campo.s25_min_C.ravel()[ocupados]
        metricas = resumen["Tmax"] if nombre == "pico" else resumen["DeltaTmax"]
        especiales[nombre] = dict(
            time=campo.tiempo_s/3600, phase=campo.fase,
            values=_float32(temperatura), s25=_float32(s25),
            metrics=dict(Tmax_C=metricas["Tmax_C"] if nombre != "final"
                         else corrida.historia[-1]["Tmax_C"],
                         Tmin_S25_C=float(np.nanmin(s25))))
    datos = dict(
        fecha=resumen["ejecutado_utc"], commit=resumen["codigo_commit"],
        sha256_ifc=fundacion.sha256_ifc, volumen_ifc=fundacion.volumen_total_mallas_m3,
        bbox=[fundacion.bbox_min_m.tolist(), fundacion.bbox_max_m.tolist()],
        contactos_esperados=contactos,
        vertidas=[dict(id=v.vertida_id, nombre=v.nombre, material=v.tipo_hormigon,
                       inicio=v.inicio_h, temperatura=v.temperatura_colocacion_C,
                       vertices=v.vertices_m.tolist(), triangulos=v.triangulos.tolist())
                  for v in fundacion.vertidas],
        grillas=[dict(
            h=h, forma=list(ids.shape), origen=grilla.origen_m.tolist(),
            rle=[[int(v), sum(1 for _ in grupo)] for v, grupo in groupby(ids.ravel())],
            ocupados=len(ocupados), volumen=len(ocupados)*h**3,
            filas=[asdict(f) for f in comparar_volumenes(fundacion, asignacion)],
            diagnostico=asdict(diagnosticar_contactos(superficies, [1, 2, 3, 4, 5], contactos)))],
        resultado_python=dict(
            resumen=resumen, historia=corrida.historia, entorno=resumen["parametros_efectivos"]["entorno"],
            numero_voxeles=len(ocupados), tiempos_h=tiempos,
            temperaturas=_float32(np.stack([t for _, t in fotogramas])),
            especiales=especiales, minimo=corrida.minimo, picos_vertidas=corrida.picos_vertidas,
            fuente=dict(q0_W_m3=q0, tau_h=fuente["tau_s"]/3600)))
    datos["grilla_inicial"] = 0
    datos["resultados_python"] = [datos["resultado_python"]]
    datos["resultado_python"] = dict(resumen=resumen)
    _escribir_html(raiz, datos, salida)


def _escribir_html(raiz, datos, salida):
    resumen = datos["resultado_python"]["resumen"]
    for resultado in datos["resultados_python"]:
        if resultado is not None:
            resultado["paneles"] = dict(
                heat=_seccion_resultados(resultado["resumen"]),
                study=_seccion_modelo(resultado["resumen"]))
    plantilla = (raiz / "Visualizadores/e07_plantilla.html").read_text(encoding="utf-8")
    adaptador = (raiz / "Visualizadores/semana4_resultados.js").read_text(encoding="utf-8-sig")
    contenido = _adaptar_plantilla(plantilla, adaptador, resumen, datos["grillas"])
    estilos = (raiz / "Visualizadores/semana4_estilos.css").read_text(encoding="utf-8-sig")
    contenido = contenido.replace("</style>", estilos + "\n</style>")
    serializado = json.dumps(datos, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    contenido = _reemplazar(contenido, "__DATOS_E07__", serializado.replace("</", "<\\/"))
    salida.parent.mkdir(parents=True, exist_ok=True)
    temporal = salida.with_suffix(".html.tmp")
    temporal.write_text(contenido, encoding="utf-8")
    temporal.replace(salida)


def _adaptar_plantilla(t, adaptador, resumen, grillas):
    caso = resumen["caso"].upper()
    t = t.replace("E08 · Laboratorio de vertidas", caso + " · Fundación térmica")
    t = t.replace("MCOC · Grupo 6 · E08", "MCOC · Grupo 6 · Semana 4")
    t = t.replace("<h1>Laboratorio de vertidas</h1>", "<h1>Fundación térmica</h1>")
    t = t.replace("Del IFC real a los voxeles, la construcción y la ecuación de calor.",
                  "Resultados de Python · " + caso + " · " + str(resumen["horizonte_h"]) + " horas")
    inicio = t.index('<div id="resolutions"')
    fin = t.index('</div>', inicio)+6
    botones = ''.join(
        '<button data-grid="' + str(i) + '">' + str(g["h"]).replace(".", ",")
        + ' m</button>' for i, g in enumerate(grillas))
    t = t[:inicio] + '<div id="resolutions" class="seg">' + botones + '</div>' + t[fin:]
    for anterior, nuevo in {
        "Resolución del voxel":"Resolución del voxel",
        'data-tab="heat">Ecuación de calor':'data-tab="heat">Resultados y entorno',
        'data-tab="study">Repaso E07':'data-tab="study">Modelo y supuestos',
        "Mínima alcanzada · corrida":"Diferencial máximo · corrida",
        "T mínima · instante actual":"T mínima S25 · instante actual",
        "Configurar y calcular":"Ver resultados y condiciones",
        "Temperaturas de un ensayo didáctico.":"Corrida calculada en Python.",
        "Tmax actual [°C]":"Tmax centros actual [°C]",
        'id="ifc" checked':'id="ifc"',
        'id="edges" checked':'id="edges"',
        'grid:1,selected:0,time:24,temporal:false':'grid:DATA.grilla_inicial,selected:0,time:0,temporal:true',
        "function setTime(t){state.time=t;":"function setTime(t){state.pythonSpecial=null;state.time=t;",
        "Math.min(336,elapsed":"Math.min(DATA.resultado_python.resumen.horizonte_h,elapsed",
        "state.time>=336":"state.time>=DATA.resultado_python.resumen.horizonte_h",
        "if(t>=336){setTime(336);":"if(t>=DATA.resultado_python.resumen.horizonte_h){setTime(DATA.resultado_python.resumen.horizonte_h);",
        "[0,...DATA.vertidas.map(v=>v.inicio),72,336]":"[0,...DATA.vertidas.map(v=>v.inicio),DATA.resultado_python.resumen.horizonte_h]",
        "['source','temperature'].includes":"['source','temperature','bc'].includes",
        "__MOTOR_TERMICO__":"",
        "Error global al refinar":"Error global por resolución",
        "Comparación de resoluciones":"Resoluciones disponibles",
    }.items():
        t = t.replace(anterior, nuevo)
    t = t.replace("Incluye centros y caras exteriores físicas. El valor actual sigue el tiempo de reproducción y puede ser interpolado. El máximo de la corrida se evalúa en cada paso calculado; el tiempo se mide desde t = 0 y la edad desde la colocación de esa vertida.",
                  "La columna actual usa centros de los campos guardados e interpolación visual. El máximo por vertida proviene de cada paso de Python e incluye caras.")
    t = t.replace('<div class="hint">Arrastra para girar',
                  '<label class="check"><input type="checkbox" id="probeMarkers" checked> Marcar sonda interior y S25 del máximo diferencial</label><div class="hint">Arrastra para girar')
    t = t.replace("Horarios y temperaturas de colocación leídos del IFC. La reproducción llega hasta 336 h. Después de 30 h avanza 10 veces más rápido: de 1,8 a 18 h por segundo.",
                  "La reproducción recorre los campos guardados en Python y se acelera después de las primeras 30 horas.")
    t = t.replace(
        "function activeIds(g,t,temporal){return temporal?",
        "function activeIds(g,t,temporal){if(state.pythonSpecial&&state.thermal.specials[state.pythonSpecial].phase==='previo')t-=1e-9;return temporal?")
    t = t.replace(
        '<button class="active" data-tab="geometry">Modelo y cortes</button>',
        '<a class="active" href="#geometry" data-tab="geometry">Modelo y cortes</a>')
    import re
    t = re.sub(r'<button data-tab="([^"]+)">([^<]+)</button>',
               r'<a href="#\1" data-tab="\1">\2</a>', t)
    t = t.replace(".tabs button", ".tabs :is(button,a)")
    t = t.replace("</style>", """
.tabs{position:sticky;top:0;z-index:5;background:var(--paper)}
.tabs a{text-decoration:none}
.tab-panel{scroll-margin-top:60px}
.tab-panel:target{display:block!important}
body:has(.tab-panel:target) #geometry:not(:target){display:none}
body:has(.tab-panel:target:not(#geometry)) #overviewPython{display:none}
</style>""")
    inicio = t.index('<div class="stats"><div class="stat"><div class="stat-label">Volumen voxelizado')
    fin = t.index('<section id="geometry"', inicio)
    t = t[:inicio] + '<div id="overviewPython">' + t[inicio:fin] + '</div>' + t[fin:]
    t = t.replace(
        "document.querySelectorAll('[data-tab]').forEach(b=>b.onclick=()=>setTab(b.dataset.tab));",
        "document.querySelectorAll('[data-tab]').forEach(b=>b.onclick=e=>{e.preventDefault();setTab(b.dataset.tab);});")
    t = t.replace(
        "function setTab(name){state.tab=name;",
        "function setTab(name){state.tab=name;if(window.location)window.location.hash=name;$('overviewPython').hidden=name!=='geometry';")
    t = t.replace(
        "if(name==='heat')drawThermalCharts();}",
        "if(name==='heat')drawThermalCharts();}")
    t = t.replace("l+i*78", "l+i*(w-l-r)/series.length")
    inicio_grafico = t.index("function chart(")
    fin_grafico = t.index("let thermalWorker=null", inicio_grafico)
    t = t[:inicio_grafico] + t[fin_grafico:]
    inicio = t.index("let thermalWorker=null")
    fin = t.index("// Renderizador WebGL", inicio)
    t = t[:inicio] + adaptador + "\n" + t[fin:]
    t = t.replace("rgb(BOUNDARY_COLORS[state.settings.bc[axis*2+(sign>0?1:0)].type])",
                  "rgb(boundaryColorPython(axis,sign,z,id))")
    t = t.replace("ctx.strokeStyle=BOUNDARY_COLORS[state.settings.bc[axis*2+(sign>0?1:0)].type]",
                  "ctx.strokeStyle=boundaryColorPython(axis,sign,p[2],at(g,...p,active))")
    t = t.replace("Tipos de borde: azul Dirichlet · ocre Neumann · violeta Robin. Las caras de un corte visual no son bordes físicos.",
                  "Violeta = aire sin capas · verde = aire con capas · café = suelo. Los cortes son visuales.")
    t = t.replace("Primero configura y ejecuta el cálculo en Ecuación de calor.", "Temperaturas calculadas en Python.")
    t = t.replace("Colores de centros; las caras Dirichlet se incluyen en los extremos.",
                  "Colores de centros. Sonda interior roja; S25 azul al seleccionar el diferencial.")
    inicio = t.index("if(terms)$('inspect').textContent+=")
    fin = t.index(";};", inicio)+1
    t = t[:inicio] + ("if(terms)$('inspect').textContent+=' · T centro '+fmt(terms.T,3)+' °C'"
                     "+(Number.isFinite(terms.s25)?' · S25 mínima de celda '+fmt(terms.s25,3)+' °C':'');") + t[fin:]
    t = t.replace("xmax:2,ylabel:'Error [%]',xticks:[[0,'1 m'],[1,'0,5 m'],[2,'0,25 m']]",
                  "xmax:Math.max(1,DATA.grillas.length-1),ylabel:'Error [%]',xticks:DATA.grillas.map((g,i)=>[i,fmt(g.h,2)+' m'])")
    t = t.replace("Ninguna de estas tres grillas está validada para el cálculo térmico definitivo.",
                  "La precisión espacial requiere verificación por vertida.")
    marcadores = """
 if($('probeMarkers').checked&&state.thermal){
   const probes=[{xyz:SUMMARY.nucleo_xyz_m,color:[.9,.1,.1]}];
   if(state.pythonSpecial==='diferencial')probes.push({xyz:SUMMARY.DeltaTmax.xyz_S25_m,color:[.1,.25,.95]});
   for(const probe of probes){
     const cell=probe.xyz.map((v,a)=>Math.floor((v-g.origen[a])/g.h));
     if(!at(g,...cell,active))continue;
     if(state.clip!=='none'&&cell[+state.clip]>state.clipIndex)continue;
     push(points,probe.xyz,probe.color);
   }
 }
 """
    t = _reemplazar(t, " upload('tri',tri);", marcadores + "\n upload('tri',tri);")
    t = t.replace(
        "Modelo completo · V = N × Δx × Δy × Δz · error = |V − V<sub>IFC</sub>| / V<sub>IFC</sub> × 100.",
        "Volumen por conteo de voxeles y comparación con la geometría IFC.")
    t = t.replace(
        '<div class="formula" style="margin-top:15px">activo = ocupado ∧ t ≥ inicio<br>edad = t − inicio<br>T<sub>nuevo</sub> = T<sub>colocación</sub></div>',
        _ecuacion("Activación y temperatura de colocación",
            '<mtable rowspacing="0.6em"><mtr><mtd><msub><mtext>activo</mtext><mi>i</mi></msub><mo>=</mo>'
            '<msub><mtext>ocupado</mtext><mi>i</mi></msub><mo>∧</mo><mi>t</mi><mo>≥</mo><msub><mi>t</mi><mi>i</mi></msub></mtd></mtr>'
            '<mtr><mtd><msub><mi>a</mi><mi>i</mi></msub><mo>=</mo><mi>t</mi><mo>−</mo><msub><mi>t</mi><mi>i</mi></msub></mtd></mtr>'
            '<mtr><mtd><msub><mi>T</mi><mi>i</mi></msub><mo>(</mo><msub><mi>t</mi><mi>i</mi></msub><mo>)</mo><mo>=</mo>'
            '<msub><mi>T</mi><mrow><mtext>col</mtext><mo>,</mo><mi>i</mi></mrow></msub></mtd></mtr></mtable>'))
    t = t.replace(
        '<div class="panel-content" id="globalChart"></div>',
        '<div class="panel-content"><p class="chart-description">Compara el volumen voxelizado total con el IFC.<br>Muestra el efecto del tamaño del voxel.</p><div id="globalChart"></div></div>')
    t = t.replace(
        '<div class="panel-content" id="localChart"></div>',
        '<div class="panel-content"><p class="chart-description">Muestra el error de volumen de cada vertida.<br>Un error global pequeño puede ocultar errores locales.</p><div id="localChart"></div></div>')
    t = t.replace(
        '<div class="table-scroll"><table><thead><tr><th>Vertida</th><th>Voxeles</th>',
        _ecuacion("Volumen y error relativo",
            '<msub><mi>V</mi><mtext>vox</mtext></msub><mo>=</mo><mi>N</mi><mi>Δx</mi><mi>Δy</mi><mi>Δz</mi><mo>,</mo><mspace width="1em"/>'
            '<msub><mi>ε</mi><mi>V</mi></msub><mo>=</mo><mfrac><mrow><mo>|</mo><msub><mi>V</mi><mtext>vox</mtext></msub><mo>−</mo>'
            '<msub><mi>V</mi><mtext>IFC</mtext></msub><mo>|</mo></mrow><msub><mi>V</mi><mtext>IFC</mtext></msub></mfrac><mo>×</mo><mn>100</mn><mo>%</mo>')
        + '<div class="table-scroll"><table><thead><tr><th>Vertida</th><th>Voxeles</th>')
    inicio = t.index('<section id="build"')
    contenido = t.index('<div class="panel"><div class="panel-head"><div><h2>Una vertida nueva', inicio)
    t = t[:inicio] + ('<section id="build" class="tab-panel" hidden>'
                     + _panel("Plan de la corrida", "<p>Inicios y temperaturas leídos del IFC y utilizados por Python. Para cambiar el plan se requiere ejecutar otra corrida.</p>")) + t[contenido:]
    for identificador, seccion in [
            ("heat", _seccion_resultados(resumen)),
            ("study", _seccion_modelo(resumen))]:
        inicio = t.index('<section id="' + identificador + '"')
        fin = t.index('</section>', inicio)+10
        t = t[:inicio] + seccion + t[fin:]
    inicio = t.index("const QUESTIONS=[")
    fin = t.index("installThermalControls();installSequenceControls();", inicio)
    fin = t.index("\n", fin)
    t = t[:inicio] + "initializePythonResult();\n" + t[fin:]
    t = t.replace("E07 · Geometría IFC y laboratorio térmico didáctico · Propiedades y bordes editables, sin calibración experimental.",
                  "Semana 4 · Resultados Python · Parámetros docentes y escenario provisional.")
    return t


def _ficha(filas):
    return '<dl class="run-facts">' + ''.join(
        '<dt>' + escape(nombre) + '</dt><dd>' + valor + '</dd>'
        for nombre, valor in filas) + '</dl>'


def _tabla(cabeceras, filas):
    return ('<div class="table-scroll"><table class="readable-table"><thead><tr>'
            + ''.join('<th>' + nombre + '</th>' for nombre in cabeceras)
            + '</tr></thead><tbody>'
            + ''.join('<tr>' + ''.join('<td>' + celda + '</td>' for celda in fila) + '</tr>'
                      for fila in filas)
            + '</tbody></table></div>')


def _numero(valor, decimales=None):
    return (f"{valor:g}" if decimales is None else f"{valor:.{decimales}f}").replace(".", ",")


def _fecha(texto):
    from datetime import datetime
    from zoneinfo import ZoneInfo
    return datetime.fromisoformat(texto).astimezone(
        ZoneInfo("America/Santiago")).strftime("%d/%m/%Y a las %H:%M")


def _periodo(inicio, horas):
    from datetime import datetime, timedelta
    fin = datetime.fromisoformat(inicio) + timedelta(hours=horas)
    return _fecha(inicio) + '<br>hasta ' + _fecha(fin.isoformat())


def _ecuacion(nombre, contenido):
    return ('<figure class="math-block"><figcaption>' + escape(nombre)
            + '</figcaption><math xmlns="http://www.w3.org/1998/Math/MathML" display="block" aria-label="'
            + escape(nombre, quote=True) + '"><mrow>' + contenido + '</mrow></math></figure>')


def _seccion_resultados(resumen):
    e, c = resumen["parametros_efectivos"]["entorno"], resumen["clima"]
    historico = c["tipo"] == "reanalisis"
    metadatos = _ficha([
        ("Tipo de datos", "Reanálisis histórico" if historico else "Pronóstico meteorológico"),
        ("Proveedor y modelo", escape(c["fuente"]) + ' · ' + escape(c["modelo_solicitado"]).upper()),
        ("Lugar", "Parque Eólico El Rosal, Los Ángeles<br>Latitud −37,277929 · longitud −72,368271"),
        ("Descarga del archivo", _fecha(c["descargado_utc"])),
        ("Datos meteorológicos usados", _periodo(resumen["inicio_serie"], resumen["horizonte_h"])),
        ("Calendario de la simulación", _periodo(resumen["inicio_escenario"], resumen["horizonte_h"])
         + ("<br><small>Fecha hipotética del escenario</small>" if historico else "")),
        ("Variable que entra al cálculo", "Temperatura del aire a 2 m, con datos horarios e interpolación lineal"),
        ("Variables archivadas", "Viento a 10 m y radiación solar")
    ])
    metadatos += '<p class="bottom-note">Todos los horarios se muestran en hora de Chile continental.</p>'
    metadatos += ('<p class="hint">Se asignó un bloque de ERA5 de '
                  + resumen["inicio_serie"][:4] + ' por hora relativa al escenario de '
                  + resumen["inicio_escenario"][:4] + '. Este escenario histórico aporta las '
                  + _numero(resumen["horizonte_h"]) + ' horas de la corrida.</p>'
                  if historico else
                  '<p class="hint">El pronóstico archivado cubre las '
                  + _numero(resumen["horizonte_h"]) + ' horas de esta demostración.</p>')
    metadatos += '<p id="pythonAirNow" class="bottom-note"></p>'
    bordes = _tabla(
        ["Región", "Tipo de condición", "Cómo se aplica"],
        [
            ["Laterales expuestos", "Robin con resistencias en serie",
             "Intercambio con el aire horario a través del moldaje y la aislación presentes."],
            ["Horizontales expuestos", "Robin convectiva",
             "Intercambio con el aire horario."],
            ["Base de la fundación", "Robin conductiva equivalente",
             "Resistencia de suelo hacia un reservorio a " + _numero(e["suelo_C"]) + " °C."],
            ["Entre voxeles activos", "Continuidad térmica",
             "Conducción interna conservativa con contacto térmico perfecto."]
        ])
    bordes += _ficha([
        ("Coeficiente convectivo", _numero(e["h_aire_W_m2K"]) + " W/(m²·K)"),
        ("Plano de contacto con el suelo", _numero(e["plano_suelo_z_m"]) + " m de altura"),
        ("Distancia efectiva en el suelo", _numero(e["profundidad_suelo_m"]) + " m"),
        ("Conductividad del suelo", _numero(e["k_suelo_W_mK"]) + " W/(m·K)")
    ])
    bordes += '<button id="showBoundaries" style="margin-top:14px">Colorear condiciones en 3D</button>'
    capas = e["capas_laterales"]
    nombres = [("Moldaje" if i == 0 else "Aislación" if i == 1 else "Capa " + str(i+1))
               for i in range(len(capas))]
    detalle = _tabla(
        ["Capa", "Espesor", "Conductividad", "Retiro desde su colocación"],
        [[nombre, _numero(c["espesor_m"]*1000) + " mm",
          _numero(c["k_W_mK"]) + " W/(m·K)",
          _numero(c["retiro_edad_h"]) + " h" if c["retiro_edad_h"] is not None else "Sin retiro"]
         for nombre, c in zip(nombres, capas)])
    estado = ('<p class="panel-intro">Indica qué capas siguen presentes en cada vertida y su resistencia térmica activa.<br>'
              'Al alcanzar la edad de retiro, la resistencia de esa capa pasa a cero.</p>')
    tabla = ('<div class="table-scroll"><table><thead><tr><th>Vertida</th><th>Edad [h]</th>'
             + ''.join('<th>' + nombre + '</th>' for nombre in nombres)
             + '</tr></thead><tbody id="layerRows"></tbody></table></div>')
    acciones = (
        '<div class="inline"><button class="primary" id="peakPython">Ver máximo térmico</button>'
        '<button id="deltaPython">Ver máximo diferencial</button><button id="finalPython">Ver estado final</button></div>'
        '<p id="pythonFrame" class="bottom-note"></p>')
    def xyz(valores):
        return "(" + "; ".join(_numero(v, 3) for v in valores) + ") m"
    pico, delta = resumen["Tmax"], resumen["DeltaTmax"]
    extremos = (
        '<p class="panel-intro">Localiza los estados más exigentes de toda la corrida para evaluar los límites térmicos.<br>'
        'La hora y posición permiten abrir esos estados y comparar distintas alternativas de construcción.</p>')
    extremos += _tabla(
        ["Extremo", "Valor", "Hora desde el inicio", "Ubicación"],
        [
            ["Temperatura máxima", _numero(pico["valor"],2) + " °C",
             _numero(pico["tiempo_h"]) + " h",
             "V0" + str(pico["vertida_Tmax"]) + " · " + xyz(pico["xyz_Tmax_m"])],
            ["Diferencial máximo", _numero(delta["valor"],2) + " K",
             _numero(delta["tiempo_h"]) + " h",
             "Punto caliente " + xyz(delta["xyz_Tmax_m"]) + "<br>Punto S25 " + xyz(delta["xyz_S25_m"])]
        ])
    extremos += ('<p class="bottom-note">Sonda interior roja ' + xyz(resumen["nucleo_xyz_m"])
                 + '. La marca azul identifica S25 al abrir el máximo diferencial.</p>'
                 '<p class="hint">Temperatura máxima '
                 + ('dentro del límite de 70 °C' if resumen["cumple_70_ensayo"] else 'sobre el límite de 70 °C')
                 + '. Diferencial '
                 + ('dentro del límite de 20 K' if resumen["cumple_20_ensayo"] else 'sobre el límite de 20 K')
                 + ' en este escenario.</p>')
    proposito = (
        '<span class="case-badge">' + escape(resumen["caso"].upper()) + '</span>'
        + ('<p>Evaluación determinista de 14 días para diagnosticar si el plan satisface los criterios de temperatura máxima y diferencial. '
           'La entrega incluye un Markdown de hasta 1400 palabras.</p>'
           if resumen["caso"] == "e12" else
           '<p>Demostración corta para comprobar que los datos meteorológicos alimentan los bordes y que los resultados se pueden inspeccionar en 3D. '
           'La entrega declara repositorio y commit.</p>'))
    s = '<section id="heat" class="tab-panel" hidden>' + _panel("Objetivo de esta corrida", proposito)
    s += _panel("Explorar los resultados", acciones) + _panel("Extremos de la corrida", extremos)
    s += '<div class="two equal">' + _panel("Clima utilizado", metadatos) + _panel("Condiciones de borde", bordes) + '</div>'
    s += _panel("Moldaje y aislación por edad", estado + detalle + tabla)
    for titulo, identificador, explicacion in [
        ("Temperaturas de la fundación", "temperatureChart",
         "Compara el máximo de la fundación, la sonda interior y el mínimo a 25 mm de la superficie.<br>Permite observar la separación térmica entre el interior y las zonas exteriores.<br>La línea verde (sonda interior) comienza a las 12 h porque ese punto pertenece a la Vertida_03, colocada en ese instante a 18 °C. Antes de su colocación, la celda no está activa y no se le asigna temperatura. Las horas se cuentan desde la primera vertida: a las 12 h globales, la Vertida_03 tiene edad cero."),
        ("Temperatura del entorno", "observerChart",
         "Muestra el aire horario que alimenta el modelo y la temperatura fija adoptada para el suelo.<br>Ayuda a relacionar el calentamiento y enfriamiento con el entorno."),
        ("Diferencial térmico", "deltaChart",
         "Resta al máximo de la fundación el mínimo de S25 en cada instante.<br>La línea de 20 K permite localizar los períodos que superan el criterio del curso."),
        ("Generación de calor en la sonda interior", "sourceChart",
         "Muestra la fuente volumétrica de hidratación en la posición de la sonda.<br>La opción cosenoidal permite comparar su forma con el pulso del ejercicio anterior."),
        ("Cambio de temperatura de la sonda", "rateChart",
         "Separa los aportes de conducción, bordes e hidratación al cambio de temperatura.<br>Los valores positivos calientan la sonda y los negativos la enfrían."),
        ("Potencias térmicas de la fundación", "powerChart",
         "Muestra la generación total por hidratación y el intercambio con aire y suelo.<br>La potencia positiva entra al hormigón; la negativa representa pérdida de calor.")
    ]:
        opciones = ('<label class="check"><input type="checkbox" id="cosineReference">'
                    ' Comparar con pulso cosenoidal de referencia · duración 12 h y pico igual a la fuente inicial</label>'
                    if identificador == "sourceChart" else "")
        s += _panel(titulo, '<p class="chart-description">' + explicacion + '</p>'
                    + opciones + '<div id="' + identificador + '" class="chart-frame"></div>')
    return s + _panel("Balance de energía", '<div id="thermalBalance"></div>') + '</section>'


def _seccion_modelo(resumen):
    fuente = resumen["parametros_efectivos"]["hidratacion"]
    e = resumen["parametros_efectivos"]["entorno"]
    q0 = fuente.get("q0_W_m3")
    if q0 is None:
        q0 = (fuente["theta_infinito_K"] * fuente["densidad_kg_m3"]
              * fuente["calor_especifico_J_kgK"] / fuente["tau_s"])
    ecuaciones = '<p class="panel-intro">El solver aplica conservación de energía a cada voxel activo y actualiza su temperatura con Euler explícito.<br>Las potencias de borde son positivas cuando entra calor al hormigón.</p>'
    ecuaciones += _ecuacion("Balance de energía de un voxel",
        '<mi>ρ</mi><msub><mi>c</mi><mi>p</mi></msub><mi>V</mi><mi>Δ</mi><msub><mi>T</mi><mi>i</mi></msub>'
        '<mo>=</mo><msub><mi>E</mi><mrow><mtext>hid</mtext><mo>,</mo><mi>i</mi></mrow></msub>'
        '<mo>+</mo><mi>Δ</mi><mi>t</mi><mo>(</mo>'
        '<msub><mi>P</mi><mrow><mtext>cond</mtext><mo>,</mo><mi>i</mi></mrow></msub><mo>+</mo>'
        '<msub><mi>P</mi><mrow><mtext>borde</mtext><mo>,</mo><mi>i</mi></mrow></msub><mo>)</mo>')
    ecuaciones += _ecuacion("Condición de Robin hacia el aire",
        '<mo>−</mo><msub><mi>k</mi><mi>c</mi></msub><mfrac><mrow><mo>∂</mo><mi>T</mi></mrow>'
        '<mrow><mo>∂</mo><mi>n</mi></mrow></mfrac><mo>=</mo><mi>h</mi><mo>(</mo>'
        '<msub><mi>T</mi><mi>s</mi></msub><mo>−</mo><msub><mi>T</mi><mtext>aire</mtext></msub><mo>)</mo>')
    ecuaciones += _ecuacion("Intercambio por una cara hacia el aire",
        '<msub><mi>P</mi><mtext>aire</mtext></msub><mo>=</mo><mfrac>'
        '<mrow><mi>A</mi><mo>(</mo><msub><mi>T</mi><mtext>aire</mtext></msub><mo>−</mo><msub><mi>T</mi><mi>c</mi></msub><mo>)</mo></mrow>'
        '<mrow><mfrac><mi>δ</mi><msub><mi>k</mi><mi>c</mi></msub></mfrac><mo>+</mo>'
        '<munder><mo>∑</mo><mi>j</mi></munder><mfrac><msub><mi>e</mi><mi>j</mi></msub><msub><mi>k</mi><mi>j</mi></msub></mfrac>'
        '<mo>+</mo><mfrac><mn>1</mn><mi>h</mi></mfrac></mrow></mfrac>')
    ecuaciones += _ecuacion("Intercambio por una cara en contacto con el suelo",
        '<msub><mi>P</mi><mtext>suelo</mtext></msub><mo>=</mo><mfrac>'
        '<mrow><mi>A</mi><mo>(</mo><msub><mi>T</mi><mtext>suelo</mtext></msub><mo>−</mo><msub><mi>T</mi><mi>c</mi></msub><mo>)</mo></mrow>'
        '<mrow><mfrac><mi>δ</mi><msub><mi>k</mi><mi>c</mi></msub></mfrac><mo>+</mo>'
        '<mfrac><msub><mi>L</mi><mtext>suelo</mtext></msub><msub><mi>k</mi><mtext>suelo</mtext></msub></mfrac></mrow></mfrac>')
    ecuaciones += _ecuacion("Hidratación por edad de cada vertida",
        '<msubsup><mi>q</mi><mi>i</mi><mo>‴</mo></msubsup><mo>(</mo><mi>t</mi><mo>)</mo><mo>=</mo>'
        '<mo stretchy="true">{</mo><mtable columnalign="left" rowspacing="0.5em">'
        '<mtr><mtd><mn>0</mn></mtd><mtd><mi>t</mi><mo>&lt;</mo><msub><mi>t</mi><mi>i</mi></msub></mtd></mtr>'
        '<mtr><mtd><msub><mi>q</mi><mn>0</mn></msub><msup><mi>e</mi><mrow><mo>−</mo><mfrac><mrow><mi>t</mi><mo>−</mo><msub><mi>t</mi><mi>i</mi></msub></mrow><mi>τ</mi></mfrac></mrow></msup></mtd>'
        '<mtd><mi>t</mi><mo>≥</mo><msub><mi>t</mi><mi>i</mi></msub></mtd></mtr></mtable>')
    ecuaciones += _ecuacion("Fuente volumétrica en una posición de la fundación",
        '<msup><mi>q</mi><mo>‴</mo></msup><mo>(</mo><mi>x</mi><mo>,</mo><mi>y</mi><mo>,</mo><mi>z</mi><mo>,</mo><mi>t</mi><mo>)</mo><mo>=</mo>'
        '<msubsup><mi>q</mi><mi>i</mi><mo>‴</mo></msubsup><mo>(</mo><mi>t</mi><mo>)</mo><mo>,</mo><mspace width="1em"/>'
        '<mo>(</mo><mi>x</mi><mo>,</mo><mi>y</mi><mo>,</mo><mi>z</mi><mo>)</mo><mo>∈</mo><msub><mi>Ω</mi><mi>i</mi></msub>')
    ecuaciones += _ecuacion("Resistencia de cada capa y retiro",
        '<msub><mi>R</mi><mi>j</mi></msub><mo>(</mo><msub><mi>a</mi><mi>i</mi></msub><mo>)</mo><mo>=</mo><mo stretchy="true">{</mo>'
        '<mtable columnalign="left" rowspacing="0.5em"><mtr><mtd><mfrac><msub><mi>e</mi><mi>j</mi></msub><msub><mi>k</mi><mi>j</mi></msub></mfrac></mtd>'
        '<mtd><msub><mi>a</mi><mi>i</mi></msub><mo>&lt;</mo><msub><mi>a</mi><mrow><mtext>retiro</mtext><mo>,</mo><mi>j</mi></mrow></msub></mtd></mtr>'
        '<mtr><mtd><mn>0</mn></mtd><mtd><msub><mi>a</mi><mi>i</mi></msub><mo>≥</mo><msub><mi>a</mi><mrow><mtext>retiro</mtext><mo>,</mo><mi>j</mi></mrow></msub></mtd></mtr></mtable>')
    ecuaciones += _ecuacion("Diferencial térmico en cada instante",
        '<mi>Δ</mi><mi>T</mi><mo>(</mo><mi>t</mi><mo>)</mo><mo>=</mo>'
        '<msub><mi>T</mi><mrow><mtext>max</mtext><mo>,</mo><mi>Ω</mi></mrow></msub><mo>(</mo><mi>t</mi><mo>)</mo><mo>−</mo>'
        '<msub><mi>T</mi><mrow><mtext>min</mtext><mo>,</mo><msub><mi>S</mi><mn>25</mn></msub></mrow></msub><mo>(</mo><mi>t</mi><mo>)</mo>')
    ecuaciones += _ecuacion("Máximos evaluados durante toda la corrida",
        '<msub><mi>T</mi><mtext>max</mtext></msub><mo>=</mo>'
        '<munder><mo>max</mo><mrow><mn>0</mn><mo>≤</mo><mi>t</mi><mo>≤</mo><msub><mi>t</mi><mi>f</mi></msub></mrow></munder>'
        '<msub><mi>T</mi><mrow><mtext>max</mtext><mo>,</mo><mi>Ω</mi></mrow></msub><mo>(</mo><mi>t</mi><mo>)</mo>'
        '<mo>,</mo><mspace width="1em"/><mi>Δ</mi><msub><mi>T</mi><mtext>max</mtext></msub><mo>=</mo>'
        '<munder><mo>max</mo><mrow><mn>0</mn><mo>≤</mo><mi>t</mi><mo>≤</mo><msub><mi>t</mi><mi>f</mi></msub></mrow></munder>'
        '<mi>Δ</mi><mi>T</mi><mo>(</mo><mi>t</mi><mo>)</mo>')
    ecuaciones += ('<p class="bottom-note">S25 representa puntos reconstruidos a 25 mm bajo las caras exteriores. '
                   'Los parámetros térmicos, el suelo y las capas son supuestos docentes pendientes de justificación para la obra.</p>')
    parametros = _ficha([
        ("Conductividad del hormigón", _numero(e["k_W_mK"]) + " W/(m·K)"),
        ("Densidad del hormigón", _numero(fuente["densidad_kg_m3"]) + " kg/m³"),
        ("Calor específico", _numero(fuente["calor_especifico_J_kgK"]) + " J/(kg·K)"),
        ("Fuente inicial de hidratación", _numero(q0) + " W/m³"),
        ("Tiempo característico", _numero(fuente["tau_s"]/3600) + " h"),
        ("Paso temporal máximo", _numero(e["dt_tope_s"]) + " s")
    ])
    simbolos = _tabla(["Símbolo", "Significado"], [
        ["<math class='inline-math'><mi>A</mi></math>", "Área de una cara del voxel."],
        ["<math class='inline-math'><mi>δ</mi><mo>=</mo><mfrac><mi>Δx</mi><mn>2</mn></mfrac></math>",
         "Distancia del centro del voxel a su cara."],
        ["<math class='inline-math'><msub><mi>T</mi><mi>c</mi></msub></math>", "Temperatura en el centro del voxel."],
        ["<math class='inline-math'><msub><mi>e</mi><mi>j</mi></msub><mo>,</mo><msub><mi>k</mi><mi>j</mi></msub></math>",
         "Espesor y conductividad de la capa j."],
        ["<math class='inline-math'><mi>h</mi></math>", "Coeficiente convectivo del aire."],
        ["<math class='inline-math'><msub><mi>a</mi><mi>i</mi></msub><mo>=</mo><mi>t</mi><mo>−</mo><msub><mi>t</mi><mi>i</mi></msub></math>",
         "Edad desde la colocación de la vertida i."]
    ])
    referencia = _ecuacion("Pulso cosenoidal de referencia",
        '<msubsup><mi>q</mi><mtext>ref</mtext><mo>‴</mo></msubsup><mo>(</mo><mi>a</mi><mo>)</mo><mo>=</mo>'
        '<mo stretchy="true">{</mo><mtable columnalign="left" rowspacing="0.5em"><mtr><mtd>'
        '<mfrac><msub><mi>q</mi><mn>0</mn></msub><mn>2</mn></mfrac><mo>[</mo><mn>1</mn><mo>−</mo><mi>cos</mi><mo>(</mo>'
        '<mfrac><mrow><mn>2</mn><mi>π</mi><mi>a</mi></mrow><mi>D</mi></mfrac><mo>)</mo><mo>]</mo></mtd>'
        '<mtd><mn>0</mn><mo>≤</mo><mi>a</mi><mo>≤</mo><mi>D</mi></mtd></mtr>'
        '<mtr><mtd><mn>0</mn></mtd><mtd><mtext>fuera del intervalo</mtext></mtd></mtr></mtable>')
    referencia += '<p class="bottom-note">La comparación usa un pico igual a la fuente inicial y una duración de 12 h desde la colocación de la sonda. Es una referencia temporal didáctica.</p>'
    trazabilidad = (
        '<p class="data-purpose">Estos datos identifican el código y las entradas que produjeron el resultado.<br>'
        'Permiten repetir la corrida y comprobar que se utilizaron los mismos archivos.</p>')
    trazabilidad += _ficha([
        ("Actividad", escape(resumen["caso"].upper())),
        ("Duración simulada", _numero(resumen["horizonte_h"]) + " h"),
        ("Tamaño del voxel", _numero(resumen["lado_m"]) + " m"),
        ("Pasos calculados", str(resumen["pasos"])),
        ("Ejecución", _fecha(resumen["ejecutado_utc"])),
        ("Versión del código calculado", '<code>' + escape(resumen["codigo_commit"]) + '</code>'),
        ("Estado del código al ejecutar", "Con cambios locales" if resumen["codigo_modificado"] else "Registrado sin cambios locales"),
        ("Campos para la animación", str(resumen["campos_html"]) + " campos · intervalo solicitado de "
         + _numero(resumen["intervalo_html_h"]) + " h, además de eventos")
    ])
    trazabilidad += _tabla(["Entrada", "Función", "Archivo"], [
        ["Geometría IFC", "Define la forma, las vertidas y su calendario.",
         '<code class="fingerprint">' + escape(resumen["parametros_efectivos"]["archivo_ifc"]) + '</code>'],
        ["Archivo meteorológico", "Aporta la serie horaria utilizada por los bordes.",
         '<code class="fingerprint">' + escape(resumen["snapshot"]) + '</code>'],
        ["Parámetros efectivos", "Fijan propiedades, suelo, capas, fuente y discretización.",
         "El JSON descargable incluye las opciones aplicadas en la ejecución."]
    ])
    trazabilidad += (
        '<details><summary>Identificadores de integridad de las entradas</summary>'
        '<p>Los identificadores SHA-256 permiten comprobar que los archivos corresponden a esta corrida.</p>'
        + _ficha([
            ("Clima", '<code>' + escape(resumen["snapshot_sha256"]) + '</code>'),
            ("IFC", '<code>' + escape(resumen["sha256_ifc"]) + '</code>'),
            ("Archivo original de parámetros", '<code>' + escape(resumen["parametros_sha256"]) + '</code>')
        ]) + '</details>'
        '<p class="bottom-note">Los colores se interpolan entre campos guardados. Los diagnósticos y extremos provienen de los pasos del solver; los botones de máximos abren sus campos exactos.</p>')
    nueva = (
        '<p>Descarga los parámetros, modifica el JSON y ejecuta Python para obtener otra corrida.</p>'
        '<button id="downloadParameters" style="margin-top:12px">Descargar parámetros de esta corrida</button>'
        '<pre style="white-space:pre-wrap">python -X utf8 -B casos/semana4/ejecutar.py '
        + escape(resumen["caso"]) + ' --parametros parametros.json</pre>')
    return ('<section id="study" class="tab-panel" hidden>'
            + _panel("Modelo térmico", ecuaciones + simbolos)
            + _panel("Parámetros físicos", parametros)
            + _panel("Referencia del ejercicio anterior", referencia)
            + _panel("Datos de la corrida", trazabilidad)
            + _panel("Preparar otra corrida", nueva) + '</section>')



def combinar_resoluciones(raiz, fundacion, archivos, salida):
    """Une corridas independientes y una malla geométrica de 1 m."""
    import re
    from .voxel import voxelizar_fundacion
    from .vertidas_voxel import asignar_vertidas
    versiones = []
    for archivo in archivos:
        html = archivo.read_text(encoding="utf-8")
        coincidencia = re.search(
            r'<script id="e07-data" type="application/json">([\s\S]*?)</script>', html)
        if coincidencia is None:
            raise ValueError("El archivo no contiene una corrida Python.")
        versiones.append(json.loads(coincidencia.group(1)))
    datos = versiones[0]
    contactos = datos["contactos_esperados"]
    asignacion = asignar_vertidas(fundacion, voxelizar_fundacion(fundacion, (1.,)*3))
    ids = asignacion.vertida_id
    superficies = clasificar_caras(asignacion)
    geometria = dict(
        h=1., forma=list(ids.shape),
        origen=asignacion.voxelizacion.grilla.origen_m.tolist(),
        rle=[[int(v), sum(1 for _ in grupo)] for v, grupo in groupby(ids.ravel())],
        ocupados=int(np.count_nonzero(ids)), volumen=float(np.count_nonzero(ids)),
        filas=[asdict(f) for f in comparar_volumenes(fundacion, asignacion)],
        diagnostico=asdict(diagnosticar_contactos(superficies, [1, 2, 3, 4, 5], contactos)))
    corridas = {}
    referencia = datos["resultado_python"]["resumen"]
    for version in versiones:
        resumen = version["resultado_python"]["resumen"]
        if (version["sha256_ifc"] != datos["sha256_ifc"]
                or any(resumen[campo] != referencia[campo] for campo in (
                    "snapshot_sha256", "inicio_serie", "inicio_escenario", "horizonte_h", "plan_vertidas"))):
            raise ValueError("Las resoluciones deben compartir IFC, clima, horizonte y plan.")
        for grilla, resultado in zip(version["grillas"], version["resultados_python"]):
            if resultado is not None:
                corridas[grilla["h"]] = (grilla, resultado)
    datos["grillas"] = [geometria] + [corridas[h][0] for h in sorted(corridas, reverse=True)]
    datos["resultados_python"] = [None] + [corridas[h][1] for h in sorted(corridas, reverse=True)]
    datos["grilla_inicial"] = next(i for i, g in enumerate(datos["grillas"])
                                  if g["h"] == datos["resultado_python"]["resumen"]["lado_m"])
    _escribir_html(raiz, datos, salida)
