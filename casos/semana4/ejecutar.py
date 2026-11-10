"""E11: 48 h de forecast. E12: 336 h de escenario análogo ERA5."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import sys
import subprocess

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "desarrollo"))
os.environ.setdefault("MPLCONFIGDIR", str(RAIZ / ".venv/cache/matplotlib"))
import numpy as np

from mcplan.bim import extraer_fundacion_ifc
from mcplan.clima import cargar_snapshot
from mcplan.clima_historico import cargar_era5, serie_aire
from mcplan.construccion import preparar_construccion
from mcplan.entorno_termico import Capa
from mcplan.hidratacion import CurvaAdiabatica
from mcplan.termica_fundacion import EntornoFundacion, simular
from mcplan.vertidas_voxel import asignar_vertidas, comparar_volumenes
from mcplan.voxel import voxelizar_fundacion


def exportar(r, ids, origen, lado, salida, resumen, clima):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    try:
        import pyvista as pv
    except ImportError as exc:
        raise SystemExit("Para exportar VTK instala PyVista (instrucciones en entregas/E11/README.md).") from exc

    salida.mkdir(parents=True, exist_ok=True)
    for nombre, campo in r.campos.items():
        malla = pv.ImageData(dimensions=tuple(n+1 for n in ids.shape[::-1]),
                             spacing=(lado,)*3, origin=tuple(origen))
        malla.cell_data["T_C"] = campo.temperatura_C.ravel()
        malla.cell_data["vertida_id"] = ids.ravel()
        malla.cell_data["activo"] = np.isfinite(campo.temperatura_C).astype(np.uint8).ravel()
        malla.cell_data["superficie"] = campo.superficie.ravel()
        malla.cell_data["T_S25_min_C"] = campo.s25_min_C.ravel()
        malla.field_data["tiempo_h"] = [campo.tiempo_s/3600]
        malla.field_data["fase"] = [campo.fase]
        malla.field_data["codigo_commit"] = [resumen["codigo_commit"]]
        malla.field_data["snapshot_sha256"] = [resumen["snapshot_sha256"]]
        malla.field_data["nucleo_xyz_m"] = np.array([r.nucleo_xyz_m])
        malla.save(salida / f"{nombre}.vti")
    (salida / "resumen.json").write_text(json.dumps(resumen, indent=2, ensure_ascii=False,
                                                  allow_nan=False) + "\n", encoding="utf-8")
    t = [x["tiempo_h"] for x in r.historia]
    fig, ax = plt.subplots(figsize=(9, 3.8), layout="constrained")
    ax.plot(np.arange(len(clima)), clima, color="#177c7a")
    ax.set(xlabel="Horas desde la primera vertida", ylabel="Aire a 2 m [°C]",
           title=f"{resumen['clima']['modelo_solicitado']} · {resumen['clima']['tipo']} · El Rosal")
    ax.grid(alpha=.25)
    fig.savefig(salida / "aire.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(2, 1, figsize=(9, 7), sharex=True, layout="constrained")
    for variable, label in [("nucleo_C", "Sonda interior"), ("Tmin_S25_C", "Mínimo S25"),
                            ("Tmax_C", "Máxima del dominio")]:
        ax[0].plot(t, [x[variable] for x in r.historia], label=label)
    ax[0].axhline(70, color="darkred", ls="--", label="Límite 70 °C")
    ax[0].set(ylabel="Temperatura [°C]", title="Fundación · ensayo determinista provisional")
    ax[0].legend(ncol=2)
    ax[1].plot(t, [x["DeltaT_K"] for x in r.historia], color="#7e4ca5", label="Tmax del dominio − Tmin S25")
    ax[1].axhline(20, color="darkred", ls="--", label="Límite 20 °C")
    ax[1].plot(r.diferencial["tiempo_h"], r.diferencial["valor"], "o", color="#7e4ca5", label="Pico")
    ax[1].set(xlabel="Horas desde la primera vertida", ylabel="Diferencial [K]")
    ax[1].legend()
    for a in ax:
        a.grid(alpha=.25)
    fig.savefig(salida / "temperaturas.png", dpi=150)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("caso", choices=["e11", "e12"])
    ap.add_argument("--parametros", type=Path, default=Path(__file__).with_name("parametros.json"))
    ap.add_argument("--lado", type=float, help="Tamaño cúbico en metros.")
    ap.add_argument("--paso-max", type=float, help="Tope temporal en segundos.")
    ap.add_argument("--salida", type=Path, help="Directorio de resultados alternativo.")
    ap.add_argument("--sin-exportar", action="store_true", help="Solo imprime el resumen, sin cambiar figuras ni VTK.")
    a = ap.parse_args()
    config = json.loads(a.parametros.read_text(encoding="utf-8"))
    escenario = config[a.caso]
    if escenario["tipo"] not in ("forecast", "reanalisis"):
        raise ValueError("Tipo meteorológico desconocido.")
    hidratacion = dict(config["hidratacion"])
    if "q0_W_m3" in hidratacion:
        # Adaptación a la representación existente, con fuente directa como entrada.
        q0 = hidratacion.pop("q0_W_m3")
        capacidad = hidratacion["densidad_kg_m3"] * hidratacion["calor_especifico_J_kgK"]
        hidratacion["theta_infinito_K"] = q0 * hidratacion["tau_s"] / capacidad
    curva = CurvaAdiabatica(**hidratacion)
    ruta = RAIZ / escenario["snapshot"]
    meta, clima = (cargar_snapshot if escenario["tipo"] == "forecast" else cargar_era5)(ruta)
    inicio = datetime.fromisoformat(escenario["inicio_serie"])
    if escenario["tipo"] == "forecast" and inicio < datetime.fromisoformat(meta["descargado_utc"]):
        raise ValueError("La simulación de pronóstico debe comenzar después de la descarga.")
    aire = serie_aire(clima, inicio, escenario["horizonte_h"])

    f = extraer_fundacion_ifc(RAIZ / config["archivo_ifc"])
    lado = a.lado if a.lado is not None else config["lado_m"]
    v = voxelizar_fundacion(f, pasos_m=(lado,)*3)
    asignacion = asignar_vertidas(f, v)
    programa = preparar_construccion(f, asignacion)
    if {c.material for c in programa.colocaciones} != {"M1"}:
        raise ValueError("Este caso tiene propiedades solo para M1.")
    ids = asignacion.vertida_id
    datos = dict(config["entorno"])
    if a.paso_max is not None:
        datos["dt_tope_s"] = a.paso_max
    datos["capas_laterales"] = tuple(Capa(**c) for c in datos["capas_laterales"])
    entorno = EntornoFundacion(**datos)
    r = simular(ids, v.grilla.origen_m, lado,
                {c.vertida_id: (c.inicio_s, c.temperatura_C) for c in programa.colocaciones},
                curva, entorno, aire, config["nucleo_xyz_m"])
    commit = subprocess.check_output(["git", "-C", str(RAIZ), "rev-parse", "HEAD"], text=True).strip()
    cambios = subprocess.check_output(
        ["git", "-C", str(RAIZ), "status", "--porcelain", "--untracked-files=no",
         "--", "desarrollo", "casos", "requirements.txt"], text=True).splitlines()
    resumen = dict(
        codigo_commit=commit, codigo_modificado=bool(cambios), cambios_codigo=cambios,
        ejecutado_utc=datetime.now(timezone.utc).isoformat(),
        parametros_sha256=sha256(a.parametros.read_bytes()).hexdigest(),
        parametros_efectivos={**config, "lado_m": lado, "entorno": {
            **config["entorno"], "dt_tope_s": entorno.dt_tope_s}},
        plan_vertidas=[dict(id=c.vertida_id, inicio_h=c.inicio_s/3600,
                            temperatura_C=c.temperatura_C, material=c.material)
                       for c in programa.colocaciones],
        caso=a.caso, clima=meta, snapshot=escenario["snapshot"],
        snapshot_sha256=sha256(ruta.read_bytes()).hexdigest(),
        inicio_serie=inicio.isoformat(), inicio_escenario=escenario.get("inicio_escenario", inicio.isoformat()),
        sha256_ifc=f.sha256_ifc, horizonte_h=escenario["horizonte_h"], lado_m=lado, pasos=r.pasos,
        volumen_ifc_m3=f.volumen_total_mallas_m3, volumen_vox_m3=int(np.count_nonzero(ids))*lado**3,
        error_por_vertida_pct={str(x.vertida_id): x.error_relativo_pct for x in comparar_volumenes(f, asignacion)},
        nucleo_xyz_m=r.nucleo_xyz_m, Tmax=r.pico, DeltaTmax=r.diferencial, balance_J=r.balance_J,
        cumple_70_ensayo=r.pico["valor"] <= 70, cumple_20_ensayo=r.diferencial["valor"] <= 20,
        S25_profundidad_m=.025, S25_reconstruida=True)
    if not a.sin_exportar:
        salida = a.salida if a.salida is not None else RAIZ / "resultados" / a.caso
        exportar(r, ids, v.grilla.origen_m, lado, salida, resumen, aire)
        print(f"Resultados: {salida}")
    print(json.dumps(resumen, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
