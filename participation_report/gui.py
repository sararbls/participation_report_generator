import io
import os
import traceback
from contextlib import redirect_stdout
from pathlib import Path

from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPolygon
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
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

PUBLICOS = [
    "Enfermeras",
    "Especialistas",
    "Gerentes y directivos",
    "Químicos Farmacéuticos",
    "Matronas",
    "Médicos generales y de medicina familiar",
    "Tecnólogos médicos de oftalmología",
]


class ArrowComboBox(QComboBox):
    def paintEvent(self, event) -> None:  # type: ignore[override]
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#35608a"))

        x = self.width() - 18
        y = self.height() // 2
        triangle = QPolygon(
            [
                QPoint(x - 4, y - 2),
                QPoint(x + 4, y - 2),
                QPoint(x, y + 3),
            ]
        )
        painter.drawPolygon(triangle)
        painter.end()


class PublicoCsvRow:
    def __init__(self, parent_layout: QVBoxLayout, publicos: list[str]) -> None:
        self.container = QFrame()
        row_layout = QHBoxLayout(self.container)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(8)

        self.publico_combo = ArrowComboBox()
        self.publico_combo.addItems(publicos)
        self.publico_combo.setMinimumWidth(320)
        self.publico_combo.setMinimumHeight(40)

        self.csv_path = QLineEdit()
        self.csv_path.setPlaceholderText("Selecciona un CSV")
        self.csv_path.setMinimumHeight(40)

        self.btn_browse = QPushButton("Examinar")
        self.btn_remove = QPushButton("Quitar")
        self.btn_remove.setObjectName("dangerButton")
        self.btn_browse.setMinimumHeight(40)
        self.btn_remove.setMinimumHeight(40)
        self.btn_browse.setMinimumWidth(96)
        self.btn_remove.setMinimumWidth(84)

        row_layout.addWidget(self.publico_combo, 3)
        row_layout.addWidget(self.csv_path, 6)
        row_layout.addWidget(self.btn_browse)
        row_layout.addWidget(self.btn_remove)
        parent_layout.addWidget(self.container)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Participation Report Generator")
        self.resize(1020, 680)

        self.empresa_value = QLineEdit()
        self.empresa_value.setPlaceholderText("Ej: Clinica Davila Vespucio")
        self.empresa_value.setMinimumHeight(40)
        self.separador_value = QLineEdit(";")
        self.separador_value.setPlaceholderText("Separador CSV, por defecto ';'")
        self.separador_value.setMinimumHeight(40)

        self.rows: list[PublicoCsvRow] = []
        self.rows_container = QWidget()
        self.rows_layout = QVBoxLayout(self.rows_container)
        self.rows_layout.setSpacing(8)
        self.rows_layout.setContentsMargins(0, 0, 0, 0)

        self.btn_add_row = QPushButton("Agregar público + CSV")
        self.btn_run = QPushButton("Generar informe")

        self.log_output = QPlainTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("Salida de ejecución")

        self._build_ui()
        self._connect_signals()
        self._apply_styles()
        self._add_row()

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        header = QLabel("Generador de Reporte de Participación")
        header.setObjectName("title")
        subtitle = QLabel(
            "Agrega uno o varios públicos y su CSV de contactos para generar un informe único"
        )
        subtitle.setObjectName("subtitle")
        layout.addWidget(header)
        layout.addWidget(subtitle)

        details_card = QFrame()
        details_card.setObjectName("card")
        details_layout = QGridLayout(details_card)
        details_layout.setContentsMargins(14, 14, 14, 14)
        details_layout.setHorizontalSpacing(12)
        details_layout.setVerticalSpacing(10)

        details_layout.addWidget(QLabel("Empresa"), 0, 0)
        details_layout.addWidget(self.empresa_value, 0, 1)
        details_layout.addWidget(QLabel("Separador"), 0, 2)
        details_layout.addWidget(self.separador_value, 0, 3)

        details_layout.addWidget(QLabel("Publico + CSV"), 1, 0, 1, 4)

        rows_scroll = QScrollArea()
        rows_scroll.setWidgetResizable(True)
        rows_scroll.setFrameShape(QFrame.Shape.NoFrame)
        rows_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        rows_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        rows_scroll.setWidget(self.rows_container)
        rows_scroll.setMinimumHeight(160)
        rows_scroll.setMaximumHeight(280)
        details_layout.addWidget(rows_scroll, 2, 0, 1, 4)

        details_layout.addWidget(self.btn_add_row, 3, 0, 1, 2)
        details_layout.setColumnStretch(1, 2)
        details_layout.setColumnStretch(3, 1)
        layout.addWidget(details_card)

        actions = QHBoxLayout()
        actions.addStretch()
        actions.addWidget(self.btn_run)
        layout.addLayout(actions)

        log_card = QFrame()
        log_card.setObjectName("card")
        log_layout = QVBoxLayout(log_card)
        log_layout.setContentsMargins(14, 14, 14, 14)
        log_layout.setSpacing(8)
        log_label = QLabel("Log")
        log_label.setObjectName("section")
        self.log_output.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        log_layout.addWidget(log_label)
        log_layout.addWidget(self.log_output)
        layout.addWidget(log_card, 1)

    def _connect_signals(self) -> None:
        self.btn_add_row.clicked.connect(self._add_row)
        self.btn_run.clicked.connect(self._run_report)

    def _apply_styles(self) -> None:
        self.setFont(QFont("Segoe UI", 10))
        style = """
            QWidget {
                background-color: #f3f6fb;
                color: #17202a;
            }
            QFrame#card {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #ffffff, stop: 1 #eef4ff
                );
                border: 1px solid #d7e2f2;
                border-radius: 14px;
            }
            QLabel#title {
                font-size: 26px;
                font-weight: 700;
                color: #0f3057;
            }
            QLabel#subtitle {
                font-size: 13px;
                color: #46627f;
            }
            QLabel#section {
                font-size: 14px;
                font-weight: 600;
                color: #1f3c64;
            }
            QLineEdit, QPlainTextEdit, QComboBox {
                background: #ffffff;
                border: 1px solid #c8d6ea;
                border-radius: 10px;
                padding: 8px;
            }
            QComboBox {
                padding-right: 34px;
            }
            QComboBox::drop-down {
                width: 28px;
                border: none;
                background: transparent;
                subcontrol-origin: padding;
                subcontrol-position: top right;
            }
            QComboBox::down-arrow {
                image: none;
                width: 0px;
                height: 0px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #c8d6ea;
                border-radius: 10px;
                background: #ffffff;
                selection-background-color: #dcecff;
                selection-color: #133b66;
                padding: 4px;
                outline: none;
            }
            QScrollArea {
                background: transparent;
                border: 1px solid #dbe6f5;
                border-radius: 10px;
            }
            QScrollBar:vertical {
                background: #eaf1fb;
                width: 10px;
                border-radius: 5px;
                margin: 4px;
            }
            QScrollBar::handle:vertical {
                background: #9eb8db;
                border-radius: 5px;
                min-height: 24px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QPushButton {
                background: #2f80ed;
                color: #ffffff;
                border: none;
                border-radius: 10px;
                padding: 9px 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #1f6fdc;
            }
            QPushButton#dangerButton {
                background: #d64545;
            }
            QPushButton#dangerButton:hover {
                background: #bf3b3b;
            }
            """
        self.setStyleSheet(style)
        for row in self.rows:
            self._set_combo_arrow(row.publico_combo)

    def _add_row(self) -> None:
        row = PublicoCsvRow(self.rows_layout, PUBLICOS)
        self._set_combo_arrow(row.publico_combo)
        row.btn_browse.clicked.connect(lambda: self._select_csv_file(row))
        row.btn_remove.clicked.connect(lambda: self._remove_row(row))
        self.rows.append(row)
        self._sync_remove_buttons()

    def _set_combo_arrow(self, combo: QComboBox) -> None:
        combo.setEditable(False)
        combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

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
            QMessageBox.information(self, "Informe generado", "El informe se genero correctamente.")
        except SystemExit as exc:
            output = buffer.getvalue().strip()
            if output:
                self._append_log(output)
            self._show_error(str(exc))
        except Exception:
            output = buffer.getvalue().strip()
            if output:
                self._append_log(output)
            self._show_error("Ocurrio un error inesperado.\n\n" + traceback.format_exc())

    def _append_log(self, text: str) -> None:
        current = self.log_output.toPlainText()
        chunk = text.strip()
        if not chunk:
            return
        if current:
            self.log_output.appendPlainText("")
        self.log_output.appendPlainText(chunk)
        self.log_output.verticalScrollBar().setValue(self.log_output.verticalScrollBar().maximum())

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
