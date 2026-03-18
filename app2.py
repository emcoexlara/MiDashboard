import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import base64

# ------------------------------
# CONFIGURACIÓN DE PÁGINA
# ------------------------------
BASE_DIR = Path(file).parent
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "datos.xlsx"
ASSETS_DIR = BASE_DIR / "assets"

st.set_page_config(
    page_title="Control Operacional Empresa de Comercio Exterior de Lara",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------
# LOGO Y FONDO
# ------------------------------
logo_path = ASSETS_DIR / "logo.png"
fondo_path = ASSETS_DIR / "fondo_comercio.jpg"

if logo_path.exists():
    st.sidebar.image(logo_path, width=150)

def set_fondo(path):
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{b64}");
            background-size: cover;
            background-position: center;
        }}
        </style>
    """, unsafe_allow_html=True)

if fondo_path.exists():
    set_fondo(fondo_path)

# ------------------------------
# CARGA DE DATOS
# ------------------------------
@st.cache_data
def cargar_datos(file=None):
    archivo = file if file else DATA_FILE
    try:
        df = pd.read_excel(archivo)
    except:
        return pd.DataFrame()
    
    df.columns = df.columns.str.strip()  # limpiar espacios
    # Intentar convertir pesos si existen
    for col in ["Peso Neto Manejado", "Peso Neto Exportado", "Peso Neto Importado"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    
    # Toneladas (solo si existen)
    if "Peso Neto Exportado" in df.columns:
        df["peso neto exportado (t)"] = df["Peso Neto Exportado"] / 1000
    if "Peso Neto Importado" in df.columns:
        df["peso neto importado (t)"] = df["Peso Neto Importado"] / 1000
    if "Peso Neto Manejado" in df.columns and "Peso Neto Exportado" in df.columns:
        df["peso total (t)"] = (df["Peso Neto Manejado"] + df["Peso Neto Exportado"]) / 1000
    
    # Fecha
    if 'FECHA' in df.columns:
        df['FECHA'] = pd.to_datetime(df['FECHA'], errors='coerce')
    
    return df

archivo_excel = st.sidebar.file_uploader("Actualizar Excel", type=["xlsx"])
df = cargar_datos(archivo_excel)

if df.empty:
    st.warning("No se pudo cargar el archivo Excel. Por favor verifica que tenga datos.")
else:
    # ------------------------------
    # FILTROS EN SIDEBAR
    # ------------------------------
    st.sidebar.markdown("### Filtros")
    
    # Fecha
    fecha_seleccion = None
    if 'FECHA' in df.columns:
        min_fecha, max_fecha = df['FECHA'].min(), df['FECHA'].max()
        fecha_seleccion = st.sidebar.date_input("Fecha", value=min_fecha, min_value=min_fecha, max_value=max_fecha)
    
    # Destino
    destino_seleccion = df['DESTINO'].unique() if 'DESTINO' in df.columns else []
    destino_seleccion = st.sidebar.multiselect("Destino", destino_seleccion, default=destino_seleccion)
    
    # Contenido
    contenido_seleccion = df['CONTENIDO'].unique() if 'CONTENIDO' in df.columns else []
    contenido_seleccion = st.sidebar.multiselect("Contenido", contenido_seleccion, default=contenido_seleccion)
    
    # ------------------------------
    # APLICAR FILTROS
    # ------------------------------
    df_filtrado = df.copy()
    if fecha_seleccion and 'FECHA' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['FECHA'] == pd.to_datetime(fecha_seleccion)]
    if destino_seleccion:
        df_filtrado = df_filtrado[df_filtrado['DESTINO'].isin(destino_seleccion)]
    if contenido_seleccion:
        df_filtrado = df_filtrado[df_filtrado['CONTENIDO'].isin(contenido_seleccion)]
        # ------------------------------
    # TÍTULO PRINCIPAL
    # ------------------------------
    st.markdown(
        """
        <h1 style='text-align:center; color:black; border: 3px solid white; padding:15px; border-radius:12px;'>
            Control Operacional Empresa de Comercio Exterior de Lara
        </h1>
        """,
        unsafe_allow_html=True
    )
    
    # ------------------------------
    # MOSTRAR DATOS FILTRADOS
    # ------------------------------
    st.markdown("### Datos Filtrados")
    st.dataframe(df_filtrado)
    
    # ------------------------------
    # KPIs dinámicos (solo si existen)
    # ------------------------------
    COLOR1 = "#1f77b4"
    COLOR2 = "#ff7f0e"
    COLOR3 = "#2ca02c"
    COLOR4 = "#d62728"
    
    col1, col2, col3, col4 = st.columns(4)
    
    if 'FECHA' in df_filtrado.columns:
        col1.metric("Operaciones", len(df_filtrado))
    if "peso neto exportado (t)" in df_filtrado.columns:
        col2.metric("Peso Neto Exportado (t)", f"{df_filtrado['peso neto exportado (t)'].sum():,.2f}")
    if "peso neto importado (t)" in df_filtrado.columns:
        col3.metric("Peso Neto Importado (t)", f"{df_filtrado['peso neto importado (t)'].sum():,.2f}")
    if "peso total (t)" in df_filtrado.columns:
        col4.metric("Peso Total (t)", f"{df_filtrado['peso total (t)'].sum():,.2f}")
    
    # ------------------------------
    # Gráficas opcionales si existen columnas de peso
    # ------------------------------
    st.markdown("### Gráficas de Pesos")
    if "peso neto exportado (t)" in df_filtrado.columns:
        fig = px.histogram(df_filtrado, x="peso neto exportado (t)")
        st.plotly_chart(fig, use_container_width=True)
    if "peso neto importado (t)" in df_filtrado.columns:
        fig2 = px.histogram(df_filtrado, x="peso neto importado (t)")
        st.plotly_chart(fig2, use_container_width=True)
