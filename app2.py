# app2.py
import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import base64

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Control Operacional de Comercio Exterior de Lara",
    page_icon="🌎",
    layout="wide"
)

# --- FUNCIONES AUXILIARES ---
def get_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def set_background(png_file):
    bin_str = get_base64(png_file)
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# --- APLICAR FONDO ---
set_background("assets/fondo_comercio.jpg")

# --- CARGAR LOGO ---
st.sidebar.image("assets/logo_empresa.png", width=120)

# --- CARGAR DATA ---
@st.cache_data
def load_data():
    df = pd.read_excel("data/datos.xlsx")
    # Convertir columnas numéricas
    cols_numeric = ['LLENOS RECIBIDOS (EXPORTADOS)', 'Peso Neto Exportado',
                    'Peso Neto Importado', 'Peso Neto Manejado']
    for col in cols_numeric:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

df = load_data()

# --- FILTROS ---
st.sidebar.header("Filtros")
fecha = st.sidebar.date_input("Fecha")
destino_seleccion = st.sidebar.multiselect("Destino", df['DESTINO'].dropna().unique())
contenido_seleccion = st.sidebar.multiselect("Contenido", df['CONTENIDO'].dropna().unique())

df_filtrado = df.copy()
if destino_seleccion:
    df_filtrado = df_filtrado[df_filtrado['DESTINO'].isin(destino_seleccion)]
if contenido_seleccion:
    df_filtrado = df_filtrado[df_filtrado['CONTENIDO'].isin(contenido_seleccion)]
if fecha:
    df_filtrado = df_filtrado[pd.to_datetime(df_filtrado['FECHA']) == pd.to_datetime(fecha)]

# --- COLORES CORPORATIVOS ---
COLOR_CUADRO = "#ffffff"
COLOR_TEXTO = "#000000"
COLOR_GRAF = "#1f77b4"  # Azul corporativo

# --- TÍTULO ---
st.markdown(
    f"<h1 style='color:{COLOR_TEXTO}; text-align:center;'>Control Operacional de Comercio Exterior de Lara</h1>",
    unsafe_allow_html=True
)

# --- KPIs ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"<div style='background-color:{COLOR_CUADRO}; padding:20px; border-radius:10px; text-align:center;'>"
        f"<img src='https://img.icons8.com/ios-filled/50/000000/container.png'/>"
        f"<h3>Operaciones</h3>"
        f"<h2>{len(df_filtrado):,}</h2>"
        f"</div>",
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"<div style='background-color:{COLOR_CUADRO}; padding:20px; border-radius:10px; text-align:center;'>"
        f"<img src='https://img.icons8.com/ios-filled/50/000000/worldwide-location.png'/>"
        f"<h3>Peso Neto Exportado (t)</h3>"
        f"<h2>{df_filtrado['Peso Neto Exportado'].sum():,.2f}</h2>"
        f"</div>",
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"<div style='background-color:{COLOR_CUADRO}; padding:20px; border-radius:10px; text-align:center;'>"
        f"<img src='https://img.icons8.com/ios-filled/50/000000/import.png'/>"
        f"<h3>Peso Neto Importado (t)</h3>"
        f"<h2>{df_filtrado['Peso Neto Importado'].sum():,.2f}</h2>"
        f"</div>",
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        f"<div style='background-color:{COLOR_CUADRO}; padding:20px; border-radius:10px; text-align:center;'>"
        f"<img src='https://img.icons8.com/ios-filled/50/000000/weight.png'/>"
        f"<h3>Peso Total (t)</h3>"
        f"<h2>{df_filtrado['Peso Neto Manejado'].sum():,.2f}</h2>"
        f"</div>",
        unsafe_allow_html=True
    )

st.markdown("---")
# --- GRÁFICO: CONTENEDORES VS TONELADAS ---
if 'CONTENIDO' in df_filtrado.columns and 'Peso Neto Exportado' in df_filtrado.columns:
    df_grouped = df_filtrado.groupby('CONTENIDO')[['LLENOS RECIBIDOS (EXPORTADOS)', 'Peso Neto Exportado']].sum().reset_index()
    fig1 = px.bar(
        df_grouped,
        x='CONTENIDO',
        y='LLENOS RECIBIDOS (EXPORTADOS)',
        text='Peso Neto Exportado',
        color_discrete_sequence=[COLOR_GRAF],
        labels={'LLENOS RECIBIDOS (EXPORTADOS)': 'Contenedores', 'Peso Neto Exportado': 'Toneladas'}
    )
    st.plotly_chart(fig1, use_container_width=True)

# --- GRÁFICO: EXPORTACIONES POR DESTINO ---
if 'DESTINO' in df_filtrado.columns and 'Peso Neto Exportado' in df_filtrado.columns:
    df_destino = df_filtrado.groupby('DESTINO')['Peso Neto Exportado'].sum().reset_index()
    fig2 = px.pie(
        df_destino,
        values='Peso Neto Exportado',
        names='DESTINO',
        color_discrete_sequence=px.colors.sequential.Blues
    )
    st.plotly_chart(fig2, use_container_width=True)

# --- MAPA 3D DE EXPORTACIONES ---
if 'DESTINO' in df_filtrado.columns:
    # Generamos coordenadas ficticias si no existen
    if 'LATITUD' not in df_filtrado.columns or 'LONGITUD' not in df_filtrado.columns:
        destinos_unicos = df_filtrado['DESTINO'].unique()
        import numpy as np
        lat_dict = {d: 10 + np.random.rand() for d in destinos_unicos}
        lon_dict = {d: -70 + np.random.rand() for d in destinos_unicos}
        df_filtrado['LATITUD'] = df_filtrado['DESTINO'].map(lat_dict)
        df_filtrado['LONGITUD'] = df_filtrado['DESTINO'].map(lon_dict)

    fig_map = px.scatter_3d(
        df_filtrado,
        x='LONGITUD',
        y='LATITUD',
        z='Peso Neto Exportado',
        color='DESTINO',
        size='Peso Neto Exportado',
        hover_name='DESTINO',
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    st.plotly_chart(fig_map, use_container_width=True)
