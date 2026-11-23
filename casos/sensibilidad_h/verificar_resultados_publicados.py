"""Comprueba las matrices publicadas del cierre sin regenerar sus archivos."""

from auditar_cierre_f02 import S, leer, pieza, riesgo


def main():
    resumen = leer(S / "resumen.json")
    piezas = 0
    transiciones = 0
    for matriz in resumen["matrices"]:
        caudal, malla = matriz["q"], matriz["h"]
        carpeta = S / f"q{caudal}/malla_{malla:g}_paso300"
        # En Windows, glob("M*.json") también devuelve "matriz.json".
        rutas = sorted(path for path in carpeta.glob("*.json") if path.name.startswith("M"))
        if len(rutas) != 24:
            raise ValueError(f"{carpeta}: se esperaban 24 escenarios, hay {len(rutas)}")

        datos = [pieza(path) for path in rutas]
        filas = [dato["corrida"] for dato in datos]
        pares = {(fila["curva"], fila["clima"]) for fila in filas}
        tempranas = [dict(dato["base_336h"], curva=fila["curva"],
                          clima=fila["clima"], peso=fila["peso"])
                     for dato, fila in zip(datos, filas)]
        if (len(pares) != 24 or riesgo(filas) != matriz["riesgo"]
                or riesgo(tempranas) != matriz["riesgo_336"]
                or max(fila["Tmax"]["valor"] for fila in filas) != matriz["Tmax"]
                or max(fila["DeltaTmax"]["valor"] for fila in filas) != matriz["Delta"]
                or sum(fila["pico_no_resuelto"] for fila in filas) != matriz["alertas"]):
            raise ValueError(f"{carpeta}: las piezas difieren del resumen publicado")
        piezas += len(datos)
        transiciones += sum(len(dato["control"]["eventos_circuitos"]) for dato in datos)
        print(f"{caudal} m³/h, {malla:g} m: 24 escenarios comprobados")
    if (piezas, transiciones) != (resumen["piezas"], resumen["transiciones"]):
        raise ValueError("El total de piezas o transiciones difiere del resumen publicado")
    print(f"Comprobados {piezas} escenarios y {transiciones} transiciones.")


if __name__ == "__main__":
    main()
