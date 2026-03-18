import streamlit as st
from pathlib import Path
import base64

# ------------------------------
# FUNCIÓN PARA CARGAR IMÁGENES
# ------------------------------
def cargar_base64(ruta):
    try:
        with open(ruta, "rb") as archivo:
            return base64.b64encode(archivo.read()).decode()
    except Exception as e:
        st.error(f"Error cargando imagen: {e}")
        return None

# ------------------------------
# DETECTAR CARPETA ASSETS
# ------------------------------
def obtener_assets():
    rutas = [
        Path.cwd() / "assets",
        Path().absolute() / "assets",
    ]
    for r in rutas:
        if r.exists():
            return r
    return None

ASSETS = obtener_assets()

if ASSETS is None:
    st.error("❌ No se encontró la carpeta 'assets'")
    st.stop()

# ------------------------------
# BUSCAR IMÁGENES AUTOMÁTICAMENTE
# ------------------------------
def buscar_archivo(nombre):
    extensiones = [".png", ".jpg", ".jpeg"]
    for ext in extensiones:
        ruta = ASSETS / f"{nombre}{ext}"
        if ruta.exists():
            return ruta
    return None

# ------------------------------
# FONDO
# ------------------------------
ruta_fondo = buscar_archivo("fondo_comercio")

if ruta_fondo:
    fondo_base64 = cargar_base64(ruta_fondo)
    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{fondo_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    </style>
    """, unsafe_allow_html=True)
else:
    st.warning("⚠️ No se encontró 'fondo_comercio' en assets")

# ------------------------------
# LOGO
# ------------------------------
ruta_logo = buscar_archivo("logo_empresa")

if ruta_logo:
    logo_base64 = cargar_base64(ruta_logo)
    st.sidebar.markdown(f"""
    <div style="text-align:center;">
        <img src="data:image/png;base64,{logo_base64}" width="150">
    </div>
    """, unsafe_allow_html=True)
else:
    st.warning("⚠️ No se encontró 'logo_empresa' en assets")
