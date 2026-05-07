# AGENTS.md

Guía para agentes que trabajen en este repositorio.

## 1) Objetivo del proyecto
- Generar un informe Excel de participación a partir de uno o varios CSV.
- Punto de entrada CLI: `main.py`.
- Punto de entrada GUI: `src/participation_report/gui.py`.
- Salida: archivo Excel en `processed_data/` con timestamp.

## 2) Stack y dependencias
- Python `>=3.14` (según `pyproject.toml`).
- Dependencias clave:
  - `pandas`: Procesamiento de datos.
  - `openpyxl`: Generación de Excel.
  - `PyQt6`: Interfaz Gráfica (GUI).
  - `svglib`: Manejo de activos SVG.
  - `python-dotenv`: Gestión de configuración.
- Gestión de entorno: `uv`.

## 3) Ejecución local
- **CLI:** `uv run python main.py`
- **GUI:** `uv run python -m participation_report.gui`
- **Tests:** `uv run pytest`
- **Linter:** `uv run ruff check .`
- **Build EXE:** `uv run python scripts/build_exe.py`

## 4) Contrato de configuración (.env)
Variables esperadas:
- `EMPRESA` (obligatoria)
- `SALIDA` (opcional)
- `SEPARADOR` (opcional, default `;`)
- Pares indexados: `PUBLICO_i`, `CSV_i`.

## 5) Comportamiento funcional clave
- **Arquitectura:** Modularizada en `src/participation_report/` (`config`, `csv_reader`, `domain`, `excel_builder`, `services`).
- **Fecha:** Extraída del nombre del archivo CSV (patrón `YYYYMMDD`).
- **Filtrado:** Por empresa, excluyendo "Anulado" y normalizando nombres "Lote".
- **Excel:** Genera tablas con fórmulas de participación automatizadas.

## 6) Convenciones para cambios
- Mantener mensajes en español.
- **Calidad Mandataria:** ANTES de cualquier commit/push, DEBEN pasar:
  - `uv run ruff check .`
  - `uv run mypy`
  - `uv run pytest`
- Si el CI falla, el agente debe corregir el entorno o el código.

## 7) Validación antes de cerrar tareas
1. Verificar ejecución exitosa (CLI o GUI).
2. Comprobar que el Excel en `processed_data/` tiene los datos correctos.
3. Asegurar que los tests (`pytest`) pasan al 100%.
4. Asegurar que no hay errores de linting o tipado.

## 8) Riesgos conocidos
- **Python 3.14+:** Requiere entorno actualizado.
- **Dependencias de Sistema:** `pycairo` requiere `libcairo2-dev` en sistemas Linux/CI.
- **Formato CSV:** Sensible a cambios en nombres de columnas de origen.

## 9) Próximos pasos (Backlog)
- Añadir fixtures reales para casos de borde en CSV.
- Evaluar lógica de duplicados de IdUsuario.
- Mejorar estilos visuales de la GUI.
