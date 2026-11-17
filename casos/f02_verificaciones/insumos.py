"""Entradas congeladas para reproducir las verificaciones de F02."""
from hashlib import sha256
from importlib.util import find_spec
import json
from pathlib import Path
import re
import sys
from types import ModuleType

import numpy as np


RAIZ = Path(__file__).resolve().parents[2]
RESULTADOS_LUIS = RAIZ / "resultados/incertidumbre"
RESULTADOS = RAIZ / "resultados/f02_verificaciones"
CONFIG = RAIZ / "casos/incertidumbre/parametros.json"
HIDRATACION = RAIZ / "datos/hidratacion"
CONFIGURACIONES = Path(__file__).with_name("configuraciones.json")


def leer(ruta):
    return json.loads(ruta.read_text(encoding="utf-8"))


def coincide(ruta, esperado):
    datos = ruta.read_bytes()
    return esperado in (sha256(datos).hexdigest(), sha256(datos.replace(b"\r\n", b"\n")).hexdigest())


def publicadas():
    base = RESULTADOS_LUIS / "enfriamiento/u5_tope12"
    rutas = {
        "unica": base / "unica",
        "rapida": base / "separacion_3h",
        "referencia": base,
        "tras_colocacion": base / "unica/tras_colocacion",
    }
    return {nombre: leer(ruta / "resumen.json") for nombre, ruta in rutas.items()}


def par(registro):
    return registro["curva"], registro["clima"]


def imprimir(etiqueta, datos):
    print(etiqueta, json.dumps(datos, ensure_ascii=False), flush=True)


def _bloquear_lectura_ifc():
    """Permite importar el solver si solo se usa una máscara ya exportada."""
    def no_disponible(atributo):
        if atributo.startswith("__"):
            raise AttributeError(atributo)
        raise RuntimeError("El cálculo con máscara exportada no puede llamar a IfcOpenShell.")

    nombres = ("ifcopenshell", "ifcopenshell.geom", "ifcopenshell.util",
               "ifcopenshell.util.element", "ifcopenshell.util.unit")
    for nombre in nombres:
        modulo = ModuleType(nombre)
        modulo.__path__ = []
        modulo.__getattr__ = no_disponible
        sys.modules[nombre] = modulo
        padre, _, hijo = nombre.rpartition(".")
        if padre:
            setattr(sys.modules[padre], hijo, modulo)


def importar_solver(origen_geometria):
    sys.path[:0] = [str(RAIZ / "desarrollo"), str(RAIZ / "casos/incertidumbre")]
    if find_spec("ifcopenshell") is None:
        if origen_geometria == "ifc":
            raise SystemExit("Para --geometria ifc se requiere IfcOpenShell. Usa la máscara exportada para reproducir el cálculo sin volver a leer el IFC.")
        _bloquear_lectura_ifc()

    import comparar_controles as controles
    from mcplan.clima_historico import cargar_era5, serie_aire
    from mcplan.termica_fundacion import EnfriamientoInterior, EntornoFundacion, simular

    return controles, EnfriamientoInterior, EntornoFundacion, simular, cargar_era5, serie_aire


def leer_malla(controles, config, lado, origen_geometria):
    ruta_ifc = RAIZ / config["archivo_ifc"]
    if origen_geometria == "ifc":
        fundacion = controles.extraer_fundacion_ifc(ruta_ifc)
        voxeles = controles.voxelizar_fundacion(fundacion, pasos_m=(lado,) * 3)
        asignacion = controles.asignar_vertidas(fundacion, voxeles)
        return asignacion.vertida_id, voxeles.grilla.origen_m

    html = (RAIZ / "resultados/e12/visualizador.html").read_text(encoding="utf-8")
    payload = re.search(r'<script id="e07-data" type="application/json">(.*?)</script>', html, re.S)
    if payload is None:
        raise ValueError("El HTML E12 no contiene la geometría voxelizada.")
    datos = json.loads(payload[1])
    if not coincide(ruta_ifc, datos["sha256_ifc"]):
        raise ValueError("La máscara exportada no corresponde al IFC de la rama.")
    malla = next((g for g in datos["grillas"] if g["h"] == lado), None)
    if malla is None:
        raise ValueError("La malla solicitada no está en el HTML E12.")
    ids = np.repeat(*zip(*malla["rle"])).astype(int).reshape(malla["forma"])
    if np.count_nonzero(ids) != malla["ocupados"] or set(np.unique(ids)) != set(range(6)):
        raise ValueError("La malla exportada no conserva los cinco identificadores de vertida.")
    return ids, malla["origen"]
