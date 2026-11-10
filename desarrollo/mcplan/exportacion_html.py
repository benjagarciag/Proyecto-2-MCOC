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


def _seccion_resultados(resumen):
    e, c = resumen["parametros_efectivos"]["entorno"], resumen["clima"]
    metadatos = (
        '<p><strong>' + escape(c["fuente"]) + ' · ' + escape(c["modelo_solicitado"]) + '</strong></p>'
        '<p>Serie desde ' + escape(resumen["inicio_serie"]) + '. Escenario desde '
        + escape(resumen["inicio_escenario"]) + '.</p><p>Descargado '
        + escape(c["descargado_utc"]) + '. Coordenadas −37,277929; −72,368271.</p>'
        '<p class="bottom-note">Tipo ' + escape(c["tipo"]) + '. Se usa aire horario interpolado. Viento y radiación permanecen archivados.</p>'
        '<p id="pythonAirNow" class="hint"></p>')
    bordes = (
        '<div class="table-scroll"><table><thead><tr><th>Región</th><th>Condición calculada</th></tr></thead><tbody>'
        '<tr><td>Laterales expuestos</td><td>Aire horario + capas activas</td></tr>'
        '<tr><td>Horizontales expuestos</td><td>Aire horario</td></tr>'
        '<tr><td>Base z = ' + str(e["plano_suelo_z_m"]) + ' m</td><td>Suelo a ' + str(e["suelo_C"]) + ' °C</td></tr>'
        '<tr><td>Interfaces activas</td><td>Conducción entre voxeles</td></tr></tbody></table></div>'
        '<p class="bottom-note">h = ' + str(e["h_aire_W_m2K"]) + ' W/(m²·K). Suelo con L = '
        + str(e["profundidad_suelo_m"]) + ' m y k = ' + str(e["k_suelo_W_mK"]) + ' W/(m·K).</p>'
        '<button id="showBoundaries">Colorear bordes en 3D</button>')
    capas = e["capas_laterales"]
    tabla = '<table><thead><tr><th>Vertida</th><th>Edad h</th>'
    tabla += ''.join('<th>Capa ' + str(i+1) + '</th>' for i in range(len(capas)))
    tabla += '</tr></thead><tbody id="layerRows"></tbody></table>'
    detalle = ''.join(
        '<p>Capa ' + str(i+1) + ' · e = ' + str(c["espesor_m"]) + ' m · k = '
        + str(c["k_W_mK"]) + ' W/(m·K) · retiro '
        + (str(c["retiro_edad_h"]) + ' h de edad' if c["retiro_edad_h"] is not None else 'sin retiro')
        + '.</p>' for i, c in enumerate(capas))
    acciones = (
        '<div class="inline"><button class="primary" id="peakPython">Ver máximo térmico</button>'
        '<button id="deltaPython">Ver máximo diferencial</button><button id="finalPython">Ver estado final</button></div>'
        '<p id="pythonFrame" class="bottom-note"></p>')
    def xyz(valores):
        return "(" + "; ".join(f"{v:.3f}" for v in valores) + ") m"
    pico, delta = resumen["Tmax"], resumen["DeltaTmax"]
    extremos = (
        '<div class="table-scroll"><table><thead><tr><th>Métrica</th><th>Valor</th><th>Hora</th><th>Ubicación</th></tr></thead><tbody>'
        '<tr><td>T máxima</td><td>' + f'{pico["valor"]:.2f}' + ' °C</td><td>'
        + str(pico["tiempo_h"]) + '</td><td>V0' + str(pico["vertida_Tmax"]) + ' '
        + xyz(pico["xyz_Tmax_m"]) + '</td></tr><tr><td>Diferencial máximo</td><td>'
        + f'{delta["valor"]:.2f}' + ' K</td><td>' + str(delta["tiempo_h"])
        + '</td><td>Tmax ' + xyz(delta["xyz_Tmax_m"]) + '<br>S25 '
        + xyz(delta["xyz_S25_m"]) + '</td></tr></tbody></table></div>'
        '<p>Sonda interior roja ' + xyz(resumen["nucleo_xyz_m"]) + '. '
        'S25 azul al seleccionar el estado de máximo diferencial.</p>'
        '<p class="bottom-note">Tmax ' + ('cumple' if resumen["cumple_70_ensayo"] else 'supera')
        + ' el criterio de 70 °C. El diferencial '
        + ('cumple' if resumen["cumple_20_ensayo"] else 'supera') + ' el criterio de 20 K en este escenario.</p>')
    s = '<section id="heat" class="tab-panel" hidden>' + _panel("Explorar la corrida", acciones)
    s += _panel("Extremos de la corrida", extremos)
    s += '<div class="two equal">' + _panel("Clima utilizado", metadatos) + _panel("Condiciones de borde", bordes) + '</div>'
    s += _panel("Moldaje y aislación por edad", detalle + '<div class="table-scroll">' + tabla + '</div>')
    for titulo, identificador in [
            ("Núcleo, superficie S25 y máximo del dominio", "temperatureChart"),
            ("Temperatura ambiente y suelo", "observerChart"), ("Diferencial térmico", "deltaChart"),
            ("Contribuciones a la tasa de temperatura del núcleo", "rateChart"),
            ("Intercambio exterior y calor de hidratación", "powerChart")]:
        s += _panel(titulo, '<div id="' + identificador + '"></div>')
    return s + _panel("Balance de energía", '<p id="thermalBalance"></p>') + '</section>'


