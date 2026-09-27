"""
Módulo de Escaneo y Diagnóstico de Archivos Excel y Tabulares
PROJ-008: Excel Analytics Studio
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import os
import warnings
import pandas as pd
import numpy as np


@dataclass
class ColumnInfo:
    name: str
    dtype: str
    inferred_type: str  # 'numeric', 'categorical', 'temporal', 'text'
    null_count: int
    null_percentage: float
    unique_count: int
    sample_values: List[Any]
    is_numeric: bool
    is_categorical: bool
    is_temporal: bool


@dataclass
class ScanResult:
    filepath: str
    filename: str
    sheet_name: str
    all_sheets: List[str]
    total_rows: int
    total_cols: int
    memory_usage_kb: float
    duplicate_rows: int
    columns: List[ColumnInfo]
    numeric_columns: List[str]
    categorical_columns: List[str]
    temporal_columns: List[str]
    df: pd.DataFrame
    preview_df: pd.DataFrame
    summary_stats: Dict[str, Any] = field(default_factory=dict)


class ExcelScanner:
    """Escáner inteligente de archivos Excel y CSV."""

    @staticmethod
    def get_sheet_names(filepath: str) -> List[str]:
        """Obtiene la lista de hojas disponibles en el libro."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"No se encontró el archivo: {filepath}")

        ext = os.path.splitext(filepath)[1].lower()
        if ext in ['.csv', '.tsv', '.txt']:
            return ["Datos_CSV"]
        elif ext in ['.xlsx', '.xlsm', '.xltx', '.xltm']:
            import openpyxl
            wb = openpyxl.load_workbook(filepath, read_only=True)
            names = wb.sheetnames
            wb.close()
            return names
        elif ext == '.xls':
            excel_file = pd.ExcelFile(filepath)
            return excel_file.sheet_names
        else:
            raise ValueError(f"Extensión no compatible: {ext}")

    @classmethod
    def scan_file(cls, filepath: str, sheet_name: Optional[str] = None) -> ScanResult:
        """
        Escanea y analiza a fondo la estructura y calidad del archivo.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"El archivo no existe: {filepath}")

        filename = os.path.basename(filepath)
        ext = os.path.splitext(filepath)[1].lower()
        all_sheets = cls.get_sheet_names(filepath)

        if not sheet_name:
            sheet_name = all_sheets[0]

        # Carga del DataFrame
        df = cls._load_dataframe(filepath, ext, sheet_name)

        if df.empty:
            raise ValueError(f"La hoja o archivo '{sheet_name}' no contiene datos legibles.")

        # Limpieza básica de encabezados
        df.columns = [str(c).strip() if str(c).strip() != "" else f"Columna_{i+1}" for i, c in enumerate(df.columns)]
        # Manejar columnas duplicadas agregando sufijo
        seen = {}
        new_cols = []
        for c in df.columns:
            if c in seen:
                seen[c] += 1
                new_cols.append(f"{c}_{seen[c]}")
            else:
                seen[c] = 0
                new_cols.append(c)
        df.columns = new_cols

        total_rows = len(df)
        total_cols = len(df.columns)
        memory_usage_kb = round(df.memory_usage(deep=True).sum() / 1024.0, 2)
        duplicate_rows = int(df.duplicated().sum())

        # Clasificación e inferencia de tipos
        columns_info: List[ColumnInfo] = []
        numeric_cols: List[str] = []
        categorical_cols: List[str] = []
        temporal_cols: List[str] = []

        for col_name in df.columns:
            series = df[col_name]
            col_info = cls._analyze_column(col_name, series, total_rows)
            columns_info.append(col_info)

            if col_info.is_numeric:
                numeric_cols.append(col_name)
            elif col_info.is_temporal:
                temporal_cols.append(col_name)
            else:
                categorical_cols.append(col_name)

        # Resumen estadístico descriptivo
        summary_stats = cls._compute_summary(df, numeric_cols, categorical_cols)

        # Vista previa optimizada (máximo 500 filas para fluidez de UI)
        preview_df = df.head(500).copy()

        return ScanResult(
            filepath=filepath,
            filename=filename,
            sheet_name=sheet_name,
            all_sheets=all_sheets,
            total_rows=total_rows,
            total_cols=total_cols,
            memory_usage_kb=memory_usage_kb,
            duplicate_rows=duplicate_rows,
            columns=columns_info,
            numeric_columns=numeric_cols,
            categorical_columns=categorical_cols,
            temporal_columns=temporal_cols,
            df=df,
            preview_df=preview_df,
            summary_stats=summary_stats
        )

    @staticmethod
    def _load_dataframe(filepath: str, ext: str, sheet_name: str) -> pd.DataFrame:
        """Carga el DataFrame según el formato y autodetecta separadores para CSV."""
        if ext in ['.csv', '.tsv', '.txt']:
            # Intentar detectar separador común
            try:
                df = pd.read_csv(filepath, sep=None, engine='python', encoding='utf-8')
            except Exception:
                try:
                    df = pd.read_csv(filepath, sep=';', encoding='latin-1')
                except Exception:
                    df = pd.read_csv(filepath, sep=',', encoding='latin-1')
            return df
        elif ext in ['.xlsx', '.xlsm', '.xltx', '.xltm']:
            return pd.read_excel(filepath, sheet_name=sheet_name, engine='openpyxl')
        elif ext == '.xls':
            return pd.read_excel(filepath, sheet_name=sheet_name)
        else:
            raise ValueError(f"Extensión '{ext}' no soportada.")

    @staticmethod
    def _analyze_column(col_name: str, series: pd.Series, total_rows: int) -> ColumnInfo:
        """Analiza minuciosamente el tipo e inferencia de una columna."""
        null_count = int(series.isna().sum())
        null_pct = round((null_count / total_rows * 100.0) if total_rows > 0 else 0.0, 2)
        valid_series = series.dropna()
        unique_count = int(valid_series.nunique())
        samples = list(valid_series.head(5).values)

        # Detección de temporal
        is_temporal = False
        is_numeric = False
        is_categorical = False
        inferred = 'categorical'

        # 1. ¿Es ya fecha o timestamp?
        if pd.api.types.is_datetime64_any_dtype(series):
            is_temporal = True
            inferred = 'temporal'
        # 2. ¿Es numérico nativo?
        elif pd.api.types.is_numeric_dtype(series):
            is_numeric = True
            inferred = 'numeric'
        else:
            # Intentar conversión a fecha si tiene strings con formato de fecha
            if not valid_series.empty:
                # Probar si es numérico con comas o puntos
                try:
                    converted_numeric = pd.to_numeric(
                        valid_series.astype(str).str.replace('$', '', regex=False)
                                               .str.replace('€', '', regex=False)
                                               .str.replace('%', '', regex=False)
                                               .str.replace(' ', '', regex=False)
                                               .str.replace(',', '.'),
                        errors='coerce'
                    )
                    if converted_numeric.notna().sum() / len(valid_series) > 0.85:
                        is_numeric = True
                        inferred = 'numeric'
                except Exception:
                    pass

                if not is_numeric:
                    try:
                        with warnings.catch_warnings():
                            warnings.simplefilter("ignore")
                            parsed_dates = pd.to_datetime(valid_series.head(20), errors='coerce')
                            if parsed_dates.notna().sum() / len(parsed_dates) > 0.80:
                                is_temporal = True
                                inferred = 'temporal'
                    except Exception:
                        pass

        if not is_numeric and not is_temporal:
            is_categorical = True
            inferred = 'categorical'

        return ColumnInfo(
            name=col_name,
            dtype=str(series.dtype),
            inferred_type=inferred,
            null_count=null_count,
            null_percentage=null_pct,
            unique_count=unique_count,
            sample_values=samples,
            is_numeric=is_numeric,
            is_categorical=is_categorical,
            is_temporal=is_temporal
        )

    @staticmethod
    def _compute_summary(df: pd.DataFrame, numeric_cols: List[str], categorical_cols: List[str]) -> Dict[str, Any]:
        """Calcula estadísticas descriptivas rápidas de las métricas principales."""
        summary = {
            'numeric': {},
            'categorical': {}
        }
        for col in numeric_cols:
            s = pd.to_numeric(df[col], errors='coerce').dropna()
            if not s.empty:
                summary['numeric'][col] = {
                    'min': float(s.min()),
                    'max': float(s.max()),
                    'mean': round(float(s.mean()), 2),
                    'median': round(float(s.median()), 2),
                    'sum': round(float(s.sum()), 2),
                    'std': round(float(s.std()), 2) if len(s) > 1 else 0.0
                }

        for col in categorical_cols:
            s = df[col].dropna()
            if not s.empty:
                val_counts = s.value_counts()
                top_val = val_counts.index[0] if not val_counts.empty else None
                top_freq = int(val_counts.iloc[0]) if not val_counts.empty else 0
                summary['categorical'][col] = {
                    'top': str(top_val),
                    'top_count': top_freq,
                    'cardinality': int(s.nunique())
                }
        return summary
