"""Verifica la evidencia guardada y permite contrastar resultados regenerados."""
import argparse
from itertools import product
from math import isclose
from pathlib import Path

import insumos


MATRICES = insumos.RESULTADOS / "matrices"
MATRICES_NUEVAS = {
    "lenta_12kw": 4,
    "unica_estratos_retrasado": 0,
    "unica_estratos_6h": 0,
    "rapida_estratos_6h": 0,
    "unica_16c": 1,
    "unica_18c": 3,
    "unica_10kw": 0,
    "unica_16c_10kw": 5,
    "unica_apagado_360h": 1,
}


def exigir(condicion, mensaje):
    if not condicion:
        raise ValueError(mensaje)


def por_escenario(filas):
    pares = {insumos.par(fila): fila for fila in filas}
    exigir(len(pares) == len(filas), "Hay pares curva y clima duplicados.")
    return pares


def riesgo(filas):
    pt = pd = pf = 0.
    for fila in filas:
        tmax, delta = fila["Tmax"]["valor"], fila["DeltaTmax"]["valor"]
        excede_t, excede_d = tmax > 70, delta > 20
        exigir((excede_t, excede_d) == (fila["excede_70"], fila["excede_20"]), "Excedencia incoherente.")
        valor = fila["DeltaTmax"]
        exigir(isclose(delta, valor["Tmax_C"] - valor["Tmin_S25_C"], abs_tol=1e-10),
               "El diferencial no resta las temperaturas del mismo instante.")
        exigir(fila["Tmax"]["tiempo_h"] <= fila["horizonte_h"]
               and valor["tiempo_h"] <= fila["horizonte_h"], "Máximo fuera de horizonte.")
        pt += fila["peso"] * excede_t
        pd += fila["peso"] * excede_d
        pf += fila["peso"] * (excede_t or excede_d)
    return dict(P_T=pt, P_delta=pd, P_union=pf)


def verificar_matriz(nombre, casos_esperados, fallos):
    salida = insumos.leer(MATRICES / f"{nombre}.json")
    filas = salida["corridas"]
    exigir(set(por_escenario(filas)) == casos_esperados, f"Faltan escenarios en {nombre}.")
    exigir(all(f["peso"] == 1 / 24 for f in filas), f"Pesos distintos de 1/24 en {nombre}.")
    base = []
    for fila in filas:
        b = fila["base_336h"]
        exigir(b["horizonte_h"] == 336 and fila["horizonte_h"] in (600, 672), "Horizonte incoherente.")
        exigir(fila["Tmax"]["valor"] >= b["Tmax"]["valor"] and fila["DeltaTmax"]["valor"] >= b["DeltaTmax"]["valor"],
               "Un máximo disminuye al extender el horizonte.")
        exigir(abs(fila["balance_J"]["residuo"]) < .001, "El balance no cierra.")
        exigir(0 <= fila["balance_J"]["enfriamiento_pico_W"] <= salida["enfriamiento"]["tope_W"],
               "Potencia fuera del tope configurado.")
        base.append(dict(b, peso=fila["peso"]))
    nuevo, a336 = riesgo(filas), riesgo(base)
    for calculado, registrado in ((nuevo, salida["riesgo"]), (a336, salida["riesgo_336"])):
        for evento, valor in calculado.items():
            exigir(isclose(valor, registrado[evento], abs_tol=1e-12), f"Riesgo incoherente en {nombre}.")
    exigir(isclose(nuevo["P_union"], fallos / 24, abs_tol=1e-12), f"Recuento inesperado en {nombre}.")
    return salida


def _comparar_metrica(fila, esperado):
    for campo in ("Tmax", "DeltaTmax"):
        lectura, referencia = fila[campo], esperado[campo]
        for nombre in ("valor", "tiempo_h", "Tmax_C"):
            exigir(isclose(lectura[nombre], referencia[nombre], rel_tol=0, abs_tol=1e-8),
                   f"{campo}.{nombre} difiere en {insumos.par(fila)}.")
        for nombre in ("xyz_Tmax_m", "xyz_S25_m"):
            if nombre in referencia:
                exigir(all(isclose(x, y, rel_tol=0, abs_tol=1e-10)
                           for x, y in zip(lectura[nombre], referencia[nombre], strict=True)),
                       f"La ubicación {nombre} difiere.")


