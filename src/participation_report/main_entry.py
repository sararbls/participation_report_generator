import argparse
import sys

from participation_report.cli import main as cli_main
from participation_report.gui import main as gui_main


def main() -> None:
    # Creamos un parser básico para detectar si el usuario quiere forzar GUI o CLI
    # o si simplemente pasó argumentos que pertenecen al CLI.
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "--gui", action="store_true", help="Forzar el inicio de la interfaz gráfica"
    )
    parser.add_argument(
        "--cli", action="store_true", help="Forzar el inicio de la interfaz de comandos"
    )

    # parse_known_args permite capturar nuestros flags sin fallar por los del CLI
    args, unknown = parser.parse_known_args()

    if args.gui:
        gui_main()
    elif args.cli:
        cli_main()
    elif len(sys.argv) > 1:
        # Si hay cualquier argumento, asumimos que se quiere usar el CLI
        cli_main()
    else:
        # Por defecto, si no hay argumentos, lanzamos la GUI
        gui_main()


if __name__ == "__main__":
    main()
