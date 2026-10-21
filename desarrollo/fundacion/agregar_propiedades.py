r"""Punto 23 de la guía: incorporar propiedades docentes a las cinco vertidas.

Ejecutar desde la raíz: .\.venv\Scripts\python.exe desarrollo/fundacion/agregar_propiedades.py
Actualiza fundacion.ifc; también acepta entrada.ifc [salida.ifc].
"""

import argparse
import os
from pathlib import Path
import tempfile

import ifcopenshell
import ifcopenshell.api.pset
import ifcopenshell.util.element


NOMBRE_SET = "UANDES_HormigonMasivo"
CARPETA = Path(__file__).resolve().parent


def agregar_propiedades(entrada: Path, salida: Path) -> None:
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

    # Escribir primero un temporal: el IFC actual solo se reemplaza al terminar.
    with tempfile.NamedTemporaryFile(dir=salida.parent, prefix=".fundacion-", suffix=".tmp", delete=False) as archivo:
        temporal = Path(archivo.name)
    try:
        modelo.write(str(temporal))
        ifcopenshell.open(str(temporal))
        os.replace(temporal, salida)
    finally:
        temporal.unlink(missing_ok=True)
    print(f"IFC con propiedades: {salida}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entrada", nargs="?", type=Path, default=CARPETA / "fundacion.ifc")
    parser.add_argument("salida", nargs="?", type=Path, help="Si se omite, actualizar la entrada")
    args = parser.parse_args()
    agregar_propiedades(args.entrada, args.salida or args.entrada)


if __name__ == "__main__":
    main()
