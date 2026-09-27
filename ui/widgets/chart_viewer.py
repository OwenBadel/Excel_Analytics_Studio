"""
Visor Híbrido de Gráficos: Pestaña Dinámica Interactiva y Pestaña Estática HD
PROJ-008: Excel Analytics Studio
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QPushButton,
    QFileDialog, QMessageBox, QLabel
)
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import os


class ChartViewer(QWidget):
    """Visor combinado de gráficos interactivos y estáticos vectoriales."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_fig: Figure = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # Barra de utilidades
        top_bar = QHBoxLayout()
        top_bar.setSpacing(8)

        self.info_label = QLabel("Visualizador de Gráficos")
        self.info_label.setStyleSheet("font-weight: 600; color: #cbd5e1; font-size: 12px;")
        top_bar.addWidget(self.info_label)
        top_bar.addStretch()

        self.btn_save_img = QPushButton("💾 Guardar Imagen (PNG)")
        self.btn_save_img.clicked.connect(self._on_save_image)
        top_bar.addWidget(self.btn_save_img)

        layout.addLayout(top_bar)

        # Pestañas: Dinámico / Estático
        self.tabs = QTabWidget()

        # Pestaña 1: Dinámico (WebEngine con Plotly)
        self.web_view = QWebEngineView()
        self.web_view.setStyleSheet("background-color: #0b0f19;")
        
        # Habilitar acceso a recursos locales en QtWebEngine
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        
        self.tabs.addTab(self.web_view, "🌐 Gráfico Dinámico (Interactivo)")

        # Pestaña 2: Estático (Matplotlib Canvas)
        self.canvas_container = QWidget()
        self.canvas_layout = QVBoxLayout(self.canvas_container)
        self.canvas_layout.setContentsMargins(0, 0, 0, 0)
        self.canvas = None
        self.tabs.addTab(self.canvas_container, "📐 Gráfico Estático (Vectorial HD)")

        layout.addWidget(self.tabs, 1)

    def load_dynamic_html(self, html_content: str, base_url: str = ""):
        """Carga el gráfico dinámico en el motor web."""
        if base_url and os.path.exists(base_url):
            if os.path.isfile(base_url):
                dir_path = os.path.dirname(base_url)
                self.web_view.setHtml(html_content, QUrl.fromLocalFile(dir_path + "/"))
            else:
                self.web_view.setHtml(html_content, QUrl.fromLocalFile(base_url))
        else:
            self.web_view.setHtml(html_content)

    def load_static_figure(self, fig: Figure):
        """Carga la figura estática de Matplotlib."""
        self.current_fig = fig

        # Limpiar canvas anterior
        if self.canvas:
            self.canvas_layout.removeWidget(self.canvas)
            self.canvas.deleteLater()
            self.canvas = None

        self.canvas = FigureCanvasQTAgg(fig)
        self.canvas_layout.addWidget(self.canvas)
        self.canvas.draw()

    def _on_save_image(self):
        """Guarda la figura actual en archivo PNG de alta resolución."""
        if not self.current_fig:
            QMessageBox.warning(self, "Aviso", "No hay ningún gráfico generado para exportar.")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Gráfico como Imagen",
            "grafico_analisis.png",
            "Imágenes PNG (*.png);;Imágenes JPEG (*.jpg);;Gráficos SVG (*.svg);;Documentos PDF (*.pdf)"
        )

        if filepath:
            try:
                self.current_fig.savefig(filepath, dpi=300, bbox_inches='tight')
                QMessageBox.information(self, "Exportación Exitosa", f"Gráfico guardado correctamente en:\n{filepath}")
            except Exception as e:
                QMessageBox.critical(self, "Error al Exportar", f"Ocurrió un error al guardar la imagen:\n{str(e)}")
