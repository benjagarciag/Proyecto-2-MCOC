"""Sensibilidad F02 a h; sin argumentos solo muestra el diseño, sin simular."""
import argparse
import csv
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from types import ModuleType, SimpleNamespace


RAIZ = Path(__file__).resolve().parents[2]
SHA = "6718163118123c4b05667b91ad5b4d50124dcf2d"
COPIA = RAIZ / ".venv/cache/f02_sensibilidad_h"
PLANES = ("publicada_unica", "publicada_rapida", "publicada_referencia", "lenta_12kw")


def preparar():
    """Extrae insumos del commit congelado, sin checkout ni modificación de main."""
    if COPIA.exists():
        if (COPIA / "COMMIT_ORIGEN").read_text(encoding="utf-8").strip() != SHA:
            raise ValueError("La copia aislada no corresponde al commit esperado.")
        return
    import io
    import zipfile
    rutas = ["desarrollo/mcplan", "desarrollo/fundacion/fundacion.ifc",
             "casos/incertidumbre", "casos/f02_verificaciones",
             "casos/semana4/parametros.json", "datos", "resultados/incertidumbre",
             "resultados/f02_verificaciones", "resultados/e12/visualizador.html"]
    contenido = subprocess.check_output(["git", "archive", "--format=zip", SHA, *rutas], cwd=RAIZ)
    with zipfile.ZipFile(io.BytesIO(contenido)) as archivo:
        COPIA.mkdir(parents=True)
        archivo.extractall(COPIA)
    (COPIA / "COMMIT_ORIGEN").write_text(SHA + "\n", encoding="utf-8")


def cargar():
    sys.path.insert(0, str(COPIA / "casos/f02_verificaciones"))
    import insumos
    ruta = COPIA / "casos/f02_verificaciones/ejecutar.py"
    fuente = ruta.read_text(encoding="utf-8")
    cambios = {
        "dt_tope_s=step)": "dt_tope_s=step, h_aire_W_m2K=H_ESTUDIO)",
        "        final = solve(horizon)": (
            "        final = solve(horizon)\n"
            "        while (controls.alertas_cola(final, horizon, duration, cfg['inicio_tardio_edad_min_h'])\n"
            "               and horizon < cfg['extension_max_h']):\n"
            "            horizon = min(horizon + 72, cfg['extension_max_h'])\n"
            "            final = solve(horizon)"),
    }
    for anterior, nuevo in cambios.items():
        if fuente.count(anterior) != 1:
            raise ValueError("Cambió el ejecutor congelado; revisar adaptación antes de calcular.")
        fuente = fuente.replace(anterior, nuevo)
    modulo = ModuleType("f02_estudio_h")
    modulo.__file__ = str(ruta)
    exec(compile(fuente, str(ruta), "exec"), modulo.__dict__)
    return insumos, modulo, sha256(fuente.encode()).hexdigest()


