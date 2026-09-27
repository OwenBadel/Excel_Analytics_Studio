"""
Módulo de Generación de Gráficos Dinámicos e Interactivos (Plotly)
PROJ-008: Excel Analytics Studio
"""
from typing import Optional, List, Dict, Any
import os
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from core.data_aggregator import AggregatedData


PALETTES = {
    'Sapphire Corporativo': ['#0284c7', '#38bdf8', '#0369a1', '#7dd3fc', '#075985', '#bae6fd'],
    'Emerald Financiero': ['#10b981', '#34d399', '#059669', '#6ee7b7', '#047857', '#a7f3d0'],
    'Sunset Atardecer': ['#f43f5e', '#fb7185', '#e11d48', '#fb923c', '#fdba74', '#f472b6'],
    'Cyber Tecnológico': ['#8b5cf6', '#06b6d4', '#ec4899', '#f59e0b', '#3b82f6', '#10b981'],
    'Slate Ejecutivo': ['#64748b', '#94a3b8', '#475569', '#334155', '#cbd5e1', '#1e293b'],
    'Vibrante Pro': ['#2563eb', '#16a34a', '#d97706', '#dc2626', '#7c3aed', '#db2777']
}


class PlotlyChartGenerator:
    """Generador de gráficos interactivos Plotly con renderizado optimizado."""

    @classmethod
    def generate_html(
        cls,
        agg_data: AggregatedData,
        chart_type: str = 'Barras Verticales',
        palette_name: str = 'Sapphire Corporativo',
        dark_mode: bool = True,
        show_data_labels: bool = True,
        show_grid: bool = True,
        custom_title: Optional[str] = None,
        x_label: Optional[str] = None,
        y_label: Optional[str] = None,
        local_plotly_path: Optional[str] = None
    ) -> str:
        """Crea el código HTML completo interactivo."""
        palette = PALETTES.get(palette_name, PALETTES['Sapphire Corporativo'])
        fig = go.Figure()

        title_text = custom_title or f"{agg_data.y_cols[0]} por {agg_data.x_col} ({agg_data.agg_func})"
        x_axis_title = x_label or agg_data.x_col
        y_axis_title = y_label or f"{agg_data.agg_func} de {agg_data.y_cols[0]}"

        # Paleta y colores de fondo
        bg_color = "#0f172a" if dark_mode else "#ffffff"
        card_bg = "#1e293b" if dark_mode else "#f8fafc"
        text_color = "#f8fafc" if dark_mode else "#0f172a"
        grid_color = "#334155" if dark_mode else "#e2e8f0"
        font_family = "Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, sans-serif"

        # Generar según tipo de gráfico
        if chart_type == 'Barras Verticales':
            for i, (series_name, vals) in enumerate(agg_data.series_dict.items()):
                color = palette[i % len(palette)]
                text_template = '%{y:,.2f}' if show_data_labels else None
                fig.add_trace(go.Bar(
                    x=agg_data.categories,
                    y=vals,
                    name=series_name,
                    marker_color=color,
                    text=vals if show_data_labels else None,
                    textposition='outside' if show_data_labels else 'none',
                    hovertemplate='<b>%{x}</b><br>' + f'{series_name}: ' + '<b>%{y:,.2f}</b><extra></extra>'
                ))
            fig.update_layout(barmode='group')

        elif chart_type == 'Barras Horizontales':
            for i, (series_name, vals) in enumerate(agg_data.series_dict.items()):
                color = palette[i % len(palette)]
                fig.add_trace(go.Bar(
                    x=vals,
                    y=agg_data.categories,
                    name=series_name,
                    orientation='h',
                    marker_color=color,
                    text=vals if show_data_labels else None,
                    textposition='outside' if show_data_labels else 'none',
                    hovertemplate='<b>%{y}</b><br>' + f'{series_name}: ' + '<b>%{x:,.2f}</b><extra></extra>'
                ))
            fig.update_layout(barmode='group')

        elif chart_type == 'Barras Apiladas':
            for i, (series_name, vals) in enumerate(agg_data.series_dict.items()):
                color = palette[i % len(palette)]
                fig.add_trace(go.Bar(
                    x=agg_data.categories,
                    y=vals,
                    name=series_name,
                    marker_color=color,
                    hovertemplate='<b>%{x}</b><br>' + f'{series_name}: ' + '<b>%{y:,.2f}</b><extra></extra>'
                ))
            fig.update_layout(barmode='stack')

        elif chart_type == 'Líneas y Tendencia':
            for i, (series_name, vals) in enumerate(agg_data.series_dict.items()):
                color = palette[i % len(palette)]
                fig.add_trace(go.Scatter(
                    x=agg_data.categories,
                    y=vals,
                    name=series_name,
                    mode='lines+markers+text' if show_data_labels else 'lines+markers',
                    line=dict(color=color, width=3),
                    marker=dict(size=7, color=color),
                    text=vals if show_data_labels else None,
                    textposition='top center' if show_data_labels else None,
                    hovertemplate='<b>%{x}</b><br>' + f'{series_name}: ' + '<b>%{y:,.2f}</b><extra></extra>'
                ))

        elif chart_type == 'Áreas':
            for i, (series_name, vals) in enumerate(agg_data.series_dict.items()):
                color = palette[i % len(palette)]
                fig.add_trace(go.Scatter(
                    x=agg_data.categories,
                    y=vals,
                    name=series_name,
                    mode='lines',
                    fill='tozeroy',
                    line=dict(color=color, width=2),
                    hovertemplate='<b>%{x}</b><br>' + f'{series_name}: ' + '<b>%{y:,.2f}</b><extra></extra>'
                ))

        elif chart_type in ['Pastel', 'Dona']:
            first_col = list(agg_data.series_dict.keys())[0]
            vals = agg_data.series_dict[first_col]
            hole_size = 0.55 if chart_type == 'Dona' else 0.0
            fig.add_trace(go.Pie(
                labels=agg_data.categories,
                values=vals,
                hole=hole_size,
                marker=dict(colors=palette),
                textinfo='label+percent' if show_data_labels else 'percent',
                hovertemplate='<b>%{label}</b><br>Valor: <b>%{value:,.2f}</b> (%{percent})<extra></extra>'
            ))

        elif chart_type == 'Dispersión (Scatter)':
            for i, (series_name, vals) in enumerate(agg_data.series_dict.items()):
                color = palette[i % len(palette)]
                fig.add_trace(go.Scatter(
                    x=agg_data.categories,
                    y=vals,
                    name=series_name,
                    mode='markers',
                    marker=dict(size=10, color=color, opacity=0.8, line=dict(width=1, color='#ffffff')),
                    hovertemplate='<b>%{x}</b><br>' + f'{series_name}: ' + '<b>%{y:,.2f}</b><extra></extra>'
                ))

        elif chart_type == 'Histograma':
            first_col = list(agg_data.series_dict.keys())[0]
            vals = agg_data.series_dict[first_col]
            fig.add_trace(go.Histogram(
                x=vals,
                marker_color=palette[0],
                opacity=0.85,
                hovertemplate='Rango: <b>%{x}</b><br>Frecuencia: <b>%{y}</b><extra></extra>'
            ))
            x_axis_title = first_col
            y_axis_title = "Frecuencia"

        elif chart_type == 'Diagrama de Caja (Box)':
            for i, (series_name, vals) in enumerate(agg_data.series_dict.items()):
                color = palette[i % len(palette)]
                fig.add_trace(go.Box(
                    y=vals,
                    name=series_name,
                    marker_color=color,
                    boxmean=True
                ))

        # Configuración común del layout
        fig.update_layout(
            title=dict(
                text=f"<b>{title_text}</b>",
                x=0.03,
                y=0.96,
                font=dict(size=18, color=text_color, family=font_family)
            ),
            paper_bgcolor=bg_color,
            plot_bgcolor=card_bg,
            font=dict(color=text_color, family=font_family, size=12),
            xaxis=dict(
                title=dict(text=x_axis_title, font=dict(size=13, color=text_color)),
                showgrid=show_grid,
                gridcolor=grid_color,
                zeroline=False,
                tickfont=dict(color=text_color)
            ),
            yaxis=dict(
                title=dict(text=y_axis_title, font=dict(size=13, color=text_color)),
                showgrid=show_grid,
                gridcolor=grid_color,
                zeroline=False,
                tickfont=dict(color=text_color)
            ),
            margin=dict(l=60, r=40, t=70, b=60),
            legend=dict(
                bgcolor='rgba(0,0,0,0)',
                font=dict(color=text_color),
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1.0
            ),
            hovermode='closest'
        )

        # Generar HTML embebible
        include_plotlyjs = False
        script_tag = ""
        if local_plotly_path and os.path.exists(local_plotly_path):
            # Cargar desde archivo local
            uri_path = local_plotly_path.replace('\\', '/')
            script_tag = f'<script src="file:///{uri_path}"></script>'
        else:
            include_plotlyjs = 'cdn'

        fig_html = fig.to_html(
            include_plotlyjs=include_plotlyjs,
            full_html=False,
            config={
                'responsive': True,
                'displayModeBar': True,
                'displaylogo': False,
                'modeBarButtonsToRemove': ['lasso2d', 'select2d']
            }
        )

        html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body, html {{
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            background-color: {bg_color};
            overflow: hidden;
            font-family: {font_family};
        }}
        #chart-container {{
            width: 100%;
            height: 100%;
            box-sizing: border-box;
            padding: 8px;
        }}
        .js-plotly-plot {{
            width: 100% !important;
            height: 100% !important;
        }}
    </style>
    <script>
        // Polyfill String.prototype.replaceAll para Chromium anterior a v85
        if (!String.prototype.replaceAll) {{
            String.prototype.replaceAll = function(search, replacement) {{
                if (search instanceof RegExp) {{
                    return this.replace(search, replacement);
                }}
                return this.split(search).join(replacement);
            }};
        }}

        // Polyfill CSSStyleSheet.prototype.insertRule para :focus-visible en Plotly ModeBar
        const _origInsertRule = CSSStyleSheet.prototype.insertRule;
        CSSStyleSheet.prototype.insertRule = function(rule, index) {{
            try {{
                return _origInsertRule.call(this, rule, index);
            }} catch(err) {{
                if (typeof rule === 'string' && rule.indexOf(':focus-visible') !== -1) {{
                    try {{
                        return _origInsertRule.call(this, rule.replace(/:focus-visible/g, ':focus'), index);
                    }} catch(err2) {{
                        return 0;
                    }}
                }}
                return 0;
            }}
        }};
    </script>
    {script_tag}
</head>
<body>
    <div id="chart-container">
        {fig_html}
    </div>
</body>
</html>"""
        return html_template
