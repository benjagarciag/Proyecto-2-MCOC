import numpy as np
import pytest

from mcplan.hidratacion import CurvaAdiabatica
from mcplan.termica_fundacion import EnfriamientoInterior, EntornoFundacion, simular


def test_enfriamiento_respeta_potencia_horario_y_balance():
    ids = np.array([[[1]]])
    entorno = EntornoFundacion(2., 0., 20., .5, 1.2, (), -10.)
    curva = CurvaAdiabatica(0, 3600, 2400, 900)
    sistema = EnfriamientoInterior(ids > 0, 100., 18., 100., .25, .75)
    r = simular(ids, (0, 0, 0), 1., {1: (0., 20.)}, curva, entorno,
                [20., 20.], (.5, .5, .5), enfriamiento=sistema)
    assert r.balance_J["enfriamiento"] == pytest.approx(-180000)
    assert r.balance_J["enfriamiento_pico_W"] == pytest.approx(100)
    assert abs(r.balance_J["residuo"]) < 1e-6
    assert r.historia[-1]["nucleo_C"] == pytest.approx(20.-180000/2160000)


def test_enfriamiento_rechaza_mascara_en_celda_vacia():
    ids = np.array([[[1, 0]]])
    entorno = EntornoFundacion(2., 0., 20., .5, 1.2, (), -10.)
    curva = CurvaAdiabatica(0, 3600, 2400, 900)
    sistema = EnfriamientoInterior(np.ones_like(ids, dtype=bool), 100., 18., 100., .25, .75)
    with pytest.raises(ValueError, match="Máscara"):
        simular(ids, (0, 0, 0), 1., {1: (0., 20.)}, curva, entorno,
                [20., 20.], (.5, .5, .5), enfriamiento=sistema)
