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
COLOR_ICONO = "#FFD700"   # dorado

# --- FUNCIONES PARA CARGAR RECURSOS ---
def get_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# Fondo y logo
fondo_path = "assets/fondo_comercio.jpg"
logo_path = "assets/logo_empresa.png"

# st.markdown(f"<h2 style='color:{COLOR_TITULO}; text-align:center;'>Mapa 3D de Exportaciones</h2>", unsafe_allow_html=True)

st.image(logo_path, width=150)

# --- CARGA DE DATOS ---
@st.cache_data
def load_data():
    df = pd.read_excel("data/datos.xlsx")
    df.columns = [col.strip() for col in df.columns]
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
df_filtrado = df.copy()  # o el df filtrado según tus multiselect

# --- KPIs CON ICONOS ---
st.markdown(
    f"<h1 style='color:{COLOR_CUADRO}; text-align:center;'>Control Operacional de Comercio Exterior de Lara</h1>",
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)
col1.markdown(f"<div style='background-color:{COLOR_CUADRO}; padding:15px; border-radius:10px; text-align:center; color:white;'>"
               f"<h3>📦 Operaciones</h3><h2>{len(df_filtrado):,}</h2></div>", unsafe_allow_html=True)
col2.markdown(f"<div style='background-color:{COLOR_CUADRO}; padding:15px; border-radius:10px; text-align:center; color:white;'>"
               f"<h3>🚢 Peso Neto Exportado (t)</h3><h2>{df_filtrado['Peso Neto Exportado'].sum():,.2f}</h2></div>", unsafe_allow_html=True)
col3.markdown(f"<div style='background-color:{COLOR_CUADRO}; padding:15px; border-radius:10px; text-align:center; color:white;'>"
               f"<h3>📥 Peso Neto Importado (t)</h3><h2>{df_filtrado['Peso Neto Importado'].sum():,.2f}</h2></div>", unsafe_allow_html=True)
col4.markdown(f"<div style='background-color:{COLOR_CUADRO}; padding:15px; border-radius:10px; text-align:center; color:white;'>"
               f"<h3>⚖️ Peso Total (t)</h3><h2>{df_filtrado['Peso Neto Manejado'].sum():,.2f}</h2></div>", unsafe_allow_html=True)

# --- GRÁFICOS ---
st.subheader("Contenedores vs Toneladas")
if 'CONTENIDO' in df_filtrado.columns:
    contenedores_df = df_filtrado.groupby('CONTENIDO')[['LLENOS RECIBIDOS (EXPORTADOS)', 'Peso Neto Exportado']].sum().reset_index()
    fig_contenedores = px.bar(contenedores_df, x='CONTENIDO', y='LLENOS RECIBIDOS (EXPORTADOS)',
                              color='Peso Neto Exportado', labels={"LLENOS RECIBIDOS (EXPORTADOS)":"Contenedores", "Peso Neto Exportado":"Toneladas"},
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

st.subheader("Distribución por País de Destino")
if 'DESTINO' in df_filtrado.columns:
    fig_destinos = px.pie(df_filtrado, names='DESTINO', values='Peso Neto Exportado', title="Peso Neto Exportado por Destino")
    st.plotly_chart(fig_destinos, use_container_width=True)

# --- MAPA DE EXPORTACIONES ---
import plotly.express as px
import streamlit as st

# --- Bloque de mapa de exportaciones por país ---

# Filtrar los datos que tengan DESTINO y Peso Neto Exportado
df_map = df[['DESTINO', 'Peso Neto Exportado']].dropna()

# Crear el mapa
fig_map = px.choropleth(
    data_frame=df_map,
    locations="DESTINO",            # Nombre de los países
    locationmode="country names",   # Reconoce nombres de países
    color="Peso Neto Exportado",    # Color según toneladas exportadas
    hover_name="DESTINO",           # Mostrar país al pasar el mouse
    color_continuous_scale=px.colors.sequential.Plasma,  # Paleta de colores
    title="Exportaciones por país (toneladas)",
    template="plotly_white"
)

# Mostrar el mapa en Streamlit
st.plotly_chart(fig_map, use_container_width=True)
