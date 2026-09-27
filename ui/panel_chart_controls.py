"""
Panel de Controles y Configuración de Gráficos
PROJ-008: Excel Analytics Studio
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QCheckBox, QSpinBox, QLineEdit, QPushButton, QFrame,
    QScrollArea
)
from PyQt5.QtCore import pyqtSignal, Qt
from core.excel_scanner import ScanResult
from core.chart_generator_plotly import PALETTES


class PanelChartControls(QFrame):
    """Panel para selección de dimensiones, métricas, paletas y estilo de gráficos."""

    # Señal emitida cuando el usuario solicita graficar
    chart_requested = pyqtSignal(dict)

    CHART_TYPES = [
        "Barras Verticales",
        "Barras Horizontales",
        "Barras Apiladas",
        "Líneas y Tendencia",
        "Áreas",
        "Pastel",
        "Dona",
        "Dispersión (Scatter)",
        "Histograma",
        "Diagrama de Caja (Box)"
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebarCard")
        self.current_scan: ScanResult = None

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 1. Tipo de Gráfico
        t1 = QLabel("📈 TIPO DE GRÁFICO")
        t1.setObjectName("sectionTitle")
        layout.addWidget(t1)

        self.combo_chart_type = QComboBox()
        self.combo_chart_type.addItems(self.CHART_TYPES)
        layout.addWidget(self.combo_chart_type)

        # 2. Ejes y Variables
        t2 = QLabel("🎯 VARIABLES Y EJES")
        t2.setObjectName("sectionTitle")
        layout.addWidget(t2)

        lbl_x = QLabel("Eje X (Categoría / Fecha):")
        lbl_x.setStyleSheet("font-size: 11px; color: #cbd5e1;")
        layout.addWidget(lbl_x)
        self.combo_x = QComboBox()
        layout.addWidget(self.combo_x)

        lbl_y = QLabel("Eje Y (Métrica / Valor):")
        lbl_y.setStyleSheet("font-size: 11px; color: #cbd5e1;")
        layout.addWidget(lbl_y)
        self.combo_y = QComboBox()
        layout.addWidget(self.combo_y)

        lbl_color = QLabel("Desglose Secundario (Opcional):")
        lbl_color.setStyleSheet("font-size: 11px; color: #cbd5e1;")
        layout.addWidget(lbl_color)
        self.combo_color = QComboBox()
        layout.addWidget(self.combo_color)

        # 3. Agregación y Ordenamiento
        t3 = QLabel("⚙️ AGREGACIÓN Y FILTROS")
        t3.setObjectName("sectionTitle")
        layout.addWidget(t3)

        lbl_agg = QLabel("Función de Agregación:")
        lbl_agg.setStyleSheet("font-size: 11px; color: #cbd5e1;")
        layout.addWidget(lbl_agg)
        self.combo_agg = QComboBox()
        self.combo_agg.addItems(["Suma", "Promedio", "Conteo", "Mediana", "Máximo", "Mínimo", "Sin Agrupar"])
        layout.addWidget(self.combo_agg)

        lbl_sort = QLabel("Orden de Datos:")
        lbl_sort.setStyleSheet("font-size: 11px; color: #cbd5e1;")
        layout.addWidget(lbl_sort)
        self.combo_sort = QComboBox()
        self.combo_sort.addItem("Mayor a Menor (Valor)", "value_desc")
        self.combo_sort.addItem("Menor a Mayor (Valor)", "value_asc")
        self.combo_sort.addItem("Alfabético (A-Z)", "label_asc")
        self.combo_sort.addItem("Alfabético (Z-A)", "label_desc")
        layout.addWidget(self.combo_sort)

        # Top N
        top_layout = QHBoxLayout()
        self.chk_top_n = QCheckBox("Top:")
        self.chk_top_n.toggled.connect(self._on_top_n_toggled)
        self.spin_top_n = QSpinBox()
        self.spin_top_n.setRange(3, 100)
        self.spin_top_n.setValue(10)
        self.spin_top_n.setEnabled(False)
        top_layout.addWidget(self.chk_top_n)
        top_layout.addWidget(self.spin_top_n)
        layout.addLayout(top_layout)

        self.chk_group_others = QCheckBox("Agrupar resto en 'Otros'")
        self.chk_group_others.setEnabled(False)
        layout.addWidget(self.chk_group_others)

        # 4. Personalización Visual
        t4 = QLabel("🎨 DISEÑO Y PALETA")
        t4.setObjectName("sectionTitle")
        layout.addWidget(t4)

        lbl_palette = QLabel("Paleta de Color:")
        lbl_palette.setStyleSheet("font-size: 11px; color: #cbd5e1;")
        layout.addWidget(lbl_palette)
        self.combo_palette = QComboBox()
        self.combo_palette.addItems(list(PALETTES.keys()))
        layout.addWidget(self.combo_palette)

        lbl_title = QLabel("Título Personalizado (Opcional):")
        lbl_title.setStyleSheet("font-size: 11px; color: #cbd5e1;")
        layout.addWidget(lbl_title)
        self.input_title = QLineEdit()
        self.input_title.setPlaceholderText("Ej: Ventas Totales por Región")
        layout.addWidget(self.input_title)

        self.chk_data_labels = QCheckBox("Mostrar valores sobre las barras/puntos")
        self.chk_data_labels.setChecked(True)
        layout.addWidget(self.chk_data_labels)

        self.chk_grid = QCheckBox("Mostrar cuadrícula")
        self.chk_grid.setChecked(True)
        layout.addWidget(self.chk_grid)

        # Botón de Generar Gráfico
        self.btn_render = QPushButton("✨ Actualizar Gráfico")
        self.btn_render.setObjectName("primaryButton")
        self.btn_render.setCursor(Qt.PointingHandCursor)
        self.btn_render.clicked.connect(self._on_render_clicked)
        layout.addWidget(self.btn_render)

        scroll.setWidget(container)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def _on_top_n_toggled(self, checked: bool):
        self.spin_top_n.setEnabled(checked)
        self.chk_group_others.setEnabled(checked)

    def populate_from_scan(self, scan: ScanResult):
        """Rellena los combos de columnas con base en el escaneo."""
        self.current_scan = scan

        all_cols = [c.name for c in scan.columns]
        num_cols = scan.numeric_columns
        cat_cols = scan.categorical_columns + scan.temporal_columns

        # Poblar X
        self.combo_x.clear()
        # Colocar primero las categóricas/fechas
        x_prioritized = cat_cols + [c for c in all_cols if c not in cat_cols]
        self.combo_x.addItems(x_prioritized)

        # Poblar Y
        self.combo_y.clear()
        # Colocar primero las numéricas
        y_prioritized = num_cols + [c for c in all_cols if c not in num_cols]
        self.combo_y.addItems(y_prioritized)

        # Poblar Desglose Color
        self.combo_color.clear()
        self.combo_color.addItem("(Ninguno)")
        self.combo_color.addItems(cat_cols)

        # Valores sugeridos inteligentes
        if cat_cols:
            self.combo_x.setCurrentText(cat_cols[0])
        if num_cols:
            self.combo_y.setCurrentText(num_cols[0])

    def _on_render_clicked(self):
        """Empaqueta la configuración y emite la señal."""
        if not self.current_scan:
            return

        x_col = self.combo_x.currentText()
        y_col = self.combo_y.currentText()
        color_col = self.combo_color.currentText()
        if color_col == "(Ninguno)":
            color_col = None

        sort_by = self.combo_sort.currentData() or "value_desc"
        top_n = self.spin_top_n.value() if self.chk_top_n.isChecked() else None

        params = {
            'chart_type': self.combo_chart_type.currentText(),
            'x_col': x_col,
            'y_col': y_col,
            'color_col': color_col,
            'agg_name': self.combo_agg.currentText(),
            'sort_by': sort_by,
            'top_n': top_n,
            'group_others': self.chk_group_others.isChecked(),
            'palette_name': self.combo_palette.currentText(),
            'custom_title': self.input_title.text().strip() or None,
            'show_data_labels': self.chk_data_labels.isChecked(),
            'show_grid': self.chk_grid.isChecked()
        }

        self.chart_requested.emit(params)
