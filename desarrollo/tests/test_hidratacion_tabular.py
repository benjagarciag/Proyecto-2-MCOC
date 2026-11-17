import numpy as np
import pytest

from mcplan.hidratacion_tabular import CurvaTabular
from mcplan.termica_fundacion import EntornoFundacion, simular


def test_tabular_preserva_energia_y_edad_de_cada_vertida():
    curva = CurvaTabular([0, 3600, 7200], [0, 2e6, 3e6], 2e6)
    assert curva.valor([0, 3600, 7200]).tolist() == pytest.approx([2e6/3600, 1e6/3600, 0])
    assert curva.energia_intervalo_J_m3(1800, 10800) == pytest.approx(2e6)
    ids = np.array([[[1, 0, 2]]])
    entorno = EntornoFundacion(2, 0, 18, .5, 1.2, (), -10)
    r = simular(ids, (0, 0, 0), 1., {1: (0, 18.), 2: (3600, 18.)}, curva, entorno,
                [18.] * 4, (.5, .5, .5))
    assert r.balance_J["hidratacion"] == pytest.approx(6e6)
    assert r.campos["final"].temperatura_C[0, 0, [0, 2]] == pytest.approx([19.5, 19.5])


def test_tabular_rechaza_acumulado_decreciente():
    with pytest.raises(ValueError, match="no decreciente"):
        CurvaTabular([0, 10, 20], [0, 3, 2], 2e6)
