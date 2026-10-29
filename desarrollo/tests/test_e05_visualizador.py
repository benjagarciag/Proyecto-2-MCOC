"""Ejecuta los mismos casos/configuraciones del visualizador, bajo petición."""
import json
from pathlib import Path
import pytest
from mcplan.visualizador_termico import CASOS, predeterminados, calcular, verificar


@pytest.mark.parametrize('caso', list(CASOS))
def test_configuracion_visualizador(caso):
    archivo = Path(__file__).resolve().parents[2]/'Visualizadores/parametros.json'
    entradas = json.loads(archivo.read_text(encoding='utf-8')) if archivo.exists() else {}
    c = {**predeterminados(caso), **entradas.get(caso,{})}
    vista = calcular(caso, c)
    ok, mensajes = verificar(vista)
    print('\n'+CASOS[caso]+'\n'+'\n'.join(mensajes))
    assert ok, '\n'.join(mensajes)
