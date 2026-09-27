"""
Módulo de Agregación, Filtrado y Transformación de Datos
PROJ-008: Excel Analytics Studio
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np


@dataclass
class AggregatedData:
    df: pd.DataFrame
    x_col: str
    y_cols: List[str]
    color_col: Optional[str]
    agg_func: str
    total_records: int
    categories: List[str]
    series_dict: Dict[str, List[float]]  # Nombre de serie -> valores
    kpi_total: float
    kpi_mean: float
    kpi_max: float
    kpi_min: float
    top_label: str
    top_value: float


class DataAggregator:
    """Motor de agrupamiento y transformación de datos para gráficos y Excel."""

    VALID_AGGS = {
        'Suma': 'sum',
        'Promedio': 'mean',
        'Conteo': 'count',
        'Mediana': 'median',
        'Máximo': 'max',
        'Mínimo': 'min',
        'Sin Agrupar': 'none'
    }

    @classmethod
    def process(
        cls,
        df: pd.DataFrame,
        x_col: str,
        y_col: str,
        color_col: Optional[str] = None,
        agg_name: str = 'Suma',
        sort_by: str = 'value_desc',
        top_n: Optional[int] = None,
        group_others: bool = False
    ) -> AggregatedData:
        """
        Transforma y resume el dataframe según las variables y funciones elegidas.
        """
        if df.empty or x_col not in df.columns:
            raise ValueError(f"Columna '{x_col}' no válida o DataFrame vacío.")

        work_df = df.copy()
        agg_key = cls.VALID_AGGS.get(agg_name, 'sum')

        # Convertir columna Y a numérico forzando errores a NaN
        if agg_key != 'count':
            work_df[y_col] = pd.to_numeric(
                work_df[y_col].astype(str).str.replace('$', '', regex=False)
                                           .str.replace('€', '', regex=False)
                                           .str.replace(',', '.'),
                errors='coerce'
            )
            # Limpiar filas con Y nulo para cálculos numéricos
            work_df = work_df.dropna(subset=[y_col])

        # Limpiar filas con X nulo
        work_df = work_df.dropna(subset=[x_col])
        if work_df.empty:
            raise ValueError("No quedan datos válidos tras limpiar valores nulos.")

        # Si X es fecha y no hay formato específico, formatear de manera legible
        if pd.api.types.is_datetime64_any_dtype(work_df[x_col]):
            work_df[x_col] = work_df[x_col].dt.strftime('%Y-%m-%d')
        else:
            work_df[x_col] = work_df[x_col].astype(str)

        # Caso 1: Con desglose de Color / Categoría secundaria
        if color_col and color_col in work_df.columns and color_col != x_col:
            work_df[color_col] = work_df[color_col].astype(str)
            if agg_key == 'none':
                result_df = work_df[[x_col, color_col, y_col]].copy()
            elif agg_key == 'count':
                result_df = work_df.groupby([x_col, color_col]).size().reset_index(name=y_col)
            else:
                result_df = work_df.groupby([x_col, color_col])[y_col].agg(agg_key).reset_index()

            # Pivot para estructurar series
            pivot_df = result_df.pivot(index=x_col, columns=color_col, values=y_col).fillna(0)
            categories = [str(c) for c in pivot_df.index]
            series_dict = {str(col): pivot_df[col].tolist() for col in pivot_df.columns}

            # KPIs generales
            all_vals = result_df[y_col].dropna()
            kpi_total = float(all_vals.sum()) if not all_vals.empty else 0.0
            kpi_mean = float(all_vals.mean()) if not all_vals.empty else 0.0
            kpi_max = float(all_vals.max()) if not all_vals.empty else 0.0
            kpi_min = float(all_vals.min()) if not all_vals.empty else 0.0

            top_row = result_df.sort_values(by=y_col, ascending=False).head(1)
            top_label = f"{top_row[x_col].values[0]} ({top_row[color_col].values[0]})" if not top_row.empty else "N/A"
            top_value = float(top_row[y_col].values[0]) if not top_row.empty else 0.0

            return AggregatedData(
                df=result_df,
                x_col=x_col,
                y_cols=[y_col],
                color_col=color_col,
                agg_func=agg_name,
                total_records=len(work_df),
                categories=categories,
                series_dict=series_dict,
                kpi_total=round(kpi_total, 2),
                kpi_mean=round(kpi_mean, 2),
                kpi_max=round(kpi_max, 2),
                kpi_min=round(kpi_min, 2),
                top_label=str(top_label),
                top_value=round(top_value, 2)
            )

        # Caso 2: Simple (X y Y sin color)
        if agg_key == 'none':
            result_df = work_df[[x_col, y_col]].copy()
        elif agg_key == 'count':
            result_df = work_df.groupby(x_col).size().reset_index(name='Conteo')
            y_col = 'Conteo'
        else:
            result_df = work_df.groupby(x_col)[y_col].agg(agg_key).reset_index()

        # Ordenamiento
        if sort_by == 'value_desc':
            result_df = result_df.sort_values(by=y_col, ascending=False)
        elif sort_by == 'value_asc':
            result_df = result_df.sort_values(by=y_col, ascending=True)
        elif sort_by == 'label_asc':
            result_df = result_df.sort_values(by=x_col, ascending=True)
        elif sort_by == 'label_desc':
            result_df = result_df.sort_values(by=x_col, ascending=False)

        # Aplicar Top N si fue solicitado
        if top_n and top_n > 0 and len(result_df) > top_n:
            top_part = result_df.head(top_n).copy()
            if group_others:
                rest_part = result_df.iloc[top_n:]
                others_val = rest_part[y_col].sum() if agg_key in ['sum', 'count'] else rest_part[y_col].mean()
                others_row = pd.DataFrame([{x_col: 'Otros', y_col: others_val}])
                result_df = pd.concat([top_part, others_row], ignore_index=True)
            else:
                result_df = top_part

        categories = [str(c) for c in result_df[x_col]]
        values = [float(v) for v in result_df[y_col]]
        series_dict = {y_col: values}

        all_vals = result_df[y_col].dropna()
        kpi_total = float(all_vals.sum()) if not all_vals.empty else 0.0
        kpi_mean = float(all_vals.mean()) if not all_vals.empty else 0.0
        kpi_max = float(all_vals.max()) if not all_vals.empty else 0.0
        kpi_min = float(all_vals.min()) if not all_vals.empty else 0.0

        top_label = categories[0] if categories else "N/A"
        top_value = values[0] if values else 0.0

        return AggregatedData(
            df=result_df,
            x_col=x_col,
            y_cols=[y_col],
            color_col=None,
            agg_func=agg_name,
            total_records=len(work_df),
            categories=categories,
            series_dict=series_dict,
            kpi_total=round(kpi_total, 2),
            kpi_mean=round(kpi_mean, 2),
            kpi_max=round(kpi_max, 2),
            kpi_min=round(kpi_min, 2),
            top_label=top_label,
            top_value=round(top_value, 2)
        )

    @staticmethod
    def get_correlation_matrix(df: pd.DataFrame, numeric_cols: List[str]) -> pd.DataFrame:
        """Calcula la matriz de correlación de Pearson entre columnas numéricas."""
        clean_numeric = pd.DataFrame()
        for col in numeric_cols:
            clean_numeric[col] = pd.to_numeric(df[col], errors='coerce')
        clean_numeric = clean_numeric.dropna(how='all')
        return clean_numeric.corr().round(3)