def _seccion_modelo(resumen):
    p = (
        '<p>Python resuelve el balance por voxel con Euler explícito. La hidratación se integra exactamente por edad. Los contactos entre celdas activas son perfectos.</p>'
        '<div class="formula">ρ cₚ V ΔT = E hidratación + Δt (P vecinos + P bordes)<br>'
        'P aire = A (T aire − T centro) / [δ/k + Σ(e/k capa) + 1/h]<br>'
        'P suelo = A (T suelo − T centro) / [δ/k + L suelo/k suelo]<br>'
        'q(a) = q₀ exp(−a/τ)<br>ΔT(t) = Tmax del dominio − Tmin S25</div>'
        '<p class="bottom-note">S25 se reconstruye a 25 mm de las caras exteriores. Parámetros térmicos, capas y suelo son supuestos docentes pendientes de justificación para la obra.</p>')
    fuente = resumen["parametros_efectivos"]["hidratacion"]
    parametros = (
        '<p>Hormigón k = ' + str(resumen["parametros_efectivos"]["entorno"]["k_W_mK"])
        + ' W/(m·K), ρ = ' + str(fuente["densidad_kg_m3"]) + ' kg/m³ y cₚ = '
        + str(fuente["calor_especifico_J_kgK"]) + ' J/(kg·K).</p>'
        '<p>Hidratación q₀ = ' + str(fuente.get("q0_W_m3", "ver parámetros"))
        + ' W/m³ y τ = ' + str(fuente["tau_s"]/3600) + ' h. Paso máximo '
        + str(resumen["parametros_efectivos"]["entorno"]["dt_tope_s"]) + ' s.</p>')
    trazabilidad = (
        '<p>Commit del código ' + escape(resumen["codigo_commit"]) + '</p>'
        '<p>Cambios locales al ejecutar ' + ('sí' if resumen["codigo_modificado"] else 'no') + '.</p>'
        '<p>Snapshot ' + escape(resumen["snapshot"]) + '</p>'
        '<p class="footer">SHA256 clima ' + escape(resumen["snapshot_sha256"])
        + '<br>SHA256 IFC ' + escape(resumen["sha256_ifc"])
        + '<br>SHA256 parámetros ' + escape(resumen["parametros_sha256"]) + '</p>'
        '<p>Se guardan campos temporales y eventos de colocación y retiro. Entre campos se interpolan los colores respetando las activaciones.</p>'
        '<p>Los máximos provienen de todos los pasos de Python. Sus botones abren campos guardados e indican si el estado es previo o posterior a un evento.</p>')
    nueva = (
        '<p>Descarga los parámetros, modifica el JSON y ejecuta Python para obtener otra corrida. Tiempo, cortes, cámara y visibilidad exploran el resultado guardado.</p>'
        '<button id="downloadParameters">Descargar parámetros de esta corrida</button>'
        '<pre style="white-space:pre-wrap">python -X utf8 -B casos/semana4/ejecutar.py '
        + escape(resumen["caso"]) + ' --parametros parametros.json</pre>'
        '<p class="bottom-note">El pronóstico archivado no cubre el escenario del 27 de noviembre. E12 usa una serie histórica análoga. La fecha del escenario es provisional.</p>')
    return ('<section id="study" class="tab-panel" hidden>'
            + _panel("Modelo térmico", p + parametros) + _panel("Datos de la corrida", trazabilidad)
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
