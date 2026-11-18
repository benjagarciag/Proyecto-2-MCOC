"""Prepara datos e imágenes de la presentación F02 a partir de resultados existentes.

No ejecuta simulaciones: solo lee CSV/JSON/NPZ ya calculados y genera
recursos en ``entregas/F02/presentacion/recursos/``.
"""
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

RAIZ = Path(__file__).resolve().parents[3]
EVID = RAIZ / "entregas/F02/evidencia_circuitos"
CORRIDA = RAIZ / "resultados/comparacion_circuitos/q60/malla_0.4/M4_SS_ERA5-2024"
SALIDA = Path(__file__).resolve().parent / "recursos"
SALIDA.mkdir(exist_ok=True)

FUENTE = "Segoe UI"
plt.rcParams.update({"font.family": FUENTE, "font.size": 20})


def leer_csv(ruta: Path) -> list[dict]:
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


# ---------------------------------------------------------------- historia S5
hist = json.load(open(f"{CORRIDA}.json", encoding="utf-8"))["historia"]
t = np.array([r["tiempo_h"] for r in hist])
idx = [int(np.argmin(abs(t - h))) for h in range(0, 601, 2)]
historia = {
    "t": [round(float(t[i]), 3) for i in idx],
    "Tmax": [round(hist[i]["Tmax_C"], 3) for i in idx],
    "S25": [round(hist[i]["Tmin_S25_C"], 3) for i in idx],
    "dT": [round(hist[i]["DeltaT_K"], 3) for i in idx],
}
i_pico = int(np.argmax([r["Tmax_C"] for r in hist]))
pico = {"t": hist[i_pico]["tiempo_h"], "T": hist[i_pico]["Tmax_C"]}

# ------------------------------------------------------------- fuentes S6/B05
filas = []
for linea in open(RAIZ / "datos/hidratacion/source_terms.txt", encoding="utf-8"):
    if linea.startswith("#") or not linea.strip():
        continue
    filas.append([float(x) if x.lower() != "nan" else None for x in linea.split()])
fuentes_t = []
fuentes = {k: [] for k in ["M1_SS", "M2_SS", "M3_SS", "M4_SS", "M1_22A", "M2_22A", "M3_22A", "M4_22A"]}
for fila in filas[::6]:  # cada hora
    if fila[0] > 240.5:
        break
    fuentes_t.append(round(fila[0], 3))
    for j, k in enumerate(fuentes):
        v = fila[1 + j]
        fuentes[k].append(None if v is None else round(v, 2))

# --------------------------------------------------------------- clima S6/B02
clima = {}
for anio in (2023, 2024, 2025):
    ruta = next((RAIZ / "datos/clima/reanalisis").glob(f"era5_{anio}-11-19_*.json"))
    d = json.load(open(ruta, encoding="utf-8"))["respuesta"]["hourly"]
    t0 = datetime(anio, 11, 19, 13, tzinfo=timezone.utc).timestamp()
    rel = [(ti - t0) / 3600 for ti in d["time"]]
    serie = [(h, T) for h, T in zip(rel, d["temperature_2m"]) if 0 <= h <= 336]
    clima[str(anio)] = {"t": [s[0] for s in serie], "T": [s[1] for s in serie]}

# ------------------------------------------------------------ tablas y capas
planes = leer_csv(EVID / "comparacion_planes.csv")
crono = leer_csv(EVID / "cronogramas.csv")
sens = leer_csv(EVID / "sensibilidad_espacial.csv")
esc = leer_csv(EVID / "escenarios.csv")
fila_b09 = next(r for r in esc if r["plan"] == "q60" and r["lado_m"] == "0.4"
                and r["horizonte_h"] == "600" and r["curva"] == "M4_SS" and r["clima"] == "ERA5-2024")

npz = np.load(f"{CORRIDA}.npz")
ids = npz["ids"]
origen = npz["origen_m"]
lado = float(npz["lado_m"])
j0 = int(round((0.0 - origen[1]) / lado - 0.5))  # fila y = 0
seccion = []
for k, c in enumerate([r for r in crono if r["plan"] == "q60"]):
    cols = np.where(ids[k, j0, :] > 0)[0]
    seccion.append({
        "capa": int(c["capa"]), "z0": float(c["z_inf_m"]), "z1": float(c["z_sup_m"]),
        "x0": float(origen[0] + lado * cols.min()), "x1": float(origen[0] + lado * (cols.max() + 1)),
        "inicio_h": float(c["inicio_h"]), "fin_h": float(c["fin_h"]), "V": float(c["volumen_m3"]),
    })

json.dump({
    "historia": historia, "pico": pico, "fuentes_t": fuentes_t, "fuentes": fuentes,
    "clima": clima, "planes": planes, "cronogramas": crono, "sensibilidad": sens,
    "fila_b09": fila_b09, "seccion": seccion,
}, open(SALIDA / "datos.json", "w", encoding="utf-8"), ensure_ascii=False)

