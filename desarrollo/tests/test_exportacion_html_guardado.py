"""Publicación del HTML sin ejecutar física ni modificar resultados del usuario."""
from pathlib import Path

import pytest

from mcplan import exportacion_html


def test_publicar_html_reemplaza_el_archivo(tmp_path):
    destino = tmp_path / "visualizador.html"
    temporal = tmp_path / "nuevo.html.tmp"
    destino.write_text("anterior", encoding="utf-8")
    temporal.write_text("nuevo: aislación", encoding="utf-8")
    exportacion_html._publicar_html(temporal, destino)
    assert destino.read_text(encoding="utf-8") == "nuevo: aislación"
    assert not temporal.exists()


def test_publicar_html_reintenta_un_bloqueo_transitorio(tmp_path, monkeypatch):
    destino = tmp_path / "visualizador.html"
    temporal = tmp_path / "nuevo.html.tmp"
    destino.write_text("anterior", encoding="utf-8")
    temporal.write_text("nuevo", encoding="utf-8")
    reemplazar = Path.replace
    intentos = []

    def bloqueado_al_principio(origen, salida):
        intentos.append(origen)
        if len(intentos) <= 2:
            assert destino.read_text(encoding="utf-8") == "anterior"
            raise PermissionError("Archivo en uso")
        return reemplazar(origen, salida)

    monkeypatch.setattr(Path, "replace", bloqueado_al_principio)
    monkeypatch.setattr(exportacion_html, "sleep", lambda _: None)
    exportacion_html._publicar_html(temporal, destino)
    assert len(intentos) == 3
    assert destino.read_text(encoding="utf-8") == "nuevo"


def test_publicar_html_conserva_ambos_archivos_si_sigue_bloqueado(tmp_path, monkeypatch):
    destino = tmp_path / "visualizador.html"
    temporal = tmp_path / "nuevo.html.tmp"
    destino.write_text("anterior", encoding="utf-8")
    temporal.write_text("nuevo", encoding="utf-8")

    def bloqueado(*_):
        raise PermissionError("Archivo en uso")

    monkeypatch.setattr(Path, "replace", bloqueado)
    monkeypatch.setattr(exportacion_html, "sleep", lambda _: None)
    with pytest.raises(PermissionError, match="no hace falta repetir") as error:
        exportacion_html._publicar_html(temporal, destino)
    assert str(temporal) in str(error.value)
    assert destino.read_text(encoding="utf-8") == "anterior"
    assert temporal.read_text(encoding="utf-8") == "nuevo"
