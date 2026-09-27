"""
Excel Analytics Studio - Core Engine
"""
from core.excel_scanner import ExcelScanner, ScanResult, ColumnInfo
from core.data_aggregator import DataAggregator, AggregatedData
from core.chart_generator_plotly import PlotlyChartGenerator, PALETTES
from core.chart_generator_matplotlib import MatplotlibChartGenerator
from core.excel_exporter_native import NativeExcelExporter
from core.excel_exporter_dashboard import ExecutiveDashboardExporter

__all__ = [
    'ExcelScanner',
    'ScanResult',
    'ColumnInfo',
    'DataAggregator',
    'AggregatedData',
    'PlotlyChartGenerator',
    'MatplotlibChartGenerator',
    'NativeExcelExporter',
    'ExecutiveDashboardExporter',
    'PALETTES'
]
