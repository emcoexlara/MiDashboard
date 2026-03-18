# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import os

# ===== CONFIGURACIÓN DE PÁGINA =====
st.set_page_config(
    page_title="Dashboard Comercio Exterior",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== RUTAS =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_PATH = os.path.join(DATA_DIR, "datos.xlsx")  # asegúrate que tu Excel se llama así

# ===== FUNCIONES DE UTILIDAD =====
def get_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def set_background(png_file):
    """Agrega fondo a Streamlit"""
    b64 = get_base64(png_file)
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{b64}");
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ===== FONDO Y LOGO =====
fondo_path = os.path.join(ASSETS_DIR, "fondo_comercio.jpg")
logo_path = os.path.join(ASSETS_DIR, "logo_empreda.png")

set_background(fondo_path)
st.image(logo_path, width=120)

# ===== TÍTULO =====
st.markdown("""
    <h1 style="color:black; border:2px solid white; padding:10px; text-align:center;">
        Dashboard Comercio Exterior
    </h1>
""", unsafe_allow_html=True)

# ===== CARGA DE DATOS =====
@st.cache_data
def load_data():
    try:
        df = pd.read_excel(DATA_PATH)
        # Normalizar nombres de columnas
        df.columns = [c.strip().upper() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"No se pudo cargar el archivo Excel: {e}")
        return pd.DataFrame()

df = load_data()
if df.empty:
    st.stop()

# ===== FILTROS LATERAL =====
st.sidebar.header("Filtros")
fecha_seleccion = st.sidebar.date_input("Fecha", [])
destino_seleccion = st.sidebar.multiselect("Destino", df['DESTINO'].dropna().unique())
contenido_seleccion = st.sidebar.multiselect("Contenido", df['CONTENIDO'].dropna().unique())

df_filtrado = df.copy()
if fecha_seleccion:
    df_filtrado = df_filtrado[df_filtrado['FECHA'].isin(fecha_seleccion)]
if destino_seleccion:
    df_filtrado = df_filtrado[df_filtrado['DESTINO'].isin(destino_seleccion)]
if contenido_seleccion:
    df_filtrado = df_filtrado[df_filtrado['CONTENIDO'].isin(contenido_seleccion)]

# ===== KPIs =====
col1, col2, col3, col4 = st.columns(4)

col1.metric("Operaciones", len(df_filtrado))
col2.metric("Peso Neto Exportado (t)", f"{df_filtrado['PESO NETO EXPORTADO'].sum():,.2f}")
col3.metric("Peso Neto Importado (t)", f"{df_filtrado['PESO NETO IMPORTADO'].sum():,.2f}")
df_filtrado["PESO TOTAL"] = df_filtrado["PESO NETO EXPORTADO"] + df_filtrado["PESO NETO IMPORTADO"]
col4.metric("Peso Total (t)", f"{df_filtrado['PESO TOTAL'].sum():,.2f}")

# ===== GRÁFICOS =====
st.markdown("### Exportaciones por Destino")
fig_destino = px.bar(df_filtrado.groupby("DESTINO")["PESO NETO EXPORTADO"].sum().reset_index(),
                     x="DESTINO", y="PESO NETO EXPORTADO",
                     color="PESO NETO EXPORTADO", color_continuous_scale="Blues")
st.plotly_chart(fig_destino, use_container_width=True)

st.markdown("### Importaciones por Contenido")
fig_contenido = px.pie(df_filtrado, names="CONTENIDO", values="PESO NETO IMPORTADO")
st.plotly_chart(fig_contenido, use_container_width=True)

# ===== MAPA 3D (OPCIONAL: requiere LATITUD y LONGITUD) =====
if "LATITUD" in df_filtrado.columns and "LONGITUD" in df_filtrado.columns:
    st.markdown("### Mapa de Destinos Exportados (3D)")
    fig_map = px.scatter_3d(df_filtrado,
                            x='LONGITUD', y='LATITUD', z='PESO NETO EXPORTADO',
                            color='DESTINO', size='PESO NETO EXPORTADO',
                            hover_name='DESTINO')
    st.plotly_chart(fig_map, use_container_width=True)
