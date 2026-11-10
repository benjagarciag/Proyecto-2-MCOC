"""Descarga aparte el bloque análogo de El Rosal (27-11 a 11-12 de 2025)."""
from datetime import date
from pathlib import Path
import sys

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "desarrollo"))
from mcplan.clima_historico import descargar_era5

if __name__ == "__main__":
    print(descargar_era5(RAIZ / "datos/clima/reanalisis", date(2025, 11, 27), date(2025, 12, 11)))
