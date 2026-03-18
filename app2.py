import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from PIL import Image
import base64

# ------------------------------
# CONFIGURACIÓN DE PÁGINA
# ------------------------------
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "datos.xlsx"
ASSETS_DIR = BASE_DIR / "assets"

st.set_page_config(
    page_title="Control Operacional Empresa de Comercio Exterior de Lara",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ------------------------------
# CARGAR LOGO Y FONDO
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
    df.columns = df.columns.str.strip().str.lower()
    for col in ["peso neto manejado", "peso neto exportado", "peso neto importado"]:
        df[col] = pd.to_numeric(df.get(col, 0), errors="coerce").fillna(0)
    df["peso neto exportado (t)"] = df["peso neto exportado"] / 1000
    df["peso neto importado (t)"] = df["peso neto importado"] / 1000
    df["peso total (t)"] = (df["peso neto manejado"] + df["peso neto exportado"]) / 1000
    return df

archivo_excel = st.sidebar.file_uploader("Actualizar Excel", type=["xlsx"])
df = cargar_datos(archivo_excel)

if df.empty:
    st.error("El archivo Excel no contiene datos válidos o las columnas necesarias.")
    st.stop()

# ------------------------------
# FILTROS
# ------------------------------
st.sidebar.markdown("### Filtros")
fechas = pd.to_datetime(df['fecha']) if 'fecha' in df.columns else pd.to_datetime([])
destinos = df['destino'].unique() if 'destino' in df.columns else []
contenidos = df['contenido'].unique() if 'contenido' in df.columns else []

fecha_seleccion = st.sidebar.date_input("Fecha", min_value=fechas.min() if not fechas.empty else None)
destino_seleccion = st.sidebar.selectbox("Destino", ['Todos'] + list(destinos))
contenido_seleccion = st.sidebar.selectbox("Contenido", ['Todos'] + list(contenidos))

df_filtrado = df.copy()
if not fechas.empty and fecha_seleccion:
    df_filtrado = df_filtrado[df_filtrado['fecha'] == pd.to_datetime(fecha_seleccion)]
if destino_seleccion != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['destino'] == destino_seleccion]
if contenido_seleccion != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['contenido'] == contenido_seleccion]

# ------------------------------
# COLORES CORPORATIVOS
# ------------------------------
COLOR1 = "#1f77b4"
COLOR2 = "#ff7f0e"
COLOR3 = "#2ca02c"
COLOR4 = "#d62728"

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
# KPIs
# ------------------------------
def kpi_cuadro(col, titulo, valor, color):
    col.markdown(
        f"""
        <div style='background:{color};padding:20px;border-radius:12px;text-align:center;color:white;'>
            <h4>{titulo}</h4>
            <h2>{valor:,.2f}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    col1, col2, col3, col4 = st.columns(4)
kpi_cuadro(col1, "Operaciones", len(df_filtrado), COLOR1)
kpi_cuadro(col2, "Peso Neto Exportado (t)", df_filtrado["peso neto exportado (t)"].sum(), COLOR2)
kpi_cuadro(col3, "Peso Neto Importado (t)", df_filtrado["peso neto importado (t)"].sum(), COLOR3)
kpi_cuadro(col4, "Peso Total (t)", df_filtrado["peso total (t)"].sum(), COLOR4)

# ------------------------------
# FUNCIONES PARA SECCIONES
# ------------------------------
def seccion_titulo(titulo):
    st.markdown(
        f"""
        <div style='background-color:white; padding:10px; border-radius:10px; margin-bottom:10px;'>
            <h2 style='color:#1f77b4'>{titulo}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

# ------------------------------
# TABS Y GRÁFICAS
# ------------------------------
tabs = st.tabs(["Resumen Ejecutivo", "Operaciones", "Países", "Mapa 3D"])

with tabs[0]:
    seccion_titulo("Resumen Ejecutivo")
    st.write("Indicadores resumidos según los filtros seleccionados.")

with tabs[1]:
    seccion_titulo("Operaciones")
    fig_exp = px.histogram(df_filtrado, x="peso neto exportado (t)", nbins=30, color_discrete_sequence=[COLOR2])
    fig_imp = px.histogram(df_filtrado, x="peso neto importado (t)", nbins=30, color_discrete_sequence=[COLOR3])
    st.plotly_chart(fig_exp, use_container_width=True)
    st.plotly_chart(fig_imp, use_container_width=True)

with tabs[2]:
    seccion_titulo("Países")
    if 'destino' in df_filtrado.columns:
        df_p = df_filtrado.groupby("destino")[["peso total (t)"]].sum().reset_index()
        fig_p = px.bar(df_p, x="destino", y="peso total (t)", color_discrete_sequence=[COLOR1])
        st.plotly_chart(fig_p, use_container_width=True)

with tabs[3]:
    seccion_titulo("Mapa 3D Destinos Exportados")
    if 'latitud' in df_filtrado.columns and 'longitud' in df_filtrado.columns:
        fig_map = px.scatter_3d(df_filtrado, x='longitud', y='latitud', z='peso total (t)',
                                color='peso total (t)', size='peso total (t)',
                                color_continuous_scale='Viridis',
                                labels={'peso total (t)': 'Toneladas'})
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning("Las columnas de latitud y longitud no existen en el Excel para el mapa 3D.")
