import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import base64
import os

# ------------------------------
# CONFIGURACIÓN
# ------------------------------
st.set_page_config(layout="wide")

BASE_DIR = Path(file).resolve().parent
ASSETS = BASE_DIR / "assets"
DATA_FILE = BASE_DIR / "datos.xlsx"

# Colores corporativos
COLOR1 = "#1f77b4"
COLOR2 = "#ff7f0e"
COLOR3 = "#2ca02c"
COLOR4 = "#d62728"

# ------------------------------
# FUNCIONES
# ------------------------------
def cargar_base64(file):
    return base64.b64encode(file.read()).decode()

def cargar_base64_ruta(ruta):
    try:
        with open(ruta, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

# ------------------------------
# DIAGNÓSTICO (IMPORTANTE)
# ------------------------------
st.sidebar.markdown("### 🔍 Diagnóstico")
st.sidebar.write("Ruta actual:", BASE_DIR)

if ASSETS.exists():
    st.sidebar.success("Carpeta assets detectada")
    st.sidebar.write(os.listdir(ASSETS))
else:
    st.sidebar.error("No existe carpeta assets")

# ------------------------------
# CARGA DE IMÁGENES (DOBLE MÉTODO)
# ------------------------------
fondo = None
logo = None

# MÉTODO 1: desde carpeta assets
if ASSETS.exists():
    ruta_fondo = ASSETS / "fondo_comercio.jpg"
    ruta_logo = ASSETS / "logo_empresa.png"

    if ruta_fondo.exists():
        fondo = cargar_base64_ruta(ruta_fondo)

    if ruta_logo.exists():
        logo = cargar_base64_ruta(ruta_logo)

# MÉTODO 2: carga manual si falla
if not fondo:
    fondo_file = st.sidebar.file_uploader("Subir fondo", type=["jpg","png","jpeg"])
    if fondo_file:
        fondo = cargar_base64(fondo_file)

if not logo:
    logo_file = st.sidebar.file_uploader("Subir logo", type=["jpg","png","jpeg"])
    if logo_file:
        logo = cargar_base64(logo_file)

# ------------------------------
# APLICAR FONDO
# ------------------------------
if fondo:
    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{fondo}");
        background-size: cover;
        background-position: center;
    }}
    </style>
    """, unsafe_allow_html=True)
else:
    st.warning("⚠️ Sin fondo")

# ------------------------------
# MOSTRAR LOGO
# ------------------------------
if logo:
    st.sidebar.markdown(f"""
    <div style="text-align:center;">
        <img src="data:image/png;base64,{logo}" width="150">
    </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.warning("⚠️ Sin logo")

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
            st.error(f"Falta columna: {col}")
            return pd.DataFrame()
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["peso neto exportado (t)"] = df["peso neto exportado"] / 1000
    df["peso neto importado (t)"] = df["peso neto importado"] / 1000
    df["peso total (t)"] = (df["peso neto manejado"] + df["peso neto exportado"]) / 1000

    return df

# ------------------------------
# SUBIR EXCEL
# ------------------------------
archivo_excel = st.sidebar.file_uploader("Actualizar Excel", type=["xlsx"])
df = cargar_datos(archivo_excel)

if df.empty:
    st.stop()

# ------------------------------
# TABS
# ------------------------------
tabs = st.tabs(["Resumen Ejecutivo", "Operaciones", "Países", "Datos"])
# ------------------------------
# KPI
# ------------------------------
def kpi(col, titulo, valor, color):
    col.markdown(f"""
    <div style="background:{color};padding:20px;border-radius:12px;text-align:center;color:white;">
        <h4>{titulo}</h4>
        <h2>{valor:,.2f}</h2>
    </div>
    """, unsafe_allow_html=True)

# ------------------------------
# RESUMEN
# ------------------------------
with tabs[0]:
    st.markdown("## 📊 Resumen Ejecutivo")

    col1, col2, col3, col4 = st.columns(4)

    kpi(col1, "Operaciones", len(df), COLOR1)
    kpi(col2, "Exportado (t)", df["peso neto exportado (t)"].sum(), COLOR2)
    kpi(col3, "Importado (t)", df["peso neto importado (t)"].sum(), COLOR3)
    kpi(col4, "Total (t)", df["peso total (t)"].sum(), COLOR4)

# ------------------------------
# OPERACIONES
# ------------------------------
with tabs[1]:
    st.markdown("## 📈 Operaciones")

    st.plotly_chart(px.histogram(df, x="peso neto exportado (t)", nbins=30, color_discrete_sequence=[COLOR1]), use_container_width=True)
    st.plotly_chart(px.histogram(df, x="peso neto importado (t)", nbins=30, color_discrete_sequence=[COLOR2]), use_container_width=True)

# ------------------------------
# PAÍSES
# ------------------------------
with tabs[2]:
    st.markdown("## 🌍 Países")

    df_paises = df.groupby("destino")[["peso total (t)"]].sum().reset_index()

    st.plotly_chart(px.bar(df_paises, x="destino", y="peso total (t)", color_discrete_sequence=[COLOR1]), use_container_width=True)

# ------------------------------
# DATOS
# ------------------------------
with tabs[3]:
    st.markdown("## 📋 Datos")

    st.dataframe(df, use_container_width=True)
