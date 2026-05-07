# participation-report

> CI badge (reemplaza `OWNER/REPO` por tu repo):
> `![CI](https://github.com/OWNER/REPO/actions/workflows/ci.yml/badge.svg)`

Genera un informe Excel de participacion a partir de uno o varios CSV.

## Requisitos
- Python >= 3.14
- `uv` recomendado (hay `uv.lock`)

Dependencias usadas:
- pandas
- openpyxl
- python-dotenv

## Configuracion
1. Copia `.env.example` a `.env`.
2. Ajusta:
- `EMPRESA` (obligatoria)
- `SALIDA` (opcional, si no se define o es `informe.xlsx`, se genera en `processed_data/` con timestamp)
- `SEPARADOR` (opcional, default `;`)
- pares `PUBLICO_i` + `CSV_i` (al menos `PUBLICO_1` + `CSV_1`)

Columnas requeridas en cada CSV:
- `IdUsuario`
- `Nombre`
- `Empresa`
- `Estado`

## Ejecucion
Compatibilidad (actual):
```powershell
uv run python main.py
```

Forma modular (equivalente):
```powershell
uv run python -m participation_report.cli
```

Alternativa sin `uv`:
```powershell
python main.py
```

## Calidad
Lint:
```powershell
uv run ruff check .
```

Formato:
```powershell
uv run ruff format .
```

Tipado:
```powershell
uv run mypy
```

Tests:
```powershell
uv run pytest -q
```

## CI
- Pipeline en GitHub Actions: `.github/workflows/ci.yml`
- Ejecuta en `push` y `pull_request`:
  - `ruff check`
  - `mypy`
  - `pytest`

## Documentacion
- Roadmap y estado de avance: [ROADMAP.md](./ROADMAP.md)
- Politica de ramas/PR: [BRANCH_POLICY.md](./BRANCH_POLICY.md)
- Guia para agentes: [AGENTS.md](./AGENTS.md)

## Resultado
Se genera un Excel en `processed_data/` con nombre timestamped por defecto con una hoja `Informe` y una seccion por publico con:
- `Nombre`
- `Estado`
- `% Participacion`
