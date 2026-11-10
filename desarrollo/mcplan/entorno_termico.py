"""Coeficientes de cara para el balance térmico por celda: P = B - H*T."""
from dataclasses import dataclass
from math import isfinite


def _validar(nombre, valor, minimo=None, estricto=False):
    if not isfinite(valor) or (minimo is not None and
            (valor < minimo or (estricto and valor == minimo))):
        raise ValueError(f"Valor inválido de {nombre}: {valor}.")


@dataclass(frozen=True)
class Capa:
    espesor_m: float
    k_W_mK: float
    retiro_edad_h: float | None = None

    def __post_init__(self):
        _validar("espesor", self.espesor_m, 0, True)
        _validar("k de capa", self.k_W_mK, 0, True)
        if self.retiro_edad_h is not None:
            _validar("edad de retiro", self.retiro_edad_h, 0)

    def resistencia_m2K_W(self, edad_h):
        if self.retiro_edad_h is not None and edad_h >= self.retiro_edad_h:
            return 0.0
        return self.espesor_m / self.k_W_mK


@dataclass(frozen=True)
class BordeEntorno:
    H_W_K: float
    B_W: float
    solar_hacia_celda_W: float = 0.0

    def potencia_entrante_W(self, temperatura_celda_C):
        return self.B_W - self.H_W_K * temperatura_celda_C


def _resistencia_celda(area_m2, distancia_m, k_W_mK):
    _validar("área", area_m2, 0, True)
    _validar("distancia centro-cara", distancia_m, 0, True)
    _validar("k hormigón", k_W_mK, 0, True)
    return distancia_m / k_W_mK


def borde_aire(*, area_m2, distancia_m, k_W_mK, aire_C, h_W_m2K,
               edad_h, capas=(), solar_incidente_W_m2=0.0, absortancia=0.0):
    """Robin con capas en serie y onda corta opcional sobre la cara externa.

    h es solo convectivo. El calor solar se absorbe en la cara exterior de
    la última capa o del hormigón. Se reparte entre la celda y el ambiente
    mediante el mismo balance superficial; no se suma dos veces.
    """
    R = _resistencia_celda(area_m2, distancia_m, k_W_mK)
    _validar("aire", aire_C)
    _validar("h", h_W_m2K, 0)
    _validar("edad", edad_h, 0)
    _validar("irradiancia", solar_incidente_W_m2, 0)
    if not 0 <= absortancia <= 1:
        raise ValueError("La absortancia debe estar entre 0 y 1.")
    R += sum(c.resistencia_m2K_W(edad_h) for c in capas)
    divisor = 1 + h_W_m2K * R
    H = area_m2 * h_W_m2K / divisor
    solar = area_m2 * absortancia * solar_incidente_W_m2 / divisor
    return BordeEntorno(H, H * aire_C + solar, solar)


def borde_suelo(*, area_m2, distancia_m, k_W_mK, suelo_C,
                profundidad_m, k_suelo_W_mK, contacto_m2K_W=0.0):
    """Conducción a un reservorio de suelo a T prescrita, sin película de aire."""
    R = _resistencia_celda(area_m2, distancia_m, k_W_mK)
    _validar("suelo", suelo_C)
    _validar("profundidad", profundidad_m, 0, True)
    _validar("k suelo", k_suelo_W_mK, 0, True)
    _validar("resistencia de contacto", contacto_m2K_W, 0)
    H = area_m2 / (R + contacto_m2K_W + profundidad_m / k_suelo_W_mK)
    return BordeEntorno(H, H * suelo_C)
