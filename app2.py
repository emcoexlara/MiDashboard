import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import os
from pathlib import Path
# Cargar archivo
df = pd.read_excel("datos.xlsx")

# ----------------------------
# 1️⃣ Cargar Excel completo
# ----------------------------
df = pd.read_excel("datos.xlsx", dtype={'Exportado': float, 'Importado': float})

# ----------------------------
# 2️⃣ Normalizar columna Destino
# ----------------------------
df['Destino'] = df['Destino'].astype(str).str.strip().str.upper()

# ----------------------------
# 3️⃣ Calcular Totales exactos
# ----------------------------
df['Total'] = df['Exportado'] + df['Importado']

# ----------------------------
# 4️⃣ Crear filtro de destinos único
# ----------------------------
filtros_destino = sorted(df['Destino'].unique())  # Lista única para filtros

# ----------------------------
# 5️⃣ Agrupar datos para gráficos/tablas resumidas
# ----------------------------
df_agrupado = df.groupby('Destino', as_index=False).agg({
    'Exportado': 'sum',
    'Importado': 'sum',
    'Total': 'sum'
})

# ----------------------------
# 6️⃣ Mostrar datos completos en el dashboard
# ----------------------------
st.title("Dashboard de Comercio Exterior")
st.subheader("Datos completos por destino")
st.dataframe(df)  # Muestra todas las filas

st.subheader("Datos resumidos por destino")
st.dataframe(df_agrupado)  # Muestra totales agrupados

