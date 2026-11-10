"""Primer cliente y lector de pronósticos horarios para El Rosal (UTC, SI)."""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import json
import math
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen
from uuid import uuid4

SITIO = {"latitud": -37.277929, "longitud": -72.368271}
ENDPOINT = "https://api.open-meteo.com/v1/forecast"
MODELO = "gfs_global"
UNIDADES = {"temperature_2m": "°C", "wind_speed_10m": "m/s", "shortwave_radiation": "W/m²"}
HORA = timedelta(hours=1)


def _utc(t):
    if t.tzinfo is None or t.utcoffset() is None:
        raise ValueError("Se requiere una fecha con huso horario explícito.")
    return t.astimezone(timezone.utc)


def url_pronostico(dias=16):
    if type(dias) is not int or not 1 <= dias <= 16:
        raise ValueError("forecast_days debe ser un entero entre 1 y 16.")
    return ENDPOINT + "?" + urlencode({
        "latitude": SITIO["latitud"], "longitude": SITIO["longitud"],
        "models": MODELO, "forecast_days": dias, "hourly": ",".join(UNIDADES),
        "wind_speed_unit": "ms", "temperature_unit": "celsius",
        "timeformat": "unixtime", "timezone": "GMT",
    })


@dataclass(frozen=True)
class HoraClima:
    tiempo_utc: datetime
    aire_C: float | None
    viento_10m_m_s: float | None
    solar_media_hora_previa_W_m2: float | None


@dataclass(frozen=True)
class Pronostico:
    horas: tuple[HoraClima, ...]

    def cobertura(self, inicio, dias=14):
        """Ventana [inicio, inicio + días), alineada a una hora.

        Cuenta horas con T de aire y, por separado, disponibilidad de viento
        y solar. No inventa valores ni extrapola fuera del snapshot.
        """
        inicio = _utc(inicio)
        if inicio.minute or inicio.second or inicio.microsecond:
            raise ValueError("El inicio de la ventana debe coincidir con una hora.")
        if type(dias) is not int or dias < 1:
            raise ValueError("Se requiere un número entero positivo de días.")
        fin = inicio + timedelta(days=dias)
        horas = [x for x in self.horas if inicio <= x.tiempo_utc < fin]
        return {
            "inicio_utc": inicio.isoformat(), "fin_exclusivo_utc": fin.isoformat(),
            "horas_solicitadas": dias * 24,
            "horas_con_aire": sum(x.aire_C is not None for x in horas),
            "horas_con_viento": sum(x.viento_10m_m_s is not None for x in horas),
            # El dato con marca t representa el intervalo [t-1 h, t).
            "horas_con_solar": sum(x.solar_media_hora_previa_W_m2 is not None
                                   for x in self.horas if inicio < x.tiempo_utc <= fin),
        }


def leer_respuesta(respuesta):
    """Valida unidad y cronología; mantiene null como faltante."""
    try:
        datos = respuesta["hourly"]
        tiempos = datos["time"]
        unidades = respuesta["hourly_units"]
        series = [datos[v] for v in UNIDADES]
        if respuesta["utc_offset_seconds"] != 0 or unidades["time"] != "unixtime":
            raise ValueError("La respuesta debe usar UTC y segundos Unix.")
        if any(unidades[v] != u for v, u in UNIDADES.items()):
            raise ValueError("Unidades meteorológicas inesperadas.")
        if not tiempos or any(type(t) is not int or t % 3600 for t in tiempos):
            raise ValueError("Los tiempos deben ser horas Unix enteras.")
        if any(b-a != 3600 for a, b in zip(tiempos, tiempos[1:])):
            raise ValueError("Se requieren horas contiguas, sin duplicados.")
        if any(len(s) != len(tiempos) for s in series):
            raise ValueError("Longitudes distintas en las series horarias.")
        for i, serie in enumerate(series):
            if any(v is not None and (type(v) not in (int, float)
                   or not math.isfinite(v) or (i > 0 and v < 0)) for v in serie):
                raise ValueError("Dato meteorológico inválido.")
        return Pronostico(tuple(HoraClima(datetime.fromtimestamp(t, timezone.utc), *v)
                                for t, *v in zip(tiempos, *series)))
    except (KeyError, TypeError) as exc:
        raise ValueError("Respuesta meteorológica incompleta.") from exc


def guardar_snapshot(carpeta, respuesta, url, descargado_en):
    pronostico = leer_respuesta(respuesta)
    instante = _utc(descargado_en)
    meta = {
        "tipo": "forecast", "fuente": "Open-Meteo", "modelo_solicitado": MODELO,
        "url": url, "descargado_utc": instante.isoformat(),
        "coordenadas_solicitadas": SITIO, "zona_horaria": "UTC",
        "variables": list(UNIDADES), "unidades": UNIDADES,
        "primera_marca_utc": pronostico.horas[0].tiempo_utc.isoformat(),
        "ultima_marca_utc": pronostico.horas[-1].tiempo_utc.isoformat(),
        "muestras_horarias": len(pronostico.horas),
    }
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / f"{instante:%Y%m%dT%H%M%S%fZ}_{uuid4().hex[:8]}.json"
    contenido = json.dumps({"version": 1, "metadata": meta, "respuesta": respuesta},
                           ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    # Creación exclusiva: nunca reemplaza una descarga previa.
    with ruta.open("x", encoding="utf-8") as archivo:
        archivo.write(contenido)
    return ruta


def descargar(carpeta, dias=16):
    url = url_pronostico(dias)
    with urlopen(url, timeout=25) as conexion:
        respuesta = json.load(conexion)
    return guardar_snapshot(carpeta, respuesta, url, datetime.now(timezone.utc))


def validar_snapshot(snapshot, tipo, modelo):
    try:
        meta = snapshot["metadata"]
        clima = leer_respuesta(snapshot["respuesta"])
        _utc(datetime.fromisoformat(meta["descargado_utc"]))
        if (snapshot.get("version") != 1 or meta.get("tipo") != tipo
                or meta.get("modelo_solicitado") != modelo
                or meta.get("coordenadas_solicitadas") != SITIO
                or meta.get("zona_horaria") != "UTC"
                or meta.get("unidades") != UNIDADES
                or meta.get("variables") != list(UNIDADES)
                or meta.get("muestras_horarias") != len(clima.horas)
                or meta.get("primera_marca_utc") != clima.horas[0].tiempo_utc.isoformat()
                or meta.get("ultima_marca_utc") != clima.horas[-1].tiempo_utc.isoformat()
                or not meta.get("fuente") or not meta.get("url")):
            raise ValueError("Metadata meteorológica inconsistente con la respuesta.")
        return meta, clima
    except (KeyError, TypeError, AttributeError) as exc:
        raise ValueError("Snapshot meteorológico incompleto.") from exc


def cargar_snapshot(ruta):
    with Path(ruta).open(encoding="utf-8") as archivo:
        snapshot = json.load(archivo)
    return validar_snapshot(snapshot, "forecast", MODELO)
