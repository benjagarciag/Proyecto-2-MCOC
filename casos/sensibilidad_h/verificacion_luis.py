"""Verificación F02 de Luis sobre 12 °C, 15 kW y h horario."""
import argparse
from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace

import numpy as np

import viento


FISICA = {
    "base": {},
    "k_1.6": {"k_W_mK": 1.6},
    "k_2.4": {"k_W_mK": 2.4},
    "suelo_12": {"suelo_C": 12},
    "h_medio": {},
    "retiro_312": {},
}


def huella(datos):
    return sha256(datos).hexdigest()


def modelo(fisica):
    viento._preparacion.preparar()
    meta, series, _ = viento.analizar(2., .14)
    coeficientes = {nombre: d["h_W_m2K"] for nombre, d in series.items()}
    if fisica == "h_medio":
        coeficientes = {nombre: [meta["h_constante_media_600h_W_m2K"]]*len(serie)
                        for nombre, serie in coeficientes.items()}
    insumos, motor, solver, hashes = viento.cargar_motor(coeficientes)
    referencia = viento.leer(viento.RAIZ / "resultados/controles_12c/unica_15kw_12c/"
                             "malla_0.5_paso900/unica_15kw_12c.json")
    anterior = referencia["estudio_controles"]
    if (any(hashes[k] != anterior[k] for k in hashes)
            or any(meta[k] != anterior["modelo_viento"][k]
                   for k in ("altura_representativa_m", "exponente_perfil", "correlacion"))):
        raise ValueError("El adaptador o el perfil de viento difieren de la candidata publicada.")
    cfg = insumos.leer(insumos.CONFIG)
    for clima in cfg["historias"]:
        ruta = insumos.RAIZ / clima["snapshot"]
        bytes_clima = ruta.read_bytes()
        lf = bytes_clima.replace(b"\r\n", b"\n")
        esperado = anterior["modelo_viento"]["clima_sha256"][clima["id"]]
        if esperado not in {huella(lf), huella(lf.replace(b"\n", b"\r\n"))}:
            raise ValueError(f"El snapshot {clima['id']} difiere de la referencia.")
    coincide_original = insumos.coincide

    def coincide(ruta, esperado):
        if coincide_original(ruta, esperado):
            return True
        if ruta.suffix.lower() != ".ifc":
            return False
        lf = ruta.read_bytes().replace(b"\r\n", b"\n")
        return esperado in {huella(lf), huella(lf.replace(b"\n", b"\r\n"))}

    insumos.coincide = coincide
    return insumos, motor, solver, meta, hashes, referencia


def aplicar_fisica(insumos, fisica, retiro_final_h=None):
    if fisica == "retiro_312":
        retiro_final_h = 312
    if not FISICA[fisica] and retiro_final_h is None:
        return
    importar = insumos.importar_solver

    def adaptado(geometria):
        partes = list(importar(geometria))
        simular = partes[3]

        def simulacion(ids, origen, lado, programa, curva, entorno, *args, **opciones):
            entorno = replace(entorno, **FISICA[fisica])
            if retiro_final_h is not None:
                def anticipar(capas):
                    return tuple(replace(c, retiro_edad_h=retiro_final_h) if c.retiro_edad_h == 360 else c
                                 for c in capas)
                entorno = replace(entorno, capas_laterales=anticipar(entorno.capas_laterales),
                                  capas_superiores=anticipar(entorno.capas_superiores))
            return simular(ids, origen, lado, programa, curva, entorno, *args, **opciones)

        partes[3] = simulacion
        return tuple(partes)

    insumos.importar_solver = adaptado


