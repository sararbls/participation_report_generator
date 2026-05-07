import re

from participation_report.services import _resolve_output_path


def test_resolve_output_path_default_va_a_processed_data(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    out = _resolve_output_path("Clínica Águila")

    assert re.match(
        r"^processed_data[/\\]reporte_participacion_Clinica_Aguila_\d{8}_\d{6}\.xlsx$",
        out,
    )


def test_resolve_output_path_nombre_simple_va_a_processed_data(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    out = _resolve_output_path("Hospital Central")

    assert re.match(
        r"^processed_data[/\\]reporte_participacion_Hospital_Central_\d{8}_\d{6}\.xlsx$",
        out,
    )