def resumir(salida):
    filas = []
    for ruta in sorted(salida.glob("h_*/*.json")):
        if ruta.name == "procedencia.json":
            continue
        d = json.loads(ruta.read_text(encoding="utf-8"))
        if "corridas" not in d:
            continue
        corridas = d["corridas"]
        if len(corridas) != 24 or abs(sum(x["peso"] for x in corridas) - 1) > 1e-10:
            raise ValueError(f"Matriz incompleta: {ruta}")
        pt = sum(x["peso"] for x in corridas if x["Tmax"]["valor"] > 70)
        pd = sum(x["peso"] for x in corridas if x["DeltaTmax"]["valor"] > 20)
        pf = sum(x["peso"] for x in corridas
                 if x["Tmax"]["valor"] > 70 or x["DeltaTmax"]["valor"] > 20)
        alertas = sum(x["pico_no_resuelto"] for x in corridas)
        filas.append(dict(h_W_m2K=float(ruta.parent.name.removeprefix("h_")),
            plan=d["experimento"], D_h=d["D_h"],
            Tmax_C=max(x["Tmax"]["valor"] for x in corridas),
            DeltaTmax_K=max(x["DeltaTmax"]["valor"] for x in corridas),
            P_T=pt, P_delta=pd, P_f=pf, alertas_cola=alertas,
            clasificacion="indeterminada: cola pendiente" if alertas else
                          ("cumple" if pf <= .05 else "excede"),
            residuo_max_J=max(abs(x["balance_J"]["residuo"]) for x in corridas)))
    if filas:
        with (salida / "comparacion.csv").open("w", encoding="utf-8", newline="") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=list(filas[0]))
            escritor.writeheader()
            escritor.writerows(filas)
        print(f"Tabla actualizada: {salida / 'comparacion.csv'}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ejecutar", action="store_true", help="Ejecuta explícitamente las simulaciones.")
    parser.add_argument("--comprobar-insumos", action="store_true", help="Solo lectura e importación; no simula.")
    parser.add_argument("--resumir", action="store_true", help="Agrega resultados existentes, sin simular.")
    parser.add_argument("--h", nargs="+", type=float, choices=(5., 10., 20.), default=[5., 10., 20.])
    parser.add_argument("--planes", nargs="+", choices=PLANES + ("publicada_tras_colocacion",), default=list(PLANES))
    parser.add_argument("--salida", type=Path, default=RAIZ / "resultados/sensibilidad_h")
    args = parser.parse_args()
    if args.resumir:
        resumir(args.salida)
        return
    print(f"Base: {SHA}\nh: {args.h} W/(m2 K)\nPlanes: {args.planes}")
    print(f"{len(set(args.h))*len(set(args.planes))*24} pares plan/h/curva/clima; cada par evalúa 336 y 600 h, ampliables a 672 h.")
    if not (args.ejecutar or args.comprobar_insumos):
        print("No se ejecutó ninguna simulación. Usa --comprobar-insumos o --ejecutar.")
        return
    preparar()
    insumos, motor, huella = cargar()
    configuraciones = insumos.leer(insumos.CONFIGURACIONES)
    if args.comprobar_insumos:
        controles, *_ = insumos.importar_solver("exportada")
        cfg = insumos.leer(insumos.CONFIG)
        base = insumos.leer(insumos.RAIZ / cfg["base"])
        fuentes = controles.materiales(base, insumos.HIDRATACION / "manifiesto.json")
        ids, _ = insumos.leer_malla(controles, base, .5, "exportada")
        for clima in cfg["historias"]:
            _, datos = controles.cargar_era5(insumos.RAIZ / clima["snapshot"])
            from datetime import datetime
            controles.serie_aire(datos, datetime.fromisoformat(clima["inicio"]), 672)
        print(f"Lectura e importación correctas: {len(fuentes)} fuentes, 3 climas hasta 672 h, máscara {ids.shape}. Sin simulaciones.")
        return
    for h in dict.fromkeys(args.h):
        salida = args.salida / f"h_{h:g}"
        salida.mkdir(parents=True, exist_ok=True)
        procedencia = dict(commit_fuentes=SHA, h_W_m2K=h, adaptacion_sha256=huella,
                           script_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                           nota="Solo cambia h; cola automática hasta 672 h. Pesos condicionados, sin probabilidad asignada a h.")
        ruta_meta = salida / "procedencia.json"
        if ruta_meta.exists() and json.loads(ruta_meta.read_text(encoding="utf-8")) != procedencia:
            raise ValueError("La procedencia cambió; elegir otra salida.")
        ruta_meta.write_text(json.dumps(procedencia, indent=2) + "\n", encoding="utf-8")
        motor.H_ESTUDIO = h
        for plan in dict.fromkeys(args.planes):
            if (salida / f"{plan}.json").exists():
                print(f"Conservado resultado existente: h={h}, {plan}")
                continue
            parametros = SimpleNamespace(experimento=plan, salida=salida, modo="completo",
                escenario=None, geometria="exportada", lado=None, paso_max=None, traza=False)
            motor.ejecutar(parametros, configuraciones)
            ruta_resultado = salida / f"{plan}.json"
            registro = json.loads(ruta_resultado.read_text(encoding="utf-8"))
            registro["estudio_h"] = procedencia
            ruta_resultado.write_text(json.dumps(registro, ensure_ascii=False, indent=2,
                                                allow_nan=False) + "\n", encoding="utf-8")
            if h == 5:
                from verificar import _comparar_metrica
                if plan == "lenta_12kw":
                    original = insumos.leer(insumos.RESULTADOS / "matrices/lenta_12kw.json")
                else:
                    original = insumos.publicadas()[plan.removeprefix("publicada_")]
                originales = {insumos.par(f): f for f in original["corridas"]}
                for fila in registro["corridas"]:
                    previa = originales[insumos.par(fila)]
                    _comparar_metrica(dict(fila["base_336h"], curva=fila["curva"], clima=fila["clima"]),
                                      previa["base_336h"])
                    if fila["horizonte_h"] == previa["horizonte_h"]:
                        _comparar_metrica(fila, previa)
                print(f"h=5: métricas de referencia reproducidas para {plan}.")
            resumir(args.salida)


if __name__ == "__main__":
    main()
