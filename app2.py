import streamlit as st
import pandas as pd
import plotly.express as px
import base64

# --- CONFIGURACIONES ---
st.set_page_config(page_title="Control Operacional de Comercio Exterior de Lara",
                   layout="wide")

# --- COLORES CORPORATIVOS ---
COLOR_TITULO = "#000000"
COLOR_CUADRO = "#FFFFFF"
COLOR_METRIC = "#1F77B4"
COLOR_FONDO = "#F5F5F5"

# --- FUNCIONES ---
def get_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def set_background(png_file):
    bin_str = get_base64(png_file)
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{bin_str}");
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# --- FONDO Y LOGO ---
set_background("assets/fondo_comercio.jpg")
st.image("assets/logo_empresa.png", width=150)

# --- TÍTULO ---
st.markdown(f"<h1 style='color:{COLOR_TITULO}; text-align:center;'>Control Operacional de Comercio Exterior de Lara</h1>", unsafe_allow_html=True)
st.markdown("---")

# --- CARGA DE DATOS ---
@st.cache_data
def load_data():
    df = pd.read_excel("data/datos.xlsx")
    # Asegurar que los campos de peso sean numéricos
    for col in ["Peso Neto Exportado", "Peso Neto Importado", "Peso Neto Manejado"]:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

df = load_data()

# --- FILTROS SIDEBAR ---
st.sidebar.header("Filtros")
fecha = st.sidebar.date_input("Fecha")
destino_seleccion = st.sidebar.multiselect("Destino", df['DESTINO'].dropna().unique())
contenido_seleccion = st.sidebar.multiselect("Contenido", df['CONTENIDO'].dropna().unique())

# --- FILTRADO DE DATOS ---
df_filtrado = df.copy()
if destino_seleccion:
    df_filtrado = df_filtrado[df_filtrado['DESTINO'].isin(destino_seleccion)]
if contenido_seleccion:
    df_filtrado = df_filtrado[df_filtrado['CONTENIDO'].isin(contenido_seleccion)]
if fecha:
    df_filtrado = df_filtrado[df_filtrado['FECHA'] == pd.to_datetime(fecha)]

# --- KPIs CON ICONOS ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"<div style='background-color:{COLOR_CUADRO}; padding:20px; border-radius:15px; text-align:center;'>"
                f"📦<h3 style='color:{COLOR_METRIC};'>Operaciones</h3>"
                f"<h2>{len(df_filtrado)}</h2></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div style='background-color:{COLOR_CUADRO}; padding:20px; border-radius:15px; text-align:center;'>"
                f"🌍<h3 style='color:{COLOR_METRIC};'>Peso Neto Exportado (t)</h3>"
                f"<h2>{df_filtrado['Peso Neto Exportado'].sum():,.2f}</h2></div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div style='background-color:{COLOR_CUADRO}; padding:20px; border-radius:15px; text-align:center;'>"
                f"🚛<h3 style='color:{COLOR_METRIC};'>Peso Neto Importado (t)</h3>"
                f"<h2>{df_filtrado['Peso Neto Importado'].sum():,.2f}</h2></div>", unsafe_allow_html=True)
with col4:
    st.markdown(f"<div style='background-color:{COLOR_CUADRO}; padding:20px; border-radius:15px; text-align:center;'>"
                f"⚖️<h3 style='color:{COLOR_METRIC};'>Peso Total (t)</h3>"
                f"<h2>{df_filtrado[['Peso Neto Exportado','Peso Neto Importado']].sum().sum():,.2f}</h2></div>", unsafe_allow_html=True)

st.markdown("---")

# --- MAPA 3D DE DESTINOS ---
if not df_filtrado.empty:
    # Asignar latitud y longitud ficticias si no existen
    if 'LATITUD' not in df_filtrado.columns or 'LONGITUD' not in df_filtrado.columns:
        import numpy as np
        df_filtrado['LATITUD'] = np.random.uniform(-15, 15, len(df_filtrado))
        df_filtrado['LONGITUD'] = np.random.uniform(-70, -60, len(df_filtrado))
        fig_map = px.scatter_3d(df_filtrado, 
                            x='LONGITUD', y='LATITUD', z='Peso Neto Exportado', 
                            color='DESTINO', size='Peso Neto Exportado', 
                            hover_name='DESTINO')
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning("No hay datos para mostrar en el mapa con los filtros seleccionados.")
