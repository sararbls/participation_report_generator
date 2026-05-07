# ROADMAP

## Objetivo
Evolucionar el proyecto hacia una herramienta mantenible, robusta y operable, manteniendo simplicidad de uso (`.env` + CLI).

## Estado actual (2026-05-07)
- Fase 1 (base tecnica): completada.
- Fase 2 (testing): completada.
- Fase 3 (calidad y DX): completada.
- Fase 4 (robustez funcional): en progreso.
- Fase 5 (distribucion/CI): completada (incluye fix de dependencias de sistema y lint).

Validacion actual:
- `uv run ruff check .` -> OK
- `uv run mypy` -> OK
- `uv run pytest -q` -> `19 passed`

## Arquitectura objetivo
```text
participation_report/
  __init__.py
  cli.py
  config.py
  csv_reader.py
  domain.py
  excel_builder.py
  services.py
tests/
  test_config.py
  test_date_parser.py
  test_csv_reader.py
  test_filters.py
  test_excel_builder.py
  test_services_output.py
  test_integration_generate_report.py
main.py
```

Responsabilidades:
- `config.py`: carga y validacion de `.env`.
- `csv_reader.py`: parseo robusto de CSV y normalizacion.
- `domain.py`: reglas de negocio.
- `excel_builder.py`: construccion y estilos del workbook.
- `services.py`: orquestacion de flujo.
- `cli.py`: interfaz de ejecucion.

## Fases

### Fase 1 - Base tecnica (completada)
- Modularizacion desde `main.py` a paquete `participation_report/`.
- `main.py` mantenido como wrapper compatible.
- Salida por defecto en `processed_data/` con timestamp.
- Ejecucion real validada con `.env` y CSV.

### Fase 2 - Testing automatizado (completada)
- Suite `pytest` creada y estable.
- Cobertura funcional: config, fecha, CSV, filtros, builder, salida, integracion.
- Estado: `19 passed`.

### Fase 3 - Calidad y DX (completada en baseline)
- `ruff` integrado (lint + format).
- `mypy` integrado y endurecido globalmente (`disallow_untyped_defs = true`).
- Comandos documentados en `README.md`.

### Fase 4 - Robustez funcional (en progreso)
Completado:
- Separadores alternativos.
- Limpieza de comillas simples/dobles.
- Tolerancia a lineas defectuosas.
- Fallback de codificacion (`utf-8`, `utf-8-sig`, `latin-1`).
- Error accionable para columnas requeridas faltantes.

Pendiente sugerido:
1. Añadir fixtures mas realistas de fuentes CSV de produccion.
2. Evaluar reglas para duplicados de usuario (segun negocio).
3. Considerar orden/sanitizacion adicional de estados antes de exportar.

### Fase 5 - Distribucion/CI (completada)
Completado:
- CI en `.github/workflows/ci.yml` con `ruff`, `mypy`, `pytest`.
- Fix de dependencias de sistema (`libcairo2-dev`) para `pycairo`.
- Fix de errores de longitud de línea (E501) en scripts y código fuente.
- Politica de ramas/PR documentada en `BRANCH_POLICY.md`.

Pendiente sugerido:
1. Activar badge CI real en README (reemplazar `OWNER/REPO`).
2. Configurar proteccion de rama `main` en GitHub.
3. Evaluar `project.scripts` para comando instalable (`participation-report`).

## Backlog priorizado
1. Cerrar Fase 4 con fixtures reales y decisiones de negocio pendientes.
2. Formalizar publicacion/uso CLI instalable.
3. Añadir versionado semantico + changelog.

## Riesgos y mitigaciones
- Riesgo: regresiones al endurecer robustez de parseo.
  - Mitigacion: ampliar tests con casos reales y mantener CI obligatoria.
- Riesgo: aumento de complejidad para un proyecto pequeno.
  - Mitigacion: cambios incrementales con criterios claros de valor.