def verificar_interfaz_y_s25(solver):
    from mcplan.hidratacion import CurvaAdiabatica

    entorno = solver.EntornoFundacion(2., 5., 15., .5, 1.2, (), -10.)
    curva = CurvaAdiabatica(0., 3600., 2476., 1023.)
    H = 1/(.5/2 + 1/5)
    una = solver.simular(np.ones((1, 1, 1), dtype=int), (0, 0, 0), 1.,
                          {1: (0., 20.)}, curva, entorno, [10., 10.], (.5, .5, .5),
                          h_aire_horario_W_m2K=[5., 5.])
    s25_exacta = 20. + H*(10.-20.)*(.5-.025)/2.
    np.testing.assert_allclose(una.historia[0]["Tmin_S25_C"], s25_exacta, atol=1e-12, rtol=0)
    dos = solver.simular(np.array([[[1, 2]]]), (0, 0, 0), 1.,
                          {1: (0., 20.), 2: (1800., 10.)}, curva, entorno, [20., 20.], (.5, .5, .5),
                          h_aire_horario_W_m2K=[5., 5.])
    assert dos.historia[0]["voxeles_activos"] == 1
    posterior = next(fila for fila in dos.historia if fila["tiempo_h"] == .5)
    assert posterior["voxeles_activos"] == 2
    np.testing.assert_allclose(posterior["aire_W"], 5*H*(20.-10.), atol=1e-12, rtol=0)
    assert abs(dos.balance_J["residuo"]) < 1e-6
    print(f"S25 analítica: {s25_exacta:.10f} °C. Interfaz activa: {posterior['aire_W']:.10f} W al aire (5 caras).")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    ruta_config = viento.RAIZ / "casos/sensibilidad_h/colocacion_12c.json"
    planes = viento.leer(ruta_config)["casos"]
    p.add_argument("--caso", choices=planes, default="unica_15kw_12c")
    p.add_argument("--lado", type=float, choices=(.5, .25), default=.5)
    p.add_argument("--paso-max", type=int, choices=(900, 450), default=900)
    p.add_argument("--activacion", choices=("bloque", "estratos", "estratos-tardio"), default="bloque")
    p.add_argument("--fisica", choices=FISICA, default="base")
    p.add_argument("--retiro-final-h", type=int, choices=(312, 324, 336, 348, 360),
                   help="Edad de retiro de la última manta en coronación y laterales.")
    p.add_argument("--escenario", nargs=2, action="append", metavar=("CURVA", "CLIMA"))
    p.add_argument("--geometria", choices=("exportada", "ifc"), default="exportada")
    p.add_argument("--comprobar", action="store_true", help="Solo insumos y verificaciones de una celda.")
    p.add_argument("--salida", type=Path)
    a = p.parse_args()
    if not a.comprobar and a.salida is None:
        p.error("Indicar una salida nueva con --salida.")
    if a.fisica != "base" and not a.escenario:
        p.error("Las sensibilidades físicas requieren pares explícitos; no se les asigna riesgo.")
    if a.fisica == "retiro_312" and a.retiro_final_h is not None:
        p.error("Elegir el retiro final con una sola opción.")
    if a.salida is not None and a.salida.exists():
        p.error("La salida ya existe. Elegir otra ruta.")
    insumos, motor, solver, meta, hashes, referencia = modelo(a.fisica)
    viento.verificar(solver)
    if a.comprobar:
        verificar_interfaz_y_s25(solver)
        control, *_ = insumos.importar_solver("ifc")
        cfg = insumos.leer(insumos.CONFIG)
        base = insumos.leer(insumos.RAIZ / cfg["base"])
        for lado in (.5, .25):
            ids, origen = insumos.leer_malla(control, base, lado, "ifc")
            guardados, origen_guardado = insumos.leer_malla(control, base, lado, "exportada")
            np.testing.assert_array_equal(ids, guardados)
            np.testing.assert_allclose(origen, origen_guardado, atol=1e-7, rtol=0)
            print(f"IFC y máscaras coinciden: {lado} m, {np.count_nonzero(ids)} celdas.")
        return
    aplicar_fisica(insumos, a.fisica, a.retiro_final_h)
    caso = deepcopy(planes[a.caso])
    caso["estratos"] = a.activacion != "bloque"
    if a.activacion == "estratos-tardio":
        caso["edad_inicio_h"] = "duracion"
    config = deepcopy(insumos.leer(insumos.CONFIGURACIONES))
    config["experimentos"][a.caso] = caso
    esperado = {(x["curva"], x["clima"]): x["peso"] for x in referencia["corridas"]}
    pares = sorted(esperado if not a.escenario else {tuple(x) for x in a.escenario})
    if not set(pares).issubset(esperado):
        p.error("Escenario ausente del catálogo.")
    control, *_ = insumos.importar_solver(a.geometria)
    filas = []
    traza_critica = None
    peor_delta = -np.inf
    with TemporaryDirectory(prefix="f02-luis-") as temporal:
        temp = Path(temporal)
        for curva, clima in pares:
            motor.ejecutar(SimpleNamespace(experimento=a.caso, salida=temp, modo="completo",
                escenario=[curva, clima], geometria=a.geometria, lado=a.lado,
                paso_max=a.paso_max, traza=True), config)
            ruta = temp / f"{a.caso}_{curva}_{clima}.json"
            corrida = insumos.leer(ruta)
            fila, = corrida["corridas"]
            historia = fila.pop("historia")
            dt = np.diff([x["tiempo_h"] for x in historia])*3600
            if not len(dt) or not (dt > 0).all():
                raise ValueError("Avance temporal registrado irregular.")
            assert dt.max() <= a.paso_max + 1e-6
            assert fila["peso"] == esperado[(curva, clima)]
            fila.update(paso_efectivo_min_s=float(dt.min()), paso_efectivo_max_s=float(dt.max()),
                        cpu_s=corrida["duracion_auditoria_s"])
            delta = fila["DeltaTmax"]["valor"]
            if not a.escenario and delta > peor_delta:
                peor_delta = delta
                traza_critica = dict(curva=curva, clima=clima, historia=historia)
            filas.append(fila)
    salida = {k:v for k,v in corrida.items() if k != "corridas"}
    completo = not a.escenario and len(filas)==24
    alertas = sum(f["pico_no_resuelto"] for f in filas)
    riesgo = control.riesgo(filas) if completo else None
    salida.update(activacion=a.activacion, fisica=a.fisica, config_sha256=huella(ruta_config.read_bytes()),
                  adaptador_viento=meta|hashes, picos_no_resueltos=alertas, riesgo=riesgo,
                  riesgo_336=control.riesgo([dict(f["base_336h"], peso=f["peso"], clima=f["clima"])
                                             for f in filas]) if completo else None,
                  horizontes_h=sorted({f["horizonte_h"] for f in filas}),
                  duracion_auditoria_s=sum(f["cpu_s"] for f in filas), corridas=filas)
    if a.retiro_final_h is not None:
        salida["retiro_final_edad_h"] = a.retiro_final_h
    if traza_critica is not None:
        salida["traza_critica"] = traza_critica
    a.salida.parent.mkdir(parents=True,exist_ok=True)
    with a.salida.open("x",encoding="utf-8") as archivo:
        json.dump(salida,archivo,ensure_ascii=False,indent=2,allow_nan=False)
        archivo.write("\n")
    print(f"{a.salida}: {len(filas)} pares, riesgo={riesgo}, alertas={alertas}", flush=True)


if __name__ == "__main__":
    main()
