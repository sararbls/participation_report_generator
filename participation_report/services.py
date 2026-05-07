import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

from participation_report.config import AppConfig
from participation_report.csv_reader import cargar_csv, fecha_desde_nombre
from participation_report.domain import procesar_publico
from participation_report.excel_builder import build_excel


def _resolve_output_path(salida_config: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    processed_dir = Path("processed_data")
    processed_dir.mkdir(parents=True, exist_ok=True)

    salida = (salida_config or "").strip()
    if not salida or salida == "informe.xlsx":
        return str(processed_dir / f"informe_{timestamp}.xlsx")

    path = Path(salida)
    if path.is_absolute():
        path.parent.mkdir(parents=True, exist_ok=True)
        return str(path)

    if path.parent == Path("."):
        suffix = path.suffix or ".xlsx"
        return str(processed_dir / f"{path.stem}_{timestamp}{suffix}")

    path.parent.mkdir(parents=True, exist_ok=True)
    return str(path)


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

    salida_final = _resolve_output_path(config.salida)
    build_excel(config.empresa, fecha, publicos, dataframes, salida_final)
    print(f"[OK] Informe guardado en: {salida_final}")
