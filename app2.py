import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64

# ===== CONFIGURACIÓN DE PÁGINA =====
st.set_page_config(page_title="Dashboard Comercio Exterior", layout="wide")

# ===== RUTAS =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_PATH = os.path.join(DATA_DIR, "datos.xlsx")  # Asegúrate del nombre exacto

# ===== FUNCIONES =====
def get_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def set_background(png_file):
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

# ===== FONDO Y LOGO =====
fondo_path = os.path.join(ASSETS_DIR, "fondo_comercio.jpg")
logo_path = os.path.join(ASSETS_DIR, "logo_empresa.png")
if os.path.exists(fondo_path):
    set_background(fondo_path)
if os.path.exists(logo_path):
    st.image(logo_path, width=120)

# ===== TÍTULO PRINCIPAL =====
st.markdown("""
<h1 style="color:black; border:2px solid white; padding:15px; text-align:center;">
Control Operacional de Comercio Exterior de Lara
</h1>
""", unsafe_allow_html=True)

# ===== CARGA DE DATOS =====
@st.cache_data
def load_data():
    try:
        df = pd.read_excel(DATA_PATH)
        # Homogeneizar nombres
        df.columns = [c.strip().upper() for c in df.columns]
        
        # Convertir columnas numéricas
        numeric_cols = ["PESO NETO EXPORTADO", "PESO NETO IMPORTADO", "PESO NETO MANEJADO"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Crear columna de peso total
        df["PESO TOTAL"] = df.get("PESO NETO EXPORTADO",0) + df.get("PESO NETO IMPORTADO",0)
        
        # Convertir FECHA a datetime
        if "FECHA" in df.columns:
            df["FECHA"] = pd.to_datetime(df["FECHA"], errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"No se pudo cargar el archivo Excel: {e}")
        return pd.DataFrame()

df = load_data()
if df.empty:
    st.stop()

# ===== FILTROS OPCIONALES =====
st.sidebar.header("Filtros (opcional)")
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

# ===== KPIs EJECUTIVOS CON ICONOS =====
st.markdown("<h2 style='color:black;'>Resumen Ejecutivo</h2>", unsafe_allow_html=True)
kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

kpi_col1.markdown(f"""
<div style="background-color:white; padding:15px; border-radius:10px; text-align:center;">
<img src="https://img.icons8.com/ios-filled/50/000000/briefcase.png"/>
<h3>Operaciones</h3>
<h2>{len(df_filtrado)}</h2>
</div>
""", unsafe_allow_html=True)

kpi_col2.markdown(f"""
<div style="background-color:white; padding:15px; border-radius:10px; text-align:center;">
<img src="https://img.icons8.com/ios-filled/50/000000/worldwide-location.png"/>
<h3>Exportador</h3>
<h2>{df_filtrado['PESO NETO EXPORTADO'].sum():,.2f} t</h2>
</div>
""", unsafe_allow_html=True)
kpi_col3.markdown(f"""
<div style="background-color:white; padding:15px; border-radius:10px; text-align:center;">
<img src="https://img.icons8.com/ios-filled/50/000000/import.png"/>
<h3>Importador</h3>
<h2>{df_filtrado['PESO NETO IMPORTADO'].sum():,.2f} t</h2>
</div>
""", unsafe_allow_html=True)

kpi_col4.markdown(f"""
<div style="background-color:white; padding:15px; border-radius:10px; text-align:center;">
<img src="https://img.icons8.com/ios-filled/50/000000/weight.png"/>
<h3>Peso Total</h3>
<h2>{df_filtrado['PESO TOTAL'].sum():,.2f} t</h2>
</div>
""", unsafe_allow_html=True)

# ===== GRÁFICOS EJECUTIVOS =====
st.markdown("<h2 style='color:black;'>Gráficos Ejecutivos</h2>", unsafe_allow_html=True)
graf_col1, graf_col2 = st.columns(2)

# Exportaciones por contenido
if 'CONTENIDO' in df_filtrado.columns:
    fig_exp = px.bar(df_filtrado.groupby("CONTENIDO")["PESO NETO EXPORTADO"].sum().reset_index(),
                     x="CONTENIDO", y="PESO NETO EXPORTADO",
                     title="Exportaciones por Contenido")
    graf_col1.plotly_chart(fig_exp, use_container_width=True)

# Importaciones por contenido
if 'CONTENIDO' in df_filtrado.columns:
    fig_imp = px.bar(df_filtrado.groupby("CONTENIDO")["PESO NETO IMPORTADO"].sum().reset_index(),
                     x="CONTENIDO", y="PESO NETO IMPORTADO",
                     title="Importaciones por Contenido")
    graf_col2.plotly_chart(fig_imp, use_container_width=True)

# ===== MAPA DE EXPORTACIONES =====
if 'DESTINO' in df_filtrado.columns and not df_filtrado['DESTINO'].empty:
    fig_map = px.scatter_geo(
        df_filtrado,
        locations="DESTINO",
        locationmode='country names',
        size="PESO NETO EXPORTADO",
        hover_name="CONTENIDO",
        title="Exportaciones por Destino"
    )
    st.plotly_chart(fig_map, use_container_width=True)
