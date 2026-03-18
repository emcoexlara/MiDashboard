# app_graficos_prioritarios.py
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64
import numpy as np

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Control Operacional de Comercio Exterior de Lara",
    layout="wide"
)

# --- COLORES ---
COLOR_TITULO = "#000000"
COLOR_CUADRO = "#FFFFFF"

# --- FONDO ---
def add_bg_from_local(image_file):
    if os.path.exists(image_file):
        with open(image_file, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/jpg;base64,{encoded}");
                background-size: cover;
            }}
            </style>
            """, unsafe_allow_html=True
        )

add_bg_from_local("assets/fondo_comercio.jpg")

# --- LOGO ---
if os.path.exists("assets/logo_empresa.png"):
    st.image("assets/logo_empresa.png", width=120)

# --- TÍTULO ---
st.markdown(f"<h1 style='color:{COLOR_TITULO}; text-align:center'>Control Operacional de Comercio Exterior de Lara</h1>", unsafe_allow_html=True)

# --- CARGA DE DATOS ---
@st.cache_data
def load_data():
    df = pd.read_excel("data/datos.xlsx")
    df.columns = df.columns.str.strip().str.upper().str.replace(" ", "_")
    # Aseguramos columnas numéricas
    for col in ["PESO_NETO_EXPORTADO", "PESO_NETO_IMPORTADO", "PESO_NETO_MANEJADO", "CONTENEDORES"]:
        if col not in df.columns:
            df[col] = 0
        else:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

df = load_data()
df_filtrado = df.copy()

# --- FILTROS SIDEBAR ---
st.sidebar.header("Filtros")
destino_seleccion = st.sidebar.multiselect("Destino", df['DESTINO'].dropna().unique() if 'DESTINO' in df.columns else [])
contenido_seleccion = st.sidebar.multiselect("Contenido", df['CONTENIDO'].dropna().unique() if 'CONTENIDO' in df.columns else [])

if destino_seleccion:
    df_filtrado = df_filtrado[df_filtrado['DESTINO'].isin(destino_seleccion)]
if contenido_seleccion:
    df_filtrado = df_filtrado[df_filtrado['CONTENIDO'].isin(contenido_seleccion)]

# --- GRÁFICO 3D POR PAÍS ---
if 'DESTINO' in df_filtrado.columns:
    if 'LATITUD' not in df_filtrado.columns or 'LONGITUD' not in df_filtrado.columns:
        destinos = df_filtrado['DESTINO'].unique()
        coords = {dest: (np.random.uniform(-20,20), np.random.uniform(-100,-60)) for dest in destinos}
        df_filtrado['LATITUD'] = df_filtrado['DESTINO'].map(lambda x: coords[x][0])
        df_filtrado['LONGITUD'] = df_filtrado['DESTINO'].map(lambda x: coords[x][1])

    fig_map = px.scatter_3d(
        df_filtrado,
        x='LONGITUD',
        y='LATITUD',
        z='PESO_NETO_EXPORTADO',
        color='DESTINO',
        size='PESO_NETO_EXPORTADO',
        hover_name='DESTINO',
        height=600,
        title="Mapa 3D por Destino y Peso Exportado"
    )
    st.plotly_chart(fig_map, use_container_width=True)

# --- GRÁFICO DE CONTENEDORES VS TONELADA ---
if 'CONTENEDORES' in df_filtrado.columns and 'PESO_NETO_MANEJADO' in df_filtrado.columns:
    fig_contenedores = px.scatter(
        df_filtrado,
        x='CONTENEDORES',
        y='PESO_NETO_MANEJADO',
        color='DESTINO',
        size='PESO_NETO_MANEJADO',
        hover_name='DESTINO',
        title="Contenedores vs Toneladas Manejadas",
        height=500
    )
    st.plotly_chart(fig_contenedores, use_container_width=True)
