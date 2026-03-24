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
    <div style='background:{COLOR_TITULO}; padding:20px; border-radius:12px;
    text-align:center; color:white; border:3px solid #00BFFF; box-shadow:0px 4px 12px rgba(0,0,0,0.25);'>
    🚢<h3 style='margin:0;'>Operaciones</h3>
    <h1 style='margin:5px 0 0 0;'>{len(df_filtrado)}</h1>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style='background:{COLOR_TITULO}; padding:20px; border-radius:12px;
    text-align:center; color:white; border:3px solid #28A745; box-shadow:0px 4px 12px rgba(0,0,0,0.25);'>
    🌍<h3 style='margin:0;'>Exportado</h3>
    <h1 style='margin:5px 0 0 0;'>{df_filtrado['Peso Neto Exportado'].sum():,.0f}</h1>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div style='background:{COLOR_TITULO}; padding:20px; border-radius:12px;
    text-align:center; color:white; border:3px solid #FFC107; box-shadow:0px 4px 12px rgba(0,0,0,0.25);'>
    📦<h3 style='margin:0;'>Importado</h3>
    <h1 style='margin:5px 0 0 0;'>{df_filtrado['Peso Neto Importado'].sum():,.0f}</h1>
    </div>
    """, unsafe_allow_html=True)

with col4:
    total = df_filtrado['Peso Neto Manejado'].sum()
    st.markdown(f"""
    <div style='background:{COLOR_TITULO}; padding:20px; border-radius:12px;
    text-align:center; color:white; border:3px solid #FF5733; box-shadow:0px 4px 12px rgba(0,0,0,0.25);'>
    ⚖️<h3 style='margin:0;'>Total</h3>
    <h1 style='margin:5px 0 0 0;'>{total:,.0f}</h1>
    </div>
    """, unsafe_allow_html=True)
import plotly.express as px

TEMPLATE_PRO = dict(
    layout=dict(
        font=dict(family="Arial", size=14, color="black"),
        title=dict(font=dict(size=20, color="black")),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
)
def contenedor_blur(fig):
    st.markdown("""
    <div style="
        background: rgba(255,255,255,0.75);
        backdrop-filter: blur(6px);
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.2);
        margin-bottom: 20px;
    ">
    """, unsafe_allow_html=True)

    contenedor_blur(fig1)
    contenedor_blur(fig2)

    st.markdown("</div>", unsafe_allow_html=True)
# ------------------------------
# GRÁFICO POR PAÍS
# ------------------------------
df_paises = df_filtrado.groupby('DESTINO')['Peso Neto Exportado'].sum().reset_index()
# ------------------------------
# ESTILO FONDO BLANCO DIFUMINADO
# ------------------------------
def aplicar_fondo_blanco(fig):
    fig.update_layout(
        paper_bgcolor="rgba(255,255,255,0.90)",  # fondo general
        plot_bgcolor="rgba(255,255,255,0.80)",   # área del gráfico
        font=dict(family="Arial Black", size=14, color="black")
    )
    return fig
fig1 = px.bar(
    df_paises,
    x='DESTINO',
    y='Peso Neto Exportado',
    text='Peso Neto Exportado'
)

fig1.update_traces(
    texttemplate='%{text:,.0f}',
    textposition='outside',
    marker_line_width=1.5
)

fig1.update_layout(
    TEMPLATE_PRO["layout"],
    title="Exportaciones por País",
    title_x=0.5,
    font=dict(size=14, family="Arial Black"),
)

# Marca de agua
fig1.add_annotation(
    text="COMERCIO EXTERIOR",
    xref="paper", yref="paper",
    x=0.5, y=0.5,
    showarrow=False,
    font=dict(size=40, color="rgba(0,0,0,0.05)"),
    align="center"
)

fig1 = aplicar_fondo_blanco(fig1)
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
    barmode='group'
)

fig2.update_layout(
    TEMPLATE_PRO["layout"],
    title="Contenedores vs Toneladas",
    title_x=0.5,
    font=dict(size=14, family="Arial Black"),
)

# Marca de agua
fig2.add_annotation(
    text="LOGÍSTICA INTERNACIONAL",
    xref="paper", yref="paper",
    x=0.5, y=0.5,
    showarrow=False,
    font=dict(size=40, color="rgba(0,0,0,0.05)")
)

fig2 = aplicar_fondo_blanco(fig2)
st.plotly_chart(fig2, use_container_width=True)
# ------------------------------
# MAPA DE EXPORTACIONES (PROFESIONAL)
# ------------------------------

import plotly.express as px

# Agrupar datos por país
df_map = df_filtrado.groupby('DESTINO', as_index=False)['Peso Neto Exportado'].sum()

# Crear mapa
fig_map = px.scatter_geo(
    df_map,
    locations='DESTINO',
    locationmode='country names',
    size='Peso Neto Exportado',
    hover_name='DESTINO',
    size_max=40,
    projection='natural earth'
)

# Diseño profesional
fig_map.update_layout(

    title=dict(
        text="Mapa de Exportaciones por País",
        x=0.5,
        font=dict(
            family="Arial Black",
            size=20,
            color="black"
        )
    ),

    # Fondo blanco elegante (SIN ERROR)
    paper_bgcolor="rgba(255,255,255,0.95)",

    geo=dict(
        bgcolor="rgba(255,255,255,0.95)",  # 🔥 clave para evitar franjas
        showland=True,
        landcolor="#F2F3F4",
        showocean=True,
        oceancolor="#D6EAF8",
        showcountries=True,
        countrycolor="#A6ACAF"
    )
)

# Marca de agua (opcional profesional)
fig_map.add_annotation(
    text="COMERCIO EXTERIOR",
    x=0.5,
    y=0.5,
    xref="paper",
    yref="paper",
    showarrow=False,
    font=dict(
        size=40,
        color="rgba(0,0,0,0.05)"
    )
)

# Mostrar mapa
st.plotly_chart(fig_map, use_container_width=True)

