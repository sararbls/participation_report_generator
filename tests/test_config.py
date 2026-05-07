import pytest

from participation_report.config import load_config


def _write_env(tmp_path, content: str):
    env_file = tmp_path / ".env"
    env_file.write_text(content, encoding="utf-8")
    return env_file


def test_load_config_ok(tmp_path, monkeypatch):
    monkeypatch.delenv("EMPRESA", raising=False)
    monkeypatch.delenv("PUBLICO_1", raising=False)
    monkeypatch.delenv("CSV_1", raising=False)

    env_file = _write_env(
        tmp_path,
        "\n".join(
            [
                "EMPRESA=Hospital Central",
                "SEPARADOR=;",
                "PUBLICO_1=Clientes",
                "CSV_1=data/clientes.csv",
            ]
        ),
    )

    cfg = load_config(str(env_file))

    assert cfg.empresa == "Hospital Central"
    assert cfg.separador == ";"
    assert cfg.publicos_y_csvs == [("Clientes", "data/clientes.csv")]


def test_load_config_falla_sin_empresa(tmp_path, monkeypatch):
    monkeypatch.delenv("EMPRESA", raising=False)
    monkeypatch.delenv("PUBLICO_1", raising=False)
    monkeypatch.delenv("CSV_1", raising=False)

    env_file = _write_env(
        tmp_path,
        "\n".join(
            [
                "PUBLICO_1=Clientes",
                "CSV_1=data/clientes.csv",
            ]
        ),
    )

    with pytest.raises(SystemExit, match="EMPRESA es obligatorio"):
        load_config(str(env_file))


def test_load_config_falla_si_par_incompleto(tmp_path, monkeypatch):
    monkeypatch.delenv("EMPRESA", raising=False)
    monkeypatch.delenv("PUBLICO_1", raising=False)
    monkeypatch.delenv("CSV_1", raising=False)

    env_file = _write_env(
        tmp_path,
        "\n".join(
            [
                "EMPRESA=Hospital Central",
                "PUBLICO_1=Clientes",
            ]
        ),
    )

    with pytest.raises(SystemExit, match="deben definirse juntos"):
        load_config(str(env_file))
