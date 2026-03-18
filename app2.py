import base64
from pathlib import Path
import streamlit as st

# ------------------------------
# DETECCIÓN AUTOMÁTICA DE RUTAS
# ------------------------------
def obtener_asseets_dir():
    posibles_rutas = [
        Path().absolute() / "asseets",
        Path(file).parent / "asseets" if "file" in globals() else None,
        Path.cwd() / "asseets",
    ]

    for ruta in posibles_rutas:
        if ruta and ruta.exists():
            return ruta

    return None

ASSETS_DIR = obtener_asseets_dir()

# ------------------------------
# FUNCION BASE64
# ------------------------------
def cargar_imagen_base64(ruta):
    try:
        with open(ruta, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

# ------------------------------
# VALIDACIÓN
# ------------------------------
if not ASSETS_DIR:
    st.error("❌ No se encontró la carpeta 'assets'")
    st.stop()

st.sidebar.success(f"Assets detectado en: {ASSETS_DIR}")

# ------------------------------
# FONDO AUTOMÁTICO
# ------------------------------
def buscar_imagen(nombre_base):
    extensiones = [".jpg", ".jpeg", ".png"]
    for ext in extensiones:
        ruta = ASSETS_DIR / f"{nombre_base}{ext}"
        if ruta.exists():
            return ruta
    return None

ruta_fondo = buscar_imagen("fondo_comercio")
img_fondo = cargar_imagen_base64(ruta_fondo) if ruta_fondo else None

if img_fondo:
    st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(255,255,255,0.3), rgba(255,255,255,0.3)),
                    url("data:image/jpg;base64,{img_fondo}");
        background-size: cover;
        background-position: center;
    }}
    </style>
    """, unsafe_allow_html=True)
else:
    st.warning("⚠️ No se encontró imagen de fondo (fondo_comercio)")

# ------------------------------
# LOGO AUTOMÁTICO
# ------------------------------
ruta_logo = buscar_imagen("logo_empresa")
img_logo = cargar_imagen_base64(ruta_logo) if ruta_logo else None

if img_logo:
    st.sidebar.markdown(f"""
    <div style="text-align:center;">
        <img src="data:image/png;base64,{img_logo}" width="150">
    </div>
    """, unsafe_allow_html=True)
else:
    st.warning("⚠️ No se encontró logo (logo_empresa)")

    st.dataframe(
        df.style.apply(estilo, subset=["peso total (t)"]),
        use_container_width=True
    )
