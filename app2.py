# -*- coding: utf-8 -*-
import streamlit as st
from pathlib import Path
from PIL import Image

# Rutas
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

# Importar módulos
from pages import resumen_ejecutivo, analisis_operaciones, analisis_paises, datos_completos

# Configuración Streamlit
st.set_page_config(
    page_title="Dashboard Empresarial",
    page_icon="📊",
    layout="wide"
)

# Barra superior corporativa
logo_path = DATA_DIR / "logo.png"  # Coloca tu logo aquí
if logo_path.exists():
    logo = Image.open(logo_path)
    col1, col2 = st.columns([0.9, 0.1])
    with col1:
        st.markdown("<h2 style='color:white; margin:0;'>Mi Empresa - Dashboard</h2>", unsafe_allow_html=True)
    with col2:
        st.image(logo, width=50)
    st.markdown("<div style='background-color:#4B7BE5; height:10px; border-radius:5px'></div>", unsafe_allow_html=True)
else:
    st.markdown("<h2 style='color:#4B7BE5;'>Mi Empresa - Dashboard (Logo no encontrado)</h2>", unsafe_allow_html=True)

# Menú lateral
st.sidebar.markdown("<h3 style='text-align:center; color:#4B7BE5'>Menu Principal</h3>", unsafe_allow_html=True)
pagina = st.sidebar.radio(
    "Selecciona una página:",
    ("Resumen Ejecutivo", "Analisis de Operaciones", "Analisis por Paises", "Datos Completos")
)

# Ejecutar página según selección
if pagina == "Resumen Ejecutivo":
    resumen_ejecutivo.run(BASE_DIR)
elif pagina == "Analisis de Operaciones":
    analisis_operaciones.run(BASE_DIR)
elif pagina == "Analisis por Paises":
    analisis_paises.run(BASE_DIR)
elif pagina == "Datos Completos":
    datos_completos.run(BASE_DIR)