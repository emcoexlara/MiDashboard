# app_dashboard_final.py
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import base64
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Control Operacional de Comercio Exterior de Lara", layout="wide")

# --- COLORES ---
COLOR_TITULO = "#003366"
COLOR_CUADRO = "#e6f0ff"
COLOR_FONDO = "#f2f2f2"

# --- FONDO ---
def add_bg(image_file):
    if os.path.exists(image_file):
        with open(image_file, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        st.markdown(f"""
            <style>
            .stApp {{
                background-image: url("data:image/jpg;base64,{encoded}");
                background-size: cover;
            }}
            </style>
        """, unsafe_allow_html=True)
add_bg("assets/fondo_comercio.jpg")

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
    numeric_cols = ["PESO_NETO_EXPORTADO", "PESO_NETO_IMPORTADO", "PESO_NETO_MANEJADO", "CONTENEDORES"]
    for col in numeric_cols:
        if col not in df.columns:
            df[col] = 0
        else:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    # Simulación de coordenadas si no existen
    if "LATITUD" not in df.columns or "LONGITUD" not in df.columns:
        destinos = df['DESTINO'].unique()
        lat_lon = {d: (np.random.uniform(-20,20), np.random.uniform(-20,20)) for d in destinos}
        df['LATITUD'] = df['DESTINO'].map(lambda x: lat_lon.get(x, (0,0))[0])
        df['LONGITUD'] = df['DESTINO'].map(lambda x: lat_lon.get(x, (0,0))[1])
    return df

df = load_data()
df_filtrado = df.copy()

# --- FILTROS SIDEBAR ---
st.sidebar.header("Filtros")
if 'DESTINO' in df.columns:
    destino_seleccion = st.sidebar.multiselect("Destino", df['DESTINO'].dropna().unique())
    if destino_seleccion:
        df_filtrado = df_filtrado[df_filtrado['DESTINO'].isin(destino_seleccion)]
if 'CONTENIDO' in df.columns:
    contenido_seleccion = st.sidebar.multiselect("Contenido", df['CONTENIDO'].dropna().unique())
    if contenido_seleccion:
        df_filtrado = df_filtrado[df_filtrado['CONTENIDO'].isin(contenido_seleccion)]

# --- KPIs CON ICONOS ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("📦 Operaciones", f"{len(df_filtrado):,}")
col2.metric("🌎 Peso Neto Exportado (t)", f"{df_filtrado['PESO_NETO_EXPORTADO'].sum():,.2f}")
col3.metric("🌍 Peso Neto Importado (t)", f"{df_filtrado['PESO_NETO_IMPORTADO'].sum():,.2f}")
col4.metric("⚖️ Peso Total (t)", f"{df_filtrado['PESO_NETO_MANEJADO'].sum():,.2f}")

# --- GRÁFICO 3D POR DESTINO ---
fig_map = px.scatter_3d(
    df_filtrado,
    x='LONGITUD',
    y='LATITUD',
    z='PESO_NETO_EXPORTADO',
    color='DESTINO',
    size='PESO_NETO_EXPORTADO',
    hover_name='DESTINO',
    title="Mapa 3D de Exportaciones por Destino"
)
st.plotly_chart(fig_map, use_container_width=True)

# --- GRÁFICO CONTENEDORES VS TONELADAS ---
if 'CONTENEDORES' in df_filtrado.columns:
    fig_cont = px.bar(
        df_filtrado.groupby('CONTENIDO')['CONTENEDORES', 'PESO_NETO_EXPORTADO'].sum().reset_index(),
        x='CONTENEDORES',
        y='PESO_NETO_EXPORTADO',
        color='CONTENIDO',
        barmode='group',
        title="Contenedores vs Peso Neto Exportado"
    )
    st.plotly_chart(fig_cont, use_container_width=True)
