import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64

# ================= CONFIGURACIÓN DE PÁGINA =================
st.set_page_config(page_title="Control Operacional Comercio Exterior", layout="wide")

# ================= RUTAS =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_PATH = os.path.join(DATA_DIR, "datos.xlsx")  # Ajusta según tu archivo real

# ================= FUNCIONES =================
def get_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def set_background(png_file):
    if os.path.exists(png_file):
        b64 = get_base64(png_file)
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{b64}");
                background-size: cover;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

# ================= FONDO Y LOGO =================
fondo_path = os.path.join(ASSETS_DIR, "fondo_comercio.jpg")
logo_path = os.path.join(ASSETS_DIR, "logo_empresa.png")
set_background(fondo_path)
if os.path.exists(logo_path):
    st.image(logo_path, width=120)

# ================= TÍTULO PRINCIPAL =================
st.markdown("""
<h1 style="color:#0B3C5D; border:3px solid #FFFFFF; padding:15px; text-align:center;">
Control Operacional de Comercio Exterior de Lara
</h1>
""", unsafe_allow_html=True)

# ================= CARGA DE DATOS =================
@st.cache_data
def load_data():
    df = pd.read_excel(DATA_PATH)
    df.columns = [c.strip().upper() for c in df.columns]

    numeric_cols = ["PESO NETO EXPORTADO", "PESO NETO IMPORTADO", "PESO NETO MANEJADO"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    df["PESO TOTAL"] = df.get("PESO NETO EXPORTADO",0) + df.get("PESO NETO IMPORTADO",0)

    if "FECHA" in df.columns:
        df["FECHA"] = pd.to_datetime(df["FECHA"], errors='coerce')

    # LATITUD y LONGITUD deben estar en Excel
    if "LATITUD" not in df.columns:
        df["LATITUD"] = None
    if "LONGITUD" not in df.columns:
        df["LONGITUD"] = None

    return df

df = load_data()
if df.empty:
    st.error("No se pudo cargar el archivo de datos.")
    st.stop()

# ================= FILTROS OPCIONALES =================
st.sidebar.header("Filtros opcionales")
fecha_seleccion = st.sidebar.date_input("Fecha")
destino_seleccion = st.sidebar.multiselect("Destino", df['DESTINO'].dropna().unique() if 'DESTINO' in df.columns else [])
contenido_seleccion = st.sidebar.multiselect("Contenido", df['CONTENIDO'].dropna().unique() if 'CONTENIDO' in df.columns else [])

df_filtrado = df.copy()
if destino_seleccion:
    df_filtrado = df_filtrado[df_filtrado['DESTINO'].isin(destino_seleccion)]
if contenido_seleccion:
    df_filtrado = df_filtrado[df_filtrado['CONTENIDO'].isin(contenido_seleccion)]
if 'FECHA' in df_filtrado.columns and fecha_seleccion:
    df_filtrado = df_filtrado[df_filtrado['FECHA'] == pd.to_datetime(fecha_seleccion)]

# ================= KPIs =================
st.markdown("<h2 style='color:#0B3C5D;'>Resumen Ejecutivo</h2>", unsafe_allow_html=True)
kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

def kpi_box(col, titulo, valor, icon_url, bg_color="#FFFFFF"):
    col.markdown(f"""
    <div style="background-color:{bg_color}; padding:15px; border-radius:10px; text-align:center;">
    <img src="{icon_url}" width="50"/>
    <h3>{titulo}</h3>
    <h2>{valor}</h2>
    </div>
    """, unsafe_allow_html=True)

kpi_box(kpi_col1, "Operaciones", len(df_filtrado), "https://img.icons8.com/ios-filled/50/0B3C5D/briefcase.png")
kpi_box(kpi_col2, "Exportador", f"{df_filtrado['PESO NETO EXPORTADO'].sum():,.2f} t", "https://img.icons8.com/ios-filled/50/0B3C5D/worldwide-location.png")
kpi_box(kpi_col3, "Importador", f"{df_filtrado['PESO NETO IMPORTADO'].sum():,.2f} t", "https://img.icons8.com/ios-filled/50/0B3C5D/import.png")
kpi_box(kpi_col4, "Peso Total", f"{df_filtrado['PESO TOTAL'].sum():,.2f} t", "https://img.icons8.com/ios-filled/50/0B3C5D/weight.png")

# ================= GRÁFICOS =================
st.markdown("<h2 style='color:#0B3C5D;'>Gráficos Ejecutivos</h2>", unsafe_allow_html=True)
graf_col1, graf_col2 = st.columns(2)

if 'CONTENIDO' in df_filtrado.columns:
    fig_exp = px.bar(df_filtrado.groupby("CONTENIDO")["PESO NETO EXPORTADO"].sum().reset_index(),
                     x="CONTENIDO", y="PESO NETO EXPORTADO",
                     title="Exportaciones por Contenido", color_discrete_sequence=["#1C7C54"])
    graf_col1.plotly_chart(fig_exp, use_container_width=True)

    fig_imp = px.bar(df_filtrado.groupby("CONTENIDO")["PESO NETO IMPORTADO"].sum().reset_index(),
                     x="CONTENIDO", y="PESO NETO IMPORTADO",
                     title="Importaciones por Contenido", color_discrete_sequence=["#F28C28"])
    graf_col2.plotly_chart(fig_imp, use_container_width=True)

# ================= MAPA 3D =================
st.markdown("<h2 style='color:#0B3C5D;'>Mapa de Destinos Exportados</h2>", unsafe_allow_html=True)
if all(col in df_filtrado.columns for col in ["LATITUD","LONGITUD","PESO NETO EXPORTADO","DESTINO"]):
    df_map = df_filtrado.dropna(subset=["LATITUD","LONGITUD"])
    if not df_map.empty:
        fig_map = px.scatter_3d(df_map,
                                x='LONGITUD', y='LATITUD', z='PESO NETO EXPORTADO',
                                color='DESTINO', size='PESO NETO EXPORTADO', hover_name='DESTINO',
                                color_discrete_sequence=px.colors.qualitative.Prism)
        st.plotly_chart(fig_map, use_container_width=True)

# ================= TABLA COMPLETA =================
st.markdown("<h2 style='color:#0B3C5D;'>Datos Completos</h2>", unsafe_allow_html=True)
st.dataframe(df_filtrado, use_container_width=True)
