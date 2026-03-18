import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import base64

# ------------------------------
# CONFIGURACIÓN GENERAL
# ------------------------------
BASE_DIR = Path().absolute()
ASSETS_DIR = BASE_DIR / "assets"
DATA_FILE = BASE_DIR / "datos.xlsx"

# Colores corporativos
COLOR1 = "#1f77b4"
COLOR2 = "#ff7f0e"
COLOR3 = "#2ca02c"
COLOR4 = "#d62728"

# ------------------------------
# FUNCION BASE64 (CLAVE)
# ------------------------------
def cargar_imagen_base64(ruta):
    try:
        with open(ruta, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

# ------------------------------
# FONDO
# ------------------------------
ruta_fondo = ASSETS_DIR / "fondo_comercio.jpg"
img_fondo = cargar_imagen_base64(ruta_fondo)

if img_fondo:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: linear-gradient(rgba(255,255,255,0.3), rgba(255,255,255,0.3)),
                        url("data:image/jpg;base64,{img_fondo}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    st.error("No se pudo cargar la imagen de fondo")

# ------------------------------
# LOGO
# ------------------------------
ruta_logo = ASSETS_DIR / "logo_empresa.png"
img_logo = cargar_imagen_base64(ruta_logo)

if img_logo:
    st.sidebar.markdown(
        f"""
        <div style="text-align:center;">
            <img src="data:image/png;base64,{img_logo}" width="150">
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.error("No se pudo cargar el logo")

# ------------------------------
# TÍTULO
# ------------------------------
st.markdown(
    "<h1 style='text-align:center; color:#1f77b4;'>Control Operacional Empresa de Comercio Exterior de Lara</h1>",
    unsafe_allow_html=True
)

# ------------------------------
# CARGA DE DATOS
# ------------------------------
@st.cache_data
def cargar_datos(archivo=None):
    if archivo:
        df = pd.read_excel(archivo)
    else:
        df = pd.read_excel(DATA_FILE)

    df.columns = df.columns.str.strip().str.lower()

    columnas = ["peso neto manejado", "peso neto exportado", "peso neto importado"]

    for col in columnas:
        if col not in df.columns:
            st.error(f"Falta la columna: {col}")
            return pd.DataFrame()
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Conversión a toneladas
    df["peso neto exportado (t)"] = df["peso neto exportado"] / 1000
    df["peso neto importado (t)"] = df["peso neto importado"] / 1000
    df["peso total (t)"] = (df["peso neto manejado"] + df["peso neto exportado"]) / 1000

    return df

# ------------------------------
# SUBIR EXCEL
# ------------------------------
archivo_excel = st.sidebar.file_uploader("Actualizar datos", type=["xlsx"])
df = cargar_datos(archivo_excel)

if df.empty:
    st.stop()

# ------------------------------
# TABS
# ------------------------------
tabs = st.tabs(["Resumen Ejecutivo", "Operaciones", "Países", "Datos"])

# ------------------------------
# RESUMEN EJECUTIVO
# ------------------------------
with tabs[0]:
    st.markdown("## 📊 Resumen Ejecutivo")

    operaciones = len(df)
    exportado = df["peso neto exportado (t)"].sum()
    importado = df["peso neto importado (t)"].sum()
    total = df["peso total (t)"].sum()

    col1, col2, col3, col4 = st.columns(4)

    def kpi(col, titulo, valor, color):
        col.markdown(f"""
        <div style="
            background-color:{color};
            padding:20px;
            border-radius:12px;
            text-align:center;
            color:white;">
            <h4>{titulo}</h4>
            <h2>{valor:,.2f}</h2>
        </div>
        """, unsafe_allow_html=True)
        kpi(col1, "Operaciones", operaciones, COLOR1)
    kpi(col2, "Exportado (t)", exportado, COLOR2)
    kpi(col3, "Importado (t)", importado, COLOR3)
    kpi(col4, "Total (t)", total, COLOR4)

# ------------------------------
# OPERACIONES
# ------------------------------
with tabs[1]:
    st.markdown("## 📈 Análisis de Operaciones")

    fig1 = px.histogram(df, x="peso neto exportado (t)", nbins=30, color_discrete_sequence=[COLOR1])
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.histogram(df, x="peso neto importado (t)", nbins=30, color_discrete_sequence=[COLOR2])
    st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.histogram(df, x="peso total (t)", nbins=30, color_discrete_sequence=[COLOR3])
    st.plotly_chart(fig3, use_container_width=True)

# ------------------------------
# PAÍSES
# ------------------------------
with tabs[2]:
    st.markdown("## 🌍 Análisis por País")

    df_paises = df.groupby("destino")[[
        "peso neto exportado (t)",
        "peso neto importado (t)",
        "peso total (t)"
    ]].sum().reset_index()

    fig = px.bar(df_paises, x="destino", y="peso total (t)", color_discrete_sequence=[COLOR1])
    st.plotly_chart(fig, use_container_width=True)

# ------------------------------
# DATOS
# ------------------------------
with tabs[3]:
    st.markdown("## 📋 Datos Completos")

    def estilo(s):
        return ["background-color: rgba(255,215,0,0.3)" for _ in s]

    st.dataframe(
        df.style.apply(estilo, subset=["peso total (t)"]),
        use_container_width=True
    )
