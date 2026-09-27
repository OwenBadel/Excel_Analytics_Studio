"""
Ventana Principal de Excel Analytics Studio
PROJ-008: Excel Analytics Studio
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTabWidget, QPushButton, QLabel, QStatusBar, QMessageBox,
    QFrame
)
from PyQt5.QtCore import Qt
import os

from core.excel_scanner import ScanResult
from core.data_aggregator import DataAggregator, AggregatedData
from core.chart_generator_plotly import PlotlyChartGenerator
from core.chart_generator_matplotlib import MatplotlibChartGenerator
from ui.panel_scanner import PanelScanner
from ui.panel_chart_controls import PanelChartControls
from ui.panel_export_dialog import ExportExcelDialog
from ui.widgets.kpi_card import KPICard
from ui.widgets.data_table_view import DataTableView
from ui.widgets.chart_viewer import ChartViewer


class MainWindow(QMainWindow):
    """Ventana principal de la suite."""

    def __init__(self, demo_file_path: str, local_plotly_path: str = None):
        super().__init__()
        self.setWindowTitle("Excel Analytics Studio — Suite Profesional de Gráficos e Informes")
        self.resize(1320, 840)
        self.setMinimumSize(1080, 680)

        self.demo_file_path = demo_file_path
        self.local_plotly_path = local_plotly_path
        self.current_scan: ScanResult = None
        self.current_agg_data: AggregatedData = None
        self.last_chart_params: dict = {}

        self._setup_ui()
        self._connect_signals()

        # Cargar demo al inicio si existe para experiencia inmediata
        if os.path.exists(self.demo_file_path):
            self.panel_scanner.load_file(self.demo_file_path)

    def _setup_ui(self):
        """Construye la arquitectura visual de la ventana."""
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(14, 12, 14, 12)
        main_layout.setSpacing(12)

        # 1. Barra Superior Corporativa
        header_bar = QHBoxLayout()
        header_bar.setSpacing(12)

        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        app_title = QLabel("⚡ EXCEL ANALYTICS STUDIO")
        app_title.setObjectName("headingLabel")
        app_title.setStyleSheet("font-size: 17px; font-weight: 800; color: #38bdf8; letter-spacing: 0.5px;")

        app_desc = QLabel("Escaneo inteligente, visualizaciones dinámicas y generación de libros Excel con gráficos nativos")
        app_desc.setObjectName("subText")
        app_desc.setStyleSheet("font-size: 11px; color: #94a3b8;")

        title_box.addWidget(app_title)
        title_box.addWidget(app_desc)
        header_bar.addLayout(title_box, 1)

        # Botón destacado de Exportar
        self.btn_export_excel = QPushButton("📊 Exportar a Excel con Gráficos")
        self.btn_export_excel.setObjectName("successButton")
        self.btn_export_excel.setCursor(Qt.PointingHandCursor)
        self.btn_export_excel.setStyleSheet("font-size: 13px; font-weight: 700; padding: 9px 20px;")
        self.btn_export_excel.clicked.connect(self._on_export_dialog)
        header_bar.addWidget(self.btn_export_excel)

        main_layout.addLayout(header_bar)

        # 2. Splitter Horizontal (Panel Izquierdo: Controles | Panel Derecho: Métricas y Visualización)
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(4)

        # Contenedor Izquierdo: Pestañas de Archivo y Controles
        left_tabs = QTabWidget()
        left_tabs.setFixedWidth(340)

        self.panel_scanner = PanelScanner(self.demo_file_path)
        self.panel_controls = PanelChartControls()

        left_tabs.addTab(self.panel_scanner, "📁 Archivo")
        left_tabs.addTab(self.panel_controls, "🎨 Gráficos")
        splitter.addWidget(left_tabs)

        # Contenedor Derecho
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)

        # Fila de 4 Tarjetas KPI
        kpi_bar = QHBoxLayout()
        kpi_bar.setSpacing(10)

        self.kpi_total = KPICard("Total Métrica", "—", "Suma acumulada", "#38bdf8")
        self.kpi_mean = KPICard("Promedio", "—", "Media por elemento", "#10b981")
        self.kpi_max = KPICard("Valor Máximo", "—", "Pico más alto", "#f59e0b")
        self.kpi_top = KPICard("Categoría Líder", "—", "Mayor contribución", "#f43f5e")

        kpi_bar.addWidget(self.kpi_total)
        kpi_bar.addWidget(self.kpi_mean)
        kpi_bar.addWidget(self.kpi_max)
        kpi_bar.addWidget(self.kpi_top)
        right_layout.addLayout(kpi_bar)

        # Pestañas Principales del Área de Trabajo
        self.work_tabs = QTabWidget()

        # Pestaña 1: Visualizador de Gráficos (Dinámico / Estático)
        self.chart_viewer = ChartViewer()
        self.work_tabs.addTab(self.chart_viewer, "📈 Visualización de Gráficos")

        # Pestaña 2: Tabla de Datos
        self.data_table = DataTableView()
        self.work_tabs.addTab(self.data_table, "📋 Vista de Datos Tabular")

        # Pestaña 3: Matriz de Correlación
        self.corr_table = DataTableView()
        self.work_tabs.addTab(self.corr_table, "🔥 Matriz de Correlación")

        right_layout.addWidget(self.work_tabs, 1)
        splitter.addWidget(right_container)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        main_layout.addWidget(splitter, 1)

        # 3. Barra de Estado
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Listo para escanear documentos de Excel.")

    def _connect_signals(self):
        """Conecta eventos entre componentes."""
        self.panel_scanner.scan_completed.connect(self._on_scan_completed)
        self.panel_controls.chart_requested.connect(self._on_chart_requested)

    def _on_scan_completed(self, scan: ScanResult):
        """Actualiza la aplicación con el resultado del escaneo."""
        self.current_scan = scan

        # Cargar tabla de datos
        self.data_table.load_dataframe(scan.df)

        # Poblar controles de gráficos
        self.panel_controls.populate_from_scan(scan)

        # Calcular y cargar matriz de correlación si hay columnas numéricas suficientes
        if len(scan.numeric_columns) >= 2:
            corr_df = DataAggregator.get_correlation_matrix(scan.df, scan.numeric_columns).reset_index()
            self.corr_table.load_dataframe(corr_df)

        self.status_bar.showMessage(
            f"Hoja '{scan.sheet_name}' cargada: {scan.total_rows:,} filas, {scan.total_cols} columnas."
        )

        # Generar gráfico inicial sugerido automáticamente
        self.panel_controls._on_render_clicked()

    def _on_chart_requested(self, params: dict):
        """Genera el gráfico según los parámetros configurados."""
        if not self.current_scan:
            return

        self.last_chart_params = params

        try:
            # 1. Transformar y agregar los datos
            agg_data = DataAggregator.process(
                df=self.current_scan.df,
                x_col=params['x_col'],
                y_col=params['y_col'],
                color_col=params['color_col'],
                agg_name=params['agg_name'],
                sort_by=params['sort_by'],
                top_n=params['top_n'],
                group_others=params['group_others']
            )
            self.current_agg_data = agg_data

            # 2. Actualizar KPIs
            self.kpi_total.set_data(f"{agg_data.kpi_total:,.2f}", f"Total {agg_data.y_cols[0]}")
            self.kpi_mean.set_data(f"{agg_data.kpi_mean:,.2f}", f"Promedio por {agg_data.x_col}")
            self.kpi_max.set_data(f"{agg_data.kpi_max:,.2f}", "Pico registrado")
            self.kpi_top.set_data(f"{agg_data.top_value:,.2f}", f"{agg_data.top_label}")

            # 3. Generar Gráfico Dinámico (HTML Plotly)
            html_content = PlotlyChartGenerator.generate_html(
                agg_data=agg_data,
                chart_type=params['chart_type'],
                palette_name=params['palette_name'],
                dark_mode=True,
                show_data_labels=params['show_data_labels'],
                show_grid=params['show_grid'],
                custom_title=params['custom_title'],
                local_plotly_path=self.local_plotly_path
            )
            self.chart_viewer.load_dynamic_html(html_content, base_url=self.local_plotly_path or "")

            # 4. Generar Gráfico Estático (Matplotlib)
            fig = MatplotlibChartGenerator.create_figure(
                agg_data=agg_data,
                chart_type=params['chart_type'],
                palette_name=params['palette_name'],
                dark_mode=True,
                show_data_labels=params['show_data_labels'],
                show_grid=params['show_grid'],
                custom_title=params['custom_title']
            )
            self.chart_viewer.load_static_figure(fig)

            self.status_bar.showMessage(
                f"Gráfico '{params['chart_type']}' generado exitosamente ({len(agg_data.categories)} categorías procesadas)."
            )

        except Exception as e:
            QMessageBox.critical(self, "Error al Generar Gráfico", f"No se pudo crear el gráfico:\n{str(e)}")

    def _on_export_dialog(self):
        """Abre el diálogo modal de exportación a Excel."""
        if not self.current_agg_data:
            QMessageBox.warning(self, "Aviso", "Primero debe cargar un archivo y generar un gráfico para exportar.")
            return

        dialog = ExportExcelDialog(
            agg_data=self.current_agg_data,
            chart_params=self.last_chart_params,
            source_df=self.current_scan.df if self.current_scan else None,
            parent=self
        )
        dialog.exec_()
