import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import os

# ------------------------------
# CONFIGURACIÓN GENERAL
# ------------------------------
st.set_page_config(layout="wide")

# ------------------------------
# COLORES
# ------------------------------
COLOR_TITULO = "#1F4E79"

# ------------------------------
# TEMPLATE GRÁFICOS
# ------------------------------
TEMPLATE_PRO = dict(
    layout=dict(
        font=dict(family="Arial", size=14, color="black"),
        title=dict(font=dict(size=20)),
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
        }}
        </style>
    """, unsafe_allow_html=True)

set_background("assets/fondo_comercio.jpg")

# ------------------------------
# LOGO Y TÍTULO
# ------------------------------
col_logo, col_titulo = st.columns([1, 5])

with col_logo:
    st.image("assets/logo_empresa.png", width=100)

with col_titulo:
    st.markdown(f"""
    <h1 style='color:{COLOR_TITULO};'>
    Control Operacional de Comercio Exterior de Lara
    </h1>
    """, unsafe_allow_html=True)

# ------------------------------
# CARGA DE DATOS
# ------------------------------
@st.cache_data
def load_data(path):
    return pd.read_excel(path)

df = load_data("data/datos.xlsx")

# ------------------------------
# LIMPIEZA DE DATOS
# ------------------------------
df.columns = df.columns.str.strip()

# 🔥 Convertir correctamente números
for col in ['Peso Neto Exportado', 'Peso Neto Importado', 'Peso Neto Manejado']:
    df[col] = df[col].astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# Fecha
df['FECHA'] = pd.to_datetime(df['FECHA'], errors='coerce')

# ID único (evita duplicados)
df['id_unico'] = df['DESTINO'].astype(str) + "_" + df['FECHA'].astype(str) + "_" + df['TIPO DE CARGA'].astype(str)
df = df.drop_duplicates(subset=['id_unico'])

# ------------------------------
# FILTROS
# ------------------------------
st.sidebar.markdown("## 🔎 Filtros")

rango_fecha = st.sidebar.date_input(
    "Rango de Fecha",
    [df['FECHA'].min(), df['FECHA'].max()]
)

destinos = st.sidebar.multiselect(
    "Destino",
    options=sorted(df['DESTINO'].dropna().unique()),
    default=sorted(df['DESTINO'].dropna().unique())
)

tipos_carga = st.sidebar.multiselect(
    "Tipo de Carga",
    options=sorted(df['TIPO DE CARGA'].dropna().unique()),
    default=sorted(df['TIPO DE CARGA'].dropna().unique())
)

# Aplicar filtros
df_filtrado = df.copy()

if len(rango_fecha) == 2:
    df_filtrado = df_filtrado[
        (df_filtrado['FECHA'] >= pd.to_datetime(rango_fecha[0])) &
        (df_filtrado['FECHA'] <= pd.to_datetime(rango_fecha[1]))
    ]

if destinos:
    df_filtrado = df_filtrado[df_filtrado['DESTINO'].isin(destinos)]

if tipos_carga:
    df_filtrado = df_filtrado[df_filtrado['TIPO DE CARGA'].isin(tipos_carga)]

# ------------------------------
# KPIs (VALORES EXACTOS)
# ------------------------------
total_operaciones = len(df_filtrado)
total_exportado = df_filtrado['Peso Neto Exportado'].sum()
total_importado = df_filtrado['Peso Neto Importado'].sum()
total_total = df_filtrado['Peso Neto Manejado'].sum()

# Formato exacto
exportado_format = f"{total_exportado:,.2f}"
importado_format = f"{total_importado:,.2f}"
total_format = f"{total_total:,.2f}"

# ------------------------------
# ESTILO KPI
# ------------------------------
st.markdown("""
<style>
.kpi-box {
    background: rgba(10, 31, 68, 0.75);
    border-radius: 18px;
    padding: 25px;
    text-align: center;
    color: white;
}
.kpi-title { font-size: 20px; }
.kpi-value { font-size: 34px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"<div class='kpi-box'><div class='kpi-title'>Operaciones</div><div class='kpi-value'>{total_operaciones}</div></div>", unsafe_allow_html=True)

with col2:
    st.markdown(f"<div class='kpi-box'><div class='kpi-title'>Exportado</div><div class='kpi-value'>{exportado_format}</div></div>", unsafe_allow_html=True)

with col3:
    st.markdown(f"<div class='kpi-box'><div class='kpi-title'>Importado</div><div class='kpi-value'>{importado_format}</div></div>", unsafe_allow_html=True)

with col4:
    st.markdown(f"<div class='kpi-box'><div class='kpi-title'>Total</div><div class='kpi-value'>{total_format}</div></div>", unsafe_allow_html=True)

# ------------------------------
# GRÁFICO EXPORTACIONES
# ------------------------------
df_paises = df_filtrado.groupby('DESTINO')['Peso Neto Exportado'].sum().reset_index()

fig1 = px.bar(
    df_paises,
    x='DESTINO',
    y='Peso Neto Exportado',
    text='Peso Neto Exportado'
)

fig1.update_traces(
    texttemplate='%{text:,.2f}',
    textposition='outside'
)

fig1.update_layout(
    TEMPLATE_PRO["layout"],
    title="Exportaciones por País",
    title_x=0.5
)

st.plotly_chart(fig1, use_container_width=True)

# ------------------------------
# MAPA
# ------------------------------
df_map = df_filtrado.groupby(['DESTINO', 'TIPO DE CARGA'], as_index=False)['Peso Neto Exportado'].sum()

fig_map = px.scatter_geo(
    df_map,
    locations='DESTINO',
    locationmode='country names',
    size='Peso Neto Exportado',
    color='TIPO DE CARGA',
    size_max=40
)

fig_map.update_layout(title="Mapa de Exportaciones", title_x=0.5)

st.plotly_chart(fig_map, use_container_width=True)
