# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import base64
from PIL import Image

# ========================
# Configuración de la página
# ========================
st.set_page_config(
    page_title="Control Operacional de Comercio Exterior de Lara",
    layout="wide",
    page_icon="🌎"
)

# ========================
# Función para fondo y logo
# ========================
def get_base64(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Paleta corporativa
COLOR_FONDO = "#F5F5F5"
COLOR_TITULO = "#000000"
COLOR_CUADRO = "#FFFFFF"

# Fondo
fondo_path = "assets/fondo_comercio.jpg"
fondo_base64 = get_base64(fondo_path)
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{fondo_base64}");
        background-size: cover;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Logo
st.sidebar.image("assets/logo_empresa.png", width=120)

# ========================
# Título principal
# ========================
st.markdown(f"<h1 style='color:{COLOR_TITULO}; text-align:center;'>Control Operacional de Comercio Exterior de Lara</h1>", unsafe_allow_html=True)
st.markdown("---")

# ========================
# Cargar datos
# ========================
@st.cache_data
def load_data():
    df = pd.read_excel("data/datos.xlsx")
    df.columns = [c.strip().upper() for c in df.columns]
    
    # Convertir columnas numéricas
    numeric_cols = ["PESO NETO EXPORTADO", "PESO NETO IMPORTADO", "PESO NETO MANEJADO"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Calcular peso total
    df['PESO TOTAL'] = df['PESO NETO EXPORTADO'] + df['PESO NETO IMPORTADO']
    
    # Crear latitud y longitud aproximadas para mapa (si no existen)
    # Para un ejemplo rápido, se asigna coordenadas ficticias a países
    paises = df['DESTINO'].dropna().unique()
    lat_map = {pais: -10 + i*2 for i, pais in enumerate(paises)}
    lon_map = {pais: -70 + i*3 for i, pais in enumerate(paises)}
    df['LATITUD'] = df['DESTINO'].map(lat_map)
    df['LONGITUD'] = df['DESTINO'].map(lon_map)
    
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"No se pudo cargar el archivo Excel: {e}")
    st.stop()

# ========================
# Filtros en sidebar
# ========================
st.sidebar.header("Filtros")
fecha_seleccion = st.sidebar.date_input("Fecha", [])
destino_seleccion = st.sidebar.multiselect("Destino", df['DESTINO'].dropna().unique())
contenido_seleccion = st.sidebar.multiselect("Contenido", df['CONTENIDO'].dropna().unique())

# Aplicar filtros
df_filtrado = df.copy()

if destino_seleccion:
    df_filtrado = df_filtrado[df_filtrado['DESTINO'].isin(destino_seleccion)]
if contenido_seleccion:
    df_filtrado = df_filtrado[df_filtrado['CONTENIDO'].isin(contenido_seleccion)]
if fecha_seleccion:
    df_filtrado = df_filtrado[df_filtrado['FECHA'].isin(fecha_seleccion)]

# ========================
# KPIs en contenedores
# ========================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"<div style='background-color:{COLOR_CUADRO}; padding:15px; border-radius:10px; text-align:center;'>"
        f"<h3>Operaciones</h3>"
        f"<p style='font-size:24px'>{len(df_filtrado)}</p></div>",
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"<div style='background-color:{COLOR_CUADRO}; padding:15px; border-radius:10px; text-align:center;'>"
        f"<h3>Exportado (t)</h3>"
        f"<p style='font-size:24px'>{df_filtrado['PESO NETO EXPORTADO'].sum():,.2f}</p></div>",
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"<div style='background-color:{COLOR_CUADRO}; padding:15px; border-radius:10px; text-align:center;'>"
        f"<h3>Importado (t)</h3>"
        f"<p style='font-size:24px'>{df_filtrado['PESO NETO IMPORTADO'].sum():,.2f}</p></div>",
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        f"<div style='background-color:{COLOR_CUADRO}; padding:15px; border-radius:10px; text-align:center;'>"
        f"<h3>Total (t)</h3>"
        f"<p style='font-size:24px'>{df_filtrado['PESO TOTAL'].sum():,.2f}</p></div>",
        unsafe_allow_html=True
    )

# ========================
# Mostrar tabla de datos filtrada
# ========================
st.dataframe(df_filtrado)

# ========================
# Mapa 3D de destinos exportados
# ========================
if not df_filtrado.empty:
    fig_map = px.scatter_3d(
        df_filtrado,
        x='LONGITUD',
        y='LATITUD',
        z='PESO NETO EXPORTADO',
        color='DESTINO',
        size='PESO NETO EXPORTADO',
        hover_name='DESTINO',
        labels={"LONGITUD":"Longitud", "LATITUD":"Latitud", "PESO NETO EXPORTADO":"Peso Exportado"}
    )
    fig_map.update_layout(height=600, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.info("No hay datos que mostrar en el mapa según los filtros aplicados.")
