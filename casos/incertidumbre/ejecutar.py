"""Comparación de planes para la revisión del 18 de noviembre."""
import argparse
import csv
from dataclasses import replace
from datetime import datetime, timedelta
from hashlib import sha256
from itertools import product
import json
from math import ceil, isclose, isfinite
from pathlib import Path
import subprocess
import sys
from time import perf_counter

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "desarrollo"))

import numpy as np

from mcplan.bim import extraer_fundacion_ifc
from mcplan.clima import cargar_snapshot
from mcplan.clima_historico import cargar_era5, serie_aire
from mcplan.construccion import preparar_construccion
from mcplan.entorno_termico import Capa
from mcplan.hidratacion import CurvaAdiabatica
from mcplan.hidratacion_tabular import CurvaTabular
from mcplan.termica_fundacion import EntornoFundacion, simular
from mcplan.vertidas_voxel import asignar_vertidas, comparar_volumenes
from mcplan.voxel import voxelizar_fundacion


def leer_json(ruta):
    return json.loads(ruta.read_text(encoding="utf-8"))


def huella(ruta):
    return sha256(ruta.read_bytes()).hexdigest()


def validar_pesos(escenarios):
    pesos = [e["peso"] for e in escenarios]
    if (len({e["id"] for e in escenarios}) != len(escenarios)
            or not all(isfinite(p) and p > 0 for p in pesos)
            or not isclose(sum(pesos), 1., rel_tol=0, abs_tol=1e-10)):
        raise ValueError("Los escenarios requieren ID único y pesos positivos que sumen uno.")


def materiales(base, manifiesto):
    datos = base["hidratacion"]
    capacidad = datos["densidad_kg_m3"] * datos["calor_especifico_J_kgK"]
    if manifiesto is None:
        curva = CurvaAdiabatica(datos["q0_W_m3"] * datos["tau_s"] / capacidad,
                              datos["tau_s"], datos["densidad_kg_m3"],
                              datos["calor_especifico_J_kgK"])
        return [dict(id="M1-exponencial-E12", peso=1., curva=curva, provisional=True,
                     q0_W_m3=datos["q0_W_m3"], tau_s=datos["tau_s"])]
    m = leer_json(manifiesto)
    if not (m["mezcla"] and m["justificacion_comparabilidad_y_pesos"]):
        raise ValueError("Identificar la mezcla y justificar comparabilidad y pesos.")
    entradas = m["curvas"]
    validar_pesos(entradas)
    if len(entradas) != 8:
        raise ValueError("Declarar las ocho curvas del ejercicio.")
    salida = []
    for e in entradas:
        original = manifiesto.parent / e["original"]
        ruta = manifiesto.parent / e["csv"]
        if not e["nota_ensayo_y_procesamiento"] or not e["justificacion_cola_cero"]:
            raise ValueError("Documentar ensayo, procesamiento y terminación de la cola.")
        with ruta.open(encoding="utf-8-sig", newline="") as archivo:
            filas = list(csv.DictReader(archivo))
        edad = np.array([float(f["edad_h"]) for f in filas]) * 3600
        valores = np.array([float(f["acumulado"]) for f in filas])
        cap = e.get("rho_kg_m3", datos["densidad_kg_m3"]) * e.get(
            "cp_J_kgK", datos["calor_especifico_J_kgK"])
        if e["unidad"] == "K_adiabatico":
            factor = cap
        elif e["unidad"] in ("J/kg_cementante", "J/g_cementante"):
            factor = e["cementante_kg_m3"] * (1000 if e["unidad"] == "J/g_cementante" else 1)
        else:
            raise ValueError("Se requiere incremento adiabático o calor acumulado por masa.")
        if not isfinite(factor) or factor <= 0:
            raise ValueError("Factor de conversión física inválido.")
        curva = CurvaTabular(edad, factor * valores, cap)
        salida.append(dict(**e, curva=curva, provisional=False, original_sha256=huella(original),
                           csv_sha256=huella(ruta), mezcla=m["mezcla"],
                           justificacion_comparabilidad_y_pesos=m["justificacion_comparabilidad_y_pesos"],
                           edad_final_h=float(edad[-1]/3600), total_J_m3=float(curva.acumulado_J_m3[-1])))
    return salida


