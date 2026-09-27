"""
Widget de Tarjeta KPI para Métricas Clave
PROJ-008: Excel Analytics Studio
"""
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt


class KPICard(QFrame):
    """Tarjeta de indicador clave de rendimiento."""

    def __init__(self, title: str, value: str = "—", subtitle: str = "", accent_color: str = "#38bdf8", parent=None):
        super().__init__(parent)
        self.setObjectName("kpiCard")
        self.accent_color = accent_color

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(4)

        self.title_label = QLabel(title.upper())
        self.title_label.setObjectName("subText")
        self.title_label.setStyleSheet("font-size: 10px; font-weight: 700; color: #94a3b8; letter-spacing: 0.5px;")

        self.val_label = QLabel(value)
        self.val_label.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {self.accent_color};")

        self.sub_label = QLabel(subtitle)
        self.sub_label.setObjectName("subText")
        self.sub_label.setStyleSheet("font-size: 11px; color: #64748b;")

        layout.addWidget(self.title_label)
        layout.addWidget(self.val_label)
        layout.addWidget(self.sub_label)

    def set_data(self, value: str, subtitle: str = ""):
        """Actualiza los datos de la tarjeta con formato."""
        self.val_label.setText(value)
        if subtitle:
            self.sub_label.setText(subtitle)
