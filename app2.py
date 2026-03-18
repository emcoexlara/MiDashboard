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
DATA_PATH = os.path.join(DATA_DIR, "datos.xlsx")  # tu archivo Excel

# ===== FUNCIONES =====
def get_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def set_background(png_file):
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
logo_path = os.path.join(ASSETS_DIR, "logo_empresa.png")

if os.path.exists(fondo_path):
    set_background(fondo_path)

if os.path.exists(logo_path):
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
        df.columns = [c.strip().upper() for c in df.columns]
        # Convertir columnas de peso a números
        for col in ["PESO NETO EXPORTADO", "PESO NETO IMPORTADO"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
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
destino_seleccion = st.sidebar.multiselect("Destino", df['DESTINO'].dropna().unique() if 'DESTINO' in df.columns else [])
contenido_seleccion = st.sidebar.multiselect("Contenido", df['CONTENIDO'].dropna().unique() if 'CONTENIDO' in df.columns else [])

df_filtrado = df.copy()
if fecha_seleccion:
    df_filtrado = df_filtrado[df_filtrado['FECHA'].isin(fecha_seleccion)]
if destino_seleccion and 'DESTINO' in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado['DESTINO'].isin(destino_seleccion)]
if contenido_seleccion and 'CONTENIDO' in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado['CONTENIDO'].isin(contenido_seleccion)]

# ===== KPIs ESTÉTICOS =====
df_filtrado["PESO TOTAL"] = df_filtrado.get("PESO NETO EXPORTADO", 0) + df_filtrado.get("PESO NETO IMPORTADO", 0)
col1, col2, col3, col4 = st.columns(4)

col1.metric("Operaciones", len(df_filtrado))
col2.metric("Peso Neto Exportado (t)", f"{df_filtrado.get('PESO NETO EXPORTADO', pd.Series([0])).sum():,.2f}")
col3.metric("Peso Neto Importado (t)", f"{df_filtrado.get('PESO NETO IMPORTADO', pd.Series([0])).sum():,.2f}")
col4.metric("Peso Total (t)", f"{df_filtrado.get('PESO TOTAL', pd.Series([0])).sum():,.2f}")

# ===== GRÁFICOS =====
st.markdown("### Exportaciones por Destino")
if "DESTINO" in df_filtrado.columns and "PESO NETO EXPORTADO" in df_filtrado.columns:
    fig_destino = px.bar(
        df_filtrado.groupby("DESTINO")["PESO NETO EXPORTADO"].sum().reset_index(),
        x="DESTINO",
        y="PESO NETO EXPORTADO",
        color="PESO NETO EXPORTADO",
        color_continuous_scale="Blues"
    )
    st.plotly_chart(fig_destino, use_container_width=True)

st.markdown("### Importaciones por Contenido")
if "CONTENIDO" in df_filtrado.columns and "PESO NETO IMPORTADO" in df_filtrado.columns:
    fig_contenido = px.pie(
        df_filtrado,
        names="CONTENIDO",
        values="PESO NETO IMPORTADO"
    )
    st.plotly_chart(fig_contenido, use_container_width=True)
    # ===== MAPA 3D (OPCIONAL) =====
if "LATITUD" in df_filtrado.columns and "LONGITUD" in df_filtrado.columns and "PESO NETO EXPORTADO" in df_filtrado.columns:
    st.markdown("### Mapa de Destinos Exportados (3D)")
    fig_map = px.scatter_3d(
        df_filtrado,
        x='LONGITUD',
        y='LATITUD',
        z='PESO NETO EXPORTADO',
        color='DESTINO' if 'DESTINO' in df_filtrado.columns else None,
        size='PESO NETO EXPORTADO',
        hover_name='DESTINO' if 'DESTINO' in df_filtrado.columns else None
    )
    st.plotly_chart(fig_map, use_container_width=True)
