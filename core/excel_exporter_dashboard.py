"""
Módulo de Exportación de Dashboard Ejecutivo a Excel con Gráficos HD e Indicadores KPI
PROJ-008: Excel Analytics Studio
"""
from typing import Optional, List, Dict, Any
import os
import tempfile
import xlsxwriter
import pandas as pd
import numpy as np
from core.data_aggregator import AggregatedData
from core.chart_generator_matplotlib import MatplotlibChartGenerator


class ExecutiveDashboardExporter:
    """Generador de Informes Ejecutivos Profesionales con KPIs y Gráficos HD."""

    @classmethod
    def export(
        cls,
        agg_data: AggregatedData,
        output_filepath: str,
        chart_type: str = 'Barras Verticales',
        palette_name: str = 'Sapphire Corporativo',
        custom_title: Optional[str] = None,
        source_df: Optional[pd.DataFrame] = None
    ) -> str:
        """Genera un archivo Excel con portada ejecutiva, tarjetas KPI e imagen HD."""
        # 1. Generar la imagen del gráfico en alta resolución
        fig = MatplotlibChartGenerator.create_figure(
            agg_data=agg_data,
            chart_type=chart_type,
            palette_name=palette_name,
            dark_mode=False,  # Tema claro para coincidir con la hoja de Excel
            show_data_labels=True,
            show_grid=True,
            custom_title=custom_title
        )

        temp_img = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        temp_img_path = temp_img.name
        temp_img.close()

        fig.savefig(temp_img_path, dpi=220, bbox_inches='tight', facecolor='#ffffff')

        # 2. Construir el libro con XlsxWriter
        wb = xlsxwriter.Workbook(output_filepath)

        # Formatos ejecutivos de celda
        fmt_banner = wb.add_format({
            'bold': True,
            'font_size': 18,
            'font_color': '#ffffff',
            'bg_color': '#0f172a',
            'font_name': 'Segoe UI',
            'valign': 'vcenter',
            'indent': 1
        })
        fmt_kpi_card = wb.add_format({
            'bg_color': '#f8fafc',
            'border': 1,
            'border_color': '#cbd5e1',
            'align': 'center',
            'valign': 'vcenter',
            'font_name': 'Segoe UI'
        })
        fmt_kpi_title = wb.add_format({
            'font_size': 9,
            'font_color': '#64748b',
            'bold': True,
            'align': 'center',
            'bg_color': '#f8fafc',
            'font_name': 'Segoe UI'
        })
        fmt_kpi_val = wb.add_format({
            'font_size': 16,
            'font_color': '#0284c7',
            'bold': True,
            'align': 'center',
            'bg_color': '#f8fafc',
            'font_name': 'Segoe UI',
            'num_format': '#,##0.00'
        })
        fmt_header = wb.add_format({
            'bold': True,
            'font_color': '#ffffff',
            'bg_color': '#1e293b',
            'border': 1,
            'border_color': '#475569',
            'align': 'center',
            'valign': 'vcenter',
            'font_name': 'Segoe UI',
            'font_size': 10
        })
        fmt_cell = wb.add_format({
            'border': 1,
            'border_color': '#e2e8f0',
            'font_name': 'Segoe UI',
            'font_size': 10
        })
        fmt_num = wb.add_format({
            'border': 1,
            'border_color': '#e2e8f0',
            'num_format': '#,##0.00',
            'font_name': 'Segoe UI',
            'font_size': 10
        })

        ws = wb.add_worksheet('Dashboard_Ejecutivo')
        ws.hide_gridlines(0)

        # Ancho de columnas para layout pro
        ws.set_column('A:A', 3)
        ws.set_column('B:B', 20)
        ws.set_column('C:E', 15)
        ws.set_column('F:F', 3)
        ws.set_column('G:P', 12)

        # Banner Superior
        ws.set_row(1, 40)
        title_text = custom_title or f"TABLERO EJECUTIVO: {agg_data.y_cols[0].upper()}"
        ws.merge_range('B2:N2', f"  {title_text}", fmt_banner)

        # 4 Tarjetas KPI en fila 4 y 5
        kpis = [
            ("TOTAL REGISTRADO", agg_data.kpi_total, '#0284c7'),
            ("PROMEDIO ESTIMADO", agg_data.kpi_mean, '#10b981'),
            ("VALOR MÁXIMO", agg_data.kpi_max, '#8b5cf6'),
            ("LÍDER PRINCIPAL", agg_data.top_value, '#f43f5e')
        ]

        card_ranges = [('B4:C4', 'B5:C5'), ('D4:E4', 'D5:E5'), ('G4:H4', 'G5:H5'), ('I4:J4', 'I5:J5')]
        for idx, (k_title, k_val, _) in enumerate(kpis):
            r_title, r_val = card_ranges[idx]
            ws.merge_range(r_title, k_title, fmt_kpi_title)
            if idx == 3:
                # Mostrar nombre líder + valor
                ws.merge_range(r_val, f"{agg_data.top_label} ({k_val:,.0f})", fmt_kpi_val)
            else:
                ws.merge_range(r_val, k_val, fmt_kpi_val)

        # Tabla de Datos (Columna B a E)
        start_row = 7
        ws.write(start_row, 1, agg_data.x_col, fmt_header)
        series_names = list(agg_data.series_dict.keys())
        for idx, s_name in enumerate(series_names):
            ws.write(start_row, 2 + idx, s_name, fmt_header)

        for r_idx, cat in enumerate(agg_data.categories):
            current_row = start_row + 1 + r_idx
            ws.write(current_row, 1, cat, fmt_cell)
            for c_idx, s_name in enumerate(series_names):
                val = agg_data.series_dict[s_name][r_idx]
                ws.write(current_row, 2 + c_idx, val, fmt_num)

        # Insertar Gráfico HD al costado de la tabla (Columna G)
        ws.insert_image('G8', temp_img_path, {'x_scale': 0.85, 'y_scale': 0.85})

        # Hoja con los datos completos
        if source_df is not None and not source_df.empty:
            ws_src = wb.add_worksheet('Datos_Detallados')
            for col_idx, col_name in enumerate(source_df.columns):
                ws_src.write(0, col_idx, str(col_name), fmt_header)
                ws_src.set_column(col_idx, col_idx, 16)
            for r_idx in range(min(len(source_df), 5000)):
                for c_idx, col_name in enumerate(source_df.columns):
                    val = source_df.iloc[r_idx, c_idx]
                    if pd.isna(val):
                        ws_src.write_blank(r_idx + 1, c_idx, None, fmt_cell)
                    elif isinstance(val, (int, float, np.number)):
                        ws_src.write_number(r_idx + 1, c_idx, float(val), fmt_num)
                    else:
                        ws_src.write_string(r_idx + 1, c_idx, str(val), fmt_cell)

        wb.close()

        # Limpiar archivo temporal de imagen
        try:
            if os.path.exists(temp_img_path):
                os.remove(temp_img_path)
        except Exception:
            pass

        return output_filepath
