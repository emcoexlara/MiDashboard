import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import os

# ===== CONFIGURACIÓN DE PÁGINA =====
st.set_page_config(
    page_title="Control Operacional de Comercio Exterior de Lara",
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
        # Calcular peso total
        df["PESO TOTAL"] = df.get("PESO NETO EXPORTADO", 0) + df.get("PESO NETO IMPORTADO", 0)
        return df
    except Exception as e:
        st.error(f"No se pudo cargar el archivo Excel: {e}")
        return pd.DataFrame()

df = load_data()
if df.empty:
    st.stop()

# ===== FILTROS LATERAL =====
st.sidebar.header("Filtros")
fecha_seleccion = st.sidebar.date_input("Fecha")
destino_seleccion = st.sidebar.multiselect("Destino", df['DESTINO'].dropna().unique() if 'DESTINO' in df.columns else [])
contenido_seleccion = st.sidebar.multiselect("Contenido", df['CONTENIDO'].dropna().unique() if 'CONTENIDO' in df.columns else [])

df_filtrado = df.copy()
if fecha_seleccion:
    if isinstance(fecha_seleccion, list):
        df_filtrado = df_filtrado[df_filtrado['FECHA'].isin(fecha_seleccion)]
    else:
        df_filtrado = df_filtrado[df_filtrado['FECHA'] == fecha_seleccion]
if destino_seleccion and 'DESTINO' in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado['DESTINO'].isin(destino_seleccion)]
if contenido_seleccion and 'CONTENIDO' in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado['CONTENIDO'].isin(contenido_seleccion)]

# ===== KPIs EJECUTIVOS CON ICONOS =====
st.markdown("### Resumen de Operaciones")
col1, col2, col3, col4 = st.columns(4)

kpi_style = "background-color:white; padding:15px; border-radius:10px; text-align:center;"

col1.markdown(f"""
<div style="{kpi_style}">
<h3>📦 Operaciones</h3>
<p style="font-size:24px;">{len(df_filtrado):,}</p>
</div>
""", unsafe_allow_html=True)

col2.markdown(f"""
<div style="{kpi_style}">
<h3>🌍 Exportaciones (t)</h3>
<p style="font-size:24px;">{df_filtrado['PESO NETO EXPORTADO'].sum():,.2f}</p>
</div>
""", unsafe_allow_html=True)

col3.markdown(f"""
<div style="{kpi_style}">
<h3>🏗️ Importaciones (t)</h3>
<p style="font-size:24px;">{df_filtrado['PESO NETO IMPORTADO'].sum():,.2f}</p>
</div>
""", unsafe_allow_html=True)

col4.markdown(f"""
<div style="{kpi_style}">
<h3>⚖️ Total (t)</h3>
<p style="font-size:24px;">{df_filtrado['PESO TOTAL'].sum():,.2f}</p>
</div>
""", unsafe_allow_html=True)
# ===== GRÁFICOS PROFESIONALES =====
st.markdown("### Exportaciones por Destino")
if "DESTINO" in df_filtrado.columns and "PESO NETO EXPORTADO" in df_filtrado.columns:
    fig_destino = px.bar(
        df_filtrado.groupby("DESTINO")["PESO NETO EXPORTADO"].sum().reset_index(),
        x="DESTINO",
        y="PESO NETO EXPORTADO",
        color="PESO NETO EXPORTADO",
        color_continuous_scale="Blues",
        title="Exportaciones por Destino"
    )
    st.plotly_chart(fig_destino, use_container_width=True)

st.markdown("### Importaciones por Contenido")
if "CONTENIDO" in df_filtrado.columns and "PESO NETO IMPORTADO" in df_filtrado.columns:
    fig_contenido = px.pie(
        df_filtrado,
        names="CONTENIDO",
        values="PESO NETO IMPORTADO",
        title="Distribución de Importaciones por Contenido"
    )
    st.plotly_chart(fig_contenido, use_container_width=True)

# ===== MAPA 3D DE DESTINOS =====
if "LATITUD" in df_filtrado.columns and "LONGITUD" in df_filtrado.columns and "PESO NETO EXPORTADO" in df_filtrado.columns:
    st.markdown("### Mapa 3D de Destinos Exportados")
    fig_map = px.scatter_3d(
        df_filtrado,
        x='LONGITUD',
        y='LATITUD',
        z='PESO NETO EXPORTADO',
        color='DESTINO' if 'DESTINO' in df_filtrado.columns else None,
        size='PESO NETO EXPORTADO',
        hover_name='DESTINO' if 'DESTINO' in df_filtrado.columns else None,
        title="Exportaciones por Destino"
    )
    st.plotly_chart(fig_map, use_container_width=True)
