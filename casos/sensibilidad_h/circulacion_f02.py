"""Controles exploratorios de circulación para el caso F02 por estratos."""

from hashlib import sha256

from viento import cambiar


POLITICAS = {
    "ciclos": {"ciclo_encendido_h": 1, "ciclo_apagado_h": 1},
    "sectores": {"cortes_z_m": [1.5, 3.0], "activar_C": 19., "desactivar_C": 18.},
}


def adaptar(codigo, politica):
    """Adapta el solver horario congelado y devuelve el código de la variante."""
    opciones = POLITICAS[politica]
    codigo = cambiar(codigo, "        fin_frio = enfriamiento.fin_h * 3600.", f"""        inicio_circulacion = enfriamiento.edad_inicio_h * 3600.
        inicio_frio = np.maximum(comienzos, inicio_circulacion)
        fin_frio = enfriamiento.fin_h * 3600.
        politica_frio = {politica!r}
        if politica_frio == "sectores":
            bandas = np.digitize(centros[refrigerables, 2], {opciones.get("cortes_z_m", [])!r})
            sectores = tuple(refrigerables[bandas == b] for b in np.unique(bandas))
            abiertos = np.zeros(len(sectores), dtype=bool)""")
    codigo = cambiar(codigo, "    T = np.full(len(ocupados), np.nan)", """        if politica_frio == "ciclos":
            cantidad = int(np.ceil((min(tf, fin_frio) - inicio_circulacion) / 3600))
            cambios = [inicio_circulacion + n*3600. for n in range(1, cantidad)]
            eventos = sorted(set(eventos).union(cambios))
    T = np.full(len(ocupados), np.nan)""")
    codigo = cambiar(codigo, "    e_extraida = potencia_frio_max = 0.", """    e_extraida = e_recibida = potencia_frio_max = 0.""")
    codigo = cambiar(codigo, "            suma[enfriados] += G_frio", """            if politica_frio == "ciclos" and len(enfriados):
                hora_ciclo = int(np.floor((t-inicio_circulacion)/3600. + 1e-9))
                if hora_ciclo % 2:
                    enfriados = enfriados[:0]
            suma[enfriados] += G_frio""")
    codigo = cambiar(codigo, """            if len(enfriados):
                extraccion = G_frio * np.maximum(T[enfriados] - enfriamiento.referencia_C, 0.)
                total = float(extraccion.sum())
                if total > enfriamiento.tope_W:
                    extraccion *= enfriamiento.tope_W / total
                    total = enfriamiento.tope_W
                potencia[enfriados] -= extraccion
                e_extraida += dt * total
                potencia_frio_max = max(potencia_frio_max, total)""", f"""            if len(enfriados):
                circulando = enfriados
                if politica_frio == "sectores":
                    for n, sector in enumerate(sectores):
                        umbral = {opciones.get("desactivar_C", 18.)!r} if abiertos[n] else {opciones.get("activar_C", 19.)!r}
                        abiertos[n] = bool(np.all(T[sector] > umbral))
                    circulando = np.concatenate([s for s, abierto in zip(sectores, abiertos) if abierto]) if abiertos.any() else enfriados[:0]
                intercambio = G_frio * (T[circulando] - enfriamiento.referencia_C)
                positivos = intercambio > 0
                extraida = float(intercambio[positivos].sum())
                if extraida > enfriamiento.tope_W:
                    intercambio[positivos] *= enfriamiento.tope_W / extraida
                    extraida = enfriamiento.tope_W
                recibida = -float(intercambio[~positivos].sum())
                potencia[circulando] -= intercambio
                e_extraida += dt * extraida
                e_recibida += dt * recibida
                potencia_frio_max = max(potencia_frio_max, extraida)""")
    return cambiar(codigo, """        balance.update(enfriamiento=-e_extraida, enfriamiento_pico_W=potencia_frio_max)
        balance["residuo"] += e_extraida""", """        balance.update(enfriamiento=e_recibida-e_extraida, enfriamiento_pico_W=potencia_frio_max,
                       agua_extraida_J=e_extraida, agua_recibida_J=e_recibida)
        balance["residuo"] += e_extraida-e_recibida""")


def transformacion(politica):
    """Registra la huella de la variante para separar ambas procedencias."""
    huellas = {}

    def transformar(codigo):
        adaptado = adaptar(codigo, politica)
        huellas["solver_circulacion_sha256"] = sha256(adaptado.encode()).hexdigest()
        return adaptado

    return transformar, huellas
