"""
Panel de Escaneo y Carga de Archivos Excel / CSV
PROJ-008: Excel Analytics Studio
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QFileDialog, QMessageBox, QFrame, QScrollArea
)
from PyQt5.QtCore import pyqtSignal, Qt
import os
from core.excel_scanner import ExcelScanner, ScanResult


class PanelScanner(QFrame):
    """Panel lateral de carga, selección de hojas y diagnóstico de datos."""

    # Señal emitida cuando un archivo o nueva hoja se carga exitosamente
    scan_completed = pyqtSignal(object)

    def __init__(self, demo_file_path: str, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebarCard")
        self.demo_file_path = demo_file_path
        self.current_filepath: str = ""
        self.current_scan: ScanResult = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        # Título del panel
        title = QLabel("📂 ARCHIVO Y HOJAS")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        # Botón principal para abrir archivo
        self.btn_open = QPushButton("📁 Abrir Excel / CSV")
        self.btn_open.setObjectName("primaryButton")
        self.btn_open.setCursor(Qt.PointingHandCursor)
        self.btn_open.clicked.connect(self._on_choose_file)
        layout.addWidget(self.btn_open)

        # Botón para cargar archivo de demostración
        self.btn_demo = QPushButton("⚡ Cargar Demo Ventas")
        self.btn_demo.setCursor(Qt.PointingHandCursor)
        self.btn_demo.clicked.connect(self._on_load_demo)
        layout.addWidget(self.btn_demo)

        # Etiqueta de archivo actual
        self.file_label = QLabel("Ningún archivo cargado")
        self.file_label.setWordWrap(True)
        self.file_label.setStyleSheet("font-size: 11px; color: #94a3b8; padding: 2px;")
        layout.addWidget(self.file_label)

        # Selector de hojas
        sheet_header = QLabel("Hoja de Cálculo Activa:")
        sheet_header.setStyleSheet("font-size: 11px; font-weight: 600; color: #cbd5e1; margin-top: 6px;")
        layout.addWidget(sheet_header)

        self.combo_sheets = QComboBox()
        self.combo_sheets.currentIndexChanged.connect(self._on_sheet_changed)
        layout.addWidget(self.combo_sheets)

        # Separador visual
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #1f2937;")
        layout.addWidget(line)

        # Sección de Diagnóstico
        diag_title = QLabel("🔍 DIAGNÓSTICO DE DATOS")
        diag_title.setObjectName("sectionTitle")
        layout.addWidget(diag_title)

        # Tarjeta resumen de diagnóstico
        self.diag_card = QFrame()
        self.diag_card.setObjectName("kpiCard")
        diag_layout = QVBoxLayout(self.diag_card)
        diag_layout.setContentsMargins(10, 8, 10, 8)
        diag_layout.setSpacing(6)

        self.lbl_filas = QLabel("• Filas: —")
        self.lbl_columnas = QLabel("• Columnas: —")
        self.lbl_memoria = QLabel("• Memoria: —")
        self.lbl_duplicados = QLabel("• Duplicados: —")
        self.lbl_nulos = QLabel("• Celdas Vacías: —")

        for lbl in [self.lbl_filas, self.lbl_columnas, self.lbl_memoria, self.lbl_duplicados, self.lbl_nulos]:
            lbl.setStyleSheet("font-size: 11px; color: #cbd5e1;")
            diag_layout.addWidget(lbl)

        layout.addWidget(self.diag_card)

        # Resumen de tipos de columnas
        self.types_title = QLabel("📊 Tipos Detectados:")
        self.types_title.setStyleSheet("font-size: 11px; font-weight: 600; color: #cbd5e1; margin-top: 4px;")
        layout.addWidget(self.types_title)

        self.lbl_types_summary = QLabel("Numéricas: 0 | Categóricas: 0 | Fechas: 0")
        self.lbl_types_summary.setWordWrap(True)
        self.lbl_types_summary.setStyleSheet("font-size: 11px; color: #38bdf8;")
        layout.addWidget(self.lbl_types_summary)

        layout.addStretch()

    def _on_choose_file(self):
        """Abre un diálogo nativo para elegir el archivo."""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Archivo de Datos",
            "",
            "Archivos Compatibles (*.xlsx *.xls *.csv *.xlsm);;Libros de Excel (*.xlsx *.xlsm);;Archivos CSV (*.csv);;Libros Excel 97-2003 (*.xls)"
        )
        if filepath:
            self.load_file(filepath)

    def _on_load_demo(self):
        """Carga el dataset corporativo de demostración."""
        if os.path.exists(self.demo_file_path):
            self.load_file(self.demo_file_path)
        else:
            QMessageBox.warning(self, "Aviso", f"No se encontró el archivo demo en:\n{self.demo_file_path}")

    def load_file(self, filepath: str, selected_sheet: str = None):
        """Escanea el archivo seleccionado y actualiza la UI."""
        try:
            # Obtener hojas
            sheet_names = ExcelScanner.get_sheet_names(filepath)
            self.current_filepath = filepath
            self.file_label.setText(f"📄 {os.path.basename(filepath)}")

            # Bloquear señales temporalmente para poblar combo
            self.combo_sheets.blockSignals(True)
            self.combo_sheets.clear()
            self.combo_sheets.addItems(sheet_names)
            if selected_sheet and selected_sheet in sheet_names:
                self.combo_sheets.setCurrentText(selected_sheet)
            else:
                self.combo_sheets.setCurrentIndex(0)
            self.combo_sheets.blockSignals(False)

            active_sheet = self.combo_sheets.currentText()
            self._execute_scan(active_sheet)

        except Exception as e:
            QMessageBox.critical(self, "Error al Escanear", f"No se pudo leer el archivo:\n{str(e)}")

    def _on_sheet_changed(self, index: int):
        """Disparado cuando el usuario cambia de hoja."""
        if index >= 0 and self.current_filepath:
            sheet_name = self.combo_sheets.currentText()
            self._execute_scan(sheet_name)

    def _execute_scan(self, sheet_name: str):
        """Ejecuta el escaneo profundo de la hoja activa."""
        try:
            scan_result = ExcelScanner.scan_file(self.current_filepath, sheet_name=sheet_name)
            self.current_scan = scan_result

            # Actualizar diagnóstico
            total_nulls = sum(col.null_count for col in scan_result.columns)
            self.lbl_filas.setText(f"• Filas: {scan_result.total_rows:,}")
            self.lbl_columnas.setText(f"• Columnas: {scan_result.total_cols}")
            self.lbl_memoria.setText(f"• Memoria: {scan_result.memory_usage_kb:,.1f} KB")
            self.lbl_duplicados.setText(f"• Duplicados: {scan_result.duplicate_rows}")
            self.lbl_nulos.setText(f"• Celdas Vacías: {total_nulls:,}")

            num_count = len(scan_result.numeric_columns)
            cat_count = len(scan_result.categorical_columns)
            temp_count = len(scan_result.temporal_columns)
            self.lbl_types_summary.setText(f"Numéricas: <b>{num_count}</b> | Categóricas: <b>{cat_count}</b> | Fechas: <b>{temp_count}</b>")

            # Emitir señal al resto de la aplicación
            self.scan_completed.emit(scan_result)

        except Exception as e:
            QMessageBox.critical(self, "Error en Escaneo", f"Ocurrió un error al procesar la hoja '{sheet_name}':\n{str(e)}")
