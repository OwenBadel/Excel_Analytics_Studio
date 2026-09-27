"""
Punto de Entrada Principal de Excel Analytics Studio
PROJ-008: Excel Analytics Studio
"""
import sys
import os

# Establecer la raíz del proyecto en sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Importar QtWebEngine antes de QApplication (requisito estricto de Qt)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow


def load_stylesheet(app: QApplication):
    """Carga y aplica la hoja de estilos moderna ejecutiva."""
    qss_path = os.path.join(PROJECT_ROOT, "assets", "style.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())


def main():
    """Inicializa y arranca la aplicación de escritorio."""
    # Configurar atributos de OpenGL y alta densidad DPI
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("Excel Analytics Studio")
    app.setOrganizationName("Lemon Fábrica de Software")

    # Aplicar estilos
    load_stylesheet(app)

    # Rutas de recursos
    demo_path = os.path.join(PROJECT_ROOT, "assets", "demo_ventas.xlsx")
    plotly_path = os.path.join(PROJECT_ROOT, "assets", "plotly.min.js")

    # Instanciar y mostrar ventana principal
    window = MainWindow(demo_file_path=demo_path, local_plotly_path=plotly_path)
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
