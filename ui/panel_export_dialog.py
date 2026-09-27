"""
Diálogo Modal de Exportación Avanzada a Excel
PROJ-008: Excel Analytics Studio
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QRadioButton,
    QPushButton, QCheckBox, QFileDialog, QMessageBox, QFrame,
    QButtonGroup
)
from PyQt5.QtCore import Qt
import os
import subprocess
from core.data_aggregator import AggregatedData
from core.excel_exporter_native import NativeExcelExporter
from core.excel_exporter_dashboard import ExecutiveDashboardExporter
import pandas as pd


class ExportExcelDialog(QDialog):
    """Diálogo modal para configurar y exportar a Excel."""

    def __init__(self, agg_data: AggregatedData, chart_params: dict, source_df: pd.DataFrame, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Exportar Informe a Excel con Gráficos")
        self.resize(550, 420)
        self.setModal(True)

        self.agg_data = agg_data
        self.chart_params = chart_params
        self.source_df = source_df
        self.generated_file = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Encabezado
        title = QLabel("📊 Exportación Profesional a Excel")
        title.setObjectName("headingLabel")
        title.setStyleSheet("font-size: 16px; font-weight: 700; color: #f8fafc;")
        layout.addWidget(title)

        subtitle = QLabel("Seleccione la modalidad de gráficos y estructura que desea para el nuevo libro:")
        subtitle.setStyleSheet("font-size: 12px; color: #94a3b8;")
        layout.addWidget(subtitle)

        # Opciones de Modo de Exportación
        options_frame = QFrame()
        options_frame.setObjectName("panelCard")
        options_layout = QVBoxLayout(options_frame)
        options_layout.setSpacing(12)

        self.btn_group = QButtonGroup(self)

        # Opción 1: Gráficos Nativos Dinámicos
        self.radio_native = QRadioButton("Gráficos NATIVOS Dinámicos de Excel")
        self.radio_native.setChecked(True)
        self.radio_native.setStyleSheet("font-weight: 600; font-size: 13px; color: #38bdf8;")
        desc_native = QLabel("Crea gráficos nativos de Microsoft Excel vinculados a las celdas. Si modifica un número en Excel, el gráfico se actualiza en tiempo real de forma automática.")
        desc_native.setWordWrap(True)
        desc_native.setStyleSheet("font-size: 11px; color: #94a3b8; margin-left: 22px;")
        self.btn_group.addButton(self.radio_native, 1)
        options_layout.addWidget(self.radio_native)
        options_layout.addWidget(desc_native)

        # Opción 2: Dashboard Ejecutivo HD
        self.radio_dashboard = QRadioButton("Informe Ejecutivo con Tarjetas KPI y Gráficos HD")
        self.radio_dashboard.setStyleSheet("font-weight: 600; font-size: 13px; color: #10b981;")
        desc_dash = QLabel("Genera una portada gerencial con 4 tarjetas de indicadores KPI, tabla formateada y el gráfico incrustado en resolución ultra nítida (300 DPI).")
        desc_dash.setWordWrap(True)
        desc_dash.setStyleSheet("font-size: 11px; color: #94a3b8; margin-left: 22px;")
        self.btn_group.addButton(self.radio_dashboard, 2)
        options_layout.addWidget(self.radio_dashboard)
        options_layout.addWidget(desc_dash)

        layout.addWidget(options_frame)

        # Configuración adicional
        self.chk_include_source = QCheckBox("Incluir hoja adicional con todos los datos originales")
        self.chk_include_source.setChecked(True)
        layout.addWidget(self.chk_include_source)

        layout.addStretch()

        # Botones de Acción
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)

        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_export = QPushButton("🚀 Generar Archivo Excel")
        self.btn_export.setObjectName("successButton")
        self.btn_export.setCursor(Qt.PointingHandCursor)
        self.btn_export.clicked.connect(self._do_export)

        actions_layout.addStretch()
        actions_layout.addWidget(self.btn_cancel)
        actions_layout.addWidget(self.btn_export)

        layout.addLayout(actions_layout)

    def _do_export(self):
        """Ejecuta la exportación según la modalidad elegida."""
        default_name = f"Analisis_{self.agg_data.y_cols[0]}_por_{self.agg_data.x_col}.xlsx".replace(" ", "_")
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Documento Excel Generado",
            default_name,
            "Libros de Excel (*.xlsx)"
        )

        if not filepath:
            return

        if not filepath.lower().endswith(".xlsx"):
            filepath += ".xlsx"

        try:
            chart_type = self.chart_params.get('chart_type', 'Barras Verticales')
            palette_name = self.chart_params.get('palette_name', 'Sapphire Corporativo')
            custom_title = self.chart_params.get('custom_title', None)
            include_source = self.chk_include_source.isChecked()

            if self.radio_native.isChecked():
                # Modo Nativo Dinámico
                NativeExcelExporter.export(
                    agg_data=self.agg_data,
                    output_filepath=filepath,
                    chart_type=chart_type,
                    palette_name=palette_name,
                    custom_title=custom_title,
                    include_source_data=include_source,
                    source_df=self.source_df if include_source else None
                )
            else:
                # Modo Dashboard Ejecutivo HD
                ExecutiveDashboardExporter.export(
                    agg_data=self.agg_data,
                    output_filepath=filepath,
                    chart_type=chart_type,
                    palette_name=palette_name,
                    custom_title=custom_title,
                    source_df=self.source_df if include_source else None
                )

            self.generated_file = filepath

            # Preguntar al usuario si desea abrir el archivo
            reply = QMessageBox.question(
                self,
                "Exportación Exitosa",
                f"El archivo Excel ha sido creado con éxito en:\n{filepath}\n\n¿Desea abrir el archivo en Excel ahora mismo?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )

            if reply == QMessageBox.Yes:
                try:
                    os.startfile(filepath)
                except Exception as e:
                    QMessageBox.warning(self, "Aviso", f"No se pudo abrir automáticamente:\n{str(e)}")

            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error al Exportar", f"Ocurrió un error al generar el archivo Excel:\n{str(e)}")