# ----------------------------
# 7️⃣ Opcional: filtro interactivo
# ----------------------------
destino_seleccionado = st.selectbox("Selecciona un destino:", filtros_destino)
df_filtrado = df[df['Destino'] == destino_seleccionado]
st.dataframe(df_filtrado)  # Solo filas del destino seleccionado
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
# TEMPLATE PROFESIONAL PARA GRÁFICOS
# ------------------------------
TEMPLATE_PRO = dict(
    layout=dict(
        font=dict(family="Arial", size=14, color="black"),
        title=dict(font=dict(size=20, color="black")),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
)
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

# Crear ID único para identificar registros duplicados
df['id_unico'] = df['DESTINO'].astype(str) + "_" + \
                 df['FECHA'].astype(str) + "_" + \
                 df['TIPO DE CARGA'].astype(str)

# Eliminar duplicados basados en ese ID
df = df.drop_duplicates(subset=['id_unico'])
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
# FILTROS DINÁMICOS
# ------------------------------

st.sidebar.markdown("## 🔎 Filtros")

# Asegurar formato de fecha
df['FECHA'] = pd.to_datetime(df['FECHA'], errors='coerce')

# FILTRO POR FECHA
fecha_min = df['FECHA'].min()
fecha_max = df['FECHA'].max()

rango_fecha = st.sidebar.date_input(
    "Rango de Fecha",
    [fecha_min, fecha_max]
)

# FILTRO DESTINO
destinos = st.sidebar.multiselect(
    "Destino",
    options=sorted(df['DESTINO'].dropna().unique()),
    default=sorted(df['DESTINO'].dropna().unique())
)

# FILTRO TIPO DE CARGA
tipos_carga = st.sidebar.multiselect(
    "Tipo de Carga",
    options=sorted(df['TIPO DE CARGA'].dropna().unique()),
    default=sorted(df['TIPO DE CARGA'].dropna().unique())
)

# ------------------------------
# APLICAR FILTROS
# ------------------------------

df_filtrado = df.copy()

# Fecha
if len(rango_fecha) == 2:
    df_filtrado = df_filtrado[
        (df_filtrado['FECHA'] >= pd.to_datetime(rango_fecha[0])) &
        (df_filtrado['FECHA'] <= pd.to_datetime(rango_fecha[1]))
    ]

# Destino
if destinos:
    df_filtrado = df_filtrado[df_filtrado['DESTINO'].isin(destinos)]

# Tipo de carga
if tipos_carga:
    df_filtrado = df_filtrado[df_filtrado['TIPO DE CARGA'].isin(tipos_carga)]
# ------------------------------
# CONTROL DE DUPLICADOS EN EL DATAFRAME
# ------------------------------
# Crear ID único para cada registro y eliminar duplicados
df['id_unico'] = df['DESTINO'].astype(str) + "_" + df['FECHA'].astype(str) + "_" + df['TIPO DE CARGA'].astype(str)
df = df.drop_duplicates(subset=['id_unico'])

# Guardar el df limpio en session_state para que no se duplique al recargar
if "df_global" not in st.session_state:
    st.session_state.df_global = df.copy()

# Usar df limpio para filtros y cálculos
df_filtrado = st.session_state.df_global.copy()
# ------------------------------
# LIMPIEZA Y UNICIDAD DE DATOS
# ------------------------------
df['id_unico'] = df['DESTINO'].astype(str) + "_" + df['FECHA'].astype(str) + "_" + df['TIPO DE CARGA'].astype(str)
df = df.drop_duplicates(subset=['id_unico'])

# =========================
# KPI FINAL (DISEÑO + DATOS EXCEL)
# =========================

# Asegurar columnas limpias
df.columns = df.columns.str.strip()

# Datos EXACTOS del Excel
total_operaciones = df['N° DE OPERACIÓN'].count()
total_exportado = int(df['Peso Neto Exportado'].sum())
total_importado = int(df['Peso Neto Importado'].sum())
total_total = int(df['Peso Neto Manejado'].sum())

# ESTILO (NO TOCAR)
st.markdown("""
<style>
.kpi-box {
    background: rgba(10, 31, 68, 0.75);
    backdrop-filter: blur(10px);
    border-radius: 18px;
    padding: 25px;
    text-align: center;
    color: white;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.25);
    border: 2px solid rgba(255,255,255,0.2);
}
.kpi-title {
    font-size: 20px;
    font-weight: 600;
}
.kpi-value {
    font-size: 38px;
    font-weight: bold;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

# COLUMNAS (UNA SOLA VEZ)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-box" style="border-left: 6px solid #00BFFF;">
        <div class="kpi-title">🚢 Operaciones</div>
        <div class="kpi-value">{total_operaciones}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-box" style="border-left: 6px solid #28A745;">
        <div class="kpi-title">🌍 Exportado</div>
        <div class="kpi-value">{total_exportado:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-box" style="border-left: 6px solid #FFC107;">
        <div class="kpi-title">📦 Importado</div>
        <div class="kpi-value">{total_importado:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-box" style="border-left: 6px solid #DC3545;">
        <div class="kpi-title">⚖️ Total</div>
        <div class="kpi-value">{total_total:,}</div>
    </div>
    """, unsafe_allow_html=True)

# ------------------------------
# GRÁFICOS Y MAPAS (ÚNICO BLOQUE)
# ------------------------------
fig_placeholder = st.container()

with fig_placeholder:
    # Exportaciones por país
    df_paises = df.groupby('DESTINO')['Peso Neto Exportado'].sum().reset_index()

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
# MAPA AVANZADO DE EXPORTACIONES
# ------------------------------

import plotly.express as px

# Agrupar datos por destino y tipo de carga
df_map = df_filtrado.groupby(
    ['DESTINO', 'TIPO DE CARGA'], 
    as_index=False
)['Peso Neto Exportado'].sum()

# Crear mapa
fig_map = px.scatter_geo(
    df_map,
    locations='DESTINO',
    locationmode='country names',
    size='Peso Neto Exportado',
    color='TIPO DE CARGA',  # 🔥 diferenciación clave
    hover_name='DESTINO',
    size_max=45,
    projection='natural earth'
)

# Diseño profesional
fig_map.update_layout(

    title=dict(
        text="Mapa de Exportaciones por País y Tipo de Carga",
        x=0.5,
        font=dict(
            family="Arial Black",
            size=20,
            color="black"
        )
    ),

    paper_bgcolor="rgba(255,255,255,0.95)",

    geo=dict(
        bgcolor="rgba(255,255,255,0.95)",
        showland=True,
        landcolor="#F4F6F7",
        showocean=True,
        oceancolor="#D6EAF8",
        showcountries=True,
        countrycolor="#A6ACAF"
    ),

    legend=dict(
        title="Tipo de Carga",
        orientation="h",
        y=-0.1
    )
)

# Marca de agua
fig_map.add_annotation(
    text="EXPORTACIONES",
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

# Mostrar
st.plotly_chart(fig_map, use_container_width=True)

