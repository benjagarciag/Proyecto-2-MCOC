import numpy as np
import pytest

from mcplan.entorno_termico import Capa, borde_aire
from mcplan.hidratacion import CurvaAdiabatica
from mcplan.termica_fundacion import EntornoFundacion, simular


def test_manta_superior_modifica_solo_la_cara_superior_y_se_retira():
    manta = Capa(.04, .042, retiro_edad_h=.5)
    entorno = EntornoFundacion(2., 5., 20., .5, 1.2, (), 0., capas_superiores=(manta,))
    curva = CurvaAdiabatica(0, 3600, 2400, 900)
    corrida = simular(np.ones((1, 1, 1), dtype=int), (0, 0, 0), 1.,
                      {1: (0., 20.)}, curva, entorno, [0., 0.], (.5, .5, .5))
    geom = dict(area_m2=1., distancia_m=.5, k_W_mK=2., aire_C=0., h_W_m2K=5.)
    libre = borde_aire(**geom, edad_h=0.).H_W_K
    cubierta = borde_aire(**geom, edad_h=0., capas=(manta,)).H_W_K
    inicio = corrida.historia[0]
    assert inicio["aire_W"] == pytest.approx(-20. * (4*libre+ cubierta))
    assert inicio["suelo_W"] == pytest.approx(0.)
    retiro = next(fila for fila in corrida.historia if fila["tiempo_h"] == .5)
    assert retiro["aire_W"] == pytest.approx(-retiro["nucleo_C"] * 5*libre)
