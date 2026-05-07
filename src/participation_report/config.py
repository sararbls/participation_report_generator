import os
import sys
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class AppConfig:
    empresa: str
    separador: str
    publicos_y_csvs: list[tuple[str, str]]


def load_config(env_file: str | None = None) -> AppConfig:
    if env_file:
        load_dotenv(env_file)
    else:
        load_dotenv()

    empresa = os.getenv("EMPRESA", "").strip()
    separador = os.getenv("SEPARADOR", ";").strip()

    publicos_y_csvs: list[tuple[str, str]] = []
    i = 1
    while True:
        publico = os.getenv(f"PUBLICO_{i}", "").strip()
        csv = os.getenv(f"CSV_{i}", "").strip()
        if not publico and not csv:
            break
        if not publico or not csv:
            sys.exit(f"[ERROR] .env: PUBLICO_{i} y CSV_{i} deben definirse juntos.")
        publicos_y_csvs.append((publico, csv))
        i += 1

    if not empresa:
        sys.exit("[ERROR] .env: EMPRESA es obligatorio.")
    if not publicos_y_csvs:
        sys.exit("[ERROR] .env: define al menos PUBLICO_1 y CSV_1.")

    return AppConfig(
        empresa=empresa,
        separador=separador,
        publicos_y_csvs=publicos_y_csvs,
    )
