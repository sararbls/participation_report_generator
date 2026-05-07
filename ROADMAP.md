# ROADMAP

## Objetivo
Transformar el generador de reportes en una aplicación profesional, robusta y distribuible, con interfaces tanto de línea de comandos (CLI) como gráfica (GUI).

## Estado actual (Mayo 2026)
- **Core:** Arquitectura modular completada y estable.
- **Calidad:** CI/CD configurado con Ruff, Mypy y Pytest (19 tests pasando).
- **Interfaces:** CLI y GUI funcionales.
- **Distribución:** Scripts de construcción de ejecutable (.exe) listos.

## Arquitectura Finalizada
El proyecto sigue el patrón de servicios y dominio, separado en:
- `participation_report/`: Lógica de negocio, configuración, lectores de CSV y constructores Excel.
- `gui.py`: Interfaz gráfica basada en PyQt6.
- `cli.py`: Interfaz de comandos.
- `tests/`: Suite completa de validación.

---

## Fases y Logros

### ✅ Fase 1: Estabilización y Modularización
- Refactorización de `main.py` a una estructura de paquete profesional.
- Implementación de `AppConfig` para validación estricta de variables de entorno.
- Creación de `CSVReader` con soporte multienconding y robustez ante errores.

### ✅ Fase 2: Calidad y Testing
- Cobertura de tests unitarios e integración (19 tests).
- Integración de `Ruff` para linting y `Mypy` para tipado estático (modo estricto).
- Pipeline de CI en GitHub Actions con correcciones para dependencias de sistema.

### ✅ Fase 3: Interfaz Gráfica (GUI)
- Desarrollo de GUI con PyQt6 para facilitar el uso a usuarios no técnicos.
- Soporte para selección de archivos, configuración visual y logs integrados.
- Assets (iconos) gestionados mediante SVG y generación automática de `.ico`.

### 🚀 Fase 4: Robustez y Distribución (En progreso)
- [x] Script de construcción de ejecutable `.exe` con `PyInstaller`.
- [ ] Implementar sistema de logs a archivo para depuración en producción.
- [ ] Añadir validación de duplicados de IdUsuario.
- [ ] Refinar la estética de la GUI (temas, espaciado, feedback visual).

---

## Backlog de Futuras Mejoras

### 🛠 Funcionalidad
1. **Manejo de Duplicados:** Decidir lógica de negocio para múltiples entradas del mismo usuario.
2. **Histórico de Procesamiento:** Guardar un registro de reportes generados.
3. **Internacionalización (i18n):** Preparar la app para múltiples idiomas (actualmente solo español).

### 📦 Distribución y Ops
1. **GitHub Releases:** Automatizar la creación de releases con el `.exe` adjunto cuando se cree un tag.
2. **Installer (MSI/InnoSetup):** Crear un instalador para Windows en lugar de un único `.exe`.
3. **Auto-update:** Notificar al usuario cuando haya una nueva versión disponible.

### 📊 Reportes
1. **Gráficos en Excel:** Insertar gráficos nativos de Excel directamente desde el generador.
2. **Múltiples Formatos:** Soporte para exportar a PDF además de XLSX.

---

## Riesgos y Mitigaciones
- **Versión de Python:** El uso de Python 3.14+ puede limitar la compatibilidad en máquinas antiguas. *Mitigación: Documentar requisitos y proveer el .exe autocontenido.*
- **Cambios en origen de datos:** Si la fuente de los CSV cambia el nombre de las columnas. *Mitigación: Implementar un mapeo de columnas configurable.*
