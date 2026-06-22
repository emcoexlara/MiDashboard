"""
Dashboard de Control Operacional de Comercio Exterior - Lara
==============================================================
Requiere: streamlit, pandas, plotly, openpyxl
Instalación: pip install streamlit pandas plotly openpyxl

Estructura de carpetas esperada (relativa a este archivo):
    data/datos.xlsx
    assets/logo_empresa.png
    assets/fondo_comercio.jpg

Ejecución:
    streamlit run dashboard_comercio_exterior.py
"""

import os
from pathlib import Path
import base64

import streamlit as st
import pandas as pd
import plotly.express as px

# ============================================================
# CONFIGURACIÓN GENERAL DE LA PÁGINA
# ============================================================
st.set_page_config(
    page_title="Comercio Exterior - Lara",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CONSTANTES Y ESTILO CORPORATIVO
# ============================================================
COLOR_TITULO = "#1F4E79"
COLOR_PRIMARIO = "#0A1F44"    # azul marino corporativo
COLOR_SECUNDARIO = "#2E75B6"  # azul medio
COLOR_ACENTO = "#FFD700"      # dorado

NOMBRE_EMPRESA = "EMCOEX"
SUBTITULO_DASHBOARD = "Panel de Indicadores en Tiempo Real"

ASSETS_DIR = Path("assets")
DATA_PATH = Path("data/datos.xlsx")

COLUMNAS_NUMERICAS = ["Peso Neto Exportado", "Peso Neto Importado", "Peso Neto Manejado"]
COLUMNAS_REQUERIDAS = ["DESTINO", "FECHA", "TIPO DE CARGA"] + COLUMNAS_NUMERICAS


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================
def set_background(image_path: Path) -> None:
    """Aplica una imagen de fondo a la app, si el archivo existe."""
    if not image_path.exists():
        return
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    ext = image_path.suffix.replace(".", "") or "jpg"
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/{ext};base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def cargar_datos(file_path: str, last_modified: float) -> pd.DataFrame:
    """Carga y limpia los datos del Excel.

    El parámetro `last_modified` se usa solo para invalidar el caché
    de Streamlit automáticamente cuando el archivo cambia en disco.
    """
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()
    return df


def formato_numero(valor: float) -> str:
    """Formatea un número al estilo latino: punto como separador de miles."""
    return f"{valor:,.0f}".replace(",", ".")


def limpiar_numero(valor) -> float:
    """Convierte un valor a float aceptando números nativos de Excel o texto
    en formato latino ('1.234.567,89'), estándar ('1234567.89'), o incluso
    mal escrito con separadores de miles repetidos ('7,605,5').

    Regla: el ÚLTIMO símbolo (',' o '.') que aparece en el texto se trata
    como separador decimal; todos los anteriores se tratan como separadores
    de miles y se descartan. Esto evita que `pd.to_numeric` convierta en 0
    valores válidos que vienen como texto con coma decimal.
    """
    if pd.isna(valor):
        return 0.0
    if isinstance(valor, (int, float)):
        return float(valor)
    s = str(valor).strip().replace(" ", "")
    if s == "":
        return 0.0
    pos_decimal = max(s.rfind(","), s.rfind("."))
    if pos_decimal == -1:
        try:
            return float(s)
        except ValueError:
            return 0.0
    entero = s[:pos_decimal].replace(",", "").replace(".", "")
    decimal = s[pos_decimal + 1:].replace(",", "").replace(".", "")
    try:
        return float(f"{entero}.{decimal}") if decimal else float(entero or 0)
    except ValueError:
        return 0.0


def normalizar_texto(serie: pd.Series) -> pd.Series:
    """Limpia una columna de texto categórico: quita espacios sobrantes,
    unifica mayúsculas/minúsculas y reemplaza vacíos por una etiqueta visible.

    Sin esto, valores como 'CONTENERIZADA ' (con espacio) y variaciones de
    mayúsculas como 'Acompañamiento...' / 'acompañamiento...' se tratan como
    categorías distintas en los filtros, fragmentando los datos.

    OJO: se hace `fillna` ANTES de `astype(str)` a propósito. En pandas con
    columnas de tipo string, `astype(str)` no convierte un NaN real en texto
    — lo deja como NaN — así que un `.replace("NAN", ...)` posterior nunca
    lo alcanza y esas filas quedan fuera de las opciones del filtro.
    """
    limpio = serie.fillna("(SIN ESPECIFICAR)").astype(str).str.strip().str.upper()
    limpio = limpio.replace({"": "(SIN ESPECIFICAR)", "NAN": "(SIN ESPECIFICAR)"})
    return limpio
filas_originales = len(df)

for col in COLUMNAS_NUMERICAS:
    df[col] = df[col].apply(limpiar_numero)
df["FECHA"] = pd.to_datetime(df["FECHA"], errors="coerce")
fechas_invalidas = int(df["FECHA"].isna().sum())

# Normalizar columnas de texto categórico (evita que "CONTENERIZADA " y
# "CONTENERIZADA" o "Acompañamiento..." y "ACOMPAÑAMIENTO..." se traten
# como categorías distintas en los filtros).
for col_categoria in ["DESTINO", "TIPO DE CARGA", "CONTENIDO", "TIPO DE SERVICIO"]:
    if col_categoria in df.columns:
        df[col_categoria] = normalizar_texto(df[col_categoria])

# Eliminar duplicados reales.
# OJO: antes se generaba una "llave" con DESTINO+FECHA+TIPO DE CARGA, pero esa
# combinación puede repetirse legítimamente entre operaciones distintas
# (dos embarques diferentes el mismo día, al mismo destino, con el mismo tipo
# de carga) — eso borraba operaciones reales. Ahora se usa el número de
# operación real como llave (o la fila completa si esa columna no existe).
if "N° DE OPERACIÓN" in df.columns:
    duplicados = int(df.duplicated(subset="N° DE OPERACIÓN").sum())
    df = df.drop_duplicates(subset="N° DE OPERACIÓN")
else:
    duplicados = int(df.duplicated().sum())
    df = df.drop_duplicates()

filas_finales = len(df)
with st.expander("🔍 Diagnóstico de calidad de datos", expanded=False):
    c1, c2, c3 = st.columns(3)
    c1.metric("Filas leídas del Excel", filas_originales)
    c2.metric("Duplicados reales eliminados", duplicados)
    c3.metric("Filas con fecha inválida", fechas_invalidas)
    st.caption(
        f"Filas activas tras limpieza: {filas_finales} de {filas_originales}. "
        "Si este número es menor de lo esperado, revisa el Excel: pueden haber "
        "filas con el mismo N° DE OPERACIÓN repetido, o fechas con formato inconsistente."
    )

# ============================================================
# FILTROS (SIDEBAR)
# ============================================================
st.sidebar.markdown("## 🔎 Filtros")

fecha_min, fecha_max = df["FECHA"].min(), df["FECHA"].max()
rango_fecha = st.sidebar.date_input("Rango de Fecha", [fecha_min, fecha_max])

destinos_disponibles = sorted(df["DESTINO"].dropna().unique())
destinos = st.sidebar.multiselect("Destino", destinos_disponibles, default=destinos_disponibles)

tipos_disponibles = sorted(df["TIPO DE CARGA"].dropna().unique())
tipos_carga = st.sidebar.multiselect("Tipo de Carga", tipos_disponibles, default=tipos_disponibles)

if "TIPO DE SERVICIO" in df.columns:
    servicios_disponibles = sorted(df["TIPO DE SERVICIO"].dropna().unique())
    servicios = st.sidebar.multiselect("Tipo de Servicio", servicios_disponibles, default=servicios_disponibles)
else:
    servicios = None

# ============================================================
# APLICAR FILTROS — ÚNICA FUENTE DE VERDAD: df_filtrado
# Todo lo que sigue (KPIs y gráficos) usa SIEMPRE df_filtrado.
# ============================================================
df_filtrado = df.copy()

if isinstance(rango_fecha, (list, tuple)) and len(rango_fecha) == 2:
    inicio, fin = pd.to_datetime(rango_fecha[0]), pd.to_datetime(rango_fecha[1])
    df_filtrado = df_filtrado[(df_filtrado["FECHA"] >= inicio) & (df_filtrado["FECHA"] <= fin)]

if destinos:
    df_filtrado = df_filtrado[df_filtrado["DESTINO"].isin(destinos)]

if tipos_carga:
    df_filtrado = df_filtrado[df_filtrado["TIPO DE CARGA"].isin(tipos_carga)]

if servicios:
    df_filtrado = df_filtrado[df_filtrado["TIPO DE SERVICIO"].isin(servicios)]
tab_resumen, tab_logistica, tab_mapa = st.tabs(
    ["📊 Exportaciones por País", "📦 Contenedores vs Toneladas", "🗺️ Mapa Global"]
st.markdown(
    f"""
    <hr style='margin-top:40px; margin-bottom:10px; border:none; border-top:1px solid #E0E0E0;'>
    <div style='text-align:center; color:#8A8F98; font-size:12px;'>
        {NOMBRE_EMPRESA} · Control Operacional de Comercio Exterior ·
        Actualizado {pd.Timestamp.now():%Y-%m-%d %H:%M}
    </div>
    """,
    unsafe_allow_html=True,
)

    unsafe_allow_html=True,
)
