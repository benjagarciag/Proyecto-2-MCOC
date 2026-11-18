"""Refina malla y paso por separado para la única con h=20; solo bajo --ejecutar."""
import argparse
import csv
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

_spec = importlib.util.spec_from_file_location("preparacion_sensibilidad_h", Path(__file__).with_name("ejecutar.py"))
_preparacion = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_preparacion)
RAIZ, SHA = _preparacion.RAIZ, _preparacion.SHA
preparar, cargar = _preparacion.preparar, _preparacion.cargar


PLAN = "publicada_unica"
RESOLUCIONES = {"malla_025_paso900": (.25, 900), "malla_050_paso450": (.5, 450)}


def leer(ruta):
    return json.loads(ruta.read_text(encoding="utf-8"))


def par(fila):
    return fila["curva"], fila["clima"]


def seleccionar(base, cercanos):
    return sorted(par(f) for f in base["corridas"] if not cercanos
                  or abs(f["DeltaTmax"]["valor"] - 20) <= 1
                  or f["excede_70"] or f["excede_20"])


def guardar_csv(ruta, filas):
    if filas:
        with ruta.open("w", encoding="utf-8", newline="") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=list(filas[0]))
            escritor.writeheader()
            escritor.writerows(filas)


def resumir(salida, base):
    referencias = {par(f): f for f in base["corridas"]}
    tabla, riesgos = [], []
    for etiqueta, (lado, paso) in RESOLUCIONES.items():
        filas = {}
        for ruta in sorted((salida / etiqueta).glob(f"{PLAN}_*.json")):
            d = leer(ruta)
            if (d["lado_m"], d["paso_max_s"]) != (lado, paso) or d["estudio_h"]["h_W_m2K"] != 20:
                raise ValueError(f"Configuración inesperada: {ruta}")
            for f in d["corridas"]:
                clave = par(f)
                if clave not in referencias or clave in filas:
                    raise ValueError("Escenario duplicado o ajeno al catálogo.")
                filas[clave] = f
                b = referencias[clave]
                tabla.append(dict(resolucion=etiqueta, curva=clave[0], clima=clave[1],
                    h_W_m2K=20, lado_m=lado, paso_max_s=paso,
                    Tmax_C=f["Tmax"]["valor"], DeltaTmax_K=f["DeltaTmax"]["valor"],
                    cambio_Tmax_K=f["Tmax"]["valor"]-b["Tmax"]["valor"],
                    cambio_DeltaT_K=f["DeltaTmax"]["valor"]-b["DeltaTmax"]["valor"],
                    excede_70=f["Tmax"]["valor"] > 70, excede_20=f["DeltaTmax"]["valor"] > 20,
                    cambia_clasificacion=(f["Tmax"]["valor"] > 70 or f["DeltaTmax"]["valor"] > 20)
                        != (b["excede_70"] or b["excede_20"]),
                    horizonte_h=f["horizonte_h"], alerta_cola=f["pico_no_resuelto"],
                    hora_DeltaT=f["DeltaTmax"]["tiempo_h"], pasos=f["pasos"],
                    residuo_J=f["balance_J"]["residuo"], archivo=str(ruta.relative_to(salida))))
        if not filas:
            continue
        completas = set(filas) == set(referencias)
        alertas = sum(f["pico_no_resuelto"] for f in filas.values())
        pt = sum(f["peso"] for f in filas.values() if f["Tmax"]["valor"] > 70)
        pd = sum(f["peso"] for f in filas.values() if f["DeltaTmax"]["valor"] > 20)
        pf = sum(f["peso"] for f in filas.values()
                 if f["Tmax"]["valor"] > 70 or f["DeltaTmax"]["valor"] > 20)
        riesgos.append(dict(resolucion=etiqueta, escenarios=len(filas), matriz_completa=completas,
            peso_evaluado=sum(f["peso"] for f in filas.values()),
            P_T=pt if completas else None, P_delta=pd if completas else None,
            P_f=pf if completas else None, peso_fallido_observado=pf, alertas_cola=alertas,
            estado=("incompleto: no estima probabilidad total" if not completas else
                    "indeterminado: cola pendiente" if alertas else
                    "cumple en esta resolución" if pf <= .05 else "excede")))
    guardar_csv(salida / "comparacion_por_escenario.csv", tabla)
    guardar_csv(salida / "riesgo_por_resolucion.csv", riesgos)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ejecutar", action="store_true")
    parser.add_argument("--comprobar-insumos", action="store_true")
    parser.add_argument("--resumir", action="store_true")
    parser.add_argument("--cercanos", action="store_true", help="Solo fallos y pares a <=1 K del umbral; sin riesgo total.")
    parser.add_argument("--resolucion", choices=RESOLUCIONES, help="Por defecto ejecuta ambas, por separado.")
    parser.add_argument("--salida", type=Path, default=RAIZ / "resultados/sensibilidad_h/refinamiento_unica_h20")
    args = parser.parse_args()
    ruta_base = RAIZ / "resultados/sensibilidad_h/h_20/publicada_unica.json"
    base = leer(ruta_base)
    assert base["estudio_h"]["h_W_m2K"] == 20 and base["lado_m"] == .5 and base["paso_max_s"] == 900
    assert len(base["corridas"]) == 24 and len({par(f) for f in base["corridas"]}) == 24
    if args.resumir:
        resumir(args.salida, base)
        return
    seleccion = seleccionar(base, args.cercanos)
    resoluciones = [args.resolucion] if args.resolucion else list(RESOLUCIONES)
    print("Única, h=20, enfriamiento desde 6 h de edad. Base: 0,50 m/900 s.")
    print(f"{len(seleccion)} escenarios x {len(resoluciones)} resoluciones; sin cambiar fuentes, clima ni controles.")
    for etiqueta in resoluciones:
        print(etiqueta, RESOLUCIONES[etiqueta])
    if not (args.ejecutar or args.comprobar_insumos):
        print("Sin simulaciones. Añadir --ejecutar para calcular o --comprobar-insumos para lectura.")
        return
    preparar()
    insumos, motor, huella = cargar()
    configuraciones = insumos.leer(insumos.CONFIGURACIONES)
    if args.comprobar_insumos:
        controles, *_ = insumos.importar_solver("exportada")
        cfg = insumos.leer(insumos.CONFIG)
        datos_base = insumos.leer(insumos.RAIZ / cfg["base"])
        for etiqueta in resoluciones:
            ids, _ = insumos.leer_malla(controles, datos_base, RESOLUCIONES[etiqueta][0], "exportada")
            print(etiqueta, "máscara disponible:", ids.shape)
        print("Comprobación sin simulaciones finalizada.")
        return
    motor.H_ESTUDIO = 20.
    for etiqueta in resoluciones:
        lado, paso = RESOLUCIONES[etiqueta]
        salida = args.salida / etiqueta
        salida.mkdir(parents=True, exist_ok=True)
        meta = dict(commit_fuentes=SHA, h_W_m2K=20, lado_m=lado, paso_max_s=paso,
            base_sha256=sha256(ruta_base.read_bytes()).hexdigest(), adaptacion_sha256=huella,
            script_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
        ruta_meta = salida / "procedencia.json"
        if ruta_meta.exists() and leer(ruta_meta) != meta:
            raise ValueError("Cambió la procedencia; usar otra salida.")
        ruta_meta.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
        for curva, clima in seleccion:
            ruta = salida / f"{PLAN}_{curva}_{clima}.json"
            if ruta.exists():
                if leer(ruta).get("estudio_h") != meta:
                    raise ValueError(f"Procedencia inconsistente: {ruta}")
                print("Conservado:", ruta.name)
                continue
            parametros = SimpleNamespace(experimento=PLAN, salida=salida, modo="completo",
                escenario=[curva, clima], geometria="exportada", lado=lado, paso_max=paso, traza=False)
            motor.ejecutar(parametros, configuraciones)
            resultado = leer(ruta)
            resultado["estudio_h"] = meta
            ruta.write_text(json.dumps(resultado, ensure_ascii=False, indent=2, allow_nan=False)+"\n", encoding="utf-8")
            resumir(args.salida, base)


if __name__ == "__main__":
    main()
