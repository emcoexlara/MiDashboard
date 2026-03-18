import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64

# ------------------------------
# CONFIGURACIÓN
# ------------------------------
st.set_page_config(layout="wide")

# ------------------------------
# IDENTIDAD VISUAL
# ------------------------------
def get_base64(file):
    with open(file, "rb") as f:
        return base64.b64encode(f.read()).decode()

try:
    fondo = get_base64("assets/fondo.jpg")
    logo = get_base64("assets/logo.png")

    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{fondo}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #0B1F3A 0%, #1E3A5F 100%);
        color: white;
    }}
    .titulo-principal {{
        text-align: center;
        font-size: 38px;
        font-weight: 900;
        color: black;
        text-shadow: 3px 3px 6px white;
        margin-bottom: 20px;
    }}
    .bloque {{
        background-color: rgba(255,255,255,0.92);
        padding: 15px;
        border-radius: 15px;
        margin-top: 15px;
        box-shadow: 3px 3px 12px rgba(0,0,0,0.35);
    }}
    .card {{
        padding: 20px;
        border-radius: 18px;
        text-align: center;
        color: white;
        font-weight: bold;
        box-shadow: 2px 2px 12px rgba(0,0,0,0.4);
    }}
    .card1 {{ background: linear-gradient(135deg, #0B1F3A, #1E3A5F); }}
    .card2 {{ background: linear-gradient(135deg, #1E8449, #27AE60); }}
    .card3 {{ background: linear-gradient(135deg, #B03A2E, #E74C3C); }}
    .card4 {{ background: linear-gradient(135deg, #7D3C98, #AF7AC5); }}
    .logo {{
        display: flex;
        justify-content: center;
        margin-bottom: 10px;
    }}
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)

    st.markdown(
        f'<div class="logo"><img src="data:image/png;base64,{logo}" width="180"></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="titulo-principal">Control Operacional Empresa de Comercio Exterior de Lara</div>',
        unsafe_allow_html=True
    )

except:
    pass

# ------------------------------
# FUNCIÓN SECCIÓN
# ------------------------------
def seccion(texto):
    st.markdown(f"""
    <div class="bloque">
        <h3 style='text-align:center; color:#0B1F3A;'>{texto}</h3>
    </div>
    """, unsafe_allow_html=True)

# ------------------------------
# CARGA DE ARCHIVO
# ------------------------------
archivo = st.file_uploader("Cargar archivo Excel", type=["xlsx"])

if archivo is None:
    st.warning("Cargue un archivo Excel")
    st.stop()

# ------------------------------
# PROCESAMIENTO
# ------------------------------
df = pd.read_excel(archivo)
df.columns = df.columns.str.strip().str.upper()

if 'FECHA' in df.columns:
    df['FECHA'] = pd.to_datetime(df['FECHA'], errors='coerce')

for col in ['PESO NETO EXPORTADO', 'PESO NETO IMPORTADO']:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

df['PESO TOTAL'] = df.get('PESO NETO EXPORTADO', 0).fillna(0) + df.get('PESO NETO IMPORTADO', 0).fillna(0)

# ------------------------------
# FILTROS
# ------------------------------
st.sidebar.title("Filtros")

df_filtrado = df.copy()

# Filtro por fecha
if 'FECHA' in df.columns:
    rango = st.sidebar.date_input(
        "Rango de fechas",
        (df['FECHA'].min(), df['FECHA'].max())
    )
    if isinstance(rango, tuple):
        df_filtrado = df_filtrado[
            (df_filtrado['FECHA'] >= pd.to_datetime(rango[0])) &
            (df_filtrado['FECHA'] <= pd.to_datetime(rango[1]))
        ]

# Filtro por destino
if 'DESTINO' in df.columns:
    sel_destino = st.sidebar.multiselect(
        "Destino",
        df['DESTINO'].dropna().unique()
    )
    if sel_destino:
        df_filtrado = df_filtrado[df_filtrado['DESTINO'].isin(sel_destino)]
        # Filtro por contenido
if 'CONTENIDO' in df.columns:
    sel_contenido = st.sidebar.multiselect(
        "Contenido",
        df['CONTENIDO'].dropna().unique()
    )
    if sel_contenido:
        df_filtrado = df_filtrado[df_filtrado['CONTENIDO'].isin(sel_contenido)]

# ------------------------------
# KPIs
# ------------------------------
seccion("Resumen Ejecutivo")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"<div class='card card1'><h4>Operaciones</h4><h2>{len(df_filtrado)}</h2></div>", unsafe_allow_html=True)

with col2:
    st.markdown(f"<div class='card card2'><h4>Exportado</h4><h2>{df_filtrado['PESO NETO EXPORTADO'].sum():,.0f}</h2></div>", unsafe_allow_html=True)

with col3:
    st.markdown(f"<div class='card card3'><h4>Importado</h4><h2>{df_filtrado['PESO NETO IMPORTADO'].sum():,.0f}</h2></div>", unsafe_allow_html=True)

with col4:
    st.markdown(f"<div class='card card4'><h4>Total</h4><h2>{df_filtrado['PESO TOTAL'].sum():,.0f}</h2></div>", unsafe_allow_html=True)

# ------------------------------
# RANKING
# ------------------------------
seccion("Top Destinos")

ranking = df_filtrado.groupby('DESTINO').size().reset_index(name='OPERACIONES')
fig = px.bar(ranking.sort_values(by='OPERACIONES', ascending=False), x='DESTINO', y='OPERACIONES')
st.plotly_chart(fig, use_container_width=True)

# ------------------------------
# TENDENCIA
# ------------------------------
seccion("Tendencia de Exportaciones")

if 'FECHA' in df_filtrado.columns:
    tendencia = df_filtrado.groupby('FECHA')['PESO NETO EXPORTADO'].sum().reset_index()
    fig2 = px.line(tendencia, x='FECHA', y='PESO NETO EXPORTADO')
    st.plotly_chart(fig2, use_container_width=True)

# ------------------------------
# TABLA
# ------------------------------
seccion("Datos")
st.dataframe(df_filtrado)
