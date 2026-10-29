"""Compara el enfriamiento uniforme con una serie independiente de Fourier."""
from dataclasses import replace
from pathlib import Path
import runpy

import numpy as np
import pytest


CASO = runpy.run_path(str(Path(__file__).resolve().parents[2] / 'casos/2d/Barra_Enfriamiento_2D.py'))


def test_barra_uniforme_estabilizacion_y_serie_analitica():
    # La prueba fija un paso estable para su malla, independiente del dt
    # que se edite al experimentar con el ejecutor interactivo.
    p = replace(CASO['PARAMETROS'], celdas_x=41, celdas_y=21, paso_tiempo_s=300)
    r, primero, pasos_hora = CASO['simular_barra'](p)
    maxima = r.temperatura_C.max(axis=(1, 2))
    assert r.temperatura_C.min() >= 10 - 1e-12
    assert np.all(np.diff(maxima) <= 1e-12)
    assert maxima[0] == 20
    assert maxima[primero] <= 10.1
    assert maxima[primero-1] > 10.1
    assert r.tiempos_s[primero]/3600 == pytest.approx(495, abs=3)
    np.testing.assert_allclose(r.tiempos_s[::pasos_hora],
                               np.arange(len(r.tiempos_s[::pasos_hora]))*3600)
    # Solución separable de interior uniforme: producto de dos series 1D.
    n = int(np.argmin(abs(r.tiempos_s-100*3600)))
    t = r.tiempos_s[n]
    impares = np.arange(1, 100, 2)
    def factor(L):
        return np.sum(4/(np.pi*impares) * (-1.)**((impares-1)//2)
                      * np.exp(-p.alpha_m2_s*(impares*np.pi/L)**2*t))
    exacta_centro = 10 + 10*factor(4)*factor(2)
    centro = CASO['temperatura_centro'](r)
    assert centro[n] == pytest.approx(exacta_centro, abs=0.03)


@pytest.mark.parametrize('tol', [0, -1, 10, float('nan')])
def test_rechaza_tolerancia_invalida(tol):
    with pytest.raises(ValueError, match='tolerancia'):
        CASO['simular_barra'](tolerancia=tol)


def test_rechaza_paso_inestable_antes_del_ajuste_horario():
    p = replace(CASO['PARAMETROS'], paso_tiempo_s=3600)
    with pytest.raises(ValueError, match='inestable'):
        CASO['simular_barra'](p)
