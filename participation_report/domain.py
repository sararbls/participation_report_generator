import pandas as pd


def procesar_publico(df: pd.DataFrame, empresa: str) -> pd.DataFrame:
    filtrado = df[df["Empresa"].str.strip() == empresa.strip()]
    filtrado = filtrado[filtrado["Estado"].str.strip() != "Anulado"]

    rows = []
    for _, r in filtrado.iterrows():
        nombre = r["IdUsuario"] if r["Nombre"].strip() == "Lote" else r["Nombre"]
        rows.append({"Nombre": nombre, "Estado": r["Estado"]})

    return pd.DataFrame(rows)
