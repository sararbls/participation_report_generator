# AGENTS.md

Guía para agentes que trabajen en este repositorio.

## 1) Objetivo del proyecto
- Generar un informe Excel de participación a partir de uno o varios CSV.
- Punto de entrada: `main.py`.
- Salida: archivo Excel (`SALIDA`, por defecto `informe.xlsx`) con una hoja `Informe`.

## 2) Stack y dependencias
- Python `>=3.14` (según `pyproject.toml`).
- Dependencias:
  - `pandas`
  - `openpyxl`
  - `python-dotenv`
- Gestión de entorno recomendada: `uv` (existe `uv.lock`).

## 3) Ejecución local
1. Crear/editar `.env` en la raíz del proyecto.
2. Ejecutar:

```powershell
uv run python main.py
```

Alternativa si no se usa `uv`:

```powershell
python main.py
```

## 4) Contrato de configuración (.env)
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

Ejemplo mínimo:

```dotenv
EMPRESA=MiEmpresa
SALIDA=informe.xlsx
SEPARADOR=;
PUBLICO_1=Clientes
CSV_1=data/clientes_20260507120000.csv
```

## 5) Comportamiento funcional clave
- Extrae la fecha desde el nombre del CSV (patrón `YYYYMMDD` o `YYYYMMDDHHMMSS`) y la formatea como `dd/mm`.
- Lee CSV con varias estrategias de parseo para tolerar comillas/separadores problemáticos.
- Requiere columnas: `IdUsuario`, `Nombre`, `Empresa`, `Estado`.
- Filtrado de datos:
  - Solo filas de `EMPRESA`.
  - Excluye `Estado == "Anulado"`.
  - Si `Nombre == "Lote"`, usa `IdUsuario` como nombre mostrado.
- Construye una sección de 3 columnas por público: `Nombre`, `Estado`, `% Participación`.
- `% Participación` se calcula con fórmula Excel (`COUNTIF/COUNTA`) por estado.

## 6) Convenciones para cambios
- Mantener los mensajes de error/aviso en español (el código actual está en español).
- Preservar el contrato de `.env` salvo que el cambio lo justifique explícitamente.
- Si se modifica el parseo de CSV, conservar compatibilidad con entradas "sucias" (comillas, separador variable, líneas defectuosas).
- Evitar introducir dependencias nuevas sin necesidad clara.
- Mantener el script ejecutable con `uv run python main.py`.

## 7) Validación antes de cerrar tareas
Checklist mínimo:
1. Ejecutar script con un `.env` realista.
2. Confirmar que se genera el archivo de salida sin excepciones.
3. Abrir el Excel y verificar:
   - Título con fecha y empresa.
   - Cabeceras y estilos básicos.
   - Fórmulas de `% Participación` presentes y con formato `%`.
4. Probar al menos un caso con filas `Anulado` y uno con `Nombre=Lote`.

## 8) Riesgos conocidos
- `requires-python = ">=3.14"` puede no estar disponible en todos los entornos; verificar versión instalada.
- El script depende de que el nombre del CSV contenga fecha válida.
- Si cambian nombres de columnas en origen, fallará por contrato de columnas requeridas.

## 9) Mejoras sugeridas (no implementadas)
- Añadir tests automatizados para:
  - extracción de fecha,
  - parseo de CSV,
  - filtrado por empresa/estado,
  - estructura del workbook.
- Separar lógica en módulos (`config`, `io_csv`, `excel_builder`) para facilitar mantenimiento.
- Añadir ejemplo `.env.example` y poblar `README.md`.
