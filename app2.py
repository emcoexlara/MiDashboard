import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import os

# --- CONFIGURACIÓN GENERAL ---
st.set_page_config(
    page_title="Control Operacional de Comercio Exterior de Lara",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- COLORES CORPORATIVOS ---
COLOR_FONDO = "#f5f5f5"
COLOR_CUADRO = "#003366"  # azul corporativo
COLOR_ICONO = "#FFD700"   # dorado para iconos

# --- FUNCIONES PARA CARGAR RECURSOS ---
def get_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# Fondo y logo
fondo_path = "assets/fondo_comercio.jpg"
logo_path = "assets/logo_empresa.png"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{get_base64(fondo_path)}");
        background-size: cover;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.image(logo_path, width=150)

# --- CARGA DE DATOS ---
@st.cache_data
def load_data():
    df = pd.read_excel("data/datos.xlsx")
    # Limpiar nombres de columnas
    df.columns = [col.strip() for col in df.columns]
    # Convertir columnas numéricas
    for col in ["Peso Neto Exportado", "Peso Neto Importado", "Peso Neto Manejado", "LLENOS RECIBIDOS (EXPORTADOS)"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

df = load_data()

# --- FILTROS LATERALES ---
st.sidebar.header("Filtros")
destino_seleccion = st.sidebar.multiselect("Destino", df['DESTINO'].dropna().unique())
contenido_seleccion = st.sidebar.multiselect("Contenido", df['CONTENIDO'].dropna().unique())

df_filtrado = df.copy()
if destino_seleccion:
    df_filtrado = df_filtrado[df_filtrado['DESTINO'].isin(destino_seleccion)]
if contenido_seleccion:
    df_filtrado = df_filtrado[df_filtrado['CONTENIDO'].isin(contenido_seleccion)]

# --- KPIs ---
col1, col2, col3, col4 = st.columns(4)

col1.metric("Operaciones", f"{len(df_filtrado):,}")
col2.metric("Peso Neto Exportado (t)", f"{df_filtrado['Peso Neto Exportado'].sum():,.2f}")
col3.metric("Peso Neto Importado (t)", f"{df_filtrado['Peso Neto Importado'].sum():,.2f}")
col4.metric("Peso Total (t)", f"{df_filtrado['Peso Neto Manejado'].sum():,.2f}")

# --- GRÁFICOS ---
st.subheader("Análisis de Contenedores vs Toneladas")
contenedores_df = df_filtrado.groupby('CONTENIDO')[['LLENOS RECIBIDOS (EXPORTADOS)', 'Peso Neto Exportado']].sum().reset_index()
fig_contenedores = px.bar(contenedores_df, x='CONTENIDO', y='LLENOS RECIBIDOS (EXPORTADOS)', color='Peso Neto Exportado',
                          labels={"LLENOS RECIBIDOS (EXPORTADOS)":"Contenedores", "Peso Neto Exportado":"Toneladas"},
                          title="Contenedores vs Toneladas")
st.plotly_chart(fig_contenedores, use_container_width=True)

st.subheader("Mapa 3D de Exportaciones")
if 'LONGITUD' in df_filtrado.columns and 'LATITUD' in df_filtrado.columns:
    fig_map = px.scatter_3d(df_filtrado, x='LONGITUD', y='LATITUD', z='Peso Neto Exportado',
                            color='DESTINO', size='Peso Neto Exportado', hover_name='DESTINO',
                            labels={"LONGITUD":"Longitud","LATITUD":"Latitud","Peso Neto Exportado":"Toneladas"})
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning("Las columnas 'LONGITUD' y 'LATITUD' no existen en los datos para mostrar el mapa 3D.")

# --- GRÁFICO DE DESTINOS ---
st.subheader("Distribución por País de Destino")
fig_destinos = px.pie(df_filtrado, names='DESTINO', values='Peso Neto Exportado', title="Peso Neto Exportado por Destino")
st.plotly_chart(fig_destinos, use_container_width=True)
