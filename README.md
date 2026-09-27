# 📊 Excel Analytics Studio (PROJ-008)

**Excel Analytics Studio** es una suite de escritorio **100% funcional, intuitiva y portable** diseñada para escanear cualquier archivo de Excel (`.xlsx`, `.xls`, `.csv`, `.xlsm`), diagnosticar la estructura y calidad de sus datos y generar gráficos profesionales de alto impacto visual, tanto dinámicos e interactivos en pantalla como **gráficos nativos y tableros ejecutivos en nuevos documentos de Excel**.

---

## ✨ Características Principales

1. **Escáner Inteligente de Archivos:**
   - Soporta libros multi-hoja (`.xlsx`, `.xls`, `.xlsm`) y archivos delimitados (`.csv`).
   - Detección automática de encabezados y clasificación de tipos: Categóricas, Numéricas y Fechas.
   - Panel de diagnóstico de calidad: total de filas, columnas, celdas vacías, duplicados y memoria utilizada.
   - Vista previa tabular con buscador en tiempo real y contador dinámico de registros.

2. **Diseñador de Gráficos de 8 Familias:**
   - **Barras:** Verticales, Horizontales y Apiladas.
   - **Líneas y Tendencia:** Con marcadores y trazado continuo.
   - **Áreas:** Evolución volumétrica simple y acumulada.
   - **Pastel y Dona:** Con porcentajes automáticos y cálculo de proporciones.
   - **Dispersión (Scatter):** Correlación de variables.
   - **Histograma:** Frecuencia y distribución de medidas.
   - **Diagrama de Caja (Boxplot):** Detección de rangos y valores atípicos.
   - **Matriz de Correlación (Heatmap):** Análisis multivariable de variables numéricas.

3. **Operaciones de Datos Avanzadas:**
   - Agregaciones automáticas: `Suma`, `Promedio`, `Conteo`, `Mediana`, `Máximo`, `Mínimo` o `Sin Agrupar`.
   - Filtro de **Top N** (Top 5, Top 10, etc.) con opción de agrupar el resto en categoría *"Otros"*.
   - Ordenamiento por valor ascendente/descendente o alfabético.
   - 6 Paletas corporativas profesionales: *Sapphire Corporativo, Emerald Financiero, Sunset Atardecer, Cyber Tecnológico, Slate Ejecutivo y Vibrante Pro*.

4. **Visualización Híbrida en Pantalla:**
   - **🌐 Modo Dinámico Interactivo:** Renderizado con Plotly en motor web acelerado local (zoom, paneo, tooltips con valores exactos, autoscale y descarga en PNG). Funciona **100% offline**.
   - **📐 Modo Estático Vectorial HD:** Renderizado con Matplotlib en alta resolución (300 DPI) para publicaciones o informes impresos.

5. **Generador y Exportador a Documentos Excel (`.xlsx`):**
   - **Opción A (Gráficos NATIVOS Dinámicos):** Crea un nuevo archivo Excel donde el gráfico es un objeto nativo de Microsoft Excel enlazado a las celdas de la tabla. Al editar un valor en Excel, el gráfico cambia automáticamente.
   - **Opción B (Informe Ejecutivo con Tarjetas KPI):** Genera una portada ejecutiva con 4 tarjetas de indicadores KPI, tabla formateada con bordes y el gráfico incrustado en alta resolución.
   - Opción para adjuntar una hoja adicional con todos los datos originales limpios.
   - Diálogo nativo para abrir el archivo generado en Excel inmediatamente con 1 clic.

---

## 🚀 Cómo Iniciar la Aplicación (Portabilidad Total)

### Opción 1: Lanzador Rápido (Recomendado)
Haga doble clic en:
```
INICIAR_APP.bat
```
El lanzador comprobará automáticamente si las librerías necesarias están instaladas (y las instalará si faltan) y abrirá la aplicación de inmediato.

### Opción 2: Lanzador Silencioso (Sin Consola)
Haga doble clic en:
```
INICIAR_APP_SILENCIOSO.vbs
```

### Opción 3: Ejecución Manual por Consola
```bash
python app.py
```

### Opción 4: Compilar un Ejecutable (.exe) Portable
Si desea generar un archivo ejecutable único para llevar en una memoria USB a cualquier equipo sin instalar Python:
Haga doble clic en:
```
compilar_ejecutable.bat
```
El archivo `.exe` autónomo quedará generado en la carpeta `dist/`.

---

## 🧪 Demostración Inmediata
El programa incluye un dataset de ventas corporativas preinstalado:
- Al abrir la aplicación, el archivo `assets/demo_ventas.xlsx` se carga automáticamente.
- También puede pulsar el botón **"⚡ Cargar Demo Ventas"** en cualquier momento para restaurar los datos de prueba.

---

## 🏛️ Estructura del Código

```
projects/PROJ_008_Excel_Analytics_Studio/
├── app.py                             # Punto de entrada principal
├── INICIAR_APP.bat                    # Lanzador rápido de un clic
├── INICIAR_APP_SILENCIOSO.vbs         # Lanzador silencioso sin consola
├── compilar_ejecutable.bat            # Compilador a .exe portable
├── requirements.txt                   # Lista de dependencias
├── assets/
│   ├── style.qss                      # Hoja de estilos moderna ejecutiva
│   ├── plotly.min.js                  # Motor Plotly offline local
│   └── demo_ventas.xlsx               # Dataset de demostración
├── core/
│   ├── excel_scanner.py               # Lector y diagnosticador de Excel/CSV
│   ├── data_aggregator.py             # Motor de agrupaciones y cálculos
│   ├── chart_generator_plotly.py      # Generador dinámico interactivo
│   ├── chart_generator_matplotlib.py  # Generador estático vectorial HD
│   ├── excel_exporter_native.py       # Generador de gráficos nativos en Excel
│   └── excel_exporter_dashboard.py    # Generador de tablero ejecutivo en Excel
└── ui/
    ├── main_window.py                 # Ventana principal e integración
    ├── panel_scanner.py               # Panel de escaneo y carga de archivos
    ├── panel_chart_controls.py        # Panel de configuración de gráficos
    ├── panel_export_dialog.py         # Modal de exportación avanzada
    └── widgets/
        ├── kpi_card.py                # Tarjetas de indicadores KPI
        ├── data_table_view.py         # Tabla con búsqueda en vivo
        └── chart_viewer.py            # Visor dual dinámico / estático
```

---

## 📜 Licencia y Gobernanza
Desarrollado bajo la directiva máster de la **Fábrica de Software Autónoma** cumpliendo el estándar **OKF (Open Knowledge Format) v1.0.0**.