def construir_planes(colocaciones, cfg):
    capacidad = cfg["capacidad_m3_h"]
    espera = cfg["espera_min_h"]
    paso = cfg["paso_inicios_h"]
    if not (isfinite(capacidad) and capacidad > 0 and isfinite(espera) and espera >= 0
            and isfinite(paso) and paso > 0):
        raise ValueError("Indicar capacidad, espera y paso válidos.")
    partes = {c.vertida_id: (c.volumen_ifc_m3, c.temperatura_C) for c in colocaciones}
    total = sum(v for v, _ in partes.values())
    prom = sum(v*t for v, t in partes.values()) / total
    planes = {"unica": [dict(id=1, inicio_h=0., duracion_h=total/capacidad, fin_h=total/capacidad,
                            volumen_m3=total, colocacion_C=prom)]}
    for intervalo in cfg["intervalos_h"]:
        plan = []
        if not isfinite(intervalo) or intervalo < paso or not isclose(intervalo/paso, round(intervalo/paso)):
            raise ValueError("Cada separación debe ser un múltiplo positivo del paso.")
        inicio = 0.
        for vid, (volumen, temperatura) in partes.items():
            if plan:
                anterior = plan[-1]
                minimo = max(anterior["inicio_h"]+intervalo, anterior["fin_h"]+espera)
                inicio = paso*ceil(minimo/paso-1e-12)
            duracion = volumen / capacidad
            plan.append(dict(id=vid, inicio_h=inicio, duracion_h=duracion, fin_h=inicio+duracion,
                             volumen_m3=volumen, colocacion_C=temperatura))
        nombre = f"separacion_{intervalo:g}h"
        planes[nombre] = plan
    for nombre, plan in planes.items():
        if any(b["inicio_h"] + 1e-9 < a["fin_h"] + espera for a, b in zip(plan, plan[1:])):
            raise ValueError(f"{nombre} solapa colocaciones o incumple la espera mínima con esos recursos.")
    return planes


def alertas_cola(r, fin_h, ultima_colocacion_h, edad_min_h):
    ventana = [x for x in r.historia if x["tiempo_h"] >= fin_h-24]
    return (fin_h-ultima_colocacion_h < edad_min_h
            or max(r.pico["tiempo_h"], r.diferencial["tiempo_h"]) >= fin_h-24
            or any(max(x[k] for x in ventana) >= max(y[k] for y in r.historia) - .01
                   for k in ("Tmax_C", "DeltaT_K"))
            or (r.historia[-1]["Tmax_C"] > ventana[0]["Tmax_C"] + .05))


def metricas(r, horas):
    return dict(horizonte_h=horas, Tmax=r.pico, DeltaTmax=r.diferencial,
                excede_70=r.pico["valor"] > 70, excede_20=r.diferencial["valor"] > 20,
                pasos=r.pasos, balance_J=r.balance_J, picos_vertidas=r.picos_vertidas)


def riesgo(filas, clima_prioritario=None):
    pesos = [f["peso"] * (2 if f["clima"] == clima_prioritario else 1) for f in filas]
    total = sum(pesos)
    return {
        "P_T": sum(w for w, f in zip(pesos, filas) if f["excede_70"])/total,
        "P_delta": sum(w for w, f in zip(pesos, filas) if f["excede_20"])/total,
        "P_union": sum(w for w, f in zip(pesos, filas) if f["excede_70"] or f["excede_20"])/total,
    }


def guardar_evidencia_unica(salida, r, ids, origen, lado):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ejes = plt.subplots(2, 1, sharex=True, figsize=(9, 6), layout="constrained")
    tiempos = [f["tiempo_h"] for f in r.historia]
    for clave, etiqueta in (("Tmax_C", "Máxima del dominio"), ("nucleo_C", "Sonda interior"),
                            ("Tmin_S25_C", "Mínimo S25"), ("aire_C", "Aire")):
        ejes[0].plot(tiempos, [f[clave] for f in r.historia], label=etiqueta)
    ejes[0].set(ylabel="Temperatura [°C]", title="Vertida única · primer escenario declarado")
    ejes[0].axhline(70, ls="--", color="brown", label="Límite 70 °C")
    ejes[0].legend()
    ejes[1].plot(tiempos, [f["DeltaT_K"] for f in r.historia], color="purple")
    ejes[1].axhline(20, ls="--", color="brown")
    ejes[1].set(xlabel="Horas desde t₀", ylabel="Diferencial [K]")
    fig.savefig(salida / "vertida_unica.png", dpi=150)
    plt.close(fig)

    import pyvista as pv
    for nombre, campo in r.campos.items():
        malla = pv.ImageData(dimensions=np.array(ids.shape[::-1])+1, origin=origen,
                             spacing=(lado,)*3)
        malla.cell_data["T_C"] = campo.temperatura_C.ravel()
        malla.cell_data["activo"] = np.isfinite(campo.temperatura_C).astype(np.uint8).ravel()
        malla.cell_data["vertida_id"] = ids.ravel()
        malla.cell_data["superficie"] = campo.superficie.ravel()
        malla.cell_data["T_S25_min_C"] = campo.s25_min_C.ravel()
        malla.field_data["tiempo_h"] = [campo.tiempo_s/3600]
        malla.field_data["nucleo_xyz_m"] = np.array([r.nucleo_xyz_m])
        malla.save(salida / f"unica_{nombre}.vti")


