import io
import os
import traceback
from contextlib import redirect_stdout
from pathlib import Path

from PyQt6.QtCore import QPoint, QRectF, Qt
from PyQt6.QtGui import QColor, QFont, QIcon, QPainter, QPaintEvent, QPixmap, QPolygon
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from participation_report.config import AppConfig
from participation_report.services import generate_report

# ── Paletas ──────────────────────────────────────────────────────────────────
THEMES: dict[str, dict[str, str]] = {
    "light": {
        "PRIMARY":   "#1cabde",
        "LIGHT1":    "#8ed0e1",
        "LIGHT2":    "#59bedf",
        "TEXT":      "#4d4d4d",
        "TEXT_SUB":  "#5a8ea0",
        "ACCENT":    "#76cce8",
        "BG":        "#eef9fc",
        "CARD":      "rgba(255,255,255,0.86)",
        "CARD_ROW":  "rgba(118,204,232,0.13)",
        "SCROLL_BG": "rgba(255,255,255,0.45)",
        "BORDER":    "#b8e4f0",
        "INPUT_BG":  "rgba(255,255,255,0.9)",
        "INPUT_FOC": "#ffffff",
        "COMBO_SEL": "#ffffff",
        "DANGER":    "#d64545",
        "DANGER_H":  "#bf3b3b",
        "SHADOW_A":  "40",
        "TOGGLE_LBL": "🌙",
    },
    "dark": {
        "PRIMARY":   "#1cabde",
        "LIGHT1":    "#3a8fa8",
        "LIGHT2":    "#2e7d99",
        "TEXT":      "#e2eef2",
        "TEXT_SUB":  "#7ab8cc",
        "ACCENT":    "#1e6a82",
        "BG":        "#0f1e24",
        "CARD":      "rgba(22,40,50,0.95)",
        "CARD_ROW":  "rgba(28,171,222,0.08)",
        "SCROLL_BG": "rgba(15,30,38,0.80)",
        "BORDER":    "#1e4d5e",
        "INPUT_BG":  "rgba(18,34,44,0.95)",
        "INPUT_FOC": "#162830",
        "COMBO_SEL": "#1a3040",
        "DANGER":    "#e05555",
        "DANGER_H":  "#c94444",
        "SHADOW_A":  "70",
        "TOGGLE_LBL": "☀️",
    },
}
# ─────────────────────────────────────────────────────────────────────────────

PUBLICOS = [
    "Enfermeras",
    "Especialistas",
    "Gerentes y directivos",
    "Químicos Farmacéuticos",
    "Matronas",
    "Médicos generales y de medicina familiar",
    "Tecnólogos médicos de oftalmología",
]


def _shadow(radius: int = 18, alpha: int = 40, dy: int = 4) -> QGraphicsDropShadowEffect:
    fx = QGraphicsDropShadowEffect()
    fx.setBlurRadius(radius)
    fx.setOffset(0, dy)
    fx.setColor(QColor(28, 171, 222, alpha))
    return fx


class ArrowComboBox(QComboBox):
    def paintEvent(self, event: QPaintEvent | None) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#1cabde"))
        x = self.width() - 20
        y = self.height() // 2
        triangle = QPolygon(
            [QPoint(x - 5, y - 3), QPoint(x + 5, y - 3), QPoint(x, y + 4)]
        )
        painter.drawPolygon(triangle)
        painter.end()