def comprobar_regenerada(ruta):
    salida = insumos.leer(ruta)
    nombre = salida["experimento"]
    if nombre.startswith("publicada_"):
        referencia = insumos.publicadas()[nombre.removeprefix("publicada_")]
    else:
        modo = salida["modo"]
        sufijo = "" if modo == "completo" else f"_{modo}"
        referencia = insumos.leer(MATRICES / f"{nombre}{sufijo}.json")
    for clave in ("lado_m", "dt_tope_s"):
        regenerada = salida["paso_max_s"] if clave == "dt_tope_s" else salida[clave]
        exigir(regenerada == referencia.get(clave, referencia.get("paso_max_s")),
               f"Configuración distinta en {clave}.")
    filas = por_escenario(referencia["corridas"])
    for fila in salida["corridas"]:
        esperado = filas[insumos.par(fila)]
        exigir(fila["pasos"] == esperado["pasos"] and fila["horizonte_h"] == esperado["horizonte_h"],
               "Pasos u horizonte distintos.")
        _comparar_metrica(fila, esperado)
        _comparar_metrica(dict(fila["base_336h"], curva=fila["curva"], clima=fila["clima"]),
                          esperado["base_336h"])
    print(f"Regeneración conforme: {ruta.name} ({len(salida['corridas'])} escenarios).")


def verificar():
    # Si un par excede ambos límites, la unión conserva su peso una sola vez.
    doble = dict(Tmax=dict(valor=71., tiempo_h=1.), DeltaTmax=dict(
        valor=21., Tmax_C=71., Tmin_S25_C=50., tiempo_h=1.),
        horizonte_h=336, peso=.25, excede_70=True, excede_20=True)
    exigir(riesgo([doble]) == dict(P_T=.25, P_delta=.25, P_union=.25),
           "La unión contó dos veces una excedencia doble.")
    curvas = insumos.leer(insumos.HIDRATACION / "manifiesto.json")["curvas"]
    climas = insumos.leer(insumos.CONFIG)["historias"]
    casos = set(product((x["id"] for x in curvas), (x["id"] for x in climas)))
    exigir(len(casos) == 24, "El catálogo no contiene 24 pares.")
    for nombre, fallos in MATRICES_NUEVAS.items():
        verificar_matriz(nombre, casos, fallos)
    colas = verificar_matriz("unica_apagado_360h_colas", casos, 1)["corridas"]
    exigir(sum(f["horizonte_h"] == 672 for f in colas) == 6
           and not any(f["pico_no_resuelto"] for f in colas), "Extensión de colas incompleta.")
    for nombre, total, fallos in (("lenta_12kw", 4, 3), ("unica_10kw", 1, 0)):
        fina = insumos.leer(MATRICES / f"{nombre}_refinar.json")
        exigir(len(fina["corridas"]) == total and fina["riesgo"] is None
               and fina["lado_m"] == .25 and fina["paso_max_s"] == 450, "Refinamiento mal identificado.")
        exigir(sum(f["excede_20"] or f["excede_70"] for f in fina["corridas"]) == fallos,
               "Recuento inesperado en refinamiento.")

    prueba = insumos.leer(insumos.RESULTADOS / "reproduccion_publicada.json")["corridas"]
    publicadas = insumos.publicadas()
    for nombre, fuente in publicadas.items():
        filas = por_escenario(fuente["corridas"])
        exigir({tuple(x["case"]) for x in prueba[nombre]} == casos, "Faltan pares en la reproducción.")
        for prueba_fila in prueba[nombre]:
            fila = filas[tuple(prueba_fila["case"])]
            exigir((prueba_fila["peak"], prueba_fila["delta"], prueba_fila["steps"])
                   == (fila["Tmax"]["valor"], fila["DeltaTmax"]["valor"], fila["pasos"]),
                   "La reproducción anterior difiere de la salida de Luis.")

    trazas = insumos.leer(insumos.RESULTADOS / "trazas_c6.json")
    exigir(len(trazas["planes"]) == 4 and all(len(x["muestras_horarias"]) == 601
           for x in trazas["planes"].values()), "Trazas horarias incompletas.")
    fuentes_trazas = {**publicadas, "lenta": insumos.leer(MATRICES / "lenta_12kw.json")}
    curva, clima = trazas["escenario"]
    for nombre, registros in trazas["planes"].items():
        referencia = por_escenario(fuentes_trazas[nombre]["corridas"])[curva, clima]
        _comparar_metrica(dict(registros, curva=curva, clima=clima), referencia)
    print("Evidencia conforme: 216 escenarios nuevos, 6 colas extendidas, 5 refinamientos y 96 reproducciones registradas.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--regenerado", nargs="+", type=Path, default=[])
    args = parser.parse_args()
    verificar()
    for ruta in args.regenerado:
        comprobar_regenerada(ruta)