def graficar_curvas(salida, fuentes):
    if fuentes[0]["provisional"]:
        return
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 4.5), layout="constrained")
    for f in fuentes:
        q = f["curva"]
        ax.plot(q.edad_s/3600, q.acumulado_J_m3/1e6, label=f["id"])
    ax.set(xlabel="Edad desde colocación [h]", ylabel="Energía acumulada [MJ/m³]")
    ax.legend(ncol=2)
    fig.savefig(salida / "curvas_hidratacion.png", dpi=150)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path(__file__).with_name("parametros.json"))
    parser.add_argument("--curvas", type=Path, help="Manifiesto de las ocho curvas originales.")
    parser.add_argument("--lado", type=float, default=.5)
    parser.add_argument("--paso-max", type=float)
    parser.add_argument("--profundidad-s25", type=float, default=.025)
    parser.add_argument("--salida", type=Path, default=RAIZ / "resultados" / "incertidumbre" / "base")
    parser.add_argument("--sin-figuras", action="store_true")
    args = parser.parse_args()
    cfg = leer_json(args.config)
    base = leer_json(RAIZ / cfg["base"])
    inicio = datetime.fromisoformat(cfg["inicio"])
    t0 = 336
    if cfg["horizonte_h"] != t0 or cfg["extension_max_h"] < t0:
        raise ValueError("Se requieren 336 h y una extensión máxima de al menos 336 h.")
    fuentes = materiales(base, args.curvas)
    historias = cfg["historias"]
    validar_pesos(historias)
    climas = []
    for h in historias:
        ruta = RAIZ / h["snapshot"]
        meta, clima = cargar_era5(ruta)
        fecha = datetime.fromisoformat(h["inicio"])
        aire = serie_aire(clima, fecha, cfg["extension_max_h"])
        climas.append(dict(**h, aire=aire, metadata=meta, sha256=huella(ruta)))
    ruta = RAIZ / cfg["forecast"]
    forecast_meta, forecast = cargar_snapshot(ruta)
    datos_forecast = dict(metadata=forecast_meta, archivo=cfg["forecast"], sha256=huella(ruta),
                          cobertura=forecast.cobertura(inicio))
    if inicio < datetime.fromisoformat(forecast_meta["descargado_utc"]):
        raise ValueError("El inicio de decisión debe ser posterior a la descarga del forecast.")
    marcas = {h.tiempo_utc: h.aire_C for h in forecast.horas}
    aire_forecast = []
    for i in range(t0+1):
        valor = marcas.get(inicio + timedelta(hours=i))
        if valor is None:
            break
        aire_forecast.append(valor)
    n_forecast = len(aire_forecast)
    datos_forecast["marcas_consecutivas_desde_t0"] = n_forecast
    datos_forecast["politica"] = (
        "Controles sin peso: GFS consecutivo desde t0, cola ERA5 por hora relativa. "
        "Se registra el salto en el empalme. La enumeración usa bloques ERA5 completos."
    )
    controles = []
    if n_forecast == t0+1:
        controles.append(("GFS-completo", aire_forecast, None))
    elif n_forecast:
        for h in climas:
            cola = h["aire"][n_forecast:t0+1]
            controles.append((h["id"], aire_forecast+cola, cola[0]-aire_forecast[-1]))

    fundacion = extraer_fundacion_ifc(RAIZ / base["archivo_ifc"])
    grilla = voxelizar_fundacion(fundacion, pasos_m=(args.lado,)*3)
    geometria = asignar_vertidas(fundacion, grilla)
    programa = preparar_construccion(fundacion, geometria)
    planes = construir_planes(programa.colocaciones, cfg)
    datos = dict(base["entorno"])
    datos["capas_laterales"] = tuple(Capa(**c) for c in datos["capas_laterales"])
    entorno = EntornoFundacion(**datos)
    if args.paso_max is not None:
        entorno = replace(entorno, dt_tope_s=args.paso_max)
    origen = grilla.grilla.origen_m
    args.salida.mkdir(parents=True, exist_ok=True)
    if not args.sin_figuras:
        graficar_curvas(args.salida, fuentes)

    tabla = []
    corridas = []
    forecast_control = []
    for nombre, plan in planes.items():
        ids = (geometria.vertida_id > 0).astype(int) if nombre == "unica" else geometria.vertida_id
        calendario = {v["id"]: (3600*v["inicio_h"], v["colocacion_C"]) for v in plan}
        D = max(v["fin_h"] for v in plan)
        if D >= t0:
            raise ValueError("La colocación debe terminar dentro del horizonte inicial.")
        filas = []
        for f, h in product(fuentes, climas):
            reloj = perf_counter()
            r = simular(ids, origen, args.lado, calendario, f["curva"], entorno, h["aire"][:t0+1],
                        base["nucleo_xyz_m"], profundidad_s25_m=args.profundidad_s25)
            registro_336 = metricas(r, t0)
            horas = t0
            while alertas_cola(r, horas, D, cfg["inicio_tardio_edad_min_h"]) and horas < cfg["extension_max_h"]:
                horas = min(horas+168, cfg["extension_max_h"])
                r = simular(ids, origen, args.lado, calendario, f["curva"], entorno, h["aire"][:horas+1],
                            base["nucleo_xyz_m"], profundidad_s25_m=args.profundidad_s25)
            fila = dict(plan=nombre, material=f["id"], clima=h["id"], peso=f["peso"]*h["peso"],
                        CPU_s=perf_counter()-reloj, base_336h=registro_336,
                        pico_no_resuelto=alertas_cola(r, horas, D, cfg["inicio_tardio_edad_min_h"]),
                        **metricas(r, horas))
            filas.append(fila)
            print(f"{nombre} {f['id']} {h['id']} | {horas} h | "
                  f"{fila['Tmax']['valor']:.2f} °C / {fila['DeltaTmax']['valor']:.2f} K | "
                  f"{fila['CPU_s']:.2f} s", flush=True)
            if nombre == "unica" and len(filas) == 1 and not args.sin_figuras:
                guardar_evidencia_unica(args.salida, r, ids, origen, args.lado)
        for cola, aire_control, salto in controles:
            f = fuentes[0]
            r = simular(ids, origen, args.lado, calendario, f["curva"], entorno, aire_control,
                        base["nucleo_xyz_m"], profundidad_s25_m=args.profundidad_s25)
            forecast_control.append(dict(plan=nombre, material=f["id"], cola=cola,
                                         salto_empalme_C=salto, **metricas(r, t0)))
        calculo = riesgo(filas)
        cola = any(f["pico_no_resuelto"] for f in filas)
        tabla.append(dict(plan=nombre, D_h=D, vertidas=plan, **calculo,
                          sensibilidad_doble_peso={h["id"]: riesgo(filas, h["id"]) for h in climas},
                          estado=("indeterminado" if cola and calculo["P_union"] <= .05 else
                                  "cumple" if calculo["P_union"] <= .05 else "excede")))
        corridas.extend(filas)
    tabla.sort(key=lambda f: f["D_h"])
    elegido = next((f["plan"] for f in tabla if f["estado"] == "cumple"), None)
    uso_provisional = fuentes[0]["provisional"] or not cfg["recursos_confirmados"]
    salida = dict(config=cfg, parametros_base=base, sha256_base=huella(RAIZ / cfg["base"]),
                  sha256_ifc=fundacion.sha256_ifc, sha256_config=huella(args.config),
                  commit_base=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=RAIZ, text=True).strip(),
                  sha256_ejecutor=huella(Path(__file__)), sha256_solver=huella(RAIZ / "desarrollo/mcplan/termica_fundacion.py"),
                  lado_m=args.lado, dt_tope_s=entorno.dt_tope_s, S25_m=args.profundidad_s25,
                  volumen_ifc_m3=fundacion.volumen_total_mallas_m3,
                  volumen_voxel_m3=float(np.count_nonzero(geometria.vertida_id)*args.lado**3),
                  error_relativo_por_vertida={v.vertida_id: v.error_relativo_pct
                                              for v in comparar_volumenes(fundacion, geometria)},
                  preliminar=uso_provisional, forecast=datos_forecast, control_forecast=forecast_control,
                  historias=[{k: v for k, v in h.items() if k != "aire"} for h in climas],
                  materiales=[{k: v for k, v in f.items() if k != "curva"} for f in fuentes],
                  planes=tabla, corridas=corridas, mas_rapido_dentro_ensayo=elegido,
                  recomendacion=elegido if not uso_provisional else None)
    (args.salida / "resumen.json").write_text(json.dumps(salida, indent=2, ensure_ascii=False,
        allow_nan=False)+"\n", encoding="utf-8")
    print(f"{len(corridas)} corridas ponderadas. Resumen: {args.salida/'resumen.json'}")


if __name__ == "__main__":
    main()
