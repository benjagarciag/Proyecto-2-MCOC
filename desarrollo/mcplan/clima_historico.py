"""Escenario análogo ERA5 de El Rosal, conservado aparte de los forecasts."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

from .clima import SITIO, UNIDADES, _utc, leer_respuesta


def descargar_era5(carpeta, fecha_inicio, fecha_fin):
    if fecha_fin < fecha_inicio:
        raise ValueError("Intervalo histórico invertido.")
    url = "https://archive-api.open-meteo.com/v1/archive?" + urlencode({
        "latitude": SITIO["latitud"], "longitude": SITIO["longitud"], "models": "era5",
        "start_date": fecha_inicio.isoformat(), "end_date": fecha_fin.isoformat(),
        "hourly": ",".join(UNIDADES), "wind_speed_unit": "ms", "temperature_unit": "celsius",
        "timeformat": "unixtime", "timezone": "GMT",
    })
    with urlopen(url, timeout=45) as conexion:
        respuesta = json.load(conexion)
    horas = leer_respuesta(respuesta).horas
    instante = datetime.now(timezone.utc)
    metadata = dict(tipo="reanalisis", fuente="Open-Meteo Historical Weather API",
                    modelo_solicitado="era5", descargado_utc=instante.isoformat(),
                    coordenadas_solicitadas=SITIO, unidades=UNIDADES, variables=list(UNIDADES),
                    zona_horaria="UTC", url=url, muestras_horarias=len(horas),
                    primera_marca_utc=horas[0].tiempo_utc.isoformat(),
                    ultima_marca_utc=horas[-1].tiempo_utc.isoformat())
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / f"era5_{fecha_inicio}_{fecha_fin}_{instante:%Y%m%dT%H%M%S%fZ}.json"
    with ruta.open("x", encoding="utf-8") as archivo:
        json.dump(dict(version=1, metadata=metadata, respuesta=respuesta), archivo,
                  ensure_ascii=False, indent=2, allow_nan=False)
        archivo.write("\n")
    return ruta


def cargar_era5(ruta):
    with Path(ruta).open(encoding="utf-8") as archivo:
        contenido = json.load(archivo)
    meta = contenido["metadata"]
    if (contenido.get("version") != 1 or meta.get("tipo") != "reanalisis"
            or meta.get("modelo_solicitado") != "era5"
            or meta.get("coordenadas_solicitadas") != SITIO):
        raise ValueError("Se esperaba el reanálisis ERA5 de El Rosal.")
    return meta, leer_respuesta(contenido["respuesta"])


def serie_aire(pronostico, inicio, horizonte_h):
    """Marcas horarias desde el inicio hasta el final inclusive, sin rellenar huecos."""
    inicio = _utc(inicio)
    if (inicio.minute or inicio.second or inicio.microsecond
            or type(horizonte_h) is not int or horizonte_h <= 0):
        raise ValueError("Inicio alineado a una hora y horizonte entero positivo.")
    por_hora = {h.tiempo_utc: h.aire_C for h in pronostico.horas}
    resultado = []
    for i in range(horizonte_h+1):
        t = inicio+timedelta(hours=i)
        valor = por_hora.get(t)
        if valor is None:
            raise ValueError(f"Falta temperatura del aire a {t.isoformat()}; no se extrapola.")
        resultado.append(valor)
    return resultado
