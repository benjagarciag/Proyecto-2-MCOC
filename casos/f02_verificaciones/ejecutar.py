"""Reproduce las matrices complementarias de F02 con el solver publicado."""
import argparse
from dataclasses import replace
from datetime import datetime
from itertools import product
import json
from math import isclose
from pathlib import Path
from time import perf_counter
from types import SimpleNamespace

import numpy as np

import insumos


def allocate(identifiers, plan, strata):
    if not strata:
        return identifiers, {x["id"]: (x["inicio_h"] * 3600, x["colocacion_C"]) for x in plan}, []
    groups = np.zeros_like(identifiers)
    schedule, details = {}, []
    for phase in plan:
        volume = int(np.count_nonzero(identifiers == phase["id"]))
        start = phase["inicio_h"]
        for z, layer in enumerate(identifiers):
            occupied = layer == phase["id"]
            count = int(occupied.sum())
            if not count:
                continue
            group = len(details) + 1
            groups[z, occupied] = group
            duration = phase["duracion_h"] * count / volume
            schedule[group] = (start * 3600, phase["colocacion_C"])
            details.append(dict(id=group, parent=phase["id"], z_index=z, voxels=count,
                                start_h=start, finish_h=start+duration))
            start += duration
        assert isclose(start, phase["fin_h"], rel_tol=0, abs_tol=1e-10)
    assert np.array_equal(groups > 0, identifiers > 0)
    return groups, schedule, details