class PublicoCsvRow:
    def __init__(self, parent_layout: QVBoxLayout, publicos: list[str]) -> None:
        self.container = QFrame()
        self.container.setObjectName("rowCard")
        row_layout = QHBoxLayout(self.container)
        row_layout.setContentsMargins(10, 8, 10, 8)
        row_layout.setSpacing(10)

        self.publico_combo = ArrowComboBox()
        self.publico_combo.addItems(publicos)
        self.publico_combo.setMinimumWidth(300)
        self.publico_combo.setFixedHeight(38)

        self.csv_path = QLineEdit()
        self.csv_path.setPlaceholderText("Selecciona un CSV…")
        self.csv_path.setFixedHeight(38)

        self.btn_browse = QPushButton("Examinar")
        self.btn_remove = QPushButton("✕")
        self.btn_remove.setObjectName("dangerButton")
        self.btn_remove.setFixedSize(38, 38)
        self.btn_browse.setFixedHeight(38)
        self.btn_browse.setMinimumWidth(90)

        row_layout.addWidget(self.publico_combo, 3)
        row_layout.addWidget(self.csv_path, 6)
        row_layout.addWidget(self.btn_browse)
        row_layout.addWidget(self.btn_remove)
        parent_layout.addWidget(self.container)


class SectionLabel(QLabel):
    """Etiqueta de sección con línea decorativa."""

    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setObjectName("section")


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._theme = "light"

        self.setWindowTitle("Participation Report Generator")
        self.setWindowIcon(QIcon("participation_report/assets/icon.ico"))
        self.resize(1060, 700)
        self.setMinimumSize(820, 560)

        self.empresa_value = QLineEdit()
        self.empresa_value.setPlaceholderText("Ej: Clínica Dávila Vespucio")
        self.empresa_value.setFixedHeight(38)

        self.separador_value = QLineEdit(";")
        self.separador_value.setPlaceholderText("Separador (por defecto ';')")
        self.separador_value.setFixedHeight(38)

        self.rows: list[PublicoCsvRow] = []
        self.rows_container = QWidget()
        self.rows_container.setObjectName("rowsContainer")
        self.rows_layout = QVBoxLayout(self.rows_container)
        self.rows_layout.setSpacing(6)
        self.rows_layout.setContentsMargins(4, 4, 4, 4)

        self.btn_add_row = QPushButton("＋  Agregar público + CSV")
        self.btn_add_row.setObjectName("secondaryButton")
        self.btn_run = QPushButton("▶  Generar informe")
        self.btn_run.setObjectName("primaryButton")

        self.log_output = QPlainTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("La salida de ejecución aparecerá aquí…")

        self._build_ui()
        self._connect_signals()
        self._apply_styles()
        self._add_row()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(28, 22, 28, 22)
        layout.setSpacing(18)

        # Header
        header_box = QVBoxLayout()
        header_box.setSpacing(6)
        header_box.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # Icono centrado — renderizado desde SVG a alta resolución
        icon_label = QLabel()
        svg_path = str(Path("participation_report/assets/icon.svg"))
        size = 72
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        renderer = QSvgRenderer(svg_path)
        painter = QPainter(pixmap)
        renderer.render(painter, QRectF(0, 0, size, size))
        painter.end()
        icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        header_box.addWidget(icon_label)

        title = QLabel("Generador de Reporte de Participación")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        subtitle = QLabel(
            "Agrega uno o varios públicos y su CSV de contactos para generar un informe único"
        )
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        header_box.addWidget(title)
        header_box.addWidget(subtitle)

        # Botón toggle de tema
        self.btn_theme = QPushButton(THEMES[self._theme]["TOGGLE_LBL"])
        self.btn_theme.setObjectName("themeButton")
        self.btn_theme.setFixedSize(36, 36)
        self.btn_theme.setToolTip("Cambiar tema")

        # Fila header: icono+texto centrados, toggle a la derecha
        header_row = QHBoxLayout()
        header_row.addStretch()
        header_row.addLayout(header_box)
        header_row.addStretch()
        header_row.addWidget(self.btn_theme, 0, Qt.AlignmentFlag.AlignTop)
        layout.addLayout(header_row)

        # Card: configuración
        cfg_card = QFrame()
        cfg_card.setObjectName("card")
        cfg_card.setGraphicsEffect(_shadow(22, 35, 5))
        cfg_layout = QVBoxLayout(cfg_card)
        cfg_layout.setContentsMargins(20, 18, 20, 18)
        cfg_layout.setSpacing(14)

        # Fila empresa / separador
        fields_row = QHBoxLayout()
        fields_row.setSpacing(16)

        empresa_col = QVBoxLayout()
        empresa_col.setSpacing(5)
        empresa_col.addWidget(QLabel("Empresa"))
        empresa_col.addWidget(self.empresa_value)

        sep_col = QVBoxLayout()
        sep_col.setSpacing(5)
        sep_col.addWidget(QLabel("Separador CSV"))
        sep_col.addWidget(self.separador_value)
        self.separador_value.setMaximumWidth(140)

        fields_row.addLayout(empresa_col, 5)
        fields_row.addLayout(sep_col, 1)
        cfg_layout.addLayout(fields_row)

        # Sección públicos
        publicos_header = QHBoxLayout()
        publicos_header.addWidget(SectionLabel("Públicos y archivos CSV"))
        publicos_header.addStretch()
        publicos_header.addWidget(self.btn_add_row)
        cfg_layout.addLayout(publicos_header)

        rows_scroll = QScrollArea()
        rows_scroll.setWidgetResizable(True)
        rows_scroll.setFrameShape(QFrame.Shape.NoFrame)
        rows_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        rows_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        rows_scroll.setWidget(self.rows_container)
        rows_scroll.setMinimumHeight(130)
        rows_scroll.setMaximumHeight(260)
        rows_scroll.setObjectName("rowsScroll")
        cfg_layout.addWidget(rows_scroll)

        layout.addWidget(cfg_card)

        # Botón generar
        actions = QHBoxLayout()
        actions.addStretch()
        actions.addWidget(self.btn_run)
        layout.addLayout(actions)

        # Card: log
        log_card = QFrame()
        log_card.setObjectName("card")
        log_card.setGraphicsEffect(_shadow(20, 28, 4))
        log_layout = QVBoxLayout(log_card)
        log_layout.setContentsMargins(20, 16, 20, 16)
        log_layout.setSpacing(8)
        log_layout.addWidget(SectionLabel("Registro de ejecución"))
        self.log_output.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        log_layout.addWidget(self.log_output)
        layout.addWidget(log_card, 1)

    # ── Señales ───────────────────────────────────────────────────────────────

    def _connect_signals(self) -> None:
        self.btn_add_row.clicked.connect(self._add_row)
        self.btn_run.clicked.connect(self._run_report)
        self.btn_theme.clicked.connect(self._toggle_theme)

    # ── Tema ──────────────────────────────────────────────────────────────────

    def _toggle_theme(self) -> None:
        self._theme = "dark" if self._theme == "light" else "light"
        self.btn_theme.setText(THEMES[self._theme]["TOGGLE_LBL"])
        self._apply_styles()

    # ── Estilos ───────────────────────────────────────────────────────────────

    def _apply_styles(self) -> None:
        t = THEMES[self._theme]
        self.setFont(QFont("Segoe UI", 10))
        style = f"""
            /* Base */
            QMainWindow, QWidget {{
                background-color: {t['BG']};
                color: {t['TEXT']};
            }}

            /* Cards */
            QFrame#card {{
                background: {t['CARD']};
                border: 1px solid {t['BORDER']};
                border-radius: 16px;
            }}

            /* Filas de público */
            QFrame#rowCard {{
                background: {t['CARD_ROW']};
                border: 1px solid {t['BORDER']};
                border-radius: 10px;
            }}

            QWidget#rowsContainer {{
                background: transparent;
            }}

            /* Scroll de filas */
            QScrollArea#rowsScroll {{
                background: {t['SCROLL_BG']};
                border: 1px solid {t['BORDER']};
                border-radius: 12px;
            }}

            /* Tipografía */
            QLabel#title {{
                font-size: 24px;
                font-weight: 700;
                color: {t['PRIMARY']};
                letter-spacing: -0.3px;
            }}
            QLabel#subtitle {{
                font-size: 12.5px;
                color: {t['TEXT_SUB']};
            }}
            QLabel#section {{
                font-size: 13px;
                font-weight: 600;
                color: {t['PRIMARY']};
                padding-bottom: 2px;
                border-bottom: 2px solid {t['ACCENT']};
            }}
            QLabel {{
                font-size: 11px;
                color: {t['TEXT']};
                background: transparent;
            }}

            /* Inputs */
            QLineEdit, QPlainTextEdit, QComboBox {{
                background: {t['INPUT_BG']};
                border: 1.5px solid {t['BORDER']};
                border-radius: 9px;
                padding: 6px 10px;
                color: {t['TEXT']};
                selection-background-color: {t['LIGHT1']};
            }}
            QLineEdit:focus, QPlainTextEdit:focus, QComboBox:focus {{
                border-color: {t['PRIMARY']};
                background: {t['INPUT_FOC']};
            }}
            QLineEdit:hover, QComboBox:hover {{
                border-color: {t['LIGHT2']};
            }}

            QComboBox {{
                padding-right: 32px;
            }}
            QComboBox::drop-down {{
                width: 32px;
                border: none;
                background: transparent;
                subcontrol-origin: padding;
                subcontrol-position: top right;
            }}
            QComboBox::down-arrow {{
                image: none;
                width: 0px;
                height: 0px;
            }}
            QComboBox QAbstractItemView {{
                border: 1px solid {t['BORDER']};
                border-radius: 9px;
                background: {t['COMBO_SEL']};
                selection-background-color: {t['ACCENT']};
                selection-color: {t['TEXT']};
                padding: 4px;
                outline: none;
            }}

            /* Scrollbars */
            QScrollBar:vertical {{
                background: transparent;
                width: 8px;
                border-radius: 4px;
                margin: 6px 2px;
            }}
            QScrollBar::handle:vertical {{
                background: {t['LIGHT1']};
                border-radius: 4px;
                min-height: 22px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {t['PRIMARY']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}

            /* Botón primario */
            QPushButton#primaryButton {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {t['PRIMARY']}, stop:1 {t['LIGHT2']}
                );
                color: #ffffff;
                border: none;
                border-radius: 10px;
                padding: 10px 28px;
                font-size: 13px;
                font-weight: 700;
                letter-spacing: 0.2px;
                min-width: 170px;
            }}
            QPushButton#primaryButton:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {t['LIGHT2']}, stop:1 {t['PRIMARY']}
                );
            }}
            QPushButton#primaryButton:pressed {{
                padding-top: 11px;
                padding-bottom: 9px;
            }}

            /* Botón secundario */
            QPushButton#secondaryButton {{
                background: rgba(28, 171, 222, 0.12);
                color: {t['PRIMARY']};
                border: 1.5px solid {t['LIGHT1']};
                border-radius: 9px;
                padding: 7px 16px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton#secondaryButton:hover {{
                background: rgba(28, 171, 222, 0.22);
                border-color: {t['PRIMARY']};
            }}

            /* Botón toggle tema */
            QPushButton#themeButton {{
                background: {t['CARD_ROW']};
                border: 1.5px solid {t['BORDER']};
                border-radius: 10px;
                font-size: 16px;
                padding: 0px;
            }}
            QPushButton#themeButton:hover {{
                background: rgba(28, 171, 222, 0.20);
                border-color: {t['PRIMARY']};
            }}

            /* Botón genérico (examinar) */
            QPushButton {{
                background: rgba(89, 190, 223, 0.15);
                color: {t['PRIMARY']};
                border: 1px solid {t['LIGHT1']};
                border-radius: 9px;
                padding: 7px 14px;
                font-weight: 600;
                font-size: 11.5px;
            }}
            QPushButton:hover {{
                background: rgba(28, 171, 222, 0.25);
                border-color: {t['PRIMARY']};
            }}
            QPushButton:pressed {{
                background: rgba(28, 171, 222, 0.38);
            }}

            /* Botón eliminar */
            QPushButton#dangerButton {{
                background: rgba(214, 69, 69, 0.10);
                color: {t['DANGER']};
                border: 1px solid rgba(214, 69, 69, 0.35);
                border-radius: 9px;
                font-size: 14px;
                font-weight: 700;
                padding: 0px;
            }}
            QPushButton#dangerButton:hover {{
                background: {t['DANGER']};
                color: #ffffff;
                border-color: {t['DANGER']};
            }}
            QPushButton#dangerButton:disabled {{
                background: rgba(180,180,180,0.08);
                color: #777;
                border-color: #555;
            }}
        """
        self.setStyleSheet(style)

    # ── Filas ─────────────────────────────────────────────────────────────────

    def _add_row(self) -> None:
        row = PublicoCsvRow(self.rows_layout, PUBLICOS)
        row.btn_browse.clicked.connect(lambda: self._select_csv_file(row))
        row.btn_remove.clicked.connect(lambda: self._remove_row(row))
        self.rows.append(row)
        self._sync_remove_buttons()

    def _remove_row(self, row: PublicoCsvRow) -> None:
        if len(self.rows) <= 1:
            return
        self.rows.remove(row)
        row.container.setParent(None)
        row.container.deleteLater()
        self._sync_remove_buttons()

    def _sync_remove_buttons(self) -> None:
        can_remove = len(self.rows) > 1
        for row in self.rows:
            row.btn_remove.setEnabled(can_remove)

    def _select_csv_file(self, row: PublicoCsvRow) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecciona archivo CSV",
            "",
            "CSV files (*.csv);;All files (*)",
        )
        if path:
            row.csv_path.setText(path)

    # ── Lógica ────────────────────────────────────────────────────────────────

    def _build_config(self) -> AppConfig:
        empresa = self.empresa_value.text().strip()
        separador = self.separador_value.text().strip() or ";"
        publicos_y_csvs: list[tuple[str, str]] = []

        if not empresa:
            raise ValueError("Debes indicar la empresa.")

        for idx, row in enumerate(self.rows, start=1):
            publico = row.publico_combo.currentText().strip()
            csv = row.csv_path.text().strip()
            if not csv:
                raise ValueError(f"Debes seleccionar un CSV en la fila {idx}.")
            if not Path(csv).exists():
                raise ValueError(f"El CSV de la fila {idx} no existe.")
            publicos_y_csvs.append((publico, csv))

        if not publicos_y_csvs:
            raise ValueError("Debes agregar al menos un publico con su CSV.")

        return AppConfig(empresa=empresa, separador=separador, publicos_y_csvs=publicos_y_csvs)

    def _run_report(self) -> None:
        try:
            config = self._build_config()
        except ValueError as exc:
            self._show_error(str(exc))
            return

        buffer = io.StringIO()
        try:
            with redirect_stdout(buffer):
                generate_report(config)
            output = buffer.getvalue().strip()
            if output:
                self._append_log(output)
            self._append_log("[OK] Proceso finalizado.")
            QMessageBox.information(self, "Informe generado", "El informe se generó correctamente.")
        except SystemExit as exc:
            output = buffer.getvalue().strip()
            if output:
                self._append_log(output)
            self._show_error(str(exc))
        except Exception:
            output = buffer.getvalue().strip()
            if output:
                self._append_log(output)
            self._show_error("Ocurrió un error inesperado.\n\n" + traceback.format_exc())

    def _append_log(self, text: str) -> None:
        current = self.log_output.toPlainText()
        chunk = text.strip()
        if not chunk:
            return
        if current:
            self.log_output.appendPlainText("")
        self.log_output.appendPlainText(chunk)
        scrollbar = self.log_output.verticalScrollBar()
        if scrollbar is not None:
            scrollbar.setValue(scrollbar.maximum())

    def _show_error(self, text: str) -> None:
        self._append_log(text)
        QMessageBox.critical(self, "Error", text)


def main() -> None:
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
    app = QApplication([])
    app.setAttribute(Qt.ApplicationAttribute.AA_DontShowIconsInMenus, False)
    window = MainWindow()
    window.show()
    app.exec()
