import streamlit as st
import pandas as pd
import plotly.express as px
import base64

# ------------------------------
# CONFIGURACIÓN
# ------------------------------
st.set_page_config(layout="wide")

# ------------------------------
# FUNCIONES BASE64 (FONDO Y LOGO)
# ------------------------------
def get_base64(file):
    with open(file, "rb") as f:
        return base64.b64encode(f.read()).decode()

# ------------------------------
# DISEÑO VISUAL
# ------------------------------
try:
    fondo = get_base64("assets/fondo.jpg")
    logo = get_base64("assets/logo.png")

    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{fondo}");
        background-size: cover;
    }}

    [data-testid="stSidebar"] {{
        background-color: rgba(255,255,255,0.85);
    }}

    .logo {{
        display: flex;
        justify-content: center;
        margin-bottom: 20px;
    }}

    .titulo-principal {{
        text-align: center;
        font-size: 36px;
        font-weight: bold;
        color: black;
        text-shadow: 2px 2px 4px white;
    }}

    .card {{
        background-color: rgba(255,255,255,0.9);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.3);
    }}

    /* LIMPIAR INTERFAZ */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="logo"><img src="data:image/png;base64,{logo}" width="200"></div>', unsafe_allow_html=True)

except:
    pass

# ------------------------------
# FUNCIÓN TÍTULOS
# ------------------------------
def titulo(texto):
    st.markdown(f"""
    <div style="
        background-color: white;
        padding: 12px;
        border-radius: 12px;
        text-align: center;
        font-weight: bold;
        font-size: 20px;
        color: black;
        margin-top: 15px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.3);
    ">
        {texto}
    </div>
    """, unsafe_allow_html=True)

# ------------------------------
# CARGA DE ARCHIVO
# ------------------------------
archivo = st.file_uploader("Cargar archivo Excel", type=["xlsx"])

if archivo is None:
    st.warning("Cargue un archivo Excel para visualizar el dashboard")
    st.stop()

# ------------------------------
# LECTURA Y LIMPIEZA
# ------------------------------
df = pd.read_excel(archivo)
df.columns = df.columns.str.strip().str.upper()

# FECHA
if 'FECHA' in df.columns:
    df['FECHA'] = pd.to_datetime(df['FECHA'], errors='coerce')

# NUMÉRICOS
for col in ['PESO NETO EXPORTADO', 'PESO NETO IMPORTADO', 'PESO NETO MANEJADO']:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# TOTAL
if 'PESO NETO EXPORTADO' in df.columns and 'PESO NETO IMPORTADO' in df.columns:
    df['PESO TOTAL'] = df['PESO NETO EXPORTADO'].fillna(0) + df['PESO NETO IMPORTADO'].fillna(0)

# ------------------------------
# FILTROS
# ------------------------------
st.sidebar.title("Filtros")
df_filtrado = df.copy()

# FECHA
if 'FECHA' in df.columns:
    min_fecha = df['FECHA'].min()
    max_fecha = df['FECHA'].max()

    rango = st.sidebar.date_input("Rango de fechas", value=(min_fecha, max_fecha))

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

def card(titulo, valor):
    st.markdown(f"""
    <div class="card">
        <h4>{titulo}</h4>
        <h2>{valor}</h2>
    </div>
    """, unsafe_allow_html=True)

with col1:
    card("Operaciones", len(df_filtrado))

with col2:
    if 'PESO NETO EXPORTADO' in df_filtrado.columns:
        card("Exportado", f"{df_filtrado['PESO NETO EXPORTADO'].sum():,.2f}")

with col3:
    if 'PESO NETO IMPORTADO' in df_filtrado.columns:
        card("Importado", f"{df_filtrado['PESO NETO IMPORTADO'].sum():,.2f}")

with col4:
    if 'PESO TOTAL' in df_filtrado.columns:
        card("Total", f"{df_filtrado['PESO TOTAL'].sum():,.2f}")

# ------------------------------
# GRÁFICOS
# ------------------------------
titulo("Operaciones por Destino")

if 'DESTINO' in df_filtrado.columns:
    grafico = df_filtrado.groupby('DESTINO').size().reset_index(name='OPERACIONES')
    fig = px.bar(grafico, x='DESTINO', y='OPERACIONES')
    st.plotly_chart(fig, use_container_width=True)

titulo("Exportaciones por Contenido")

if 'CONTENIDO' in df_filtrado.columns:
    grafico2 = df_filtrado.groupby('CONTENIDO')['PESO NETO EXPORTADO'].sum().reset_index()
    fig2 = px.pie(grafico2, names='CONTENIDO', values='PESO NETO EXPORTADO')
    st.plotly_chart(fig2, use_container_width=True)

# ------------------------------
# MAPA
# ------------------------------
titulo("Mapa de Destinos")

coordenadas = {
    "USA": [37.0902, -95.7129],
    "ESPAÑA": [40.4637, -3.7492],
    "BRASIL": [-14.2350, -51.9253],
    "MEXICO": [23.6345, -102.5528],
    "COLOMBIA": [4.5709, -74.2973],
    "PANAMA": [8.5379, -80.7821]
}

if 'DESTINO' in df_filtrado.columns:
    mapa = df_filtrado[['DESTINO']].copy()
    mapa['lat'] = mapa['DESTINO'].map(lambda x: coordenadas.get(str(x).upper(), [None, None])[0])
    mapa['lon'] = mapa['DESTINO'].map(lambda x: coordenadas.get(str(x).upper(), [None, None])[1])
    mapa = mapa.dropna()

    if not mapa.empty:
        st.map(mapa)
    else:
        st.info("No hay coordenadas disponibles para los destinos")

# ------------------------------
# TABLA
# ------------------------------
titulo("Datos Filtrados")
st.dataframe(df_filtrado)
