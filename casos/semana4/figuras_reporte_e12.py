"""Genera figuras del reporte E12 leyendo resultados guardados; no ejecuta el solver."""
import json
import os
from pathlib import Path
import re

RAIZ = Path(__file__).resolve().parents[2]
os.environ.setdefault("MPLCONFIGDIR", str(RAIZ / ".venv/cache/matplotlib"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from ver_3d import pv

SALIDA = RAIZ / "resultados/e12"
COLORES = dict(maximo="#b44a36", interior="#187f70", superficie="#276eaa", delta="#7850a0")


def leer_corridas():
    html = (SALIDA / "visualizador.html").read_text(encoding="utf-8")
    datos = json.loads(re.search(
        r'<script id="e07-data" type="application/json">([\s\S]*?)</script>', html).group(1))
    corridas = {r["resumen"]["lado_m"]: r for r in datos["resultados_python"] if r is not None}
    for lado, carpeta in [(.5, SALIDA), (.25, SALIDA / "malla_025")]:
        resumen = json.loads((carpeta / "resumen.json").read_text(encoding="utf-8"))
        if corridas[lado]["resumen"] != resumen:
            raise ValueError(f"El HTML y el resumen de {lado} m no corresponden a la misma corrida.")
    return corridas


def curvas(corridas):
    r = corridas[.5]
    resumen, historia = r["resumen"], r["historia"]
    t = np.array([fila["tiempo_h"] for fila in historia])
    fig, axes = plt.subplots(2, 1, figsize=(11, 7.6), sharex=True, layout="constrained")
    for clave, texto, color in [
        ("Tmax_C", "Máximo del dominio", COLORES["maximo"]),
        ("nucleo_C", "Sonda interior fija", COLORES["interior"]),
        ("Tmin_S25_C", "Mínimo S25 reconstruido", COLORES["superficie"]),
    ]:
        axes[0].plot(t, [fila[clave] for fila in historia], label=texto, color=color, lw=2)
    axes[0].axhline(70, color="#a34336", ls="--", lw=1.3, label="Límite: 70 °C")
    pico = resumen["Tmax"]
    axes[0].plot(pico["tiempo_h"], pico["valor"], "o", color=COLORES["maximo"])
    axes[0].annotate(f"Máximo: {pico['valor']:.2f} °C\na las {pico['tiempo_h']:g} h",
                     (pico["tiempo_h"], pico["valor"]), xytext=(215, 64),
                     arrowprops=dict(arrowstyle="-", color=COLORES["maximo"]), fontsize=10)
    axes[0].set(ylabel="Temperatura [°C]", ylim=(10, 75),
                title="E12 · Evolución de 14 días · malla de 0,50 m")
    axes[0].legend(loc="lower right", ncol=2, fontsize=9)
    axes[1].plot(t, [fila["DeltaT_K"] for fila in historia], color=COLORES["delta"], lw=2,
                 label="Tmax del dominio − Tmin de S25")
    axes[1].axhline(20, color="#a34336", ls="--", lw=1.3, label="Límite: 20 °C de diferencia")
    delta = resumen["DeltaTmax"]
    axes[1].plot(delta["tiempo_h"], delta["valor"], "o", color=COLORES["delta"])
    axes[1].annotate(f"Diferencial máximo: {delta['valor']:.2f} °C\na las {delta['tiempo_h']:g} h",
                     (delta["tiempo_h"], delta["valor"]), xytext=(235, 29),
                     arrowprops=dict(arrowstyle="-", color=COLORES["delta"]), fontsize=10)
    axes[1].axvspan(72, 120, color="#d4c8ad", alpha=.32,
                   label="Retiros escalonados de capas: 72–120 h")
    axes[1].set(ylabel="Diferencial [°C de diferencia]", ylim=(0, 48), xlim=(0, 336),
                xlabel="Horas desde la primera vertida")
    axes[1].legend(loc="lower right", fontsize=9)
    for ax in axes:
        ax.grid(alpha=.18)
        ax.spines[["top", "right"]].set_visible(False)
    fig.savefig(SALIDA / "temperaturas.png", dpi=170)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(11, 3.9), layout="constrained")
    for lado, color, estilo in [(.5, "#187f70", "-"), (.25, "#c47424", "--")]:
        filas = corridas[lado]["historia"]
        tiempo = [fila["tiempo_h"] for fila in filas]
        for ax, clave in zip(axes, ("Tmax_C", "DeltaT_K")):
            ax.plot(tiempo, [fila[clave] for fila in filas], color=color, ls=estilo,
                    lw=2, label=f"Malla {lado:g} m")
    for ax, limite, titulo, unidad in zip(axes, (70, 20),
            ("Máximo de la fundación", "Diferencial térmico"),
            ("Temperatura [°C]", "Diferencial [°C de diferencia]")):
        ax.axhline(limite, color="#a34336", ls=":", label=f"Límite: {limite} °C")
        ax.set(title=titulo, ylabel=unidad, xlabel="Tiempo desde la primera vertida [h]", xlim=(0, 336))
        ax.grid(alpha=.18)
        ax.spines[["top", "right"]].set_visible(False)
        ax.legend(fontsize=9)
    fig.savefig(SALIDA / "comparacion_mallas.png", dpi=170)
    plt.close(fig)


def escena(plot, nombre, resumen):
    datos = pv.read(SALIDA / f"{nombre}.vti")
    metricas = resumen["Tmax"] if nombre == "pico" else resumen["DeltaTmax"]
    if abs(float(datos.field_data["tiempo_h"][0])-metricas["tiempo_h"]) > 1e-8:
        raise ValueError("El VTI no corresponde al instante del resumen.")
    if str(datos.field_data["snapshot_sha256"][0]) != resumen["snapshot_sha256"]:
        raise ValueError("El VTI corresponde a otro archivo meteorológico.")
    malla = datos.threshold(.5, scalars="activo", preference="cell")
    punto = np.array(metricas["xyz_Tmax_m"])
    plot.set_background("white")
    plot.add_mesh(malla.extract_surface(algorithm="dataset_surface"), color="#9daeb3", opacity=.10)
    seccion = malla.slice(normal="y", origin=punto)
    plot.add_mesh(seccion, scalars="T_C", cmap="turbo", clim=(15, 65), lighting=False,
                  show_edges=True, edge_color="#667375", line_width=.25,
                  scalar_bar_args=dict(title=f"Temperatura de centros [°C] · {metricas['tiempo_h']:g} h", vertical=False,
                      position_x=.20, position_y=.06, width=.62, height=.08,
                      title_font_size=15, label_font_size=13, color="#20313a", n_labels=6))
    titulo = "Máxima temperatura" if nombre == "pico" else "Máximo diferencial"
    plot.add_text(f"{titulo} · {metricas['tiempo_h']:g} h", position="upper_left",
                  font_size=18, color="#20313a")
    plot.add_point_labels(np.array([punto]), [f"Máximo: {metricas['Tmax_C']:.2f} °C · V{metricas['vertida_Tmax']:02d}"],
                         point_color="#ad3227", text_color="#20313a", point_size=13,
                         font_size=15, shape_color="white", shape_opacity=.9, always_visible=True)
    if nombre == "diferencial":
        plot.add_point_labels(np.array([metricas["xyz_S25_m"]]),
                             [f"S25 mínima: {metricas['Tmin_S25_C']:.2f} °C · V{metricas['vertida_S25']:02d}"],
                             point_color="#2466ae", text_color="#20313a", point_size=13,
                             font_size=15, shape_color="white", shape_opacity=.9, always_visible=True)
    plot.add_text(f"Corte XZ en y = {punto[1]:.2f} m\nMalla 0,50 m · geometría a escala real",
                  position="lower_left", font_size=11, color="#51656f")
    plot.camera_position = [(27, -34, 25), (0, 0, 1.5), (0, 0, 1)]
    plot.enable_parallel_projection()
    plot.reset_camera()
    plot.camera.zoom(1.1)
    plot.add_axes()


def capturas(resumen):
    plot = pv.Plotter(off_screen=True, shape=(1, 2), window_size=(1900, 760))
    for i, nombre in enumerate(("pico", "diferencial")):
        plot.subplot(0, i)
        escena(plot, nombre, resumen)
    plot.screenshot(SALIDA / "estados_3d.png")
    plot.close()
    plot = pv.Plotter(off_screen=True, window_size=(1400, 850))
    escena(plot, "diferencial", resumen)
    plot.screenshot(SALIDA / "corte.png")
    plot.close()


def main():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
    corridas = leer_corridas()
    curvas(corridas)
    capturas(corridas[.5]["resumen"])
    print("Figuras actualizadas desde HTML, resúmenes y VTI existentes; sin simulación.")


if __name__ == "__main__":
    main()
