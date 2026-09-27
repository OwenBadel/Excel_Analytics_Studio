"""
Suite de Pruebas Automatizadas de Calidad
PROJ-008: Excel Analytics Studio
"""
import os
import sys
import tempfile
import unittest
import pandas as pd

# Añadir raíz del proyecto a sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.excel_scanner import ExcelScanner
from core.data_aggregator import DataAggregator
from core.chart_generator_plotly import PlotlyChartGenerator
from core.chart_generator_matplotlib import MatplotlibChartGenerator
from core.excel_exporter_native import NativeExcelExporter
from core.excel_exporter_dashboard import ExecutiveDashboardExporter


class TestExcelAnalyticsStudio(unittest.TestCase):
    """Pruebas unitarias y de integración de los motores principales."""

    @classmethod
    def setUpClass(cls):
        cls.demo_path = os.path.join(PROJECT_ROOT, "assets", "demo_ventas.xlsx")
        cls.plotly_path = os.path.join(PROJECT_ROOT, "assets", "plotly.min.js")
        assert os.path.exists(cls.demo_path), "El archivo demo_ventas.xlsx no existe."

    def test_01_scanner(self):
        """Valida que el escáner detecte hojas, columnas y tipos correctamente."""
        sheets = ExcelScanner.get_sheet_names(self.demo_path)
        self.assertGreater(len(sheets), 0)

        scan = ExcelScanner.scan_file(self.demo_path)
        self.assertEqual(scan.total_rows, 150)
        self.assertGreater(len(scan.numeric_columns), 0)
        self.assertGreater(len(scan.categorical_columns), 0)
        self.assertIn('Ventas_Totales', scan.numeric_columns)
        self.assertIn('Categoría', scan.categorical_columns)
        print(" -> Test 01 Scanner: PASADO")

    def test_02_aggregator(self):
        """Valida las funciones de agregación y filtros."""
        scan = ExcelScanner.scan_file(self.demo_path)
        agg = DataAggregator.process(
            df=scan.df,
            x_col='Categoría',
            y_col='Ventas_Totales',
            agg_name='Suma',
            sort_by='value_desc'
        )
        self.assertGreater(len(agg.categories), 0)
        self.assertGreater(agg.kpi_total, 0)
        self.assertGreater(agg.kpi_mean, 0)

        # Probar con Top 2
        agg_top = DataAggregator.process(
            df=scan.df,
            x_col='Categoría',
            y_col='Ventas_Totales',
            agg_name='Suma',
            top_n=2,
            group_others=True
        )
        self.assertEqual(len(agg_top.categories), 3)  # 2 + 'Otros'
        print(" -> Test 02 Aggregator: PASADO")

    def test_03_plotly_html(self):
        """Valida que el generador Plotly produzca HTML válido para todos los tipos."""
        scan = ExcelScanner.scan_file(self.demo_path)
        agg = DataAggregator.process(scan.df, 'Categoría', 'Ventas_Totales', agg_name='Suma')

        chart_types = [
            "Barras Verticales", "Barras Horizontales", "Barras Apiladas",
            "Líneas y Tendencia", "Áreas", "Pastel", "Dona",
            "Dispersión (Scatter)", "Histograma", "Diagrama de Caja (Box)"
        ]

        for c_type in chart_types:
            html = PlotlyChartGenerator.generate_html(
                agg_data=agg,
                chart_type=c_type,
                palette_name='Sapphire Corporativo',
                local_plotly_path=self.plotly_path
            )
            self.assertIn("<html", html.lower())
            self.assertIn("plotly", html.lower())

        print(" -> Test 03 Plotly HTML: PASADO")

    def test_04_matplotlib_figure(self):
        """Valida que Matplotlib genere figuras y permita exportación PNG."""
        scan = ExcelScanner.scan_file(self.demo_path)
        agg = DataAggregator.process(scan.df, 'Categoría', 'Ventas_Totales', agg_name='Suma')

        fig = MatplotlibChartGenerator.create_figure(
            agg_data=agg,
            chart_type='Barras Verticales',
            palette_name='Emerald Financiero'
        )
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp_path = tmp.name

        MatplotlibChartGenerator.export_image(fig, tmp_path)
        self.assertTrue(os.path.exists(tmp_path))
        self.assertGreater(os.path.getsize(tmp_path), 1000)
        os.remove(tmp_path)
        print(" -> Test 04 Matplotlib Export: PASADO")

    def test_05_native_excel_export(self):
        """Valida la generación de archivos Excel con gráficos NATIVOS dinámicos."""
        scan = ExcelScanner.scan_file(self.demo_path)
        agg = DataAggregator.process(scan.df, 'Categoría', 'Ventas_Totales', agg_name='Suma')

        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            out_excel = tmp.name

        NativeExcelExporter.export(
            agg_data=agg,
            output_filepath=out_excel,
            chart_type='Barras Verticales',
            palette_name='Sapphire Corporativo',
            include_source_data=True,
            source_df=scan.df
        )

        self.assertTrue(os.path.exists(out_excel))
        self.assertGreater(os.path.getsize(out_excel), 5000)

        # Validar lectura con pandas/openpyxl
        df_read = pd.read_excel(out_excel, sheet_name='Reporte_Grafico')
        self.assertGreater(len(df_read), 0)

        os.remove(out_excel)
        print(" -> Test 05 Native Excel Export: PASADO")

    def test_06_dashboard_excel_export(self):
        """Valida la generación del Dashboard Ejecutivo en Excel con gráficos HD."""
        scan = ExcelScanner.scan_file(self.demo_path)
        agg = DataAggregator.process(scan.df, 'Categoría', 'Ventas_Totales', agg_name='Suma')

        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            out_excel = tmp.name

        ExecutiveDashboardExporter.export(
            agg_data=agg,
            output_filepath=out_excel,
            chart_type='Barras Verticales',
            palette_name='Sunset Atardecer',
            source_df=scan.df
        )

        self.assertTrue(os.path.exists(out_excel))
        self.assertGreater(os.path.getsize(out_excel), 10000)

        os.remove(out_excel)
        print(" -> Test 06 Dashboard Excel Export: PASADO")


if __name__ == '__main__':
    unittest.main()
