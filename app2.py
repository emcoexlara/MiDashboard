import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import os
from pathlib import Path

# ------------------------------
# CONFIGURACIÓN GENERAL
# ------------------------------
st.set_page_config(layout="wide")

# ------------------------------
# COLORES CORPORATIVOS
# ------------------------------
COLOR_TITULO = "#1F4E79"
COLOR_CUADRO = "#F2F2F2"
COLOR_FONDO = "#f5f5f5"
COLOR_CUADRO = "#003366"  # azul corporativo
COLOR_ICONO = "#FFD700"   # dorado

# ------------------------------
# FONDO
# ------------------------------
def set_background(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
    """, unsafe_allow_html=True)

set_background("assets/fondo_comercio.jpg")
st.markdown("""
<style>
h1 {
    font-size: 32px !important;
    font-weight: 700 !important;
}
h4 {
    margin-bottom: 5px;
}
</style>
""", unsafe_allow_html=True)
# ------------------------------
# LOGO
# ------------------------------
col_logo, col_titulo = st.columns([1, 5])

with col_logo:
    st.image("assets/logo_empresa.png", width=100)

with col_titulo:
    st.markdown(f"""
    <div style='display:flex; align-items:center; height:100%;'>
        <h1 style='color:{COLOR_TITULO}; margin:0;'>
        Control Operacional de Comercio Exterior de Lara
        </h1>
    </div>
    """, unsafe_allow_html=True)
# ------------------------------
# CARGA AUTOMÁTICA DE DATOS
# ------------------------------
@st.cache_data
def load_data(file_path, last_modified):
    df = pd.read_excel(file_path)
    return df

file_path = "data/datos.xlsx"
last_modified = os.path.getmtime(file_path)

# ✅ PRIMERO: cargar datos
df = load_data(file_path, last_modified)

# ✅ DESPUÉS: trabajar con df
df.columns = df.columns.str.strip()

columnas_requeridas = [
    'DESTINO',
    'Peso Neto Exportado',
    'Peso Neto Importado',
    'Peso Neto Manejado'
]

faltantes = [col for col in columnas_requeridas if col not in df.columns]

if faltantes:
    st.error(f"❌ Faltan columnas en el Excel: {faltantes}")
    st.stop()

for col in columnas_requeridas[1:]:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

df_filtrado = df.copy()
# ------------------------------
# VALIDACIÓN DE COLUMNAS
# ------------------------------

# Limpiar nombres de columnas (elimina espacios ocultos)
df.columns = df.columns.str.strip()

# Columnas obligatorias
columnas_requeridas = [
    'DESTINO',
    'Peso Neto Exportado',
    'Peso Neto Importado',
    'Peso Neto Manejado'
]

# Verificar si faltan columnas
faltantes = [col for col in columnas_requeridas if col not in df.columns]

if faltantes:
    st.error(f"❌ Faltan columnas en el Excel: {faltantes}")
    st.stop()

# Convertir columnas a numérico (evita errores y ceros)
for col in columnas_requeridas[1:]:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# Crear df_filtrado correctamente
df_filtrado = df.copy()
# ------------------------------
# LIMPIEZA DE DATOS
# ------------------------------
df.columns = df.columns.str.strip()

df['Peso Neto Exportado'] = pd.to_numeric(df['Peso Neto Exportado'], errors='coerce').fillna(0)
df['Peso Neto Importado'] = pd.to_numeric(df['Peso Neto Importado'], errors='coerce').fillna(0)
df['Peso Neto Manejado'] = pd.to_numeric(df['Peso Neto Manejado'], errors='coerce').fillna(0)

df_filtrado = df.copy()
# ------------------------------
# MÉTRICAS
col1, col2, col3, col4 = st.columns(4)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div style='background:{COLOR_TITULO}; padding:15px; border-radius:10px; text-align:center; color:white; box-shadow:0px 4px 10px rgba(0,0,0,0.2);'>
    🚢<h4>Operaciones</h4>
    <h2>{len(df_filtrado)}</h2>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style='background:{COLOR_TITULO}; padding:15px; border-radius:10px; text-align:center; color:white; box-shadow:0px 4px 10px rgba(0,0,0,0.2);'>
    🌍<h4>Exportado</h4>
    <h2>{df_filtrado['Peso Neto Exportado'].sum():,.2f}</h2>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div style='background:{COLOR_TITULO}; padding:15px; border-radius:10px; text-align:center; color:white; box-shadow:0px 4px 10px rgba(0,0,0,0.2);'>
    📦<h4>Importado</h4>
    <h2>{df_filtrado['Peso Neto Importado'].sum():,.2f}</h2>
    </div>
    """, unsafe_allow_html=True)

with col4:
    total = df_filtrado['Peso Neto Manejado'].sum()
    st.markdown(f"""
    <div style='background:{COLOR_TITULO}; padding:15px; border-radius:10px; text-align:center; color:white; box-shadow:0px 4px 10px rgba(0,0,0,0.2);'>
    ⚖️<h4>Total</h4>
    <h2>{total:,.2f}</h2>
    </div>
    """, unsafe_allow_html=True)

# ------------------------------
# GRÁFICO POR PAÍS
# ------------------------------
df_pais = df_filtrado.groupby('DESTINO')['Peso Neto Exportado'].sum().reset_index()

fig1 = px.bar(df_pais, x='DESTINO', y='Peso Neto Exportado', title="Exportaciones por País")
st.plotly_chart(fig1, use_container_width=True)

# ------------------------------
# CONTENEDORES VS TONELADAS
# ------------------------------
if 'CONTENIDO' in df_filtrado.columns and 'LLENOS RECIBIDOS (EXPORTADOS)' in df_filtrado.columns:

    df_cont = df_filtrado.groupby('CONTENIDO')[['LLENOS RECIBIDOS (EXPORTADOS)', 'Peso Neto Exportado']].sum().reset_index()

    fig2 = px.bar(
        df_cont,
        x='CONTENIDO',
        y=['LLENOS RECIBIDOS (EXPORTADOS)', 'Peso Neto Exportado'],
        barmode='group',
        title="Contenedores vs Toneladas"
    )
    st.plotly_chart(fig2, use_container_width=True)

# ------------------------------
# MAPA (SIN 3D - CORREGIDO)
# ------------------------------
df_map = df_filtrado.groupby('DESTINO', as_index=False)['Peso Neto Exportado'].sum()
fig_map = px.choropleth(
    data_frame=df_map,
    locations="DESTINO",
    locationmode="country names",
    color="Peso Neto Exportado",
    hover_name="DESTINO",
    color_continuous_scale=px.colors.sequential.Plasma,
    template="plotly_white"
)

fig_map.update_layout(
    margin={"r":0,"t":0,"l":0,"b":0},
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)"
)

st.plotly_chart(fig_map, use_container_width=True)
