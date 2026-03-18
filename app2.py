import streamlit as st
from pathlib import Path
import base64

# ------------------------------
# UBICACIÓN REAL DEL PROYECTO
# ------------------------------
BASE_DIR = Path(file).resolve().parent
ASSETS = BASE_DIR / "assets"

st.write("BASE_DIR:", BASE_DIR)
st.write("ASSETS:", ASSETS)

# ------------------------------
# VALIDACIÓN
# ------------------------------
if not ASSETS.exists():
    st.error(f"No se encontró la carpeta assets en: {ASSETS}")
    st.stop()

# ------------------------------
# FUNCIÓN BASE64
# ------------------------------
def cargar_base64(ruta):
    try:
        with open(ruta, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception as e:
        st.error(f"Error cargando imagen: {e}")
        return None

# ------------------------------
# FONDO
# ------------------------------
ruta_fondo = ASSETS / "fondo_comercio.jpg"

if ruta_fondo.exists():
    fondo = cargar_base64(ruta_fondo)
    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{fondo}");
        background-size: cover;
        background-position: center;
    }}
    </style>
    """, unsafe_allow_html=True)
else:
    st.error(f"No se encontró fondo en: {ruta_fondo}")

# ------------------------------
# LOGO
# ------------------------------
ruta_logo = ASSETS / "logo_empresa.png"

if ruta_logo.exists():
    logo = cargar_base64(ruta_logo)
    st.sidebar.markdown(f"""
    <img src="data:image/png;base64,{logo}" width="150">
    """, unsafe_allow_html=True)
else:
    st.error(f"No se encontró logo en: {ruta_logo}")
