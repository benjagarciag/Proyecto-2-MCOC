"""Euler explícito conservativo en la máscara IFC, con clima horario y colocaciones."""
from dataclasses import dataclass
from math import isfinite

import numpy as np

from .entorno_termico import Capa, borde_aire, borde_suelo
from .hidratacion import CurvaAdiabatica


@dataclass(frozen=True)
class EntornoFundacion:
    k_W_mK: float
    h_aire_W_m2K: float
    suelo_C: float
    profundidad_suelo_m: float
    k_suelo_W_mK: float
    capas_laterales: tuple[Capa, ...]
    plano_suelo_z_m: float
    dt_tope_s: float = 900.

    def __post_init__(self):
        if not all(isfinite(x) and x > 0 for x in (
                self.k_W_mK, self.profundidad_suelo_m, self.k_suelo_W_mK, self.dt_tope_s)):
            raise ValueError("k, profundidad y paso tope deben ser finitos y positivos.")
        if not (isfinite(self.h_aire_W_m2K) and self.h_aire_W_m2K >= 0
                and isfinite(self.suelo_C) and isfinite(self.plano_suelo_z_m)):
            raise ValueError("Datos de aire o suelo inválidos.")


@dataclass
class Campo:
    tiempo_s: float
    fase: str
    temperatura_C: np.ndarray
    superficie: np.ndarray
    s25_min_C: np.ndarray


@dataclass
class Corrida:
    historia: list[dict]
    pico: dict
    diferencial: dict
    campos: dict[str, Campo]
    balance_J: dict
    pasos: int
    nucleo_xyz_m: tuple


def _vecindad(ids, ocupados):
    """Vecinos compactos (vacío = -1), orden -Z,+Z,-Y,+Y,-X,+X."""
    mapa = np.full(ids.shape, -1, dtype=np.intp)
    mapa[ids > 0] = np.arange(len(ocupados))
    extendido = np.pad(mapa, 1, constant_values=-1)
    coords = np.column_stack(np.unravel_index(ocupados, ids.shape))
    vecinos = []
    for eje in range(3):
        for signo in (-1, 1):
            q = coords + 1
            q[:, eje] += signo
            vecinos.append(extendido[tuple(q.T)])
    return coords, np.column_stack(vecinos)


