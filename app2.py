import streamlit as st
import pandas as pd
import base64
import plotly.express as px
from datetime import datetime

# ------------------------------
# Función para cargar imágenes base64
# ------------------------------
def get_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Fondo y logo
fondo = get_base64("assets/fondo_comercio.jpg")
logo = get_base64("assets/logo_empreda.png")
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{fondo}");
        background-size: cover;
    }}
    .logo {{
        height: 80px;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Título
st.image(f"assets/logo_empreda.png", width=120)
st.markdown('<h1 style="color:black; background:white; padding:10px; border-radius:10px;">Control Operacional Empresa de Comercio Exterior de Lara</h1>', unsafe_allow_html=True)

# ------------------------------
# CARGAR EXCEL
# ------------------------------
try:
    df = pd.read_excel("data/datos.xlsx")
except FileNotFoundError:
    st.error("Archivo Excel no encontrado.")
    st.stop()
except Exception as e:
    st.error(f"No se pudo cargar el Excel: {e}")
    st.stop()

# ------------------------------
# FILTROS EN SIDEBAR
# ------------------------------
st.sidebar.header("Filtros")
fecha_seleccion = st.sidebar.date_input("Fecha", [])
destino_seleccion = st.sidebar.multiselect("Destino", df['DESTINO'].dropna().unique())
contenido_seleccion = st.sidebar.multiselect("Contenido", df['CONTENIDO'].dropna().unique())

# Filtrado seguro
df_filtrado = df.copy()
if fecha_seleccion:
    df_filtrado = df_filtrado[df_filtrado['FECHA'].isin(fecha_seleccion)]
if destino_seleccion:
    df_filtrado = df_filtrado[df_filtrado['DESTINO'].isin(destino_seleccion)]
if contenido_seleccion:
    df_filtrado = df_filtrado[df_filtrado['CONTENIDO'].isin(contenido_seleccion)]

# ------------------------------
# KPIs CON CONTENEDORES
# ------------------------------
operaciones = len(df_filtrado) if 'FECHA' in df_filtrado.columns else 0
peso_exportado = df_filtrado['Peso Neto Exportado'].sum() if 'Peso Neto Exportado' in df_filtrado.columns else 0
peso_importado = df_filtrado['Peso Neto Importado'].sum() if 'Peso Neto Importado' in df_filtrado.columns else 0
peso_total = peso_exportado + peso_importado

st.markdown(
    """
    <style>
    .metric-container {display:flex; justify-content:space-between; margin-bottom:20px;}
    .metric-box {background:#FFF; border-radius:15px; padding:20px; flex:1; margin:0 10px; box-shadow:0 4px 8px rgba(0,0,0,0.1); text-align:center;}
    .metric-box h3 {color:#000; margin:10px 0;}
    .metric-icon {font-size:40px; margin-bottom:10px;}
    </style>
    """, unsafe_allow_html=True
)

st.markdown('<div class="metric-container">', unsafe_allow_html=True)
# Operaciones
st.markdown(f'<div class="metric-box"><div class="metric-icon">📦</div><h3>Operaciones</h3><p style="font-size:24px;font-weight:bold;">{operaciones}</p></div>', unsafe_allow_html=True)
# Exportado
st.markdown(f'<div class="metric-box"><div class="metric-icon">🌎</div><h3>Exportado</h3><p style="font-size:24px;font-weight:bold;">{peso_exportado:,.2f} t</p></div>', unsafe_allow_html=True)
# Importado
st.markdown(f'<div class="metric-box"><div class="metric-icon">🛬</div><h3>Importado</h3><p style="font-size:24px;font-weight:bold;">{peso_importado:,.2f} t</p></div>', unsafe_allow_html=True)
# Total
st.markdown(f'<div class="metric-box"><div class="metric-icon">⚖️</div><h3>Peso Total</h3><p style="font-size:24px;font-weight:bold;">{peso_total:,.2f} t</p></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------
# MAPA 3D DESTINOS
# ------------------------------
if 'DESTINO' in df_filtrado.columns:
    import random
    if 'LATITUD' not in df_filtrado.columns or 'LONGITUD' not in df_filtrado.columns:
        coords = {}
        for d in df_filtrado['DESTINO'].unique():
            coords[d] = {'LAT': random.uniform(-10,10), 'LON': random.uniform(-70,-60)}
        df_filtrado['LATITUD'] = df_filtrado['DESTINO'].apply(lambda x: coords[x]['LAT'])
        df_filtrado['LONGITUD'] = df_filtrado['DESTINO'].apply(lambda x: coords[x]['LON'])
    # Convertir a numérico y eliminar filas inválidas
    df_filtrado['LATITUD'] = pd.to_numeric(df_filtrado['LATITUD'], errors='coerce')
    df_filtrado['LONGITUD'] = pd.to_numeric(df_filtrado['LONGITUD'], errors='coerce')
    df_filtrado['Peso Neto Exportado'] = pd.to_numeric(df_filtrado['Peso Neto Exportado'], errors='coerce')
    df_mapa = df_filtrado.dropna(subset=['LATITUD','LONGITUD','Peso Neto Exportado'])
    if not df_mapa.empty:
        st.markdown('<h3>Mapa de Destinos Exportados (3D)</h3>', unsafe_allow_html=True)
        fig_map = px.scatter_3d(df_mapa, x='LONGITUD', y='LATITUD', z='Peso Neto Exportado',
                                color='DESTINO', size='Peso Neto Exportado', hover_name='DESTINO')
        fig_map.update_layout(scene=dict(xaxis_title='Longitud', yaxis_title='Latitud', zaxis_title='Peso Exportado (t)'))
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("No hay datos válidos para mostrar en el mapa 3D.")
