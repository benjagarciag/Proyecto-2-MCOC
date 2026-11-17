"""Compara controles térmicos del plan de cinco vertidas con escenarios F02."""
import argparse
import csv
from dataclasses import replace
from datetime import datetime
from itertools import product
from pathlib import Path
from time import perf_counter
import json

from ejecutar import (RAIZ, Capa, EntornoFundacion, alertas_cola, asignar_vertidas,
                      cargar_era5, construir_planes, extraer_fundacion_ifc, huella,
                      leer_json, materiales, metricas, preparar_construccion, riesgo,
                      serie_aire, simular, voxelizar_fundacion)


# Cambio de T de colocación [K], espesor de lana [m], edades de retiro por capa [h].
VARIANTES = {
    "base": (0, 0, ()),
    "frio": (-4, 0, ()),
    "proteccion": (0, .04, (240,)),
    "combinada": (-4, .04, (240,)),
    "retiro_escalonado": (-6, .04, (240, 360)),
}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("variante", choices=VARIANTES)
    p.add_argument("--lado", type=float, default=.5)
    p.add_argument("--paso-max", type=float, default=900)
    p.add_argument("--cercanos", action="store_true",
                   help="Repita los tres escenarios de referencia más cercanos a los límites.")
    args = p.parse_args()
    nombre = args.variante
    ajuste, espesor, retiros = VARIANTES[nombre]
    ruta_config = RAIZ / "casos/incertidumbre/parametros.json"
    cfg = leer_json(ruta_config)
    ruta_base = RAIZ / cfg["base"]
    base = leer_json(ruta_base)
    manifest = RAIZ / "datos/hidratacion/manifiesto.json"
    fuentes = materiales(base, manifest)
    climas = []
    for h in cfg["historias"]:
        path = RAIZ / h["snapshot"]
        _, clima = cargar_era5(path)
        fecha = datetime.fromisoformat(h["inicio"])
        climas.append(dict(**h, aire=serie_aire(clima, fecha, cfg["extension_max_h"]), sha256=huella(path)))

    geometria = extraer_fundacion_ifc(RAIZ / base["archivo_ifc"])
    vox = voxelizar_fundacion(geometria, pasos_m=(args.lado,)*3)
    asignacion = asignar_vertidas(geometria, vox)
    programa = preparar_construccion(geometria, asignacion)
    plan = construir_planes(programa.colocaciones, cfg)["separacion_6h"]
    plan = [{**v, "colocacion_C": v["colocacion_C"]+ajuste} for v in plan]
    calendario = {v["id"]: (v["inicio_h"]*3600, v["colocacion_C"]) for v in plan}
    datos = dict(base["entorno"])
    moldaje, aislacion = (Capa(**c) for c in datos.pop("capas_laterales"))
    mantas = tuple(Capa(espesor, aislacion.k_W_mK, h) for h in retiros)
    entorno = EntornoFundacion(**datos, capas_laterales=(moldaje, *(mantas or (aislacion,))),
                               capas_superiores=mantas)
    entorno = replace(entorno, dt_tope_s=args.paso_max)
    fin_colocacion = max(v["fin_h"] for v in plan)
    raiz = RAIZ / "resultados/incertidumbre/controles" / nombre
    salida = raiz if not args.cercanos else raiz / f"sensibilidad_{args.lado:g}m_{args.paso_max:g}s"
    salida.mkdir(parents=True, exist_ok=True)
    seleccionados = None
    if args.cercanos:
        anteriores = leer_json(raiz / "resumen.json")["corridas"]
        seleccionados = {(x["curva"], x["clima"]) for x in sorted(
            anteriores, key=lambda x: abs(max(x["Tmax"]["valor"]-70, x["DeltaTmax"]["valor"]-20)),
        )[:3]}
    filas = []
    for f, h in product(fuentes, climas):
        if seleccionados is not None and (f["id"], h["id"]) not in seleccionados:
            continue
        tic = perf_counter()
        def resolver(horas):
            return simular(asignacion.vertida_id, vox.grilla.origen_m, args.lado, calendario,
                           f["curva"], entorno, h["aire"][:horas+1], base["nucleo_xyz_m"])

        inicial = cfg["horizonte_h"]
        r0 = resolver(inicial)
        horas = inicial
        r = r0
        ultima_retiro = max(v["inicio_h"]+max(retiros) for v in plan) if retiros else 0
        if retiros:
            # Cubrir retiro y al menos siete días posteriores dentro de los archivos congelados.
            horas = min(max(horas, int(ultima_retiro)+168), cfg["extension_max_h"])
        if horas > inicial:
            r = resolver(horas)
        while (alertas_cola(r, horas, fin_colocacion, cfg["inicio_tardio_edad_min_h"])
               and horas < cfg["extension_max_h"]):
            horas = min(horas+168, cfg["extension_max_h"])
            r = resolver(horas)
        filas.append(dict(curva=f["id"], clima=h["id"], peso=f["peso"]*h["peso"], CPU_s=perf_counter()-tic,
                          base_336h=metricas(r0, inicial), **metricas(r, horas),
                          pico_no_resuelto=alertas_cola(r, horas, fin_colocacion,
                                                       cfg["inicio_tardio_edad_min_h"])))
        print(f"{nombre}, {f['id']}, {h['id']}: {r.pico['valor']:.2f} °C / "
              f"{r.diferencial['valor']:.2f} K a {horas} h", flush=True)
    agregado = riesgo(filas) if seleccionados is None else None
    resumen = dict(variante=nombre, D_h=fin_colocacion, t0=cfg["inicio"], plan=plan,
                   lado_m=args.lado, dt_tope_s=args.paso_max, cambio_colocacion_K=ajuste,
                   espesor_capa_m=espesor, retiros_edad_h=retiros,
                   base_sha256=huella(ruta_base), config_sha256=huella(ruta_config),
                   solver_sha256=huella(RAIZ / "desarrollo/mcplan/termica_fundacion.py"),
                   manifiesto_sha256=huella(manifest),
                   clima_sha256={h["id"]: h["sha256"] for h in climas},
                   agregado=agregado, corridas=filas)
    (salida/"resumen.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=2)+"\n",
                                      encoding="utf-8")
    with (salida/"escenarios.csv").open("w", encoding="utf-8", newline="") as archivo:
        w = csv.writer(archivo, lineterminator="\n")
        w.writerow(("curva", "clima", "peso", "horizonte_h", "Tmax_C", "hora_Tmax",
                    "DeltaTmax_K", "hora_DeltaTmax", "excede_70", "excede_20", "pico_no_resuelto"))
        for f in filas:
            t, d = f["Tmax"], f["DeltaTmax"]
            w.writerow((f["curva"], f["clima"], f["peso"], f["horizonte_h"],
                        t["valor"], t["tiempo_h"], d["valor"], d["tiempo_h"],
                        f["excede_70"], f["excede_20"], f["pico_no_resuelto"]))


if __name__ == "__main__":
    main()
