# Participation Report Generator

Genera un informe Excel de participación a partir de uno o varios archivos CSV de contactos, permitiendo filtrar y agrupar por diferentes públicos.

## 🚀 Requisitos
- Python >= 3.14
- [uv](https://github.com/astral-sh/uv) (recomendado para gestión de dependencias)

## 📁 Estructura del Proyecto
- `src/`: Carpeta raíz del código fuente (Patrón Industria).
  - `participation_report/`: Paquete principal con la lógica de negocio y GUI.
- `main.py`: Lanzador unificado en la raíz.
- `scripts/`: Herramientas de mantenimiento y automatización.
- `data/`: Directorio para los archivos CSV de entrada.
- `processed_data/`: Directorio de salida para los informes generados.
- `tests/`: Pruebas unitarias e integración.

## ⚙️ Configuración
1. Copia `.env.example` a `.env`.
2. Ajusta las variables necesarias:
   - `EMPRESA`: Nombre de la organización (obligatorio).
   - `SEPARADOR`: Carácter separador del CSV (por defecto `;`).
   - Pares `PUBLICO_i` y `CSV_i`: Para configurar múltiples fuentes en modo CLI.

### Requisitos del CSV
Cada archivo CSV debe contener al menos las siguientes columnas:
- `IdUsuario`
- `Nombre`
- `Empresa`
- `Estado`

## 💻 Ejecución

### Interfaz Gráfica (Recomendado)
```powershell
uv run main.py
```

### Modo CLI (Automatización)
```powershell
uv run main.py --cli --env-file .env
```

### Como módulo de Python
```powershell
uv run python -m participation_report
```

## 🛠️ Desarrollo y Mantenimiento

### Generar Icono
Si actualizas el archivo SVG, regenera el icono multi-resolución:
```powershell
uv run scripts/generate_icon.py
```

### Construir Ejecutable (.exe)
Genera el paquete distribuible para Windows:
```powershell
uv run scripts/build_exe.py
```

## 🧪 Calidad y Tests
```powershell
uv run ruff check .      # Linting
uv run ruff format .     # Formateo automático
uv run mypy              # Comprobación de tipos
uv run pytest            # Ejecución de tests
```

## 📄 Documentación Adicional
- [ROADMAP.md](./ROADMAP.md): Estado de avance y próximas tareas.
- [BRANCH_POLICY.md](./BRANCH_POLICY.md): Guía de contribución y ramas.
- [AGENTS.md](./AGENTS.md): Instrucciones específicas para agentes IA.

## 📊 Resultado
El sistema genera un archivo Excel en `processed_data/` con el formato `reporte_participacion_[EMPRESA]_[TIMESTAMP].xlsx`. Incluye un resumen general y secciones detalladas por público con porcentajes de participación.
