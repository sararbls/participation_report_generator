import os
from pathlib import Path

from PIL import Image
from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg


def generate_pro_ico(svg_path, output_path):
    if not os.path.exists(svg_path):
        print(f"Error: No se encuentra {svg_path}")
        return

    print(f"Leyendo SVG: {svg_path}...")
    drawing = svg2rlg(svg_path)

    # Tamaños estándar de Windows
    sizes = [16, 32, 48, 64, 128, 256]
    layers = []

    print("Generando capas de alta resolución...")
    for size in sizes:
        # Renderizamos el SVG a un tamaño grande primero para mantener calidad
        # O escalamos directamente en el renderizado
        scaling_factor = size / drawing.width

        # Guardamos temporalmente como PNG de alta calidad
        temp_png = f"temp_{size}.png"
        renderPM.drawToFile(drawing, temp_png, fmt="PNG", configScale=scaling_factor)

        # Abrimos con PIL para asegurar formato y transparencia
        img = Image.open(temp_png).convert("RGBA")
        layers.append(img)

        # Limpieza temporal
        os.remove(temp_png)
        print(f" - Capa {size}x{size} lista.")

    # Guardar como ICO
    # El archivo DEBERÍA pesar entre 50KB y 400KB si tiene todas las capas
    layers[0].save(
        output_path, format="ICO", sizes=[(s, s) for s in sizes], append_images=layers[1:]
    )

    file_size = os.path.getsize(output_path)
    print(f"\n[OK] Icono generado: {output_path}")
    print(f"Tamaño final: {file_size / 1024:.2f} KB")

    if file_size < 10000:
        print("ADVERTENCIA: El archivo sigue siendo sospechosamente pequeño.")
    else:
        print("El tamaño del archivo parece correcto para un icono multi-resolución.")


if __name__ == "__main__":
    assets_dir = Path("src/participation_report/assets")
    svg_input = assets_dir / "icon.svg"
    ico_output = assets_dir / "icon.ico"
    generate_pro_ico(svg_input, ico_output)
