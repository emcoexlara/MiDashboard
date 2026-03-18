import streamlit as st
import pandas as pd
import plotly.express as px
import base64
from PIL import Image
import os

# --- CONFIGURACIÓN GENERAL ---
st.set_page_config(page_title="Control Operacional de Comercio Exterior de Lara", layout="wide")

# --- COLORES CORPORATIVOS ---
COLOR_FONDO = "#f0f2f6"
COLOR_TITULO = "#1f4e79"
COLOR_CUADRO = "#ffffff"
COLOR_ICONO = "#1f77b4"

# --- FONDO Y LOGO ---
def get_base64(file):
    with open(file, "rb") as f:
        return base64.b64encode(f.read()).decode()

fondo_path = "assets/fondo_comercio.jpg"
logo_path = "assets/logo_empresa.png"

if os.path.exists(fondo_path):
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

# Logo y título
col1, col2 = st.columns([1, 5])
with col1:
    if os.path.exists(logo_path):
        st.image(logo_path, width=120)
with col2:
    st.markdown(f"<h1 style='color:{COLOR_TITULO};'>Control Operacional de Comercio Exterior de Lara</h1>", unsafe_allow_html=True)

# --- CARGA DE DATOS ---
@st.cache_data
def load_data():
    df = pd.read_excel("data/datos.xlsx")
    # Convertir a numérico los pesos
    for col in ["Peso Neto Exportado", "Peso Neto Importado", "Peso Neto Manejado"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

df = load_data()

# --- FILTROS LATERALES ---
st.sidebar.header("Filtros")
destino_seleccion = st.sidebar.multiselect("Destino", df['DESTINO'].dropna().unique()) if 'DESTINO' in df.columns else []
contenido_seleccion = st.sidebar.multiselect("Contenido", df['CONTENIDO'].dropna().unique()) if 'CONTENIDO' in df.columns else []

df_filtrado = df.copy()
if destino_seleccion:
    df_filtrado = df_filtrado[df_filtrado['DESTINO'].isin(destino_seleccion)]
if contenido_seleccion:
    df_filtrado = df_filtrado[df_filtrado['CONTENIDO'].isin(contenido_seleccion)]

# --- KPIs ---
col_op, col_exp, col_imp, col_tot = st.columns(4)

with col_op:
    st.markdown(f"<div style='background-color:{COLOR_CUADRO}; padding:15px; border-radius:10px; text-align:center;'>"
                f"<h3 style='color:{COLOR_ICONO};'>📦 Operaciones</h3>"
                f"<h2>{len(df_filtrado)}</h2></div>", unsafe_allow_html=True)

with col_exp:
    st.markdown(f"<div style='background-color:{COLOR_CUADRO}; padding:15px; border-radius:10px; text-align:center;'>"
                f"<h3 style='color:{COLOR_ICONO};'>🌎 Peso Neto Exportado (t)</h3>"
                f"<h2>{df_filtrado['Peso Neto Exportado'].sum():,.2f}</h2></div>", unsafe_allow_html=True)

with col_imp:
    st.markdown(f"<div style='background-color:{COLOR_CUADRO}; padding:15px; border-radius:10px; text-align:center;'>"
                f"<h3 style='color:{COLOR_ICONO};'>📥 Peso Neto Importado (t)</h3>"
                f"<h2>{df_filtrado['Peso Neto Importado'].sum():,.2f}</h2></div>", unsafe_allow_html=True)

with col_tot:
    st.markdown(f"<div style='background-color:{COLOR_CUADRO}; padding:15px; border-radius:10px; text-align:center;'>"
                f"<h3 style='color:{COLOR_ICONO};'>⚖️ Peso Total (t)</h3>"
                f"<h2>{df_filtrado['Peso Neto Manejado'].sum():,.2f}</h2></div>", unsafe_allow_html=True)

# --- GRÁFICO CONTENEDORES VS TONELADAS ---
if 'CONTENIDO' in df_filtrado.columns:
    df_graf = df_filtrado.groupby('CONTENIDO')[['LLENOS RECIBIDOS (EXPORTADOS)', 'Peso Neto Exportado']].sum().reset_index()
    fig_bar = px.bar(df_graf,
                     x='CONTENIDO',
                     y='LLENOS RECIBIDOS (EXPORTADOS)',
                     text='Peso Neto Exportado',
                     labels={'LLENOS RECIBIDOS (EXPORTADOS)': 'Contenedores', 'Peso Neto Exportado': 'Toneladas'},
                     title="Contenedores vs Peso Neto Exportado")
    st.plotly_chart(fig_bar, use_container_width=True)
    # --- MAPA 3D DESTINOS ---
if 'LATITUD' in df_filtrado.columns and 'LONGITUD' in df_filtrado.columns:
    fig_map = px.scatter_3d(df_filtrado,
                            x='LONGITUD',
                            y='LATITUD',
                            z='Peso Neto Exportado',
                            color='DESTINO',
                            size='Peso Neto Exportado',
                            hover_name='DESTINO',
                            title="Mapa 3D de Destinos")
    st.plotly_chart(fig_map, use_container_width=True)
