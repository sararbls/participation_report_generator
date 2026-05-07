# AGENTS.md

Gu�a para agentes que trabajen en este repositorio.

## 1) Objetivo del proyecto
- Generar un informe Excel de participaci�n a partir de uno o varios CSV.
- Punto de entrada: `main.py`.
- Salida: archivo Excel (`SALIDA`, por defecto `informe.xlsx`) con una hoja `Informe`.

## 2) Stack y dependencias
- Python `>=3.14` (seg�n `pyproject.toml`).
- Dependencias:
  - `pandas`
  - `openpyxl`
  - `python-dotenv`
- Gesti�n de entorno recomendada: `uv` (existe `uv.lock`).

## 3) Ejecuci�n local
1. Crear/editar `.env` en la ra�z del proyecto.
2. Ejecutar:

```powershell
uv run python main.py
```

Alternativa si no se usa `uv`:

```powershell
python main.py
```

## 4) Contrato de configuraci�n (.env)
Variables esperadas:
- `EMPRESA` (obligatoria)
- `SALIDA` (opcional, default `informe.xlsx`)
- `SEPARADOR` (opcional, default `;`)
- Pares indexados obligatorios en conjunto:
  - `PUBLICO_1`, `CSV_1`
  - `PUBLICO_2`, `CSV_2`
  - ...

Reglas:
- Cada `PUBLICO_i` debe tener su `CSV_i` y viceversa.
- Debe existir al menos el par `PUBLICO_1` + `CSV_1`.

Ejemplo m�nimo:

```dotenv
EMPRESA=MiEmpresa
SALIDA=informe.xlsx
SEPARADOR=;
PUBLICO_1=Clientes
CSV_1=data/clientes_20260507120000.csv
```

## 5) Comportamiento funcional clave
- Extrae la fecha desde el nombre del CSV (patr�n `YYYYMMDD` o `YYYYMMDDHHMMSS`) y la formatea como `dd/mm`.
- Lee CSV con varias estrategias de parseo para tolerar comillas/separadores problem�ticos.
- Requiere columnas: `IdUsuario`, `Nombre`, `Empresa`, `Estado`.
- Filtrado de datos:
  - Solo filas de `EMPRESA`.
  - Excluye `Estado == "Anulado"`.
  - Si `Nombre == "Lote"`, usa `IdUsuario` como nombre mostrado.
- Construye una secci�n de 3 columnas por p�blico: `Nombre`, `Estado`, `% Participaci�n`.
- `% Participaci�n` se calcula con f�rmula Excel (`COUNTIF/COUNTA`) por estado.

## 6) Convenciones para cambios
- Mantener los mensajes de error/aviso en espaol.
- Preservar el contrato de `.env`.
- **Calidad Mandataria:** ANTES de cualquier `git add`, `git commit` o `git push`, el agente DEBE ejecutar localmente y asegurar que pasen:
  - `uv run ruff check .`
  - `uv run mypy`
  - `uv run pytest`
- Si el CI falla, el agente es responsable de corregir el error (ej. dependencias de sistema faltantes en `.github/workflows/ci.yml`).

## 7) Validacin antes de cerrar tareas
Checklist mnimo:
1. Ejecutar script con un `.env` realista.
2. Confirmar que se genera el archivo de salida sin excepciones.
3. Abrir el Excel (si es posible) y verificar frmulas y datos.
4. **Verificar que los tests pasen (`pytest`).**
5. **Verificar que el linter y tipado pasen (`ruff` y `mypy`).**

## 8) Riesgos conocidos
- `requires-python = ">=3.14"`: Entorno de ejecucin y CI deben soportar Python 3.14+.
- Dependencias de sistema: Algunas libreras como `pycairo` requieren dependencias de SO (`libcairo2-dev` en Ubuntu/CI).


## 9) Mejoras sugeridas (no implementadas)
- A�adir tests automatizados para:
  - extracci�n de fecha,
  - parseo de CSV,
  - filtrado por empresa/estado,
  - estructura del workbook.
- Separar l�gica en m�dulos (`config`, `io_csv`, `excel_builder`) para facilitar mantenimiento.
- A�adir ejemplo `.env.example` y poblar `README.md`.
