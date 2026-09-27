"""
Prueba de Integración de la Interfaz Gráfica (PyQt5) con Captura de Consola JavaScript
PROJ-008: Excel Analytics Studio
"""
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtCore import Qt, QCoreApplication, QTimer
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow

errors_detected = []

class CustomWebPage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, msg, line, source):
        print(f"  [JS Console {level}]: {msg} (line {line})")
        if "Uncaught" in msg or "ReferenceError" in msg or "SyntaxError" in msg:
            errors_detected.append(msg)

def test_gui_run():
    print("Iniciando prueba de GUI y consola JS...")
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    demo_path = os.path.join(PROJECT_ROOT, "assets", "demo_ventas.xlsx")
    plotly_path = os.path.join(PROJECT_ROOT, "assets", "plotly.min.js")

    window = MainWindow(demo_file_path=demo_path, local_plotly_path=plotly_path)
    
    # Interceptar consola JS
    custom_page = CustomWebPage(window.chart_viewer.web_view)
    window.chart_viewer.web_view.setPage(custom_page)
    
    window.show()

    # Recargar gráfico para que se renderice en la página con listener
    window.panel_controls._on_render_clicked()

    # Probar cambio de tipo a Líneas
    window.panel_controls.combo_chart_type.setCurrentText("Líneas y Tendencia")
    window.panel_controls._on_render_clicked()

    def check_and_exit():
        window.close()
        app.quit()
        if errors_detected:
            print(f"FAILED: Se detectaron {len(errors_detected)} errores JS: {errors_detected}")
            sys.exit(1)
        else:
            print("SUCCESS: 0 errores JS en la consola de QtWebEngine.")

    QTimer.singleShot(2500, check_and_exit)
    app.exec_()

if __name__ == "__main__":
    test_gui_run()
