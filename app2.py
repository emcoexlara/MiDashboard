import streamlit as st
import pandas as pd
import streamlit as st
import pandas as pd

# --- Función para cargar datos ---
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("data/datos.xlsx")
        # Normalizar nombres
        df.columns = df.columns.str.strip().str.upper().str.replace(" ", "_").str.replace("Á","A").str.replace("É","E").str.replace("Í","I").str.replace("Ó","O").str.replace("Ú","U")
        # Convertir pesos a numéricos
        for col in ["PESO_NETO_EXPORTADO", "PESO_NETO_IMPORTADO", "PESO_NETO_MANEJADO"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                df[col] = 0
        return df
    except Exception as e:
        st.error(f"No se pudo cargar el archivo Excel: {e}")
        return pd.DataFrame()  # devuelve DF vacío para que no rompa la app

# --- Cargar datos ---
df = load_data()

# --- Verificar si df se cargó ---
if df.empty:
    st.stop()  # Detiene la app si no hay datos

# --- Copiar df para filtros ---
df_filtrado = df.copy()import plotly.express as px
import base64

# --- CONFIGURACIONES ---
st.set_page_config(page_title="Control Operacional de Comercio Exterior de Lara",
                   layout="wide")

# --- COLORES CORPORATIVOS ---
COLOR_TITULO = "#000000"
COLOR_CUADRO = "#FFFFFF"
COLOR_METRIC = "#1F77B4"
COLOR_FONDO = "#F5F5F5"

# --- FUNCIONES ---
def get_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def set_background(png_file):
    bin_str = get_base64(png_file)
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{bin_str}");
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# --- FONDO Y LOGO ---
set_background("assets/fondo_comercio.jpg")
st.image("assets/logo_empresa.png", width=150)

# --- TÍTULO ---
st.markdown(f"<h1 style='color:{COLOR_TITULO}; text-align:center;'>Control Operacional de Comercio Exterior de Lara</h1>", unsafe_allow_html=True)
st.markdown("---")

# --- CARGA DE DATOS ---
@st.cache_data
def load_data():
    df = pd.read_excel("data/datos.xlsx")
    # Asegurar que los campos de peso sean numéricos
    for col in ["Peso Neto Exportado", "Peso Neto Importado", "Peso Neto Manejado"]:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

@st.cache_data
def load_data():
    df = pd.read_excel("data/datos.xlsx")
    # Normalizar nombres: quitar espacios, mayúsculas y acentos
    df.columns = df.columns.str.strip().str.upper().str.replace(" ", "_").str.replace("Á","A").str.replace("É","E").str.replace("Í","I").str.replace("Ó","O").str.replace("Ú","U")
    
    # Asegurar que los campos de peso sean numéricos
    for col in ["PESO_NETO_EXPORTADO", "PESO_NETO_IMPORTADO", "PESO_NETO_MANEJADO"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        else:
            df[col] = 0
    return df
  
# --- FILTRADO DE DATOS ---
df_filtrado = df.copy()
if destino_seleccion:
    df_filtrado = df_filtrado[df_filtrado['DESTINO'].isin(destino_seleccion)]
if contenido_seleccion:
    df_filtrado = df_filtrado[df_filtrado['CONTENIDO'].isin(contenido_seleccion)]
if fecha:
    df_filtrado = df_filtrado[df_filtrado['FECHA'] == pd.to_datetime(fecha)]

# --- KPIs CON ICONOS ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"<div style='background-color:{COLOR_CUADRO}; padding:20px; border-radius:15px; text-align:center;'>"
                f"📦<h3 style='color:{COLOR_METRIC};'>Operaciones</h3>"
                f"<h2>{len(df_filtrado)}</h2></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div style='background-color:{COLOR_CUADRO}; padding:20px; border-radius:15px; text-align:center;'>"
                f"🌍<h3 style='color:{COLOR_METRIC};'>Peso Neto Exportado (t)</h3>"
                f"<h2>{df_filtrado['Peso Neto Exportado'].sum():,.2f}</h2></div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div style='background-color:{COLOR_CUADRO}; padding:20px; border-radius:15px; text-align:center;'>"
                f"🚛<h3 style='color:{COLOR_METRIC};'>Peso Neto Importado (t)</h3>"
                f"<h2>{df_filtrado['Peso Neto Importado'].sum():,.2f}</h2></div>", unsafe_allow_html=True)
with col4:
    st.markdown(f"<div style='background-color:{COLOR_CUADRO}; padding:20px; border-radius:15px; text-align:center;'>"
                f"⚖️<h3 style='color:{COLOR_METRIC};'>Peso Total (t)</h3>"
                f"<h2>{df_filtrado[['Peso Neto Exportado','Peso Neto Importado']].sum().sum():,.2f}</h2></div>", unsafe_allow_html=True)

st.markdown("---")

# --- MAPA 3D DE DESTINOS ---
if not df_filtrado.empty:
    # Asignar latitud y longitud ficticias si no existen
    if 'LATITUD' not in df_filtrado.columns or 'LONGITUD' not in df_filtrado.columns:
        import numpy as np
        df_filtrado['LATITUD'] = np.random.uniform(-15, 15, len(df_filtrado))
        df_filtrado['LONGITUD'] = np.random.uniform(-70, -60, len(df_filtrado))
        fig_map = px.scatter_3d(df_filtrado, 
                            x='LONGITUD', y='LATITUD', z='Peso Neto Exportado', 
                            color='DESTINO', size='Peso Neto Exportado', 
                            hover_name='DESTINO')
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning("No hay datos para mostrar en el mapa con los filtros seleccionados.")
