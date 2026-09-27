"""
Módulo de Exportación a Excel con Gráficos NATIVOS Dinámicos
PROJ-008: Excel Analytics Studio
"""
from typing import Optional, List, Dict, Any
import os
import xlsxwriter
import pandas as pd
import numpy as np
from core.data_aggregator import AggregatedData
from core.chart_generator_plotly import PALETTES


CHART_TYPE_MAP = {
    'Barras Verticales': 'column',
    'Barras Horizontales': 'bar',
    'Barras Apiladas': 'column',
    'Líneas y Tendencia': 'line',
    'Áreas': 'area',
    'Pastel': 'pie',
    'Dona': 'doughnut',
    'Dispersión (Scatter)': 'scatter'
}


class NativeExcelExporter:
    """Generador de libros Excel con gráficos nativos dinámicos de Microsoft Excel."""

    @classmethod
    def export(
        cls,
        agg_data: AggregatedData,
        output_filepath: str,
        chart_type: str = 'Barras Verticales',
        palette_name: str = 'Sapphire Corporativo',
        custom_title: Optional[str] = None,
        include_source_data: bool = True,
        source_df: Optional[pd.DataFrame] = None
    ) -> str:
        """
        Crea un nuevo archivo Excel con hoja de datos formateada y gráfico nativo incrustado.
        """
        palette = PALETTES.get(palette_name, PALETTES['Sapphire Corporativo'])
        wb = xlsxwriter.Workbook(output_filepath)

        # Formatos ejecutivos
        fmt_header = wb.add_format({
            'bold': True,
            'font_color': '#ffffff',
            'bg_color': '#0f172a',
            'border': 1,
            'border_color': '#334155',
            'align': 'center',
            'valign': 'vcenter',
            'font_name': 'Segoe UI',
            'font_size': 11
        })
        fmt_category = wb.add_format({
            'border': 1,
            'border_color': '#cbd5e1',
            'font_name': 'Segoe UI',
            'font_size': 10
        })
        fmt_number = wb.add_format({
            'border': 1,
            'border_color': '#cbd5e1',
            'num_format': '#,##0.00',
            'font_name': 'Segoe UI',
            'font_size': 10
        })
        fmt_title = wb.add_format({
            'bold': True,
            'font_size': 16,
            'font_color': '#0f172a',
            'font_name': 'Segoe UI'
        })
        fmt_subtitle = wb.add_format({
            'italic': True,
            'font_size': 10,
            'font_color': '#64748b',
            'font_name': 'Segoe UI'
        })

        # Hoja principal: Reporte y Gráfico
        ws_report = wb.add_worksheet('Reporte_Grafico')
        ws_report.hide_gridlines(0)  # Mostrar cuadrícula limpia

        title_text = custom_title or f"Análisis de {agg_data.y_cols[0]} por {agg_data.x_col}"
        ws_report.write('B2', title_text, fmt_title)
        ws_report.write('B3', f"Función de agregación: {agg_data.agg_func} | Generado por Excel Analytics Studio", fmt_subtitle)

        # Escribir tabla de datos agregados
        start_row = 5
        start_col = 1  # Columna B

        # Cabecera
        ws_report.write(start_row, start_col, agg_data.x_col, fmt_header)
        series_names = list(agg_data.series_dict.keys())
        for idx, s_name in enumerate(series_names):
            ws_report.write(start_row, start_col + 1 + idx, s_name, fmt_header)

        # Filas de datos
        num_rows = len(agg_data.categories)
        for r_idx, cat in enumerate(agg_data.categories):
            row_num = start_row + 1 + r_idx
            ws_report.write(row_num, start_col, cat, fmt_category)
            for c_idx, s_name in enumerate(series_names):
                val = agg_data.series_dict[s_name][r_idx]
                ws_report.write(row_num, start_col + 1 + c_idx, val, fmt_number)

        # Ajuste de ancho de columnas
        ws_report.set_column(start_col, start_col, 22)
        for idx in range(len(series_names)):
            ws_report.set_column(start_col + 1 + idx, start_col + 1 + idx, 16)

        # Crear Gráfico Nativo
        native_type = CHART_TYPE_MAP.get(chart_type, 'column')
        chart_subtype = 'stacked' if chart_type == 'Barras Apiladas' else None

        chart_options = {'type': native_type}
        if chart_subtype:
            chart_options['subtype'] = chart_subtype
        chart = wb.add_chart(chart_options)

        # Rango de categorías: =Reporte_Grafico!$B$7:$B$N
        cat_range = [ws_report.get_name(), start_row + 1, start_col, start_row + num_rows, start_col]

        for idx, s_name in enumerate(series_names):
            val_col = start_col + 1 + idx
            val_range = [ws_report.get_name(), start_row + 1, val_col, start_row + num_rows, val_col]
            series_opts = {
                'name': ['Reporte_Grafico', start_row, val_col],
                'categories': cat_range,
                'values': val_range,
            }
            # Asignar color corporativo si la paleta está disponible
            color_hex = palette[idx % len(palette)]
            series_opts['line'] = {'color': color_hex}
            series_opts['fill'] = {'color': color_hex}

            chart.add_series(series_opts)

        chart.set_title({'name': title_text, 'name_font': {'name': 'Segoe UI', 'size': 12, 'bold': True}})
        if native_type not in ['pie', 'doughnut']:
            chart.set_x_axis({'name': agg_data.x_col, 'name_font': {'name': 'Segoe UI', 'size': 10}})
            chart.set_y_axis({'name': f"{agg_data.agg_func} de {agg_data.y_cols[0]}", 'name_font': {'name': 'Segoe UI', 'size': 10}, 'major_gridlines': {'visible': True, 'line': {'color': '#e2e8f0'}}})

        chart.set_size({'width': 640, 'height': 380})
        chart.set_style(10)

        # Insertar gráfico a la derecha de la tabla
        chart_col_letter = chr(ord('B') + len(series_names) + 2)
        ws_report.insert_chart(f"{chart_col_letter}6", chart)

        # Hoja de datos fuente (opcional)
        if include_source_data and source_df is not None and not source_df.empty:
            ws_source = wb.add_worksheet('Datos_Originales')
            # Escribir encabezados
            for col_idx, col_name in enumerate(source_df.columns):
                ws_source.write(0, col_idx, str(col_name), fmt_header)
                ws_source.set_column(col_idx, col_idx, 15)

            # Escribir hasta 5000 filas de datos limpios
            max_rows = min(len(source_df), 5000)
            for r_idx in range(max_rows):
                for c_idx, col_name in enumerate(source_df.columns):
                    val = source_df.iloc[r_idx, c_idx]
                    if pd.isna(val):
                        ws_source.write_blank(r_idx + 1, c_idx, None, fmt_category)
                    elif isinstance(val, (int, float, np.number)):
                        ws_source.write_number(r_idx + 1, c_idx, float(val), fmt_number)
                    else:
                        ws_source.write_string(r_idx + 1, c_idx, str(val), fmt_category)

        wb.close()
        return output_filepath
