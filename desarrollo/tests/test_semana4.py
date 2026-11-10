from datetime import datetime, timedelta, timezone

import numpy as np
import pytest

from mcplan.clima import HoraClima, Pronostico
from mcplan.clima_historico import serie_aire
from mcplan.hidratacion import CurvaAdiabatica
from mcplan.termica_fundacion import EntornoFundacion, simular


def entorno(h=0, dt=3600):
    # Plano de suelo alejado: estos casos analíticos no intercambian con tierra.
    return EntornoFundacion(2, h, 15, .5, 1.2, (), -1, dt)


def curva(theta=0):
    return CurvaAdiabatica(theta, 3600, 2400, 900)


def test_no_extrapola_y_exige_marca_final():
    t = datetime(2026, 11, 10, tzinfo=timezone.utc)
    clima = Pronostico((HoraClima(t, 10, None, None), HoraClima(t+timedelta(hours=1), 12, None, None)))
    assert serie_aire(clima, t, 1) == [10, 12]
    with pytest.raises(ValueError, match="no se extrapola"):
        serie_aire(clima, t, 2)


def test_fuente_adiabatica_integrada_con_dos_pasos():
    for dt in (900, 450):
        r = simular(np.ones((1, 1, 1), dtype=int), [0, 0, 0], 1, {1: (0, 20)},
                    curva(10), entorno(dt=dt), [10, 30], [.5, .5, .5])
        assert r.pico["valor"] == pytest.approx(20 + 10*(1-np.exp(-1)))
        assert r.diferencial["valor"] == pytest.approx(0)
        assert r.balance_J["residuo"] == pytest.approx(0, abs=1e-6)


def test_aire_horario_alimenta_robin_y_s25_no_es_la_cara():
    r = simular(np.ones((1, 1, 1), dtype=int), [0, 0, 0], 1, {1: (0, 20)},
                curva(), entorno(h=5), [10, 30, 30], [.5, .5, .5])
    H = 1/(.5/2 + 1/5)
    C = 2400*900
    primero = 20 + 3600*6*H*(10-20)/C
    segundo = primero + 3600*6*H*(30-primero)/C
    assert [x["nucleo_C"] for x in r.historia] == pytest.approx([20, primero, segundo])
    assert r.historia[0]["Tmin_S25_C"] == pytest.approx(20+H*(10-20)*(.5-.025)/2)
    assert r.balance_J["residuo"] == pytest.approx(0, abs=1e-6)


def test_activar_exactamente_al_final_sin_reiniciar_primera_celda():
    r = simular(np.array([[[1, 2]]]), [0, 0, 0], 1, {1: (0, 20), 2: (3600, 30)},
                curva(), entorno(), [10, 10], [.5, .5, .5])
    np.testing.assert_allclose(r.campos["final"].temperatura_C, [[[20, 30]]])
    assert r.historia[0]["voxeles_activos"] == 1 and r.historia[-1]["voxeles_activos"] == 2
    assert r.pico["tiempo_h"] == 1
    assert r.balance_J["colocacion"] == 2400*900*50


def test_conduccion_interna_conserva_y_no_cruza_vacio():
    for ids in (np.array([[[1, 2]]]), np.array([[[1, 0, 2]]])):
        r = simular(ids, [0, 0, 0], 1, {1: (0, 20), 2: (0, 30)},
                    curva(), entorno(), [10, 10], [.5, .5, .5])
        T = r.campos["final"].temperatura_C
        assert np.nansum(T) == pytest.approx(50)
        if ids.size == 2:
            assert T[0, 0, 0] == pytest.approx(20+3600*2*10/(2400*900))
        else:
            assert T[0, 0, 0] == 20 and np.isnan(T[0, 0, 1]) and T[0, 0, 2] == 30
