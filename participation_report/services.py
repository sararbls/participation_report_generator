import sys
from datetime import datetime
from pathlib import Path
import re
import unicodedata

import pandas as pd

from participation_report.config import AppConfig
from participation_report.csv_reader import cargar_csv, fecha_desde_nombre
from participation_report.domain import procesar_publico
from participation_report.excel_builder import build_excel


def _slug_empresa(empresa: str) -> str:
    base = unicodedata.normalize("NFD", empresa.strip())
    sin_tildes = "".join(ch for ch in base if unicodedata.category(ch) != "Mn")
    limpio = re.sub(r"[^A-Za-z0-9_-]+", "_", sin_tildes).strip("_")
    return limpio or "empresa"


def _resolve_output_path(empresa: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    processed_dir = Path("processed_data")
    processed_dir.mkdir(parents=True, exist_ok=True)

    default_name = f"reporte_participacion_{_slug_empresa(empresa)}_{timestamp}.xlsx"
    return str(processed_dir / default_name)


def generate_report(config: AppConfig) -> None:
    if not config.publicos_y_csvs:
        sys.exit("[ERROR] PUBLICOS_Y_CSVS esta vacio. Edita la configuracion.")
    if not config.empresa.strip():
        sys.exit("[ERROR] EMPRESA esta vacio. Edita la configuracion.")

    publicos: list[str] = []
    dataframes: list[pd.DataFrame] = []
    fecha: str | None = None

    for pub_nombre, csv_path in config.publicos_y_csvs:
        raw = cargar_csv(csv_path, config.separador)

        if fecha is None:
            fecha = fecha_desde_nombre(csv_path)

        df = procesar_publico(raw, config.empresa)
        if df.empty:
            aviso = (
                f"[AVISO] '{pub_nombre}': ningun contacto encontrado para "
                f"'{config.empresa}'. Se omite."
            )
            print(aviso)
            continue

        publicos.append(pub_nombre)
        dataframes.append(df)

    if not publicos:
        sys.exit(f"[ERROR] No se encontraron contactos para '{config.empresa}' en ningun CSV.")
    if fecha is None:
        sys.exit("[ERROR] No se pudo determinar la fecha desde los CSV configurados.")

    print(f"[INFO] Empresa : {config.empresa}")
    print(f"[INFO] Fecha   : {fecha}")
    print(f"[INFO] Publicos: {', '.join(publicos)}")

    salida_final = _resolve_output_path(config.empresa)
    build_excel(config.empresa, fecha, publicos, dataframes, salida_final)
    print(f"[OK] Informe guardado en: {salida_final}")
