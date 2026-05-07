# Branch and PR Policy

## Ramas
- Rama principal: `main`.
- Desarrollo en ramas cortas por cambio: `feature/*`, `fix/*`, `chore/*`.

## Pull Requests
- Abrir PR hacia `main`.
- Titulo claro y descriptivo.
- Incluir contexto, cambio aplicado y validacion local.

## Checks requeridos (antes de merge)
- CI en verde (`ruff`, `mypy`, `pytest`).
- Sin cambios pendientes de resolver en revisión.

## Reglas de proteccion recomendadas para `main`
- Requerir PR para merge (sin push directo).
- Requerir checks de estado en verde.
- Requerir rama actualizada antes de merge.
- Requerir al menos 1 aprobación.
