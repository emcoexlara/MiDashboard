import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import os

# ------------------------------
# CONFIGURACIÓN
# ------------------------------
st.set_page_config(layout="wide", page_title="Dashboard Ejecutivo")

# ------------------------------
# RUTAS DE ARCHIVOS
# ------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(file))

def get_base64(file):
    with open(file, "rb") as f:
        return base64.b64encode(f.read()).decode()

fondo_path = os.path.join(BASE_DIR, "assets", "fondo.jpg")
logo_path = os.path.join(BASE_DIR, "assets", "logo.png")
excel_path = os.path.join(BASE_DIR, "data", "data.xlsx")

fondo = get_base64(fondo_path)
logo = get_base64(logo_path)

# ------------------------------
# ESTILOS CSS
# ------------------------------
st.markdown(f"""
<style>
.stApp {{
    background-image: url("data:image/jpg;base64,{fondo}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}
.titulo-principal {{
    text-align: center;
    font-size: 40px;
    font-weight: 900;
    color: black;
    text-shadow: 2px 2px 6px white;
    margin-bottom: 20px;
}}
.bloque {{
    background-color: rgba(255,255,255,0.9);
    padding: 20px;
    border-radius: 15px;
    margin-top: 15px;
    box-shadow: 3px 3px 12px rgba(0,0,0,0.35);
}}
.card {{
    padding: 25px;
    border-radius: 20px;
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
    margin-bottom: 15px;
}}
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# ------------------------------
# LOGO Y TÍTULO
# ------------------------------
st.markdown(f'<div class="logo"><img src="data:image/png;base64,{logo}" width="180"></div>', unsafe_allow_html=True)
st.markdown('<div class="titulo-principal">Control Operacional Empresa de Comercio Exterior de Lara</div>', unsafe_allow_html=True)

# ------------------------------
# CARGA DE DATOS
# ------------------------------
df = pd.read_excel(excel_path)
df.columns = df.columns.str.strip().str.upper()

# Convertir fechas
if 'FECHA' in df.columns:
    df['FECHA'] = pd.to_datetime(df['FECHA'], errors='coerce')

# Convertir columnas numéricas
for col in ['PESO NETO EXPORTADO', 'PESO NETO IMPORTADO', 'PESO NETO MANEJADO']:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# Peso total
df['PESO TOTAL'] = df.get('PESO NETO EXPORTADO',0).fillna(0) + df.get('PESO NETO IMPORTADO',0).fillna(0)
df_filtrado = df.copy()

# ------------------------------
# FILTROS OPCIONALES
# ------------------------------
st.sidebar.title("Filtros (Opcionales)")

# Fecha
if 'FECHA' in df.columns:
    rango = st.sidebar.date_input("Rango de fechas", (df['FECHA'].min(), df['FECHA'].max()))
    if isinstance(rango, tuple):
        df_filtrado = df_filtrado[(df_filtrado['FECHA']>=pd.to_datetime(rango[0])) & (df_filtrado['FECHA']<=pd.to_datetime(rango[1]))]

# Destino
if 'DESTINO' in df.columns:
    sel_destino = st.sidebar.multiselect("Destino", df['DESTINO'].dropna().unique())
    if sel_destino:
        df_filtrado = df_filtrado[df_filtrado['DESTINO'].isin(sel_destino)]

# Contenido
if 'CONTENIDO' in df.columns:
    sel_contenido = st.sidebar.multiselect("Contenido", df['CONTENIDO'].dropna().unique())
    if sel_contenido:
        df_filtrado = df_filtrado[df_filtrado['CONTENIDO'].isin(sel_contenido)]

# ------------------------------
# KPIs
# ------------------------------
def tarjeta(title, valor, clase):
    st.markdown(f'<div class="card {clase}"><h4>{title}</h4><h2>{valor:,.2f}</h2></div>', unsafe_allow_html=True)
    st.markdown('<div class="bloque"><h3>Resumen Ejecutivo</h3></div>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
with col1: tarjeta("Operaciones", len(df_filtrado), "card1")
with col2: tarjeta("Exportado (t)", df_filtrado['PESO NETO EXPORTADO'].sum(), "card2")
with col3: tarjeta("Importado (t)", df_filtrado['PESO NETO IMPORTADO'].sum(), "card3")
with col4: tarjeta("Total (t)", df_filtrado['PESO TOTAL'].sum(), "card4")

# ------------------------------
# GRÁFICOS
# ------------------------------
st.markdown('<div class="bloque"><h3>Ranking Destinos</h3></div>', unsafe_allow_html=True)
ranking = df_filtrado.groupby('DESTINO').size().reset_index(name='OPERACIONES')
fig = px.bar(ranking.sort_values('OPERACIONES', ascending=False), x='DESTINO', y='OPERACIONES', text='OPERACIONES', color='OPERACIONES', color_continuous_scale='Blues')
st.plotly_chart(fig, use_container_width=True)

st.markdown('<div class="bloque"><h3>Tendencia Exportaciones</h3></div>', unsafe_allow_html=True)
if 'FECHA' in df_filtrado.columns:
    tendencia = df_filtrado.groupby('FECHA')['PESO NETO EXPORTADO'].sum().reset_index()
    fig2 = px.line(tendencia, x='FECHA', y='PESO NETO EXPORTADO', markers=True, line_shape='spline')
    st.plotly_chart(fig2, use_container_width=True)

# ------------------------------
# TABLA DE DATOS
# ------------------------------
st.markdown('<div class="bloque"><h3>Tabla de Operaciones</h3></div>', unsafe_allow_html=True)
st.dataframe(df_filtrado)
