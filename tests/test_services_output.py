import re
from pathlib import Path

from participation_report.services import _resolve_output_path


def test_resolve_output_path_default_va_a_processed_data(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    out = _resolve_output_path("informe.xlsx")

    assert re.match(r"^processed_data[/\\]informe_\d{8}_\d{6}\.xlsx$", out)
    assert Path("processed_data").exists()


def test_resolve_output_path_nombre_simple_va_a_processed_data(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    out = _resolve_output_path("reporte.xlsx")

    assert re.match(r"^processed_data[/\\]reporte_\d{8}_\d{6}\.xlsx$", out)


def test_resolve_output_path_con_subcarpeta_respeta_ruta(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    out = _resolve_output_path("salidas/reporte.xlsx")

    assert out == str(Path("salidas") / "reporte.xlsx")
    assert Path("salidas").exists()
