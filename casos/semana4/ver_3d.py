"""Inspección interactiva del VTI: slice o clipping sin recalcular la física."""
import argparse
import json
from pathlib import Path

import numpy as np
import pyvista as pv


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("vti", type=Path)
    p.add_argument("--modo", choices=["corte", "recorte"], default="corte")
    p.add_argument("--eje", choices=["x", "y", "z"], default="y")
    p.add_argument("--captura", type=Path, help="Guarda un corte fijo para comprobar el VTI sin ventana.")
    a = p.parse_args()
    datos = pv.read(a.vti)
    malla = datos.threshold(.5, scalars="activo", preference="cell")
    t = float(datos.field_data["tiempo_h"][0])
    sonda = datos.field_data["nucleo_xyz_m"][0]
    plot = pv.Plotter(off_screen=bool(a.captura))
    plot.set_background("white")
    plot.add_mesh(malla.extract_surface(algorithm="dataset_surface"), color="#778b95", opacity=.14)
    limites = (float(malla["T_C"].min()), float(malla["T_C"].max()))
    opts = dict(scalars="T_C", cmap="turbo", clim=limites, scalar_bar_args={"title": "T [°C]"})
    if a.captura:
        plot.add_mesh(malla.slice(normal=a.eje, origin=sonda), **opts)
    elif a.modo == "corte":
        plot.add_mesh_slice(malla, normal=a.eje, origin=sonda, **opts)
    else:
        plot.add_mesh_clip_plane(malla, normal=a.eje, origin=sonda, **opts)
    plot.add_text(f"Fundación | {t:.2f} h | {a.vti.stem}", color="#172a37", font_size=12)
    plot.add_point_labels(np.array([sonda]), ["Sonda interior"], text_color="#172a37",
                          point_color="black", always_visible=True, font_size=11)
    if a.vti.stem == "diferencial":
        resumen = json.loads(a.vti.with_name("resumen.json").read_text(encoding="utf-8"))
        s25 = resumen["DeltaTmax"]["xyz_S25_m"]
        plot.add_point_labels(np.array([s25]), ["S25 mínima"], text_color="#172a37",
                              point_color="blue", always_visible=True, font_size=11)
    plot.show_axes()
    plot.show(screenshot=str(a.captura) if a.captura else None)


if __name__ == "__main__":
    main()
