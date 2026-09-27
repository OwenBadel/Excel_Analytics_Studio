"""
Widget de Tabla de Datos con Filtro de Búsqueda y Paginación Eficiente
PROJ-008: Excel Analytics Studio
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt
import pandas as pd


class DataTableView(QWidget):
    """Visualizador tabular de datos con búsqueda en tiempo real."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.df: pd.DataFrame = pd.DataFrame()
        self.filtered_indices = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Barra superior con búsqueda y conteo
        top_bar = QHBoxLayout()
        top_bar.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Filtrar registros por cualquier campo...")
        self.search_input.textChanged.connect(self._on_search)

        self.count_label = QLabel("0 registros")
        self.count_label.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: 500;")

        top_bar.addWidget(self.search_input, 1)
        top_bar.addWidget(self.count_label)
        layout.addLayout(top_bar)

        # Tabla
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setDefaultSectionSize(26)
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table)

    def load_dataframe(self, df: pd.DataFrame):
        """Carga un DataFrame en la tabla limitando la vista previa a las primeras 500 filas."""
        self.df = df
        self.search_input.clear()
        self._populate_table(self.df)

    def _populate_table(self, target_df: pd.DataFrame):
        self.table.setSortingEnabled(False)
        self.table.clear()

        if target_df.empty:
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            self.count_label.setText("0 registros")
            return

        cols = list(target_df.columns)
        self.table.setColumnCount(len(cols))
        self.table.setHorizontalHeaderLabels(cols)

        # Máximo 500 filas en UI para no degradar rendimiento
        display_df = target_df.head(500)
        num_rows = len(display_df)
        self.table.setRowCount(num_rows)

        for r_idx in range(num_rows):
            for c_idx, col in enumerate(cols):
                val = display_df.iloc[r_idx, c_idx]
                val_str = "" if pd.isna(val) else str(val)
                item = QTableWidgetItem(val_str)
                # Alinear a la derecha si es numérico
                if isinstance(val, (int, float)) and not pd.isna(val):
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                else:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.table.setItem(r_idx, c_idx, item)

        self.table.setSortingEnabled(True)

        if len(target_df) > 500:
            self.count_label.setText(f"Mostrando primeros 500 de {len(target_df):,} registros")
        else:
            self.count_label.setText(f"{len(target_df):,} registros")

    def _on_search(self, query: str):
        """Filtra el dataframe en tiempo real."""
        if self.df.empty:
            return

        query = query.strip().lower()
        if not query:
            self._populate_table(self.df)
            return

        # Búsqueda vectorial
        mask = self.df.astype(str).apply(lambda col: col.str.lower().str.contains(query, regex=False)).any(axis=1)
        filtered = self.df[mask]
        self._populate_table(filtered)
