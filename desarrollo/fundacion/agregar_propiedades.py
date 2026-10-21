r"""Punto 23 de la guía: incorporar propiedades docentes a las cinco vertidas.

Ejecutar desde la raíz: .\.venv\Scripts\python.exe desarrollo/fundacion/agregar_propiedades.py
También acepta dos rutas: entrada.ifc salida.ifc.
"""

import argparse
from pathlib import Path

import ifcopenshell
import ifcopenshell.api.pset
import ifcopenshell.util.element


NOMBRE_SET = "UANDES_HormigonMasivo"
CARPETA = Path(__file__).resolve().parent


def agregar_propiedades(entrada: Path, salida: Path) -> None:
    if entrada.resolve() == salida.resolve():
        raise ValueError("La salida debe ser distinta de la entrada para conservar el original.")

    modelo = ifcopenshell.open(str(entrada))
    vertidas = []
    # Validar todos los nombres antes de modificar o escribir el modelo.
    for numero in range(1, 6):
        nombre = f"Vertida_{numero:02d}"
        candidatos = [p for p in modelo.by_type("IfcProduct") if p.Name == nombre]
        if len(candidatos) != 1:
            raise ValueError(f"Se esperaba una única {nombre}; se encontraron {len(candidatos)}.")
        vertidas.append(candidatos[0])

    for numero, vertida in enumerate(vertidas, start=1):
        # Valores del ejemplo docente de §24; no constituyen un plan validado.
        propiedades = {
            "VertidaID": numero,
            "Inicio_h": float((numero - 1) * 6),
            "TemperaturaColocacion_C": 18.0,
            "TipoHormigon": "M1",
            "Moldaje": "TBD",
            "Aislacion": "TBD",
            "RetiroMoldaje_h": 72.0,
        }
        existentes = ifcopenshell.util.element.get_pset(
            vertida, NOMBRE_SET, should_inherit=False
        )
        if existentes:
            pset = modelo.by_id(existentes["id"])
            # Completar campos faltantes sin borrar decisiones ya guardadas.
            propiedades = {k: v for k, v in propiedades.items() if k not in existentes}
        else:
            pset = ifcopenshell.api.pset.add_pset(
                modelo, product=vertida, name=NOMBRE_SET
            )
        if propiedades:
            ifcopenshell.api.pset.edit_pset(modelo, pset=pset, properties=propiedades)
        print(f"OK: {vertida.Name}")

    modelo.write(str(salida))
    print(f"IFC con propiedades: {salida}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entrada", nargs="?", type=Path, default=CARPETA / "fundacion.ifc")
    parser.add_argument("salida", nargs="?", type=Path, default=CARPETA / "fundacion_props.ifc")
    args = parser.parse_args()
    agregar_propiedades(args.entrada, args.salida)


if __name__ == "__main__":
    main()