def ejecutar(args, configuraciones):
    start_wall = perf_counter()
    experiment, directory, mode = args.experimento, args.salida, args.modo
    suffix = "" if mode == "completo" else f"_{mode}"
    if args.escenario:
        suffix += "_" + "_".join(args.escenario)
    path = directory / f"{experiment}{suffix}.json"
    if path.exists():
        raise FileExistsError(f"El resultado ya existe. Usa otro directorio de salida: {path}")
    controls, Cooling, Environment, simulate, load_era5, air_series = insumos.importar_solver(args.geometria)
    cfg = insumos.leer(insumos.CONFIG)
    base = insumos.leer(insumos.RAIZ / cfg["base"])
    manifest = insumos.HIDRATACION / "manifiesto.json"
    materials = controls.materiales(base, manifest)
    published = insumos.publicadas()
    reference = published["referencia"]
    fuentes = insumos.leer(insumos.RESULTADOS_LUIS / "curvas_reales/resumen.json")
    huellas = {
        insumos.CONFIG: reference["config_sha256"],
        insumos.RAIZ / cfg["base"]: reference["base_sha256"],
        manifest: reference["manifiesto_sha256"],
        insumos.RAIZ / "desarrollo/mcplan/termica_fundacion.py": reference["solver_sha256"],
        insumos.RAIZ / base["archivo_ifc"]: fuentes["sha256_ifc"],
    }
    for fuente in fuentes["materiales"]:
        huellas[insumos.HIDRATACION / fuente["csv"]] = fuente["csv_sha256"]
        huellas[insumos.HIDRATACION / fuente["original"]] = fuente["original_sha256"]
    for ruta, huella in huellas.items():
        if not insumos.coincide(ruta, huella):
            raise ValueError(f"La huella no coincide con la evidencia publicada: {ruta.relative_to(insumos.RAIZ)}")
    base_plans = {plan["plan"]: plan["vertidas"] for plan in fuentes["planes"]}
    original_plan = [SimpleNamespace(vertida_id=v["id"], volumen_ifc_m3=v["volumen_m3"],
                        temperatura_C=v["colocacion_C"]) for v in base_plans["separacion_6h"]]
    schedules = controls.construir_planes(original_plan, cfg)
    assert schedules["separacion_9h"] == base_plans["separacion_9h"]
    shift, thickness, removals = controls.VARIANTES["retiro_escalonado"]
    assert shift == -6
    selected = configuraciones["experimentos"][experiment]
    plan = [dict(v, colocacion_C=selected.get("temperatura_C", v["colocacion_C"] + shift))
            for v in schedules[selected["plan"]]]
    duration = max(v["fin_h"] for v in plan)
    side, step = (.25, 450) if mode == "refinar" else (args.lado or reference["lado_m"], args.paso_max or reference["dt_tope_s"])
    geometry, origin = insumos.leer_malla(controls, base, side, args.geometria)
    if selected["plan"] == "unica":
        geometry = (geometry > 0).astype(int)
    ids, schedule, strata = allocate(geometry, plan, selected.get("estratos", False))
    properties = dict(base["entorno"])
    form, insulation = (controls.Capa(**item) for item in properties.pop("capas_laterales"))
    layers = tuple(controls.Capa(thickness, insulation.k_W_mK, hour) for hour in removals)
    env = replace(Environment(**properties, capas_laterales=(form, *layers), capas_superiores=layers),
                  dt_tope_s=step)
    settings = reference["enfriamiento"]
    age_setting = selected["edad_inicio_h"]
    age = duration if age_setting == "duracion" else age_setting
    mask = controls.nucleo_refrigerable(ids, side)
    cooling = Cooling(mask, settings["u_W_m3K"], settings["referencia_C"], selected.get("tope_W", settings["tope_W"]),
                      age, selected.get("fin_h", settings["fin_h"]))
    if side == reference["lado_m"]:
        assert mask.sum()*side**3 == settings["volumen_m3"]
    comparator_name = {"unica": "tras_colocacion" if age_setting == "duracion" else "unica",
                       "separacion_3h": "rapida", "separacion_6h": "referencia",
                       "separacion_9h": "referencia"}[selected["plan"]]
    comparator = {insumos.par(row):row for row in published[comparator_name]["corridas"]}
    assert len(comparator) == 24 and isclose(sum(row["peso"] for row in comparator.values()), 1)
    climas = []
    for definition in cfg["historias"]:
        snapshot = insumos.RAIZ / definition["snapshot"]
        if not insumos.coincide(snapshot, reference["clima_sha256"][definition["id"]]):
            raise ValueError(f"El snapshot de {definition['id']} no coincide con la huella publicada.")
        _, weather = load_era5(snapshot)
        air = air_series(weather, datetime.fromisoformat(definition["inicio"]), cfg["extension_max_h"])
        climas.append((definition, air))
    previous = {}
    selection = set(comparator)
    if mode != "completo":
        original = insumos.RESULTADOS / "matrices" / f"{experiment}.json"
        previous = {insumos.par(row):row for row in insumos.leer(original)["corridas"]}
    if mode == "refinar":
        selection = {key for key, row in previous.items() if row["excede_70"] or row["excede_20"]}
        selection.add(max(previous, key=lambda key:previous[key]["DeltaTmax"]["valor"]))
    if args.escenario:
        key = tuple(args.escenario)
        if key not in comparator:
            raise ValueError("El par curva/clima no corresponde a los 24 escenarios publicados.")
        selection = {key}
    rows = []
    for material, (weather, air) in product(materials, climas):
        key = material["id"], weather["id"]
        weight = material["peso"] * weather["peso"]
        assert weight == comparator[key]["peso"] == 1/24

        def solve(hours):
            return simulate(ids, origin, side, schedule, material["curva"], env,
                            air[:hours+1], base["nucleo_xyz_m"], enfriamiento=cooling)

        if mode == "colas" and not previous[key]["pico_no_resuelto"]:
            rows.append(previous[key])
            continue
        if key not in selection:
            continue
        horizon = cfg["extension_max_h"] if mode == "colas" else 600
        first = (previous[key]["base_336h"] if mode == "colas" else controls.metricas(solve(336), 336))
        final = solve(horizon)
        assert abs(final.balance_J["residuo"]) < .001
        assert 0 <= final.balance_J["enfriamiento_pico_W"] <= cooling.tope_W
        tail_flag = controls.alertas_cola(final, horizon, duration, cfg["inicio_tardio_edad_min_h"])
        end = controls.metricas(final, horizon)
        comparison = comparator[key]
        row = dict(curva=key[0], clima=key[1], peso=weight, base_336h=first,
                         pico_no_resuelto=tail_flag, **end,
                         diferencia_delta_con_publicada_K=end["DeltaTmax"]["valor"]-comparison["DeltaTmax"]["valor"])
        if args.traza:
            row["historia"] = final.historia
        rows.append(row)
        insumos.imprimir("CORRIDA", dict(experimento=experiment, escenario=key, Tmax=final.pico["valor"],
                                  delta=final.diferencial["valor"], hora=final.diferencial["tiempo_h"],
                                  pico_no_resuelto=tail_flag))
    full = mode != "refinar" and not args.escenario
    assert {insumos.par(row) for row in rows} == selection
    risk = controls.riesgo(rows) if full else None
    output = dict(
        experimento=experiment, commit=configuraciones["commit_base"], origen=cfg["inicio"],
        geometria=args.geometria, comparador_publicado=comparator_name,
        modo=mode, lado_m=side, paso_max_s=step, S25_m=.025,
        horizontes_h=sorted({row["horizonte_h"] for row in rows}), D_h=duration,
        plan=plan, grupos_de_activacion=strata, capacidad_m3_h=cfg["capacidad_m3_h"],
        enfriamiento=dict(U_W_m3K=cooling.u_W_m3K, referencia_C=cooling.referencia_C, tope_W=cooling.tope_W,
                          comienzo_edad_h=cooling.edad_inicio_h, apagado_h=cooling.fin_h,
                          volumen_m3=float(mask.sum()*side**3)),
        clima_sha256=reference["clima_sha256"], configuracion_sha256=reference["config_sha256"],
        manifiesto_sha256=reference["manifiesto_sha256"], solver_sha256=reference["solver_sha256"],
        picos_no_resueltos=sum(row["pico_no_resuelto"] for row in rows),
        riesgo=risk, riesgo_336=controls.riesgo([dict(row["base_336h"], peso=row["peso"], clima=row["clima"])
                                                for row in rows]) if full else None,
        sensibilidades_pesos=({w["id"]:controls.riesgo(rows, w["id"]) for w in cfg["historias"]} if full else None),
        corridas=rows, duracion_auditoria_s=perf_counter()-start_wall,
    )
    directory.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(output, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")
    peak = max(rows, key=lambda row: row["Tmax"]["valor"])
    delta = max(rows, key=lambda row: row["DeltaTmax"]["valor"])
    insumos.imprimir("FIN", dict(experimento=experiment, D=duration, Tmax=peak["Tmax"], caso_Tmax=insumos.par(peak),
                              delta=delta["DeltaTmax"], caso_delta=insumos.par(delta), riesgo=risk,
                              picos_no_resueltos=output["picos_no_resueltos"], segundos=output["duracion_auditoria_s"]))


if __name__ == "__main__":
    configuraciones = insumos.leer(insumos.CONFIGURACIONES)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("experimento", choices=configuraciones["experimentos"])
    parser.add_argument("--salida", type=Path, required=True, help="Directorio para los resultados nuevos.")
    parser.add_argument("--modo", choices=("completo", "colas", "refinar"), default="completo")
    parser.add_argument("--geometria", choices=("exportada", "ifc"), default="exportada")
    parser.add_argument("--escenario", nargs=2, metavar=("CURVA", "CLIMA"))
    parser.add_argument("--traza", action="store_true", help="Conservar la serie temporal del escenario seleccionado.")
    parser.add_argument("--lado", type=float, choices=(.5, .25))
    parser.add_argument("--paso-max", type=int, choices=(450, 900))
    args = parser.parse_args()
    if args.escenario and args.modo != "completo":
        parser.error("--escenario requiere --modo completo.")
    if (args.traza or args.lado or args.paso_max) and not args.escenario:
        parser.error("--traza, --lado y --paso-max requieren --escenario.")
    if args.modo != "completo" and args.experimento.startswith("publicada_"):
        parser.error("Las corridas de Luis se reproducen mediante --modo completo.")
    ejecutar(args, configuraciones)
