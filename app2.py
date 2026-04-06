import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import os

# 1. CONFIGURACIÓN (Debe ser lo primero)
st.set_page_config(layout="wide", page_title="Control Operacional Lara")

# 2. CARGA DE DATOS CON CACHÉ
@st.cache_data
def load_data(file_path):
    if not os.path.exists(file_path):
        st.error(f"No se encontró el archivo en: {file_path}")
        st.stop()
    
    df = pd.read_excel(file_path)
    
    # --- LIMPIEZA ÚNICA ---
    df.columns = df.columns.str.strip()
    
    # Crear ID único y eliminar duplicados una sola vez
    # Usamos fillna('') para evitar errores de concatenación con Nulos
    df['id_unico'] = (df['DESTINO'].astype(str) + "_" + 
                      df['FECHA'].astype(str) + "_" + 
                      df['TIPO DE CARGA'].astype(str))
    df = df.drop_duplicates(subset=['id_unico'])
    
    # Asegurar tipos de datos
    df['FECHA'] = pd.to_datetime(df['FECHA'], errors='coerce')
    columnas_numericas = ['Peso Neto Exportado', 'Peso Neto Importado', 'Peso Neto Manejado']
    for col in columnas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    return df

file_path = "data/datos.xlsx" # Asegúrate que esta ruta sea correcta
df = load_data(file_path)

# 3. INTERFAZ Y ESTILOS
COLOR_TITULO = "#1F4E79"

def set_background(image_file):
    if os.path.exists(image_file):
        with open(image_file, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        st.markdown(f"""
            <style>
            .stApp {{
                background-image: url("data:image/jpg;base64,{encoded}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
            </style>
        """, unsafe_allow_html=True)

set_background("assets/fondo_comercio.jpg")

# 4. BARRA LATERAL (FILTROS)
st.sidebar.markdown("## 🔎 Filtros")

# Filtro de Fecha
fecha_min, fecha_max = df['FECHA'].min(), df['FECHA'].max()
rango_fecha = st.sidebar.date_input("Rango de Fecha", [fecha_min, fecha_max])

# Filtro Destino
destinos_m = st.sidebar.multiselect(
    "Destino", options=sorted(df['DESTINO'].dropna().unique()),
    default=sorted(df['DESTINO'].dropna().unique())
)

# Filtro Tipo Carga
tipos_carga_m = st.sidebar.multiselect(
    "Tipo de Carga", options=sorted(df['TIPO DE CARGA'].dropna().unique()),
    default=sorted(df['TIPO DE CARGA'].dropna().unique())
)

# --- APLICAR FILTROS AL DF_FILTRADO ---
mask = (df['DESTINO'].isin(destinos_m)) & (df['TIPO DE CARGA'].isin(tipos_carga_m))
if len(rango_fecha) == 2:
    mask = mask & (df['FECHA'] >= pd.to_datetime(rango_fecha[0])) & (df['FECHA'] <= pd.to_datetime(rango_fecha[1]))

df_filtrado = df[mask]

# 5. CÁLCULO DE MÉTRICAS (KPIs)
total_operaciones = len(df_filtrado)
total_exportado = df_filtrado['Peso Neto Exportado'].sum()
total_importado = df_filtrado['Peso Neto Importado'].sum()
total_total = df_filtrado['Peso Neto Manejado'].sum()

# 6. ENCABEZADO
col_logo, col_titulo = st.columns([1, 5])
with col_logo:
    if os.path.exists("assets/logo_empresa.png"):
        st.image("assets/logo_empresa.png", width=100)

with col_titulo:
    st.markdown(f"<h1 style='color:{COLOR_TITULO};'>Control Operacional de Comercio Exterior</h1>", unsafe_allow_html=True)

# 7. RENDERIZADO DE KPIs
st.markdown("""
<style>
.kpi-box { background: rgba(10, 31, 68, 0.8); border-radius: 15px; padding: 20px; text-align: center; color: white; border: 1px solid rgba(255,255,255,0.2); }
.kpi-value { font-size: 30px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
c1.markdown(f'<div class="kpi-box">🚢 Operaciones<br><span class="kpi-value">{total_operaciones}</span></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="kpi-box">🌍 Exportado<br><span class="kpi-value">{total_exportado:,.0f}</span></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="kpi-box">📦 Importado<br><span class="kpi-value">{total_importado:,.0f}</span></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="kpi-box">⚖️ Total<br><span class="kpi-value">{total_total:,.0f}</span></div>', unsafe_allow_html=True)

st.divider()

# 8. GRÁFICOS
def aplicar_estilo_grafico(fig):
    fig.update_layout(
        paper_bgcolor="rgba(255,255,255,0.9)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="black")
    )
    return fig

# Gráfico 1: Exportación por País
df_paises = df_filtrado.groupby('DESTINO')['Peso Neto Exportado'].sum().reset_index()
fig1 = px.bar(df_paises, x='DESTINO', y='Peso Neto Exportado', title="Exportaciones por País", text_auto='.2s')
st.plotly_chart(aplicar_estilo_grafico(fig1), use_container_width=True)

# Mapa
df_map = df_filtrado.groupby(['DESTINO', 'TIPO DE CARGA'], as_index=False)['Peso Neto Exportado'].sum()
fig_map = px.scatter_geo(df_map, locations='DESTINO', locationmode='country names', 
                         size='Peso Neto Exportado', color='TIPO DE CARGA', title="Mapa Global de Carga")
st.plotly_chart(aplicar_estilo_grafico(fig_map), use_container_width=True)