# ------------------------------------------------- vista isométrica S1 (voxel)
def caras_voxel(mask: np.ndarray):
    """Devuelve caras exteriores (lista de 4 vértices) y su capa."""
    nz, ny, nx = mask.shape
    caras, capas = [], []
    zcap = [(s["z0"], s["z1"]) for s in seccion]
    for k in range(nz):
        za, zb = zcap[k]
        for j in range(ny):
            for i in range(nx):
                if not mask[k, j, i]:
                    continue
                x0, y0 = origen[0] + lado * i, origen[1] + lado * j
                x1, y1 = x0 + lado, y0 + lado
                def vecino(dk, dj, di):
                    kk, jj, ii = k + dk, j + dj, i + di
                    return 0 <= kk < nz and 0 <= jj < ny and 0 <= ii < nx and mask[kk, jj, ii]
                if not vecino(1, 0, 0):
                    caras.append([(x0, y0, zb), (x1, y0, zb), (x1, y1, zb), (x0, y1, zb)]); capas.append((k, "top"))
                if not vecino(0, -1, 0):
                    caras.append([(x0, y0, za), (x1, y0, za), (x1, y0, zb), (x0, y0, zb)]); capas.append((k, "front"))
                if not vecino(0, 0, -1):
                    caras.append([(x0, y0, za), (x0, y1, za), (x0, y1, zb), (x0, y0, zb)]); capas.append((k, "left"))
                if not vecino(0, 0, 1):
                    caras.append([(x1, y0, za), (x1, y1, za), (x1, y1, zb), (x1, y0, zb)]); capas.append((k, "right"))
                if not vecino(0, 1, 0):
                    caras.append([(x0, y1, za), (x1, y1, za), (x1, y1, zb), (x0, y1, zb)]); capas.append((k, "back"))
    return caras, capas


mask = ids > 0
caras, capas = caras_voxel(mask)
luz = {"top": 1.0, "front": 0.62, "left": 0.78, "right": 0.5, "back": 0.5}


def iso(nombre: str, base_rgb, borde: str, por_capa: bool = False):
    fig = plt.figure(figsize=(10, 7), dpi=200)
    ax = fig.add_subplot(111, projection="3d")
    ax.set_proj_type("ortho")
    cols = []
    cmap = plt.get_cmap("YlGnBu")
    for k, tipo in capas:
        base = np.array(cmap(0.25 + 0.6 * k / 10)[:3]) if por_capa else np.array(base_rgb)
        cols.append(tuple(np.clip(base * luz[tipo], 0, 1)))
    pc = Poly3DCollection(caras, facecolors=cols, edgecolors=borde, linewidths=0.15)
    ax.add_collection3d(pc)
    ax.set_xlim(-9, 9); ax.set_ylim(-9, 9); ax.set_zlim(0, 4.3)
    ax.set_box_aspect((18, 18, 4.3 * 1.6))
    ax.view_init(elev=24, azim=-58)
    ax.set_axis_off()
    fig.subplots_adjust(0, 0, 1, 1)
    fig.savefig(SALIDA / nombre, transparent=True, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    from PIL import Image
    im = Image.open(SALIDA / nombre)
    im.crop(im.getchannel("A").getbbox()).save(SALIDA / nombre)


iso("iso_oscura.png", (0.62, 0.66, 0.68), "#2a3640")
iso("iso_capas.png", None, "#ffffff", por_capa=True)

# -------------------------------------------------------- corte a 428 h (S5)
campo = npz["comun_428h_T_C"]
fig, ax = plt.subplots(figsize=(9, 4.4), dpi=200)
plano = np.where(ids[:, j0, :] > 0, campo[:, j0, :], np.nan)
xs = origen[0] + lado * np.arange(ids.shape[2] + 1)
zs = [0.0] + [s["z1"] for s in seccion]
m = ax.pcolormesh(xs, zs, np.ma.masked_invalid(plano), cmap="inferno", vmin=8, vmax=35, shading="flat")
ax.set_aspect("equal")
ax.set_xlim(-9.2, 9.2); ax.set_ylim(0, 4.5)
ax.set_xlabel("x [m]"); ax.set_ylabel("z [m]")
ax.set_xticks([-9, -4.5, 0, 4.5, 9]); ax.set_yticks([0, 2, 4])
for s in ax.spines.values():
    s.set_visible(False)
cb = fig.colorbar(m, ax=ax, orientation="horizontal", fraction=0.08, pad=0.28, aspect=40)
cb.set_label("Temperatura de centro [°C]", fontsize=18)
cb.set_ticks([10, 15, 20, 25, 30, 35])
ax.tick_params(labelsize=17)
fig.savefig(SALIDA / "corte_428h.png", bbox_inches="tight", pad_inches=0.05, transparent=True)
plt.close(fig)

print("Recursos en", SALIDA)
