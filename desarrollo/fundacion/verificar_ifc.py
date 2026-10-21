"""Punto 25: leer identidad, propiedades y geometría del IFC sin modificarlo."""

import argparse
from pathlib import Path

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.element
import ifcopenshell.util.unit
import numpy as np


def verificar(ruta: Path) -> None:
    modelo = ifcopenshell.open(str(ruta))
    print("Archivo:", ruta)
    print("Schema:", modelo.schema)
    print("Escala de longitud IFC a metros:", ifcopenshell.util.unit.calculate_unit_scale(modelo))
    vertidas = sorted(
        [p for p in modelo.by_type("IfcProduct") if (p.Name or "").startswith("Vertida_")],
        key=lambda p: p.Name,
    )
    nombres = [f"Vertida_{i:02d}" for i in range(1, 6)]
    if [p.Name for p in vertidas] != nombres:
        raise ValueError(f"Se esperaban exactamente {nombres}; encontrados {[p.Name for p in vertidas]}.")

    settings = ifcopenshell.geom.settings()
    settings.set("use-world-coords", True)
    minimos, maximos = [], []
    fallos = []
    requeridas = {
        "VertidaID", "Inicio_h", "TemperaturaColocacion_C", "TipoHormigon",
        "Moldaje", "Aislacion", "RetiroMoldaje_h",
    }
    for producto in vertidas:
        print("\n" + "=" * 60)
        print("Nombre:", producto.Name)
        print("Clase:", producto.is_a())
        print("GUID:", producto.GlobalId)
        psets = ifcopenshell.util.element.get_psets(producto)
        print("Property sets:", psets)
        faltantes = requeridas - psets.get("UANDES_HormigonMasivo", {}).keys()
        if faltantes:
            fallos.append(f"{producto.Name}: propiedades faltantes: {sorted(faltantes)}")
        if not producto.is_a("IfcFooting"):
            fallos.append(f"{producto.Name}: se esperaba clase IfcFooting")
        try:
            # IfcOpenShell entrega la geometría en metros con esta configuración.
            shape = ifcopenshell.geom.create_shape(settings, producto)
            vertices = np.asarray(shape.geometry.verts, dtype=float).reshape(-1, 3)
            if not len(vertices) or not np.isfinite(vertices).all():
                raise ValueError("Geometría vacía o coordenadas no finitas")
            lo, hi = vertices.min(axis=0), vertices.max(axis=0)
            minimos.append(lo)
            maximos.append(hi)
            print("BBox min [m]:", np.round(lo, 4))
            print("BBox max [m]:", np.round(hi, 4))
            print("Dimensiones X/Y/Z [m]:", np.round(hi - lo, 4))
            print("Triángulos:", len(shape.geometry.faces) // 3)
        except Exception as error:
            fallos.append(f"{producto.Name}: error de geometría: {error}")

    if minimos:
        lo = np.min(minimos, axis=0)
        hi = np.max(maximos, axis=0)
        print("\nGLOBAL")
        print("BBox min [m]:", np.round(lo, 4))
        print("BBox max [m]:", np.round(hi, 4))
        print("Dimensiones X/Y/Z [m]:", np.round(hi - lo, 4))
    print("Número de vertidas:", len(vertidas))
    if fallos:
        raise SystemExit("\nVERIFICACIÓN CON ERRORES:\n" + "\n".join(fallos))
    print("VERIFICACIÓN OK: identidad, propiedades y triangulación de las cinco vertidas.")
    print("Esta lectura no verifica solapes, estanqueidad ni conformidad con todas las cotas docentes.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "archivo", nargs="?", type=Path,
        default=Path(__file__).resolve().parent / "fundacion.ifc",
    )
    verificar(parser.parse_args().archivo)
