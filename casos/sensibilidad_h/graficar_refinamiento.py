"""Grafica resultados existentes del refinamiento; no importa ni ejecuta el solver."""
import json
import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
os.environ.setdefault("MPLCONFIGDIR", str(RAIZ / ".venv/cache/matplotlib"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def leer(ruta):
    return json.loads(ruta.read_text(encoding="utf-8"))


def main():
    carpeta = RAIZ / "resultados/sensibilidad_h"
    base = leer(carpeta / "h_20/publicada_unica.json")
    grupos = [base["corridas"]]
    tiempos = [base["duracion_auditoria_s"] / 60]
    for nombre in ("malla_025_paso900", "malla_050_paso450"):
        archivos = sorted((carpeta / "refinamiento_unica_h20" / nombre).glob("publicada_unica_*.json"))
        matrices = [leer(p) for p in archivos]
        grupos.append([f for d in matrices for f in d["corridas"]])
        tiempos.append(sum(d["duracion_auditoria_s"] for d in matrices) / 60)
    for filas in grupos:
        if len(filas) != 24 or len({(f['curva'],f['clima']) for f in filas}) != 24:
            raise ValueError("Se requieren las matrices completas de las tres resoluciones.")
    etiquetas = ["Base\n0,50 m / 900 s", "Malla fina\n0,25 m / 900 s", "Paso menor\n0,50 m / 450 s"]
    colores = ["#52647e", "#178073", "#ce8530"]
    plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(1, 3, figsize=(15, 6.4))
    x = np.arange(3)
    maximos = [max(f["DeltaTmax"]["valor"] for f in g) for g in grupos]
    cercano = [next(f["DeltaTmax"]["valor"] for f in g
                    if (f["curva"],f["clima"]) == ("M4_SS", "ERA5-2025")) for g in grupos]
    ax = axes[0]
    ax.plot(x,maximos,"o-",color="#b74a48",label="M4_SS × 2024 (único fallo)")
    ax.plot(x,cercano,"s-",color="#178073",label="M4_SS × 2025 (cercano)")
    ax.axhline(20,color="#555",ls="--",lw=1,label="Límite: 20 °C")
    for valores,offset in ((maximos, .065),(cercano,-.16)):
        for i,v in enumerate(valores):
            ax.text(i,v+offset,f"{v:.3f}",ha="center",fontsize=10)
    ax.set(title="Diferencial: clasificación estable",ylabel="Máximo diferencial [°C]",ylim=(19.55,21.55))
    ax.legend(loc="upper center",bbox_to_anchor=(.5,-.20),fontsize=9,frameon=False)
    ax.set_xlim(-.3,2.3)
    ax = axes[1]
    temperaturas = [max(f["Tmax"]["valor"] for f in g) for g in grupos]
    ax.bar(x,temperaturas,color=colores,width=.55)
    for i,v in enumerate(temperaturas):
        ax.text(i,v+.004,f"{v:.3f}",ha="center")
    ax.set(title="Temperatura máxima",ylabel="Peor Tmax [°C]",ylim=(46.70,46.83))
    ax.text(.5,.04,"Eje ampliado: todas están bajo 70 °C",transform=ax.transAxes,
            ha="center",fontsize=9,color="#555")
    ax = axes[2]
    ax.bar(x,tiempos,color=colores,width=.55)
    for i,v in enumerate(tiempos):
        ax.text(i,v+.12,f"{v:.2f} min",ha="center")
    ax.set(title="Costo observado de las corridas",ylabel="Tiempo acumulado [min]",ylim=(0,max(tiempos)*1.18))
    ax.text(.5,.03,"24 pares; ventanas de 336 y 600 h",transform=ax.transAxes,
            ha="center",fontsize=9,color="#555")
    for ax in axes:
        ax.set_xticks(x,etiquetas,fontsize=9)
        ax.grid(axis="y",alpha=.18)
        ax.set_axisbelow(True)
    fig.suptitle("Sensibilidad numérica | Vertida única, h = 20 W/(m²·K)",fontsize=16,fontweight="bold",y=.98)
    fig.text(.5,.035,"P conjunta = 1/24 = 4,17 % en las tres resoluciones. Pesos iguales y enfriamiento desde 6 h.\n"
             "Dos niveles por variable muestran sensibilidad; no prueban una resolución óptima ni una cota del error.\n"
             "Tiempos de ejecuciones separadas del usuario; comparación orientativa, sin benchmark controlado.",
             ha="center",fontsize=10,color="#444")
    fig.subplots_adjust(left=.06,right=.985,top=.86,bottom=.38,wspace=.34)
    destino=carpeta / "figuras"
    destino.mkdir(exist_ok=True)
    fig.savefig(destino / "refinamiento_unica_h20.png",dpi=180,facecolor="white")
    plt.close(fig)
    print(destino / "refinamiento_unica_h20.png")


if __name__ == "__main__":
    main()
