import os
import subprocess
import sys


def build():
    """
    Script para construir el ejecutable (.exe) del generador de reportes.
    Utiliza PyInstaller para empaquetar la aplicación.
    """

    # Definición de rutas
    icon_path = os.path.join("src", "participation_report", "assets", "icon.ico")
    assets_src = os.path.join("src", "participation_report", "assets")
    assets_dest = os.path.join("participation_report", "assets")

    # Construcción del comando
    # Usamos sys.executable para obtener el path del python actual y ejecutar pyinstaller como módulo o buscar su exe
    pyinstaller_exe = os.path.join(os.path.dirname(sys.executable), "pyinstaller.exe")
    if not os.path.exists(pyinstaller_exe):
        pyinstaller_exe = "pyinstaller"  # Fallback

    command = [
        pyinstaller_exe,
        "--noconfirm",
        "--onefile",
        "--windowed",
        f"--icon={icon_path}",
        f"--add-data={assets_src}{os.pathsep}{assets_dest}",
        "--name=GeneradorReporteParticipacion",
        "main.py",
    ]

    print("Iniciando la construcción del ejecutable...")
    print(f"Comando: {' '.join(command)}\n")

    try:
        # Ejecutamos PyInstaller
        # Usamos shell=True en Windows para asegurar que encuentre el ejecutable en el PATH del venv
        subprocess.run(command, check=True, shell=sys.platform == "win32")

        print("\n" + "=" * 50)
        print("[OK] ¡Proceso completado con éxito!")
        print(
            f"El ejecutable se encuentra en: {os.path.abspath('dist/GeneradorReporteParticipacion.exe')}"
        )
        print("=" * 50)

    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Error durante la construcción: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Ocurrió un error inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    build()
