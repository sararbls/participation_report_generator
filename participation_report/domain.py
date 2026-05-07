import unicodedata

import pandas as pd


def procesar_publico(df: pd.DataFrame, empresa: str) -> pd.DataFrame:
    def normalizar_texto(valor: str) -> str:
        base = unicodedata.normalize("NFD", valor.strip())
        sin_tildes = "".join(ch for ch in base if unicodedata.category(ch) != "Mn")
        return sin_tildes.casefold()

    def es_lote(valor: str) -> bool:
        return valor.strip().casefold() == "lote"

    empresa_objetivo = normalizar_texto(empresa)
    empresa_col = df["Empresa"].astype(str).map(normalizar_texto)
    filtrado = df[empresa_col == empresa_objetivo]
    filtrado = filtrado[filtrado["Estado"].str.strip() != "Anulado"]

    nombres = filtrado["Nombre"].astype(str).map(str.strip)
    hay_nombres_normales = any((not es_lote(nombre)) and nombre != "" for nombre in nombres)

    rows = []
    for _, r in filtrado.iterrows():
        nombre_original = str(r["Nombre"]).strip()
        if es_lote(nombre_original):
            if hay_nombres_normales:
                continue
            nombre = r["IdUsuario"]
        else:
            nombre = nombre_original
        rows.append({"Nombre": nombre, "Estado": r["Estado"]})

    return pd.DataFrame(rows)
