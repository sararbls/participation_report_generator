import argparse

from participation_report.config import load_config
from participation_report.services import generate_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Genera informe Excel de participación desde CSV")
    parser.add_argument("--env-file", default=None, help="Ruta a archivo .env (opcional)")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = load_config(args.env_file)
    generate_report(config)


if __name__ == "__main__":
    main()
