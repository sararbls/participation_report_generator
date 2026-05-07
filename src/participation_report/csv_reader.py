import re
import sys
from pathlib import Path
from typing import Any

import pandas as pd


def fecha_desde_nombre(csv_path: str) -> str:
    stem = Path(csv_path).stem
    m = re.search(r"(\d{8})\d{6}", stem)
    if not m:
        m = re.search(r"(\d{8})", stem)
    if not m:
        sys.exit(
            f"[ERROR] No se pudo extraer la fecha del nombre '{csv_path}'.\n"
            "        El nombre debe contener la fecha en formato YYYYMMDD (p.ej. 20260507)."
        )
    raw = m.group(1)
    return f"{raw[6:8]}/{raw[4:6]}"


def cargar_csv(path: str, separador: str) -> pd.DataFrame:
    if not Path(path).exists():
        sys.exit(f"[ERROR] Archivo no encontrado: '{path}'")

    required = {"IdUsuario", "Nombre", "Empresa", "Estado"}
    estrategias: list[dict[str, Any]] = [
        dict(sep=separador, quotechar='"', engine="python", dtype=str),
        dict(sep=separador, quotechar="'", engine="python", dtype=str),
        dict(sep=separador, quoting=3, engine="python", dtype=str),
        dict(sep=separador, engine="python", dtype=str),
        dict(sep=separador, quotechar='"', engine="c", dtype=str, on_bad_lines="skip"),
        dict(sep=separador, quoting=3, engine="c", dtype=str, on_bad_lines="skip"),
    ]
    encodings = ["utf-8", "utf-8-sig", "latin-1"]

    last_error = None
    missing_required: set[str] | None = None
    seen_columns: list[str] | None = None
    for encoding in encodings:
        for kwargs in estrategias:
            try:
                df = pd.read_csv(path, encoding=encoding, **kwargs).fillna("")
                df.columns = [c.strip().strip('"').strip("'") for c in df.columns]
                text_cols = df.select_dtypes(include=["string", "object"]).columns
                for col in text_cols:
                    df[col] = df[col].astype(str).str.strip().str.strip('"').str.strip("'")
                if required.issubset(set(df.columns)):
                    return df
                missing_required = required - set(df.columns)
                seen_columns = list(df.columns)
            except Exception as e:
                last_error = e
                continue

    try:
        with open(path, "rb") as f:
            head = f.read(512)
        print(f"[DIAGNOSTICO] Primeros bytes:\n{head[:200]!r}")
    except Exception:
        pass

    if missing_required:
        faltan = ", ".join(sorted(missing_required))
        presentes = ", ".join(seen_columns or [])
        sys.exit(
            f"[ERROR] El CSV '{path}' no contiene todas las columnas requeridas.\n"
            f"        Faltan: {faltan}\n"
            f"        Encontradas: {presentes}"
        )

    sys.exit(
        f"[ERROR] No se pudo leer '{path}' con ninguna estrategia de parseo.\n"
        f"        Ultimo error: {last_error}\n"
        f"        Comprueba que SEPARADOR='{separador}' es correcto y la codificacion "
        f"sea compatible (utf-8/utf-8-sig/latin-1)."
    )
