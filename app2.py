# app_completo.py
import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Control Operacional de Comercio Exterior de Lara",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PALETA CORPORATIVA ---
COLOR_TITULO = "#000000"
COLOR_CUADRO = "#FFFFFF"
COLOR_TEXTO = "#003366"
COLOR_FONDO = "#F0F2F6"  # gris claro de fondo

st.markdown(
    f"""
    <style>
        .stApp {{
            background-color: {COLOR_FONDO};
        }}
        .titulo {{
            color: {COLOR_TITULO};
            font-size: 36px;
            font-weight: bold;
            text-align: center;
            border: 2px solid white;
            padding: 10px;
            border-radius: 10px;
        }}
        .cuadro {{
            background-color: {COLOR_CUADRO};
            padding: 15px;
            border-radius: 10px;
            text-align:center;
        }}
    </style>
    """, unsafe_allow_html=True
)

# --- TÍTULO ---
st.markdown(f"<div class='titulo'>Control Operacional de Comercio Exterior de Lara</div>", unsafe_allow_html=True)

# --- LOGO ---
logo_path = "assets/logo_empresa.png"
if os.path.exists(logo_path):
    st.image(logo_path, width=120)

# --- FUNCIÓN PARA CARGAR DATOS ---
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("data/datos.xlsx")
        # Normalizar nombres
        df.columns = df.columns.str.strip().str.upper().str.replace(" ", "_")
        # Columnas numéricas
        for col in ["PESO_NETO_EXPORTADO", "PESO_NETO_IMPORTADO", "PESO_NETO_MANEJADO"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                df[col] = 0
        return df
    except Exception as e:
        st.error(f"No se pudo cargar el archivo Excel: {e}")
        return pd.DataFrame()

# --- CARGAR DATA ---
df = load_data()
if df.empty:
    st.stop()

df_filtrado = df.copy()

# --- SIDEBAR FILTROS ---
st.sidebar.header("Filtros")
fecha_seleccion = st.sidebar.date_input("Fecha", [])
destino_seleccion = st.sidebar.multiselect("Destino", df['DESTINO'].dropna().unique() if 'DESTINO' in df.columns else [])
contenido_seleccion = st.sidebar.multiselect("Contenido", df['CONTENIDO'].dropna().unique() if 'CONTENIDO' in df.columns else [])

# --- FILTRAR DATA ---
if fecha_seleccion:
    df_filtrado = df_filtrado[df_filtrado['FECHA'].isin(fecha_seleccion)]
if destino_seleccion:
    df_filtrado = df_filtrado[df_filtrado['DESTINO'].isin(destino_seleccion)]
if contenido_seleccion:
    df_filtrado = df_filtrado[df_filtrado['CONTENIDO'].isin(contenido_seleccion)]

# --- KPI METRICS ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"<div class='cuadro'>📦<br>Operaciones<br>{len(df_filtrado)}</div>", unsafe_allow_html=True)

with col2:
    peso_exportado = df_filtrado["PESO_NETO_EXPORTADO"].sum() if "PESO_NETO_EXPORTADO" in df_filtrado.columns else 0
    st.markdown(f"<div class='cuadro'>🌍<br>Peso Neto Exportado (t)<br>{peso_exportado:,.2f}</div>", unsafe_allow_html=True)

with col3:
    peso_importado = df_filtrado["PESO_NETO_IMPORTADO"].sum() if "PESO_NETO_IMPORTADO" in df_filtrado.columns else 0
    st.markdown(f"<div class='cuadro'>📥<br>Peso Neto Importado (t)<br>{peso_importado:,.2f}</div>", unsafe_allow_html=True)

with col4:
    peso_total = df_filtrado["PESO_NETO_MANEJADO"].sum() if "PESO_NETO_MANEJADO" in df_filtrado.columns else 0
    st.markdown(f"<div class='cuadro'>⚖️<br>Peso Total (t)<br>{peso_total:,.2f}</div>", unsafe_allow_html=True)

# --- MAPA 3D DE DESTINOS ---
if 'DESTINO' in df_filtrado.columns:
    # Usar latitud y longitud simuladas si no existen
    if 'LATITUD' not in df_filtrado.columns or 'LONGITUD' not in df_filtrado.columns:
        # Generar coordenadas aleatorias por destino
        import numpy as np
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
        height=600
    )
    st.plotly_chart(fig_map, use_container_width=True)
