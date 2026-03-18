# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import os, base64

# ----------------------------
# RUTAS DE ARCHIVOS
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "assets", "logo_empresa.png")
FONDO_PATH = os.path.join(BASE_DIR, "assets", "fondo_comercio.jpg")
DATA_PATH = os.path.join(BASE_DIR, "data", "datos.xlsx")

# ----------------------------
# FUNCIONES
# ----------------------------
def get_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def load_data():
    try:
        df = pd.read_excel(DATA_PATH)
        return df
    except Exception as e:
        st.error(f"No se pudo cargar el archivo Excel: {e}")
        return pd.DataFrame()

# ----------------------------
# ESTILOS
# ----------------------------
fondo_b64 = get_base64(FONDO_PATH)
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{fondo_b64}");
        background-size: cover;
        background-attachment: fixed;
    }}
    .titulo-principal {{
        color: black;
        font-size: 36px;
        font-weight: bold;
        border: 3px solid white;
        padding: 10px;
        text-align: center;
        border-radius: 10px;
        background-color: rgba(255,255,255,0.7);
    }}
    .kpi-container {{
        background-color: rgba(255,255,255,0.8);
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        margin-bottom: 10px;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------------------
# HEADER
# ----------------------------
st.image(LOGO_PATH, width=120)
st.markdown('<div class="titulo-principal">Dashboard de Comercio Exterior</div>', unsafe_allow_html=True)
st.write("---")

# ----------------------------
# CARGA DE DATOS
# ----------------------------
df = load_data()
if df.empty:
    st.stop()

# ----------------------------
# FILTROS LATERAL
# ----------------------------
st.sidebar.header("Filtros")
fecha_seleccion = st.sidebar.date_input("Fecha", [])
destino_seleccion = st.sidebar.multiselect("Destino", df['DESTINO'].dropna().unique())
contenido_seleccion = st.sidebar.multiselect("Contenido", df['CONTENIDO'].dropna().unique())

df_filtrado = df.copy()

if fecha_seleccion:
    df_filtrado = df_filtrado[df_filtrado['FECHA'].isin(fecha_seleccion)]
if destino_seleccion:
    df_filtrado = df_filtrado[df_filtrado['DESTINO'].isin(destino_seleccion)]
if contenido_seleccion:
    df_filtrado = df_filtrado[df_filtrado['CONTENIDO'].isin(contenido_seleccion)]

# ----------------------------
# KPIs CON ICONOS
# ----------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="kpi-container">📦<br>Operaciones<br><b>{}</b></div>'.format(len(df_filtrado)), unsafe_allow_html=True)

with col2:
    st.markdown('<div class="kpi-container">🌍<br>Exportado (t)<br><b>{:,.2f}</b></div>'.format(df_filtrado['Peso Neto Exportado'].sum()), unsafe_allow_html=True)

with col3:
    st.markdown('<div class="kpi-container">📥<br>Importado (t)<br><b>{:,.2f}</b></div>'.format(df_filtrado['Peso Neto Importado'].sum()), unsafe_allow_html=True)

with col4:
    st.markdown('<div class="kpi-container">⚖️<br>Total (t)<br><b>{:,.2f}</b></div>'.format(df_filtrado['Peso Neto Exportado'].sum() + df_filtrado['Peso Neto Importado'].sum()), unsafe_allow_html=True)

st.write("---")

# ----------------------------
# GRÁFICOS
# ----------------------------
# Exportaciones por contenido
fig1 = px.bar(df_filtrado, x='CONTENIDO', y='Peso Neto Exportado', color='CONTENIDO',
              title="Exportaciones por Contenido", text_auto=True)
st.plotly_chart(fig1, use_container_width=True)

# Importaciones por destino
fig2 = px.bar(df_filtrado, x='DESTINO', y='Peso Neto Importado', color='DESTINO',
              title="Importaciones por Destino", text_auto=True)
st.plotly_chart(fig2, use_container_width=True)
# MAPA 3D de exportaciones si existen lat/lon
if 'LATITUD' in df_filtrado.columns and 'LONGITUD' in df_filtrado.columns:
    fig_map = px.scatter_3d(df_filtrado, x='LONGITUD', y='LATITUD', z='Peso Neto Exportado',
                            color='DESTINO', size='Peso Neto Exportado', hover_name='DESTINO',
                            title="Mapa 3D de Destinos Exportados")
    st.plotly_chart(fig_map, use_container_width=True)
