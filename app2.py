import streamlit as st
from pathlib import Path
from pages import resumen_ejecutivo, analisis_operaciones, analisis_paises, datos_completos

BASE_DIR = Path(file).parent

st.sidebar.image(BASE_DIR / "logo.png", use_column_width=True)
st.sidebar.title("Dashboard Comercio Exterior")

pagina = st.sidebar.radio(
    "Selecciona la página",
    ["Resumen Ejecutivo", "Análisis de Operaciones", "Análisis por Países", "Datos Completos"]
)

if pagina == "Resumen Ejecutivo":
    resumen_ejecutivo.run(BASE_DIR)
elif pagina == "Análisis de Operaciones":
    analisis_operaciones.run(BASE_DIR)
elif pagina == "Análisis por Países":
    analisis_paises.run(BASE_DIR)
elif pagina == "Datos Completos":
    datos_completos.run(BASE_DIR)
