import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import os

# ------------------------------
# CONFIGURACIÓN
# ------------------------------
st.set_page_config(layout="wide")

COLOR_TITULO = "#1F4E79"

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
            background-attachment: fixed;
        }}
        </style>
    """, unsafe_allow_html=True)

set_background("assets/fondo_comercio.jpg")

# ------------------------------
# HEADER
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
# LIMPIEZA
# ------------------------------
df.columns = df.columns.str.strip()

# Convertir números correctamente
for col in ['Peso Neto Exportado', 'Peso Neto Importado', 'Peso Neto Manejado']:
    df[col] = df[col].astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# Fecha
df['FECHA'] = pd.to_datetime(df['FECHA'], errors='coerce')

# Eliminar duplicados
df['id_unico'] = df['DESTINO'].astype(str) + "_" + df['FECHA'].astype(str) + "_" + df['TIPO DE CARGA'].astype(str)
df = df.drop_duplicates(subset=['id_unico'])

# ------------------------------
# FILTROS (SOLO UNA VEZ)
# ------------------------------
st.sidebar.markdown("## 🔎 Filtros")

fecha_min = df['FECHA'].min()
fecha_max = df['FECHA'].max()

rango_fecha = st.sidebar.date_input(
    "Rango de Fecha",
    [fecha_min, fecha_max]
)

destinos = st.sidebar.multiselect(
    "Destino",
    sorted(df['DESTINO'].dropna().unique()),
    default=sorted(df['DESTINO'].dropna().unique())
)

tipos_carga = st.sidebar.multiselect(
    "Tipo de Carga",
    sorted(df['TIPO DE CARGA'].dropna().unique()),
    default=sorted(df['TIPO DE CARGA'].dropna().unique())
)

# ------------------------------
# APLICAR FILTROS (CLAVE 🔥)
# ------------------------------
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
# KPIs (CORRECTOS)
# ------------------------------
total_operaciones = len(df_filtrado)
total_exportado = df_filtrado['Peso Neto Exportado'].sum()
total_importado = df_filtrado['Peso Neto Importado'].sum()
total_total = df_filtrado['Peso Neto Manejado'].sum()

exportado_format = f"{total_exportado:,.2f}"
importado_format = f"{total_importado:,.2f}"
total_format = f"{total_total:,.2f}"

# ------------------------------
# KPI VISUAL
# ------------------------------
st.markdown("""
<style>
.kpi-box {
    background: rgba(10,31,68,0.75);
    border-radius: 18px;
    padding: 25px;
    text-align: center;
    color: white;
}
.kpi-value { font-size: 34px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

c1.markdown(f"<div class='kpi-box'><div>Operaciones</div><div class='kpi-value'>{total_operaciones}</div></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='kpi-box'><div>Exportado</div><div class='kpi-value'>{exportado_format}</div></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='kpi-box'><div>Importado</div><div class='kpi-value'>{importado_format}</div></div>", unsafe_allow_html=True)
c4.markdown(f"<div class='kpi-box'><div>Total</div><div class='kpi-value'>{total_format}</div></div>", unsafe_allow_html=True)

# ------------------------------
# GRÁFICO EXPORTACIONES
# ------------------------------
df_paises = df_filtrado.groupby('DESTINO')['Peso Neto Exportado'].sum().reset_index()

fig1 = px.bar(df_paises, x='DESTINO', y='Peso Neto Exportado', text='Peso Neto Exportado')

fig1.update_traces(texttemplate='%{text:,.2f}', textposition='outside')

fig1.update_layout(TEMPLATE_PRO["layout"], title="Exportaciones por País", title_x=0.5)

st.plotly_chart(fig1, use_container_width=True)

# ------------------------------
# CONTENEDORES VS TONELADAS
# ------------------------------
if 'CONTENIDO' in df_filtrado.columns and 'LLENOS RECIBIDOS (EXPORTADOS)' in df_filtrado.columns:

    df_cont = df_filtrado.groupby('CONTENIDO')[[
        'LLENOS RECIBIDOS (EXPORTADOS)',
        'Peso Neto Exportado'
    ]].sum().reset_index()

    fig2 = px.bar(
        df_cont,
        x='CONTENIDO',
        y=['LLENOS RECIBIDOS (EXPORTADOS)', 'Peso Neto Exportado'],
        barmode='group'
    )

    fig2.update_traces(texttemplate='%{value:,.2f}')

    fig2.update_layout(TEMPLATE_PRO["layout"], title="Contenedores vs Toneladas", title_x=0.5)

    st.plotly_chart(fig2, use_container_width=True)

# ------------------------------
# MAPA (COMPLETO)
# ------------------------------
df_map = df_filtrado.groupby(['DESTINO', 'TIPO DE CARGA'], as_index=False)['Peso Neto Exportado'].sum()

fig_map = px.scatter_geo(
    df_map,
    locations='DESTINO',
    locationmode='country names',
    size='Peso Neto Exportado',
    color='TIPO DE CARGA',
    size_max=45,
    projection='natural earth'
)

fig_map.update_layout(
    title=dict(
        text="Mapa de Exportaciones por País y Tipo de Carga",
        x=0.5,
        font=dict(family="Arial Black", size=20)
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
    )
)

st.plotly_chart(fig_map, use_container_width=True)
