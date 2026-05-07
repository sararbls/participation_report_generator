import pytest

from participation_report.csv_reader import cargar_csv


def test_cargar_csv_ok(write_contacts_csv):
    csv_file = write_contacts_csv(
        "contactos_20260507.csv",
        [
            {
                "IdUsuario": "u1",
                "Nombre": "Ana",
                "Empresa": "Hospital Central",
                "Estado": "Completa",
            }
        ],
    )

    df = cargar_csv(str(csv_file), ";")

    assert list(df.columns) == ["IdUsuario", "Nombre", "Empresa", "Estado"]
    assert len(df) == 1
    assert df.iloc[0]["Nombre"] == "Ana"


def test_cargar_csv_falla_si_faltan_columnas(tmp_path):
    csv_file = tmp_path / "contactos_20260507.csv"
    csv_file.write_text(
        "IdUsuario;Nombre;Empresa\nu1;Ana;Hospital Central\n",
        encoding="utf-8",
    )

    with pytest.raises(SystemExit) as exc:
        cargar_csv(str(csv_file), ";")
    msg = str(exc.value)
    assert "no contiene todas las columnas requeridas" in msg
    assert "Faltan: Estado" in msg


def test_cargar_csv_con_separador_coma(tmp_path):
    csv_file = tmp_path / "contactos_20260507.csv"
    csv_file.write_text(
        "IdUsuario,Nombre,Empresa,Estado\n"
        "u1,Ana,Hospital Central,Completa\n",
        encoding="utf-8",
    )

    df = cargar_csv(str(csv_file), ",")

    assert len(df) == 1
    assert df.iloc[0]["Empresa"] == "Hospital Central"


def test_cargar_csv_limpia_comillas_simple_y_doble(tmp_path):
    csv_file = tmp_path / "contactos_20260507.csv"
    csv_file.write_text(
        "\"IdUsuario\";\"Nombre\";\"Empresa\";\"Estado\"\n"
        "'u1';'Ana';'Hospital Central';'Completa'\n",
        encoding="utf-8",
    )

    df = cargar_csv(str(csv_file), ";")

    assert list(df.columns) == ["IdUsuario", "Nombre", "Empresa", "Estado"]
    assert df.iloc[0]["IdUsuario"] == "u1"
    assert df.iloc[0]["Nombre"] == "Ana"


def test_cargar_csv_tolera_linea_defectuosa_en_engine_c(tmp_path):
    csv_file = tmp_path / "contactos_20260507.csv"
    csv_file.write_text(
        "IdUsuario;Nombre;Empresa;Estado\n"
        "u1;Ana;Hospital Central;Completa\n"
        "linea;defectuosa\n"
        "u2;Luis;Hospital Central;Pendiente\n",
        encoding="utf-8",
    )

    df = cargar_csv(str(csv_file), ";")

    assert len(df) >= 2
    assert set(df["IdUsuario"].tolist()) >= {"u1", "u2"}


def test_cargar_csv_soporta_utf8_sig(tmp_path):
    csv_file = tmp_path / "contactos_20260507.csv"
    csv_file.write_text(
        "IdUsuario;Nombre;Empresa;Estado\n"
        "u1;Ána;Hospital Central;Completa\n",
        encoding="utf-8-sig",
    )

    df = cargar_csv(str(csv_file), ";")

    assert len(df) == 1
    assert df.iloc[0]["Nombre"] == "Ána"


def test_cargar_csv_soporta_latin1(tmp_path):
    csv_file = tmp_path / "contactos_20260507.csv"
    csv_file.write_text(
        "IdUsuario;Nombre;Empresa;Estado\n"
        "u1;Peña;Hospital Central;Completa\n",
        encoding="latin-1",
    )

    df = cargar_csv(str(csv_file), ";")

    assert len(df) == 1
    assert df.iloc[0]["Nombre"] == "Peña"
