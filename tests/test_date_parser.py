import pytest

from participation_report.csv_reader import fecha_desde_nombre


def test_fecha_desde_nombre_con_timestamp_14_digitos():
    assert fecha_desde_nombre("data/clientes_20260507101650.csv") == "07/05"


def test_fecha_desde_nombre_con_solo_8_digitos():
    assert fecha_desde_nombre("datos_20260131.csv") == "31/01"


def test_fecha_desde_nombre_falla_si_no_hay_fecha():
    with pytest.raises(SystemExit, match="No se pudo extraer la fecha"):
        fecha_desde_nombre("clientes_sin_fecha.csv")
