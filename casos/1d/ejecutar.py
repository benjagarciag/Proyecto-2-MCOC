"""Ejecuta el caso 1D y actualiza sus resultados en una carpeta fija."""

import argparse
from dataclasses import replace
import json
import os
from pathlib import Path
import sys
import subprocess

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "desarrollo"))
os.environ.setdefault("MPLCONFIGDIR", str(RAIZ / ".venv" / "cache" / "matplotlib"))

import matplotlib
matplotlib.use("Agg")  # Generar PNG sin requerir una ventana gráfica.
import matplotlib.pyplot as plt
import numpy as np

from mcplan.difusion_1d import Parametros1D, perfil_estacionario, resolver_1d, solucion_exacta
from mcplan.ejemplos_1d import resolver_ejemplo


def ejecutar_script(nombre, args):
    """Guardar la misma figura del script de clase, sin redibujarla."""
    scripts = {
        "dirichlet": ("01_1d_dirichlet_verification.py", "base"),
        "neumann": ("03_1d_neumann.py", "neumann"),
        "robin": ("04_1d_robin.py", "robin"),
        "calor_interno": ("05_calor_interno.py", "calor_interno"),
    }
    archivo, carpeta = scripts[nombre]
    salida = args.salida or RAIZ / "resultados" / "1d" / carpeta
    entorno = os.environ.copy()
    entorno.update(MPLBACKEND="Agg", MCOC_SIN_VENTANA="1", MCOC_SALIDA_1D=str(salida.resolve()))
    subprocess.run([sys.executable, str(Path(__file__).with_name("codigos") / archivo)],
                   env=entorno, check=True)
    print(f"{nombre}: {salida.resolve()}")


def ejecutar_dirichlet(args):
    try:
        archivo = args.parametros or Path(__file__).with_name("parametros.json")
        p = Parametros1D(**json.loads(archivo.read_text(encoding="utf-8")))
        cambios = {}
        for nombre, valor in (
            ("n_intervalos", args.intervalos), ("paso_tiempo_s", args.dt),
            ("tiempo_final_s", args.tiempo_final),
        ):
            if valor is not None:
                cambios[nombre] = valor
        p = replace(p, **cambios)
        r = resolver_1d(p)
    except (ValueError, TypeError, OSError):
        raise

    nombre_carpeta = "base" if p.perfil_inicial == "uniforme" else "verificacion_seno"
    salida = args.salida or RAIZ / "resultados" / "1d" / nombre_carpeta
    # Reutilizar la carpeta y actualizar los mismos archivos en cada ejecución.
    salida.mkdir(parents=True, exist_ok=True)

    exacta = (solucion_exacta(p, r.x_m, p.tiempo_final_s)
              if p.perfil_inicial == "seno" else None)
    estacionario = perfil_estacionario(p, r.x_m)
    pasos_perfiles = np.unique(np.rint(np.linspace(0, p.n_pasos, 20)).astype(int))

    fig, ax = plt.subplots(figsize=(8, 5), layout="constrained")
    colores = plt.cm.viridis(np.linspace(0, 1, len(pasos_perfiles)))
    for n, color in zip(pasos_perfiles, colores):
        ax.plot(r.x_m, r.temperatura_C[n], color=color)
    fig.colorbar(plt.cm.ScalarMappable(norm=plt.Normalize(0, max(p.tiempo_final_s / 60, 1e-12)),
                                     cmap="viridis"), ax=ax, label="Tiempo [min]")
    if exacta is not None:
        ax.plot(r.x_m, exacta, "k--", linewidth=1.5, label="Exacta al tiempo final")
    else:
        ax.plot(r.x_m, estacionario, "k--", linewidth=1.5, label="Estado estacionario")
    ax.set(xlabel="Posición [m]", ylabel="Temperatura [°C]", title="Enfriamiento por conducción 1D")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.savefig(salida / "perfiles_temperatura.png", dpi=160)
    plt.close(fig)

    print(f"r = {p.fourier:.6g}; dt efectivo = {p.dt_s:.8g} s; dt máximo = {p.dt_max_s:.6g} s")
    if exacta is not None:
        print(f"Error máximo final = {np.max(np.abs(r.temperatura_C[-1] - exacta)):.8f} K")
    else:
        print(f"Temperatura central final = {np.interp(p.longitud_m / 2, r.x_m, r.temperatura_C[-1]):.8f} °C")
    print(f"Resultados: {salida.resolve()}")


def ejecutar_adicional(nombre, args):
    r = resolver_ejemplo(nombre, args.intervalos, args.dt, args.tiempo_final)
    salida = args.salida or RAIZ / "resultados" / "1d" / nombre
    salida.mkdir(parents=True, exist_ok=True)
    titulos = {"neumann": "Neumann: extremo derecho adiabático",
               "robin": "Robin: intercambio con aire oscilante",
               "calor_interno": "Calor interno con extremos a 0 °C"}
    fig, ax = plt.subplots(figsize=(8, 5), layout="constrained")
    final_perfiles = max(float(r.tiempos_perfiles_s[-1]), 1e-12)
    for tiempo, perfil in zip(r.tiempos_perfiles_s, r.perfiles_C):
        ax.plot(r.x_m, perfil, color=plt.cm.viridis(tiempo/final_perfiles))
    fig.colorbar(plt.cm.ScalarMappable(norm=plt.Normalize(0, final_perfiles/3600), cmap="viridis"),
                 ax=ax, label="Tiempo [h]")
    ax.set(xlabel="Posición [m]", ylabel="Temperatura [°C]", title=titulos[nombre])
    ax.grid(alpha=0.25)
    fig.savefig(salida / "perfiles_temperatura.png", dpi=160)
    plt.close(fig)

    print(f"{nombre}: {salida.resolve()}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--caso", choices=["todos", "dirichlet", "neumann", "robin", "calor_interno"])
    parser.add_argument("--parametros", type=Path, help="Entradas de Dirichlet; sin --caso, ejecutar solo este caso")
    parser.add_argument("--intervalos", type=int)
    parser.add_argument("--dt", type=float)
    parser.add_argument("--tiempo-final", type=float)
    parser.add_argument("--salida", type=Path, help="Carpeta fija; con todos, contiene una subcarpeta por caso")
    args = parser.parse_args()
    seleccion = args.caso or ("dirichlet" if args.parametros is not None else "todos")
    if args.parametros is not None and seleccion not in ("dirichlet", "todos"):
        parser.error("--parametros corresponde al caso Dirichlet.")
    nombres = ["dirichlet", "neumann", "robin", "calor_interno"] if seleccion == "todos" else [seleccion]
    try:
        for nombre in nombres:
            salida = args.salida
            if seleccion == "todos" and salida is not None:
                carpeta = ("verificacion_seno" if args.parametros is not None and
                           "seno" == json.loads(args.parametros.read_text(encoding="utf-8")).get("perfil_inicial")
                           else "base") if nombre == "dirichlet" else nombre
                salida = salida / carpeta
            individuales = argparse.Namespace(**vars(args))
            individuales.salida = salida
            originales = all(valor is None for valor in
                             (args.parametros, args.intervalos, args.dt, args.tiempo_final))
            if originales:
                ejecutar_script(nombre, individuales)
            elif nombre == "dirichlet":
                ejecutar_dirichlet(individuales)
            else:
                ejecutar_adicional(nombre, individuales)
    except (ValueError, TypeError, OSError, subprocess.CalledProcessError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
