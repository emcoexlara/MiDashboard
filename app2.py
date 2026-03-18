import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------------------
# CONFIGURACIÓN
# ------------------------------
st.set_page_config(layout="wide")

# ------------------------------
# ESTILOS (TÍTULOS PROFESIONALES)
# ------------------------------
st.markdown("""
    <style>
    .titulo {
        background-color: white;
        padding: 10px;
        border-radius: 10px;
        color: black;
        font-weight: bold;
        font-size: 20px;
        text-align: center;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

def titulo(texto):
    st.markdown(f'<div class="titulo">{texto}</div>', unsafe_allow_html=True)

# ------------------------------
# CARGA DE ARCHIVO
# ------------------------------
archivo = st.file_uploader("Cargar archivo Excel", type=["xlsx"])

if archivo is None:
    st.warning("Cargue un archivo para visualizar el dashboard")
    st.stop()

# ------------------------------
# LECTURA Y LIMPIEZA
# ------------------------------
df = pd.read_excel(archivo)

# Normalizar nombres de columnas
df.columns = df.columns.str.strip().str.upper()

# Convertir fecha
if 'FECHA' in df.columns:
    df['FECHA'] = pd.to_datetime(df['FECHA'], errors='coerce')

# Convertir numéricos
columnas_numericas = [
    'PESO NETO EXPORTADO',
    'PESO NETO IMPORTADO',
    'PESO NETO MANEJADO'
]

for col in columnas_numericas:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# Crear columna total
if 'PESO NETO EXPORTADO' in df.columns and 'PESO NETO IMPORTADO' in df.columns:
    df['PESO TOTAL'] = df['PESO NETO EXPORTADO'].fillna(0) + df['PESO NETO IMPORTADO'].fillna(0)

# ------------------------------
# FILTROS (SIDEBAR)
# ------------------------------
st.sidebar.title("Filtros")

df_filtrado = df.copy()

# FECHA (RANGO)
if 'FECHA' in df.columns:
    min_fecha = df['FECHA'].min()
    max_fecha = df['FECHA'].max()

    rango = st.sidebar.date_input(
        "Rango de fechas",
        value=(min_fecha, max_fecha)
    )

    if isinstance(rango, tuple):
        inicio, fin = rango
        df_filtrado = df_filtrado[
            (df_filtrado['FECHA'] >= pd.to_datetime(inicio)) &
            (df_filtrado['FECHA'] <= pd.to_datetime(fin))
        ]

# DESTINO
if 'DESTINO' in df.columns:
    destinos = df['DESTINO'].dropna().unique()
    sel_destino = st.sidebar.multiselect("Destino", destinos)

    if sel_destino:
        df_filtrado = df_filtrado[df_filtrado['DESTINO'].isin(sel_destino)]

# CONTENIDO
if 'CONTENIDO' in df.columns:
    contenidos = df['CONTENIDO'].dropna().unique()
    sel_contenido = st.sidebar.multiselect("Contenido", contenidos)

    if sel_contenido:
        df_filtrado = df_filtrado[df_filtrado['CONTENIDO'].isin(sel_contenido)]

# ------------------------------
# KPIs
# ------------------------------
titulo("Resumen Ejecutivo")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Operaciones", len(df_filtrado))

if 'PESO NETO EXPORTADO' in df_filtrado.columns:
    col2.metric(
        "Exportado",
        f"{df_filtrado['PESO NETO EXPORTADO'].sum():,.2f}"
    )

if 'PESO NETO IMPORTADO' in df_filtrado.columns:
    col3.metric(
        "Importado",
        f"{df_filtrado['PESO NETO IMPORTADO'].sum():,.2f}"
    )

if 'PESO TOTAL' in df_filtrado.columns:
    col4.metric(
        "Total",
        f"{df_filtrado['PESO TOTAL'].sum():,.2f}"
    )

# ------------------------------
# GRÁFICOS
# ------------------------------
titulo("Operaciones por Destino")

if 'DESTINO' in df_filtrado.columns:
    grafico_destino = df_filtrado.groupby('DESTINO').size().reset_index(name='OPERACIONES')
    fig1 = px.bar(grafico_destino, x='DESTINO', y='OPERACIONES')
    st.plotly_chart(fig1, use_container_width=True)

titulo("Exportaciones por Contenido")
if 'CONTENIDO' in df_filtrado.columns and 'PESO NETO EXPORTADO' in df_filtrado.columns:
    grafico_cont = df_filtrado.groupby('CONTENIDO')['PESO NETO EXPORTADO'].sum().reset_index()
    fig2 = px.pie(grafico_cont, names='CONTENIDO', values='PESO NETO EXPORTADO')
    st.plotly_chart(fig2, use_container_width=True)

# ------------------------------
# MAPA (SIN LAT/LONG)
# ------------------------------
titulo("Mapa de Destinos")

# Coordenadas básicas (puedes ampliarlas)
coordenadas = {
    "USA": [37.0902, -95.7129],
    "ESPAÑA": [40.4637, -3.7492],
    "BRASIL": [-14.2350, -51.9253],
    "MÉXICO": [23.6345, -102.5528],
    "COLOMBIA": [4.5709, -74.2973],
    "PANAMÁ": [8.5379, -80.7821]
}

if 'DESTINO' in df_filtrado.columns:
    mapa_df = df_filtrado[['DESTINO']].copy()
    mapa_df['LAT'] = mapa_df['DESTINO'].map(lambda x: coordenadas.get(str(x).upper(), [None, None])[0])
    mapa_df['LON'] = mapa_df['DESTINO'].map(lambda x: coordenadas.get(str(x).upper(), [None, None])[1])

    mapa_df = mapa_df.dropna()

    if not mapa_df.empty:
        st.map(mapa_df.rename(columns={"LAT": "lat", "LON": "lon"}))
    else:
        st.info("No hay coordenadas disponibles para los destinos")

# ------------------------------
# TABLA FINAL
# ------------------------------
titulo("Datos Filtrados")
st.dataframe(df_filtrado)