def simular(ids, origen_xyz_m, h_m, programa, curva, entorno, aire_horario_C,
            nucleo_xyz_m, *, profundidad_s25_m=.025):
    """programa: ID → (inicio [s], colocación [°C]); aire: marcas cada hora, incluido tf."""
    ids = np.asarray(ids)
    origen = np.asarray(origen_xyz_m, dtype=float)
    aire = np.asarray(aire_horario_C, dtype=float)
    if (ids.ndim != 3 or ids.dtype.kind not in "iu" or (ids < 0).any()
            or origen.shape != (3,) or not np.isfinite(origen).all()
            or not isfinite(h_m) or not 0 < profundidad_s25_m <= h_m/2):
        raise ValueError("Grilla inválida o S25 más profunda que media celda.")
    if aire.ndim != 1 or len(aire) < 2 or not np.isfinite(aire).all():
        raise ValueError("Se requiere aire horario completo, incluida la última marca.")
    if not isinstance(curva, CurvaAdiabatica):
        raise ValueError("Se requiere una curva de hidratación común al hormigón.")
    ocupados = np.flatnonzero(ids)
    propietarios = ids.ravel()[ocupados]
    if not len(ocupados) or set(propietarios) != set(programa):
        raise ValueError("Todas las vertidas del programa deben aparecer en la grilla.")
    for inicio, temperatura in programa.values():
        if not isfinite(inicio) or inicio < 0 or not isfinite(temperatura):
            raise ValueError("Cada colocación requiere un inicio no negativo y T finita.")
    if min(v[0] for v in programa.values()) != 0:
        raise ValueError("El horizonte debe empezar en la primera colocación (t=0).")
    comienzos = np.array([programa[i][0] for i in propietarios])
    colocacion = np.array([programa[i][1] for i in propietarios])
    coords, vecinos = _vecindad(ids, ocupados)
    centros = origen + (coords[:, ::-1] + .5) * h_m
    nucleo = np.asarray(nucleo_xyz_m, dtype=float)
    if nucleo.shape != (3,) or not np.isfinite(nucleo).all():
        raise ValueError("Punto de núcleo XYZ inválido.")
    i_nucleo = int(np.argmin(((centros - nucleo)**2).sum(axis=1)))
    if not np.all(abs(centros[i_nucleo] - nucleo) <= h_m/2 + 1e-12):
        raise ValueError("El punto de núcleo no cae en una celda de hormigón.")

    A, V = h_m**2, h_m**3
    k, distancia = entorno.k_W_mK, h_m/2
    C, G = curva.capacidad_volumetrica_J_m3K * V, k*A/h_m
    geom = dict(area_m2=A, distancia_m=distancia, k_W_mK=k)
    suelo = borde_suelo(**geom, suelo_C=entorno.suelo_C,
                        profundidad_m=entorno.profundidad_suelo_m,
                        k_suelo_W_mK=entorno.k_suelo_W_mK)
    tf = (len(aire)-1)*3600.
    eventos = sorted({0., tf, *[float(x) for x in range(3600, int(tf), 3600)],
                      *[inicio for inicio, _ in programa.values() if inicio < tf],
                      *[inicio+c.retiro_edad_h*3600 for inicio, _ in programa.values()
                        for c in entorno.capas_laterales if c.retiro_edad_h is not None
                        and inicio+c.retiro_edad_h*3600 < tf]})
    T = np.full(len(ocupados), np.nan)
    historia, campos = [], {}
    pico, diferencial = {"valor": -np.inf}, {"valor": -np.inf}
    e_colocada = e_suelo = e_aire = e_hidratacion = 0.
    pasos = 0

    def preparar(t):
        activos = comienzos <= t
        # Cada enlace interno se calcula solo una vez, desde la dirección positiva.
        ia = np.flatnonzero(activos)
        pares = []
        suma = np.zeros(len(T))
        for d in (1, 3, 5):
            j = vecinos[ia, d]
            ok = (j >= 0) & activos[j]
            a, b = ia[ok], j[ok]
            pares.append((a, b))
            suma[a] += G
            suma[b] += G
        j = vecinos[ia]
        fila, d = np.where((j < 0) | ~activos[j])
        i = ia[fila]
        es_suelo = (d == 0) & np.isclose(centros[i, 2]-distancia, entorno.plano_suelo_z_m,
                                        atol=1e-7, rtol=0)
        H = np.zeros(len(i))
        H[es_suelo] = suelo.H_W_K
        H[~es_suelo] = borde_aire(**geom, aire_C=0, h_W_m2K=entorno.h_aire_W_m2K,
                                  edad_h=0).H_W_K
        for vid, (inicio, _) in programa.items():
            caras = (~es_suelo) & (d >= 2) & (propietarios[i] == vid)
            if caras.any():
                H[caras] = borde_aire(**geom, aire_C=0, h_W_m2K=entorno.h_aire_W_m2K,
                                      edad_h=(t-inicio)/3600, capas=entorno.capas_laterales).H_W_K
        suma += np.bincount(i, weights=H, minlength=len(T))
        dt = min(entorno.dt_tope_s, .8*C/suma.max()) if suma.max() > 0 else entorno.dt_tope_s
        return ia, pares, i, d, es_suelo, H, dt

    def aire_en(t):
        j = min(int(t//3600), len(aire)-2)
        return float(aire[j] + (aire[j+1]-aire[j])*(t/3600-j))

    def potencia_borde(op, t):
        _, _, i, _, suelo_mask, H, _ = op
        return H*(np.where(suelo_mask, entorno.suelo_C, aire_en(t))-T[i])

    def guardar(t, fase, i, s25):
        campo = np.full(ids.size, np.nan)
        campo[ocupados] = T
        es_superficie = np.zeros(ids.size, dtype=np.uint8)
        es_superficie[ocupados[i]] = 1
        temp_s25 = np.full(len(T), np.inf)
        np.minimum.at(temp_s25, i, s25)
        temp_s25[~np.isfinite(temp_s25)] = np.nan
        superficial = np.full(ids.size, np.nan)
        superficial[ocupados] = temp_s25
        return Campo(t, fase, campo.reshape(ids.shape), es_superficie.reshape(ids.shape),
                     superficial.reshape(ids.shape))

    def punto_cara(i, d, desplazamiento):
        p = centros[i].copy()
        p[2-d//2] += desplazamiento * (1 if d % 2 else -1)
        return p.tolist()

    def medir(t, op, fase, registrar=True):
        nonlocal pico, diferencial
        ia, _, i, d, _, _, _ = op
        P = potencia_borde(op, t)
        cara = T[i] + P*distancia/(k*A)
        s25 = T[i] + P*(distancia-profundidad_s25_m)/(k*A)
        caliente = ia[np.argmax(T[ia])]
        j = int(np.argmax(cara))
        Tmax = float(T[caliente])
        xyz_max = centros[caliente].tolist()
        tipo = "centro"
        if cara[j] > Tmax:
            caliente, Tmax, tipo = i[j], float(cara[j]), "cara"
            xyz_max = punto_cara(caliente, d[j], distancia)
        m = int(np.argmin(s25))
        Tmin = float(s25[m])
        base = dict(tiempo_h=t/3600, fase=fase, Tmax_C=Tmax, xyz_Tmax_m=xyz_max,
                    lugar_Tmax=tipo, vertida_Tmax=int(propietarios[caliente]))
        if Tmax > pico["valor"]:
            pico = {**base, "valor": Tmax}
            campos["pico"] = guardar(t, fase, i, s25)
        if Tmax-Tmin > diferencial["valor"]:
            diferencial = {**base, "valor": Tmax-Tmin, "Tmin_S25_C": Tmin,
                           "xyz_S25_m": punto_cara(i[m], d[m], distancia-profundidad_s25_m),
                           "vertida_S25": int(propietarios[i[m]])}
            campos["diferencial"] = guardar(t, fase, i, s25)
        if registrar:
            historia.append(dict(tiempo_h=t/3600, aire_C=aire_en(t), Tmax_C=Tmax,
                                 Tmin_S25_C=Tmin, DeltaT_K=Tmax-Tmin,
                                 nucleo_C=float(T[i_nucleo]), voxeles_activos=len(ia)))
        if t == tf and registrar:
            campos["final"] = guardar(t, fase, i, s25)

    def activar(t):
        nonlocal e_colocada
        nuevos = (comienzos <= t) & ~np.isfinite(T)
        T[nuevos] = colocacion[nuevos]
        e_colocada += float(C*T[nuevos].sum())

    activar(0.)
    for inicio, fin in zip(eventos, eventos[1:]):
        op = preparar(inicio)
        ia, pares, i, _, suelo_mask, _, dt_max = op
        t = inicio
        medir(t, op, "posterior")
        while t < fin:
            siguiente = min(t+dt_max, fin)
            dt = siguiente-t
            P_borde = potencia_borde(op, t)
            potencia = np.bincount(i, weights=P_borde, minlength=len(T))
            for a, b in pares:
                flujo = G*(T[b]-T[a])
                potencia[a] += flujo
                potencia[b] -= flujo
            energia = V*curva.energia_intervalo_J_m3(t-comienzos[ia], siguiente-comienzos[ia])
            T[ia] += (dt*potencia[ia] + energia)/C
            e_hidratacion += float(energia.sum())
            e_suelo += dt*float(P_borde[suelo_mask].sum())
            e_aire += dt*float(P_borde[~suelo_mask].sum())
            pasos += 1
            t = siguiente
            if t < fin:
                medir(t, op, "paso")
        # Estado por la izquierda: justo antes de cambios de contacto o resistencia.
        medir(fin, op, "previo", registrar=False)
        activar(fin)
    medir(tf, preparar(tf), "posterior")
    e_final = float(C*np.nansum(T))
    balance = dict(colocacion=e_colocada, hidratacion=e_hidratacion, aire=e_aire, suelo=e_suelo,
                   final=e_final, residuo=e_final-e_colocada-e_hidratacion-e_aire-e_suelo)
    return Corrida(historia, pico, diferencial, campos, balance, pasos, tuple(centros[i_nucleo]))
