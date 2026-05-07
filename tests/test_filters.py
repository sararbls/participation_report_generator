import pandas as pd

from participation_report.domain import procesar_publico


def test_procesar_publico_filtra_empresa_excluye_anulado_y_aplica_lote():
    df = pd.DataFrame(
        [
            {
                "IdUsuario": "u1",
                "Nombre": "Ana",
                "Empresa": "Hospital Central",
                "Estado": "Completa",
            },
            {
                "IdUsuario": "u2",
                "Nombre": "Lote",
                "Empresa": "Hospital Central",
                "Estado": "Pendiente",
            },
            {
                "IdUsuario": "u3",
                "Nombre": "Luis",
                "Empresa": "Hospital Central",
                "Estado": "Anulado",
            },
            {"IdUsuario": "u4", "Nombre": "Eva", "Empresa": "Otra", "Estado": "Completa"},
        ]
    )

    result = procesar_publico(df, "Hospital Central")

    assert len(result) == 1
    assert result.to_dict("records") == [
        {"Nombre": "Ana", "Estado": "Completa"},
    ]


def test_procesar_publico_compara_empresa_sin_tildes():
    df = pd.DataFrame(
        [
            {
                "IdUsuario": "u1",
                "Nombre": "Ana",
                "Empresa": "Clínica Águila",
                "Estado": "Completa",
            },
            {
                "IdUsuario": "u2",
                "Nombre": "Luis",
                "Empresa": "Clinica Aguila",
                "Estado": "Pendiente",
            },
        ]
    )

    result = procesar_publico(df, "Clinica Aguila")

    assert result.to_dict("records") == [
        {"Nombre": "Ana", "Estado": "Completa"},
        {"Nombre": "Luis", "Estado": "Pendiente"},
    ]


def test_procesar_publico_usa_id_solo_si_no_hay_nombres_normales():
    df = pd.DataFrame(
        [
            {
                "IdUsuario": "u1",
                "Nombre": "Lote",
                "Empresa": "Hospital Central",
                "Estado": "Completa",
            },
            {
                "IdUsuario": "u2",
                "Nombre": "Lote",
                "Empresa": "Hospital Central",
                "Estado": "Pendiente",
            },
        ]
    )

    result = procesar_publico(df, "Hospital Central")

    assert result.to_dict("records") == [
        {"Nombre": "u1", "Estado": "Completa"},
        {"Nombre": "u2", "Estado": "Pendiente"},
    ]
