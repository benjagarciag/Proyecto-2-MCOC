"""Compara controles térmicos del plan de cinco vertidas con escenarios F02."""
import argparse
import csv
from dataclasses import replace
from datetime import datetime
from itertools import product
from pathlib import Path
from time import perf_counter
import json
from math import ceil

import numpy as np

from ejecutar import (RAIZ, Capa, EntornoFundacion, alertas_cola, asignar_vertidas,
                      cargar_era5, construir_planes, extraer_fundacion_ifc, huella,
                      leer_json, materiales, metricas, preparar_construccion, riesgo,
                      serie_aire, simular, voxelizar_fundacion)
from mcplan.termica_fundacion import EnfriamientoInterior


# Cambio de T de colocación [K], espesor de lana [m], edades de retiro por capa [h].
VARIANTES = {
    "base": (0, 0, ()),
    "frio": (-4, 0, ()),
    "proteccion": (0, .04, (240,)),
    "combinada": (-4, .04, (240,)),
    "retiro_escalonado": (-6, .04, (240, 360)),
}


def nucleo_refrigerable(ids, lado):
    """Retira capas de voxeles que lindan con aire o suelo en el dominio final."""
    interior = ids > 0
    forma = interior.shape
    for _ in range(ceil(.5/lado)):
        exterior = np.pad(interior, 1)
        siguiente = interior.copy()
        for eje in range(3):
            for desplazamiento in (0, 2):
                corte = [slice(1, -1)]*3
                corte[eje] = slice(desplazamiento, desplazamiento+forma[eje])
                siguiente &= exterior[tuple(corte)]
        interior = siguiente
    return interior


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("variante", choices=VARIANTES)
    p.add_argument("--plan", choices=("unica", "separacion_3h", "separacion_6h"),
                   default="separacion_6h", help="Cronograma evaluado con las mismas condiciones térmicas.")
    p.add_argument("--lado", type=float, default=.5)
    p.add_argument("--paso-max", type=float, default=900)
    p.add_argument("--cercanos", action="store_true",
                   help="Repita los tres escenarios de referencia más cercanos a los límites.")
    p.add_argument("--enfriamiento", nargs=2, type=float, metavar=("U_W_M3K", "TOPE_KW"),
                   help="Extracción equivalente interior, con consigna 18 °C.")
    p.add_argument("--cribado", action="store_true", help="Solo M4_SS y M1_22A; sin pesos agregados.")
    p.add_argument("--enfriar-tras-colocacion", action="store_true",
                   help="Para vertida única, iniciar la extracción al término físico.")
    p.add_argument("--visor", action="store_true",
                   help="Reproduce el escenario crítico guardado y exporta el complemento HTML.")
    args = p.parse_args()
    if args.cribado and args.cercanos:
        p.error("Elegir cribado o sensibilidad, no ambos.")
    if args.enfriamiento and args.variante != "retiro_escalonado":
        p.error("El ensayo de enfriamiento parte de la variante con retiro escalonado.")
    if args.enfriar_tras_colocacion and (args.plan != "unica" or not args.enfriamiento):
        p.error("El inicio al término físico requiere vertida única con enfriamiento.")
    if args.visor and (not args.enfriar_tras_colocacion or args.cribado or args.cercanos
                       or args.lado != .5 or args.paso_max != 900 or args.enfriamiento != [5., 12.]):
        p.error("El complemento requiere vertida única a 12 kW tras colocación, malla 0,50 m y paso 900 s.")
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
    plan = construir_planes(programa.colocaciones, cfg)[args.plan]
    ids = asignacion.vertida_id
    if args.plan == "unica":
        ids = (ids > 0).astype(ids.dtype)
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
    enfriamiento = None
    if args.enfriamiento:
        u, tope = args.enfriamiento
        edad_inicio = fin_colocacion if args.enfriar_tras_colocacion else 6.
        enfriamiento = EnfriamientoInterior(nucleo_refrigerable(ids, args.lado),
                                            u, 18., tope*1000, edad_inicio, 432.)
        raiz = RAIZ / "resultados/incertidumbre/enfriamiento" / f"u{u:g}_tope{tope:g}"
    if args.plan != "separacion_6h":
        raiz = raiz / args.plan
    if args.enfriar_tras_colocacion:
        raiz = raiz / "tras_colocacion"
    salida = raiz
    if args.cercanos:
        salida = raiz / f"sensibilidad_{args.lado:g}m_{args.paso_max:g}s"
    elif args.cribado:
        salida = raiz / "cribado"
        if args.lado != .5 or args.paso_max != 900:
            salida = salida / f"{args.lado:g}m_{args.paso_max:g}s"
    elif args.lado != .5 or args.paso_max != 900:
        salida = raiz / f"completo_{args.lado:g}m_{args.paso_max:g}s"
    salida.mkdir(parents=True, exist_ok=True)
    seleccionados = None
    if args.cercanos:
        anteriores = leer_json(raiz / "resumen.json")["corridas"]
        seleccionados = {(x["curva"], x["clima"]) for x in sorted(
            anteriores, key=lambda x: abs(max(x["Tmax"]["valor"]-70, x["DeltaTmax"]["valor"]-20)),
        )[:3]}
    if args.visor:
        registro = leer_json(salida / "resumen.json")
        critico = max(registro["corridas"], key=lambda fila: fila["DeltaTmax"]["valor"])
        fuente = next(f for f in fuentes if f["id"] == critico["curva"])
        clima = next(h for h in climas if h["id"] == critico["clima"])
        corrida = simular(ids, vox.grilla.origen_m, args.lado, calendario, fuente["curva"],
                          entorno, clima["aire"][:critico["horizonte_h"]+1], base["nucleo_xyz_m"],
                          enfriamiento=enfriamiento)
        if corrida.diferencial != critico["DeltaTmax"] or corrida.pico != critico["Tmax"]:
            raise ValueError("La corrida reproducida difiere de la evidencia guardada.")
        from visor_cronograma import exportar_complemento
        exportar_complemento(RAIZ, salida, registro, critico, corrida, vox.grilla.origen_m)
        return
    filas = []
    for f, h in product(fuentes, climas):
        if args.cribado and f["id"] not in ("M4_SS", "M1_22A"):
            continue
        if seleccionados is not None and (f["id"], h["id"]) not in seleccionados:
            continue
        tic = perf_counter()
        def resolver(horas):
            return simular(ids, vox.grilla.origen_m, args.lado, calendario,
                           f["curva"], entorno, h["aire"][:horas+1], base["nucleo_xyz_m"],
                           enfriamiento=enfriamiento)

        inicial = cfg["horizonte_h"]
        r0 = resolver(inicial)
        horas = inicial
        r = r0
        ultima_retiro = max(v["inicio_h"]+max(retiros) for v in plan) if retiros else 0
        ultimo_evento = max(ultima_retiro, enfriamiento.fin_h if enfriamiento else 0)
        if ultimo_evento:
            # Cubrir retiro y apagado, más siete días posteriores.
            horas = min(max(horas, ceil(ultimo_evento)+168), cfg["extension_max_h"])
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
    agregado = riesgo(filas) if seleccionados is None and not args.cribado else None
    resumen = dict(variante=nombre, plan_id=args.plan, D_h=fin_colocacion, t0=cfg["inicio"], plan=plan,
                   lado_m=args.lado, dt_tope_s=args.paso_max, cambio_colocacion_K=ajuste,
                   espesor_capa_m=espesor, retiros_edad_h=retiros,
                   base_sha256=huella(ruta_base), config_sha256=huella(ruta_config),
                   solver_sha256=huella(RAIZ / "desarrollo/mcplan/termica_fundacion.py"),
                   manifiesto_sha256=huella(manifest),
                   clima_sha256={h["id"]: h["sha256"] for h in climas},
                   agregado=agregado, corridas=filas)
    if enfriamiento is not None:
        resumen["enfriamiento"] = dict(u_W_m3K=enfriamiento.u_W_m3K, tope_W=enfriamiento.tope_W,
            referencia_C=enfriamiento.referencia_C, edad_inicio_h=enfriamiento.edad_inicio_h,
            fin_h=enfriamiento.fin_h, volumen_m3=float(enfriamiento.mascara.sum()*args.lado**3))
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
