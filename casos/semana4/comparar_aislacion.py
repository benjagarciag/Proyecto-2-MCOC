"""Compara lana de vidrio de 40/50 mm con el mismo caso y malla, bajo ejecución del usuario."""
import json
from pathlib import Path
import subprocess
import sys

from ejecutar import elegir_en_terminal

RAIZ = Path(__file__).resolve().parents[2]
CARPETA = Path(__file__).resolve().parent


def tabla_comparacion(corridas):
    filas = ["| Aislación | Tmax [°C] | Tiempo [h] | DeltaTmax [°C] | Tiempo [h] | Ambos límites en el ensayo |",
             "| --- | ---: | ---: | ---: | ---: | --- |"]
    for mm, r in corridas:
        cumple = r['Tmax']['valor'] <= 70 and r['DeltaTmax']['valor'] <= 20
        filas.append(f"| {mm} mm | {r['Tmax']['valor']:.3f} | {r['Tmax']['tiempo_h']:.2f} "
                     f"| {r['DeltaTmax']['valor']:.3f} | {r['DeltaTmax']['tiempo_h']:.2f} "
                     f"| {'Sí' if cumple else 'No'} |")
    return '\n'.join(filas)


def main():
    try:
        caso = elegir_en_terminal("¿Qué horizonte quieres comparar?", [
            ("E12 — 14 días, recomendado para evaluar los límites", "e12"),
            ("E11 — 48 h, comparación parcial", "e11"),
        ])
        lado = elegir_en_terminal("¿Qué malla usar en ambas corridas?", [
            ("0,50 m — más rápida", .5),
            ("0,25 m — más fina", .25),
        ])
    except (EOFError, KeyboardInterrupt):
        raise SystemExit("\nSelección cancelada; no se ejecutó ninguna simulación.") from None
    entradas = [CARPETA / f"aislacion_{mm}mm.json" for mm in (40, 50)]
    configs = [json.loads(p.read_text(encoding="utf-8")) for p in entradas]
    # Proteger la comparación contra cambios accidentales de otras entradas.
    normalizados = []
    for config in configs:
        c = json.loads(json.dumps(config))
        c.pop("documentacion_capas_laterales", None)
        c['entorno']['capas_laterales'][1]['espesor_m'] = 0
        c['entorno']['capas_laterales'][1]['k_W_mK'] = 0
        normalizados.append(c)
    if normalizados[0] != normalizados[1]:
        raise SystemExit("Las entradas difieren en más que el aislante. Revisarlas antes de comparar.")
    for config, mm, k in zip(configs, (40, 50), (.042, .041)):
        capa = config['entorno']['capas_laterales'][1]
        if capa['espesor_m'] != mm/1000 or capa['k_W_mK'] != k:
            raise SystemExit(f"La entrada de {mm} mm no coincide con la ficha documentada.")
    salida = RAIZ / "resultados" / caso / "comparacion_aislacion" / ("malla_050" if lado == .5 else "malla_025")
    corridas = []
    for mm, entrada in zip((40, 50), entradas):
        destino = salida / f"lana_{mm}mm"
        print(f"\nCalculando {caso.upper()}, malla {lado:g} m, lana de {mm} mm…", flush=True)
        comando = [sys.executable, "-X", "utf8", "-B", str(CARPETA / "ejecutar.py"),
                   caso, "--parametros", str(entrada), "--lado", str(lado),
                   "--intervalo-html", "1" if lado == .5 else "4", "--salida", str(destino)]
        proceso = subprocess.run(comando, cwd=RAIZ, stdout=subprocess.PIPE,
                                 text=True, encoding="utf-8")
        if proceso.returncode:
            print(proceso.stdout)
            raise SystemExit(f"Falló la corrida de {mm} mm; no se generó una conclusión comparativa.")
        r = json.loads((destino / "resumen.json").read_text(encoding="utf-8"))
        corridas.append((mm, r))
        print(f"HTML: {destino / 'visualizador.html'}", flush=True)
    tabla = tabla_comparacion(corridas)
    nota = ("Comparación de 336 h: revisar ambos límites, sensibilidad a la malla y montaje antes de decidir."
            if caso == "e12" else "Comparación parcial de 48 h: no permite concluir cumplimiento de 14 días.")
    texto = f"# Comparación lana 40/50 mm — {caso.upper()} — malla {lado:g} m\n\n{tabla}\n\n{nota}\n"
    (salida / "comparacion.md").write_text(texto, encoding="utf-8")
    print('\n' + tabla + '\n\n' + nota)
    print(f"Tabla guardada: {salida / 'comparacion.md'}")


if __name__ == "__main__":
    main()
