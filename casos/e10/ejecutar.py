"""Descarga o reabre un snapshot, e ilustra cómo su T de aire entra al borde."""
import argparse
from datetime import datetime
from pathlib import Path
import sys

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "desarrollo"))
from mcplan.clima import HoraClima, cargar_snapshot, descargar
from mcplan.entorno_termico import Capa, borde_aire, borde_suelo


def comparar_bordes(hora):
    # Ejemplo docente: celda de 0,5 m; propiedades elegidas solo para mostrar el efecto.
    geometria = dict(area_m2=.25, distancia_m=.25, k_W_mK=2.)
    T = 35.
    capas = (Capa(.020, .13, retiro_edad_h=72), Capa(.030, .040, retiro_edad_h=96))
    print(f"Aire: {hora.aire_C:.2f} °C; celda: {T:g} °C; h convectivo: 5 W/(m²·K).")
    print("Potencias entrantes por cara (negativo = el hormigón pierde calor):")
    for edad in (71.999, 72, 96):
        aire = borde_aire(**geometria, aire_C=hora.aire_C, h_W_m2K=5, edad_h=edad, capas=capas)
        print(f"  Edad {edad:6.3f} h: aire, P = {aire.potencia_entrante_W(T):+.3f} W")
    suelo = borde_suelo(**geometria, suelo_C=15, profundidad_m=.50, k_suelo_W_mK=1.2)
    print(f"  Base hacia suelo prescrito a 15 °C: P = {suelo.potencia_entrante_W(T):+.3f} W")
    if hora.solar_media_hora_previa_W_m2 is not None:
        # GHI representa la hora que termina en la marca del dato.
        superior = borde_aire(**geometria, aire_C=hora.aire_C, h_W_m2K=5, edad_h=96,
            solar_incidente_W_m2=hora.solar_media_hora_previa_W_m2, absortancia=.6)
        print(f"  Cara superior sin capas: aporte solar a la celda = {superior.solar_hacia_celda_W:.3f} W "
              "(irradiancia de la hora previa; ejemplo de coeficientes, no avance temporal).")
    print("Suelo, h, capas, horarios, absortancia y T de celda son valores docentes.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modos = parser.add_mutually_exclusive_group(required=True)
    modos.add_argument("--descargar", action="store_true")
    modos.add_argument("--snapshot", type=Path)
    modos.add_argument("--demo", action="store_true", help="Caso sin red, con aire y solar sintéticos.")
    parser.add_argument("--carpeta", type=Path, default=RAIZ / "datos/clima/forecasts")
    parser.add_argument("--inicio", type=datetime.fromisoformat,
                        help="Fecha/hora inicial ISO 8601 con offset para evaluar cobertura de 14 días.")
    args = parser.parse_args()
    try:
        if args.demo:
            print("DEMO SINTÉTICA: no corresponde a un forecast.")
            comparar_bordes(HoraClima(datetime.fromisoformat("2026-11-11T12:00:00+00:00"), 10, 3, 200))
            return
        ruta = descargar(args.carpeta) if args.descargar else args.snapshot
        meta, pronostico = cargar_snapshot(ruta)
        print(f"Snapshot: {ruta}")
        print(f"{meta['fuente']} | {meta['modelo_solicitado']} | descarga {meta['descargado_utc']}")
        print(f"{meta['primera_marca_utc']} → {meta['ultima_marca_utc']} | {meta['muestras_horarias']} marcas UTC")
        if args.inicio:
            c = pronostico.cobertura(args.inicio)
            n = c["horas_solicitadas"]
            print(f"Ventana {c['inicio_utc']} → {c['fin_exclusivo_utc']} (fin exclusivo)")
            for variable in ("aire", "viento", "solar"):
                cubiertas = c[f"horas_con_{variable}"]
                print(f"  {variable}: {cubiertas}/{n} h; faltan {n-cubiertas} h")
        descarga = datetime.fromisoformat(meta["descargado_utc"])
        muestra = next((h for h in pronostico.horas if h.tiempo_utc >= descarga and h.aire_C is not None), None)
        if muestra is None:
            print("No hay una hora futura con temperatura de aire válida en este snapshot.")
        else:
            print(f"Ejemplo de borde con la primera hora futura disponible: {muestra.tiempo_utc.isoformat()}")
            comparar_bordes(muestra)
    except (ValueError, OSError) as exc:
        parser.exit(1, f"E10: {exc}\n")


if __name__ == "__main__":
    main()
