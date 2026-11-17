"""Presenta un campo térmico crítico y los escenarios F02 en un HTML autónomo."""
from base64 import b64encode
from html import escape
from io import BytesIO
import json
from pathlib import Path

import numpy as np


def imagen_corte(campo, origen, lado, metrica, extremos):
    import pyvista as pv

    malla = pv.ImageData(dimensions=tuple(n+1 for n in campo.shape[::-1]),
                         origin=tuple(origen), spacing=(lado,)*3)
    malla.cell_data["Temperatura"] = campo.ravel()
    malla.cell_data["activo"] = np.isfinite(campo).astype(np.uint8).ravel()
    solido = malla.threshold(.5, scalars="activo", preference="cell")
    p = pv.Plotter(off_screen=True, window_size=(1030, 680))
    p.set_background("#edf3f5")
    try:
        p.add_mesh(solido.extract_surface(algorithm="dataset_surface"), color="#8fa5ad", opacity=.20)
        origen_corte = metrica["xyz_Tmax_m"]
        p.add_mesh(solido.slice(normal="y", origin=origen_corte), scalars="Temperatura",
                   clim=extremos, cmap="viridis", show_edges=False,
                   scalar_bar_args={"title": "Temperatura (°C)", "color": "#203a45"})
        p.add_points(np.array([origen_corte]), color="#ff632f", point_size=14,
                     render_points_as_spheres=True)
        p.show_axes()
        p.view_isometric()
        p.camera.zoom(1.18)
        imagen = p.screenshot(return_img=True)
    finally:
        p.close()
    from PIL import Image

    salida = BytesIO()
    Image.fromarray(imagen).save(salida, format="PNG")
    return "data:image/png;base64," + b64encode(salida.getvalue()).decode("ascii")


def numero(valor, decimales=2):
    return f"{valor:.{decimales}f}".replace(".", ",")


def agregar_acceso(raiz, salida):
    existente = raiz / "resultados/e12/visualizador.html"
    enlace = ('<a href="../incertidumbre/enfriamiento/u5_tope12/unica/tras_colocacion/'
              'visualizador.html" target="_blank" rel="noopener">Vertida única · 12 kW</a>')
    if salida != raiz / "resultados/incertidumbre/enfriamiento/u5_tope12/unica/tras_colocacion":
        return
    texto = existente.read_bytes()
    etiqueta = enlace.encode()
    if etiqueta not in texto:
        inicio = texto.index(b'<nav class="tabs" aria-label="Secciones">')
        cierre = texto.index(b"</nav>", inicio)
        existente.write_bytes(texto[:cierre] + etiqueta + texto[cierre:])


def exportar_complemento(raiz, salida, registro, critico, corrida, origen):
    plantilla = (raiz / "Visualizadores/f02_cronograma_plantilla.html").read_text(encoding="utf-8")
    filas = sorted(registro["corridas"], key=lambda f: f["DeltaTmax"]["valor"], reverse=True)
    metrica = critico["DeltaTmax"]
    campo = corrida.campos["diferencial"].temperatura_C
    extremos = [float(np.nanmin(campo)), float(np.nanmax(campo))]
    lado = registro["lado_m"]
    datos = dict(campo=[float(x) if np.isfinite(x) else None for x in campo.ravel()],
                 forma=campo.shape, origen=list(origen), paso=lado, extremos=extremos,
                 puntos=[metrica["xyz_Tmax_m"], metrica["xyz_S25_m"]])
    tabla = []
    for f in filas:
        fallo = f["excede_70"] or f["excede_20"]
        etiqueta = "Excede" if fallo else "Cumple"
        marca = ' class="critico"' if f is critico else ""
        tabla.append(f'<tr{marca}><th scope="row">{escape(f["curva"])}</th>'
                     f'<td>{escape(f["clima"])}</td>'
                     f'<td>{numero(f["Tmax"]["valor"])}</td>'
                     f'<td>{numero(f["DeltaTmax"]["valor"])}</td>'
                     f'<td>{numero(f["DeltaTmax"]["tiempo_h"], 1)}</td>'
                     f'<td>{etiqueta}</td></tr>')
    valores = {
        "duracion": numero(registro["D_h"]),
        "volumen": numero(sum(v["volumen_m3"] for v in registro["plan"])),
        "riesgo": numero(registro["agregado"]["P_union"] * 100, 0),
        "delta": numero(metrica["valor"]),
        "tmax": numero(max(f["Tmax"]["valor"] for f in filas)),
        "cantidad": str(len(filas)),
        "fallas": str(sum(f["excede_70"] or f["excede_20"] for f in filas)),
        "curva": escape(critico["curva"]),
        "clima": escape(critico["clima"]),
        "hora": numero(metrica["tiempo_h"], 0),
        "caliente": numero(metrica["Tmax_C"]),
        "frio": numero(metrica["Tmin_S25_C"]),
        "tabla": "\n".join(tabla),
        "imagen": imagen_corte(campo, origen, lado, metrica, extremos),
        "datos": json.dumps(datos, ensure_ascii=False, separators=(",", ":"), allow_nan=False),
        "colocacion": numero(registro["plan"][0]["colocacion_C"]),
        "horizonte": str(critico["horizonte_h"]),
    }
    for nombre, valor in valores.items():
        plantilla = plantilla.replace("{{"+nombre+"}}", valor)
    destino = salida / "visualizador.html"
    destino.write_text(plantilla, encoding="utf-8")
    agregar_acceso(raiz, salida)
    print(f"Complemento exportado: {destino}")
