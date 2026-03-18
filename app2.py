import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
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
    
    # Normalizar nombres de columnas (sin espacios al inicio/final)
    df.columns = df.columns.str.strip()
    
    # Convertir pesos a numérico
    for col in ["Peso Neto Manejado", "Peso Neto Exportado", "Peso Neto Importado", "LLENOS RECIBIDOS (EXPORTADOS)"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    
    # Toneladas
    df["peso neto exportado (t)"] = df["Peso Neto Exportado"] / 1000 if "Peso Neto Exportado" in df.columns else 0
    df["peso neto importado (t)"] = df["Peso Neto Importado"] / 1000 if "Peso Neto Importado" in df.columns else 0
    df["peso total (t)"] = ((df["Peso Neto Manejado"] if "Peso Neto Manejado" in df.columns else 0) +
                             (df["Peso Neto Exportado"] if "Peso Neto Exportado" in df.columns else 0)) / 1000
    
    # Fecha
    if 'FECHA' in df.columns:
        df['FECHA'] = pd.to_datetime(df['FECHA'], errors='coerce')
    
    return df

archivo_excel = st.sidebar.file_uploader("Actualizar Excel", type=["xlsx"])
df = cargar_datos(archivo_excel)

if df.empty:
    st.error("El archivo Excel no contiene datos válidos o las columnas necesarias.")
    st.stop()

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
destinos = df['DESTINO'].unique() if 'DESTINO' in df.columns else []
destino_seleccion = st.sidebar.multiselect("Destino", destinos, default=destinos)

# Contenido
contenidos = df['CONTENIDO'].unique() if 'CONTENIDO' in df.columns else []
contenido_seleccion = st.sidebar.multiselect("Contenido", contenidos, default=contenidos)

# Pesos
pnm_seleccion = (0,0)
if 'Peso Neto Manejado' in df.columns:
    min_val, max_val = df['Peso Neto Manejado'].min(), df['Peso Neto Manejado'].max()
    pnm_seleccion = st.sidebar.slider("Peso Neto Manejado (kg)", float(min_val), float(max_val), (float(min_val), float(max_val)))

pne_seleccion = (0,0)
if 'Peso Neto Exportado' in df.columns:
    min_val, max_val = df['Peso Neto Exportado'].min(), df['Peso Neto Exportado'].max()
    pne_seleccion = st.sidebar.slider("Peso Neto Exportado (kg)", float(min_val), float(max_val), (float(min_val), float(max_val)))
    pni_seleccion = (0,0)
if 'Peso Neto Importado' in df.columns:
    min_val, max_val = df['Peso Neto Importado'].min(), df['Peso Neto Importado'].max()
    pni_seleccion = st.sidebar.slider("Peso Neto Importado (kg)", float(min_val), float(max_val), (float(min_val), float(max_val)))

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
if 'Peso Neto Manejado' in df_filtrado.columns:
    df_filtrado = df_filtrado[
        (df_filtrado['Peso Neto Manejado'] >= pnm_seleccion[0]) &
        (df_filtrado['Peso Neto Manejado'] <= pnm_seleccion[1])
    ]
if 'Peso Neto Exportado' in df_filtrado.columns:
    df_filtrado = df_filtrado[
        (df_filtrado['Peso Neto Exportado'] >= pne_seleccion[0]) &
        (df_filtrado['Peso Neto Exportado'] <= pne_seleccion[1])
    ]
if 'Peso Neto Importado' in df_filtrado.columns:
    df_filtrado = df_filtrado[
        (df_filtrado['Peso Neto Importado'] >= pni_seleccion[0]) &
        (df_filtrado['Peso Neto Importado'] <= pni_seleccion[1])
    ]

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
# SECCIONES
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
    if 'DESTINO' in df_filtrado.columns:
        df_p = df_filtrado.groupby("DESTINO")[["peso total (t)"]].sum().reset_index()
        fig_p = px.bar(df_p, x="DESTINO", y="peso total (t)", color_discrete_sequence=[COLOR1])
        st.plotly_chart(fig_p, use_container_width=True)
with tabs[3]:
    seccion_titulo("Mapa 3D Destinos Exportados")
    st.info("No se puede mostrar el mapa 3D porque las columnas de latitud y longitud no existen en el Excel.")
