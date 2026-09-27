"""
Módulo de Generación de Gráficos Estáticos Vectoriales de Alta Resolución (Matplotlib)
PROJ-008: Excel Analytics Studio
"""
from typing import Optional, List, Dict, Any
import matplotlib
matplotlib.use('Agg')  # Modo no interactivo para seguridad de hilos
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.figure import Figure
import numpy as np
from core.data_aggregator import AggregatedData
from core.chart_generator_plotly import PALETTES


class MatplotlibChartGenerator:
    """Generador estático con calidad editorial y exportación a 300 DPI."""

    @classmethod
    def create_figure(
        cls,
        agg_data: AggregatedData,
        chart_type: str = 'Barras Verticales',
        palette_name: str = 'Sapphire Corporativo',
        dark_mode: bool = True,
        show_data_labels: bool = True,
        show_grid: bool = True,
        custom_title: Optional[str] = None,
        x_label: Optional[str] = None,
        y_label: Optional[str] = None
    ) -> Figure:
        """Crea y estiliza una figura Matplotlib completa."""
        palette = PALETTES.get(palette_name, PALETTES['Sapphire Corporativo'])
        fig = Figure(figsize=(9, 5.5), dpi=100)
        ax = fig.add_subplot(111)

        # Colores de tema
        bg_color = "#0f172a" if dark_mode else "#ffffff"
        card_bg = "#1e293b" if dark_mode else "#f8fafc"
        text_color = "#f8fafc" if dark_mode else "#0f172a"
        grid_color = "#334155" if dark_mode else "#e2e8f0"
        spine_color = "#475569" if dark_mode else "#cbd5e1"

        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(card_bg)

        title_text = custom_title or f"{agg_data.y_cols[0]} por {agg_data.x_col} ({agg_data.agg_func})"
        x_axis_title = x_label or agg_data.x_col
        y_axis_title = y_label or f"{agg_data.agg_func} de {agg_data.y_cols[0]}"

        # Renderizado según tipo
        categories = agg_data.categories
        num_categories = len(categories)
        x_indices = np.arange(num_categories)
        series_items = list(agg_data.series_dict.items())
        num_series = len(series_items)

        if chart_type == 'Barras Verticales':
            bar_width = 0.8 / max(num_series, 1)
            for i, (s_name, vals) in enumerate(series_items):
                offset = (i - num_series / 2 + 0.5) * bar_width
                color = palette[i % len(palette)]
                bars = ax.bar(x_indices + offset, vals, width=bar_width, label=s_name, color=color, edgecolor='none')
                if show_data_labels:
                    for bar in bars:
                        height = bar.get_height()
                        ax.annotate(f'{height:,.0f}',
                                    xy=(bar.get_x() + bar.get_width() / 2, height),
                                    xytext=(0, 3), textcoords="offset points",
                                    ha='center', va='bottom', fontsize=8, color=text_color)
            ax.set_xticks(x_indices)
            ax.set_xticklabels(categories, rotation=25, ha='right', fontsize=9, color=text_color)

        elif chart_type == 'Barras Horizontales':
            bar_width = 0.8 / max(num_series, 1)
            for i, (s_name, vals) in enumerate(series_items):
                offset = (i - num_series / 2 + 0.5) * bar_width
                color = palette[i % len(palette)]
                bars = ax.barh(x_indices + offset, vals, height=bar_width, label=s_name, color=color)
                if show_data_labels:
                    for bar in bars:
                        width = bar.get_width()
                        ax.annotate(f'{width:,.0f}',
                                    xy=(width, bar.get_y() + bar.get_height() / 2),
                                    xytext=(5, 0), textcoords="offset points",
                                    ha='left', va='center', fontsize=8, color=text_color)
            ax.set_yticks(x_indices)
            ax.set_yticklabels(categories, fontsize=9, color=text_color)

        elif chart_type == 'Líneas y Tendencia':
            for i, (s_name, vals) in enumerate(series_items):
                color = palette[i % len(palette)]
                ax.plot(x_indices, vals, label=s_name, color=color, linewidth=2.5, marker='o', markersize=6)
                if show_data_labels:
                    for xi, yi in zip(x_indices, vals):
                        ax.annotate(f'{yi:,.0f}', xy=(xi, yi), xytext=(0, 5),
                                    textcoords="offset points", ha='center', fontsize=8, color=text_color)
            ax.set_xticks(x_indices)
            ax.set_xticklabels(categories, rotation=25, ha='right', fontsize=9, color=text_color)

        elif chart_type == 'Áreas':
            for i, (s_name, vals) in enumerate(series_items):
                color = palette[i % len(palette)]
                ax.plot(x_indices, vals, label=s_name, color=color, linewidth=2)
                ax.fill_between(x_indices, vals, alpha=0.35, color=color)
            ax.set_xticks(x_indices)
            ax.set_xticklabels(categories, rotation=25, ha='right', fontsize=9, color=text_color)

        elif chart_type in ['Pastel', 'Dona']:
            first_col = series_items[0][0]
            vals = series_items[0][1]
            wedges, texts, autotexts = ax.pie(
                vals, labels=categories, colors=palette[:len(categories)],
                autopct='%1.1f%%' if show_data_labels else None,
                pctdistance=0.75 if chart_type == 'Dona' else 0.6,
                startangle=140,
                wedgeprops=dict(width=0.45 if chart_type == 'Dona' else 1.0, edgecolor=bg_color, linewidth=2)
            )
            for t in texts:
                t.set_color(text_color)
                t.set_fontsize(9)
            for at in autotexts:
                at.set_color('#ffffff' if dark_mode else '#0f172a')
                at.set_fontsize(8)
                at.set_weight('bold')

        elif chart_type == 'Dispersión (Scatter)':
            for i, (s_name, vals) in enumerate(series_items):
                color = palette[i % len(palette)]
                ax.scatter(x_indices, vals, label=s_name, color=color, s=70, alpha=0.85, edgecolors='white')
            ax.set_xticks(x_indices)
            ax.set_xticklabels(categories, rotation=25, ha='right', fontsize=9, color=text_color)

        elif chart_type == 'Histograma':
            vals = series_items[0][1]
            ax.hist(vals, bins=12, color=palette[0], edgecolor=bg_color, alpha=0.85)
            x_axis_title = series_items[0][0]
            y_axis_title = "Frecuencia"

        # Títulos y formato
        if chart_type not in ['Pastel', 'Dona']:
            ax.set_xlabel(x_axis_title, color=text_color, fontsize=10, labelpad=8)
            ax.set_ylabel(y_axis_title, color=text_color, fontsize=10, labelpad=8)
            if show_grid:
                ax.grid(True, linestyle='--', alpha=0.4, color=grid_color)
            ax.tick_params(colors=text_color, labelsize=9)
            for spine in ax.spines.values():
                spine.set_color(spine_color)

        ax.set_title(title_text, color=text_color, fontsize=13, weight='bold', pad=15)

        if num_series > 1 and chart_type not in ['Pastel', 'Dona']:
            legend = ax.legend(loc='upper right', frameon=True, facecolor=card_bg, edgecolor=spine_color)
            for text in legend.get_texts():
                text.set_color(text_color)

        fig.tight_layout()
        return fig

    @classmethod
    def export_image(cls, fig: Figure, output_path: str, dpi: int = 300) -> str:
        """Exporta la figura a un archivo de imagen en alta resolución."""
        fig.savefig(output_path, dpi=dpi, bbox_inches='tight')
        return output_path
