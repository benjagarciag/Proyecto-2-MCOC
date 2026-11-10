from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse

import pytest

from mcplan.bordes_termicos import Robin, coeficientes_cara
from mcplan.clima import SITIO, UNIDADES, cargar_snapshot, guardar_snapshot, leer_respuesta, url_pronostico
from mcplan.entorno_termico import Capa, borde_aire, borde_suelo

INICIO = datetime(2026, 11, 27, 13, tzinfo=timezone.utc)
CARA = dict(area_m2=.25, distancia_m=.25, k_W_mK=2.)


def respuesta():
    t = int(INICIO.timestamp())
    return {"utc_offset_seconds": 0, "hourly_units": {"time": "unixtime", **UNIDADES},
            "hourly": {"time": [t, t+3600, t+7200], "temperature_2m": [10, 11, None],
                       "wind_speed_10m": [2, 3, 4], "shortwave_radiation": [0, 200, 300]}}


def test_url_de_la_ubicacion_asignada():
    consulta = parse_qs(urlparse(url_pronostico()).query)
    assert consulta["latitude"] == [str(SITIO["latitud"])]
    assert consulta["longitude"] == [str(SITIO["longitud"])]
    assert consulta["models"] == ["gfs_global"]
    assert consulta["timeformat"] == ["unixtime"]


def test_snapshots_exclusivos_y_cobertura(tmp_path):
    a = guardar_snapshot(tmp_path, respuesta(), url_pronostico(), INICIO)
    original = a.read_bytes()
    b = guardar_snapshot(tmp_path, respuesta(), url_pronostico(), INICIO)
    assert a != b and a.read_bytes() == original
    meta, clima = cargar_snapshot(b)
    assert meta["muestras_horarias"] == 3
    c = clima.cobertura(INICIO)
    assert (c["horas_solicitadas"], c["horas_con_aire"], c["horas_con_viento"],
            c["horas_con_solar"]) == (336, 2, 3, 2)
    assert clima.cobertura(INICIO + timedelta(days=1))["horas_con_aire"] == 0


@pytest.mark.parametrize("fallo", ["unidad", "tiempo", "longitud"])
def test_rechaza_respuesta_invalida(fallo):
    r = respuesta()
    if fallo == "unidad":
        r["hourly_units"]["wind_speed_10m"] = "km/h"
    elif fallo == "tiempo":
        r["hourly"]["time"][1] += 3600
    else:
        r["hourly"]["temperature_2m"].pop()
    with pytest.raises(ValueError):
        leer_respuesta(r)


def test_robin_sin_capas_equivale_al_borde_previo():
    aire = borde_aire(**CARA, aire_C=10, h_W_m2K=5, edad_h=0)
    assert (aire.H_W_K, aire.B_W) == pytest.approx(coeficientes_cara(Robin(5, 10), .25, .25, 2))
    assert aire.potencia_entrante_W(10) == pytest.approx(0)


def test_retirar_moldaje_no_retira_aislacion_antes_de_su_evento():
    capas = (Capa(.02, .13, 72), Capa(.03, .04, 96))
    antes, retiro, desnudo = [borde_aire(**CARA, aire_C=10, h_W_m2K=5, edad_h=t, capas=capas)
                             for t in (71.999, 72, 96)]
    assert antes.H_W_K < retiro.H_W_K < desnudo.H_W_K
    assert retiro.H_W_K == pytest.approx(.25/(.25/2+.03/.04+1/5))
    assert antes.potencia_entrante_W(30) > retiro.potencia_entrante_W(30) > desnudo.potencia_entrante_W(30)


def test_solar_balance_de_superficie_y_aislamiento():
    aire = borde_aire(**CARA, aire_C=10, h_W_m2K=5, edad_h=0,
                     solar_incidente_W_m2=100, absortancia=.6)
    P = aire.potencia_entrante_W(30)
    T_superficie = 30 + (P/.25)*(.25/2)
    assert P == pytest.approx(.25*(60 + 5*(10-T_superficie)))
    aislado = borde_aire(**CARA, aire_C=10, h_W_m2K=0, edad_h=0)
    assert aislado.potencia_entrante_W(30) == 0


def test_suelo_resistencias_serie_y_signo():
    suelo = borde_suelo(**CARA, suelo_C=15, profundidad_m=.5, k_suelo_W_mK=1,
                        contacto_m2K_W=.1)
    assert suelo.potencia_entrante_W(35) == pytest.approx(.25*(15-35)/(.125+.5+.1))
    assert suelo.potencia_entrante_W(10) > 0


@pytest.mark.parametrize("campo,valor", [
    ("modelo_solicitado", "era5"),
    ("unidades", {}),
    ("muestras_horarias", 999),
    ("ultima_marca_utc", "2026-12-31T00:00:00+00:00"),
    ("descargado_utc", "2026-11-10T10:00:00"),
])
def test_rechaza_metadata_inconsistente(tmp_path, campo, valor):
    import json
    ruta = guardar_snapshot(tmp_path, respuesta(), url_pronostico(), INICIO)
    snapshot = json.loads(ruta.read_text(encoding="utf-8"))
    snapshot["metadata"][campo] = valor
    ruta.write_text(json.dumps(snapshot), encoding="utf-8")
    with pytest.raises(ValueError):
        cargar_snapshot(ruta)


def test_snapshot_incompleto_tiene_error_descriptivo(tmp_path):
    ruta = tmp_path / "incompleto.json"
    ruta.write_text('{"version": 1}', encoding="utf-8")
    with pytest.raises(ValueError, match="incompleto"):
        cargar_snapshot(ruta)
