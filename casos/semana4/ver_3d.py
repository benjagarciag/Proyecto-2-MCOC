"""Inspección interactiva del VTI: slice o clipping sin recalcular la física."""
import argparse
import json
from pathlib import Path
import site

RAIZ = Path(__file__).resolve().parents[2]
VISTA_LOCAL = RAIZ / ".venv/cache/visualizacion"
if VISTA_LOCAL.is_dir():
    site.addsitedir(str(VISTA_LOCAL))

import numpy as np
import pyvista as pv


def elegir_opcion(titulo, opciones):
    print(f"\n{titulo}")
    for numero, (etiqueta, _) in enumerate(opciones, 1):
        print(f"  {numero}. {etiqueta}")
    while True:
        try:
            respuesta = input(f"Elige el número [1-{len(opciones)}]: ").strip()
        except (EOFError, KeyboardInterrupt):
            raise SystemExit("\nSelección cancelada.") from None
        if respuesta in {str(i) for i in range(1, len(opciones)+1)}:
            return opciones[int(respuesta)-1][1]
        print("Opción inválida. Escribe uno de los números de la lista.")


def seleccionar_vti():
    """Elige caso, malla y resultado entre los archivos ya calculados."""
    casos = []
    for caso in ("e11", "e12"):
        archivos = sorted((RAIZ / "resultados" / caso).rglob("*.vti"))
        if archivos:
            casos.append((caso.upper(), archivos))
    if not casos:
        raise SystemExit("No hay archivos VTI de E11/E12. Ejecuta primero la simulación.")
    archivos = elegir_opcion("¿Qué caso quieres abrir?", casos)
    carpetas = sorted({ruta.parent for ruta in archivos})
    mallas = []
    for carpeta in carpetas:
        resumen = carpeta / "resumen.json"
        lado = json.loads(resumen.read_text(encoding="utf-8")).get("lado_m") if resumen.exists() else None
        etiqueta = f"{lado:g} m" if lado is not None else "Resolución sin metadata"
        # La carpeta distingue exportaciones diferentes incluso si tienen igual resolución.
        etiqueta += f" — {carpeta.relative_to(RAIZ / 'resultados')}"
        mallas.append((etiqueta, carpeta))
    carpeta = elegir_opcion("¿Qué malla quieres abrir?", mallas)
    nombres = {
        "diferencial": "Máximo diferencial térmico",
        "pico": "Máxima temperatura",
        "final": "Estado final",
    }
    orden = {nombre: i for i, nombre in enumerate(nombres)}
    resultados = sorted((ruta for ruta in archivos if ruta.parent == carpeta),
                        key=lambda ruta: (orden.get(ruta.stem, 99), ruta.name))
    return elegir_opcion("¿Qué resultado quieres ver?", [
        (f"{nombres.get(ruta.stem, ruta.stem)} — {ruta.name}", ruta)
        for ruta in resultados
    ])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("vti", type=Path, nargs="?",
                   help="Archivo VTI; si se omite, permite elegirlo en la terminal.")
    p.add_argument("--modo", choices=["corte", "recorte"], default="corte")
    p.add_argument("--eje", choices=["x", "y", "z"], default="y")
    p.add_argument("--captura", type=Path, help="Guarda un corte fijo para comprobar el VTI sin ventana.")
    a = p.parse_args()
    if a.vti is None:
        a.vti = seleccionar_vti()
    if not a.vti.is_file():
        p.error(f"No existe el archivo: {a.vti}")
    print(f"Abriendo: {a.vti}")
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
        vista = (malla.slice(normal=a.eje, origin=sonda) if a.modo == "corte"
                 else malla.clip(normal=a.eje, origin=sonda))
        plot.add_mesh(vista, **opts)
    elif a.modo == "corte":
        plot.add_mesh_slice(malla, normal=a.eje, origin=sonda, **opts)
    else:
        plot.add_mesh_clip_plane(malla, normal=a.eje, origin=sonda, **opts)
    fase = str(datos.field_data["fase"][0]) if "fase" in datos.field_data else "sin metadata de fase"
    plot.add_text(f"Fundación | {t:.2f} h | {a.vti.stem} | {fase}", color="#172a37", font_size=12)
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
