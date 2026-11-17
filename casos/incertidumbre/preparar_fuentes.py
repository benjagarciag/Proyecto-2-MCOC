"""Convierte las series Q(t) originales a acumulados para el solver."""
import csv
from pathlib import Path

import numpy as np


def main():
    carpeta = Path(__file__).resolve().parents[2] / "datos" / "hidratacion"
    datos = np.loadtxt(carpeta / "source_terms.txt")
    nombres = [f"M{n}_{campaña}" for campaña in ("SS", "22A") for n in range(1, 5)]
    for i, nombre in enumerate(nombres, 1):
        fuente = datos[:, i]
        fin = int(np.count_nonzero(np.isfinite(fuente)))
        potencia = fuente[:fin]
        edad_h = np.arange(fin)/6
        if (fin < 2 or not np.isfinite(potencia).all() or (potencia < 0).any()
                or not np.allclose(edad_h, datos[:fin, 0], atol=.00051, rtol=0)):
            raise ValueError(f"Serie inválida o con un hueco antes del final: {nombre}.")
        energia = np.r_[0, np.cumsum((potencia[:-1]+potencia[1:])*300)]
        with (carpeta / f"{nombre}.csv").open("w", newline="", encoding="utf-8") as archivo:
            tabla = csv.writer(archivo, lineterminator="\n")
            tabla.writerow(["edad_h", "acumulado"])
            tabla.writerows(zip(edad_h, energia))
        print(f"{nombre}: {energia[-1]/1e6:.3f} MJ/m³ hasta {edad_h[-1]:.3f} h")


if __name__ == "__main__":
    main()
