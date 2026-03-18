import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import base64

# ------------------------------
# CONFIGURACIÓN
# ------------------------------
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "datos.xlsx"
ASSETS_DIR = BASE_DIR / "assets"

st.set_page_config(
    page_title="Control Operacional Empresa de Comercio Exterior de Lara",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------
# LOGO Y FONDO
# ------------------------------
logo_path = ASSETS_DIR / "logo.png"
fondo_path = ASSETS_DIR / "fondo_comercio.jpg"

if logo_path.exists():
    st.sidebar.image(logo_path, width=150)

def set_fondo(path):
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{b64}");
            background-size: cover;
            background-position: center;
        }}
        </style>
    """, unsafe_allow_html=True)

if fondo_path.exists():
    set_fondo(fondo_path)

# ------------------------------
# CARGA DE DATOS
# ------------------------------
@st.cache_data
def cargar_datos(file=None):
    archivo = file if file else DATA_FILE
    try:
        df = pd.read_excel(archivo)
    except:
        return pd.DataFrame()
    
    df.columns = df.columns.str.strip()
    
    # Convertir pesos a numérico
    for col in ["Peso Neto Manejado", "Peso Neto Exportado", "Peso Neto Importado"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    
    # Toneladas
    if "Peso Neto Exportado" in df.columns:
        df["peso neto exportado (t)"] = df["Peso Neto Exportado"] / 1000
    if "Peso Neto Importado" in df.columns:
        df["peso neto importado (t)"] = df["Peso Neto Importado"] / 1000
    if "Peso Neto Manejado" in df.columns and "Peso Neto Exportado" in df.columns:
        df["peso total (t)"] = (df["Peso Neto Manejado"] + df["Peso Neto Exportado"]) / 1000
    
    # Fecha
    if 'FECHA' in df.columns:
        df['FECHA'] = pd.to_datetime(df['FECHA'], errors='coerce')
    
    return df

archivo_excel = st.sidebar.file_uploader("Actualizar Excel", type=["xlsx"])
df = cargar_datos(archivo_excel)

if df.empty:
    st.warning("No se pudo cargar el archivo Excel o no contiene datos.")
else:
   # ------------------------------
# FILTROS
# ------------------------------
df_filtrado = df.copy()

# FILTRO DE FECHA (RANGO)
if 'FECHA' in df_filtrado.columns:
    min_fecha = df_filtrado['FECHA'].min()
    max_fecha = df_filtrado['FECHA'].max()

    rango_fechas = st.sidebar.date_input(
        "Rango de Fechas",
        value=(min_fecha, max_fecha)
    )

    if isinstance(rango_fechas, tuple):
        fecha_inicio, fecha_fin = rango_fechas
        df_filtrado = df_filtrado[
            (df_filtrado['FECHA'] >= pd.to_datetime(fecha_inicio)) &
            (df_filtrado['FECHA'] <= pd.to_datetime(fecha_fin))
        ]

# FILTRO DESTINO
if 'DESTINO' in df_filtrado.columns:
    destinos = df_filtrado['DESTINO'].dropna().unique()
    destino_seleccion = st.sidebar.multiselect("Destino", destinos)

    if destino_seleccion:
        df_filtrado = df_filtrado[
            df_filtrado['DESTINO'].isin(destino_seleccion)
        ]

# FILTRO CONTENIDO
if 'CONTENIDO' in df_filtrado.columns:
    contenidos = df_filtrado['CONTENIDO'].dropna().unique()
    contenido_seleccion = st.sidebar.multiselect("Contenido", contenidos)

    if contenido_seleccion:
        df_filtrado = df_filtrado[
            df_filtrado['CONTENIDO'].isin(contenido_seleccion)
        ]
    
    # ------------------------------
    # APLICAR FILTROS
    # ------------------------------
    df_filtrado = df.copy()

# FILTRO POR FECHA (RANGO)
if 'FECHA' in df_filtrado.columns and isinstance(rango_fechas, tuple):
    fecha_inicio, fecha_fin = rango_fechas
    df_filtrado = df_filtrado[
        (df_filtrado['FECHA'] >= pd.to_datetime(fecha_inicio)) &
        (df_filtrado['FECHA'] <= pd.to_datetime(fecha_fin))
    ]
        df_filtrado = df_filtrado[df_filtrado['DESTINO'].isin(destino_seleccion)]
    if contenido_seleccion:
        df_filtrado = df_filtrado[df_filtrado['CONTENIDO'].isin(contenido_seleccion)]
    
    # ------------------------------# TÍTULO PRINCIPAL
    # ------------------------------
    st.markdown(
        """
        <h1 style='text-align:center; color:black; border:3px solid white; padding:15px; border-radius:12px;'>
            Control Operacional Empresa de Comercio Exterior de Lara
        </h1>
        """,
        unsafe_allow_html=True
    )
    
    # ------------------------------
    # KPIs
    # ------------------------------
    COLOR1 = "#1f77b4"
    COLOR2 = "#ff7f0e"
    COLOR3 = "#2ca02c"
    COLOR4 = "#d62728"
    
    col1, col2, col3, col4 = st.columns(4)
    
    col1, col2, col3, col4 = st.columns(4)

# KPI 1: Operaciones
if 'FECHA' in df_filtrado.columns:
    col1.metric("Operaciones", len(df_filtrado))

# KPI 2: Exportado
if "peso neto exportado (t)" in df_filtrado.columns:
    total_exportado = df_filtrado["peso neto exportado (t)"].sum()
    col2.metric("Peso Neto Exportado (t)", f"{total_exportado:,.2f}")

# KPI 3: Importado
if "peso neto importado (t)" in df_filtrado.columns:
    total_importado = df_filtrado["peso neto importado (t)"].sum()
    col3.metric("Peso Neto Importado (t)", f"{total_importado:,.2f}")

# KPI 4: Total
if "peso total (t)" in df_filtrado.columns:
    total_general = df_filtrado["peso total (t)"].sum()
    col4.metric("Peso Total (t)", f"{total_general:,.2f}")
    # ------------------------------
    # GRÁFICAS
    # ------------------------------
    st.markdown("### Gráficas de Pesos")
    if "peso neto exportado (t)" in df_filtrado.columns:
        fig = px.histogram(df_filtrado, x="peso neto exportado (t)", color="DESTINO", title="Peso Neto Exportado por Destino")
        st.plotly_chart(fig, use_container_width=True)
    if "peso neto importado (t)" in df_filtrado.columns:
        fig2 = px.histogram(df_filtrado, x="peso neto importado (t)", color="DESTINO", title="Peso Neto Importado por Destino")
        st.plotly_chart(fig2, use_container_width=True)
    
    # ------------------------------
    # MAPA 3D DESTINOS
    # ------------------------------
    st.markdown("### Mapa 3D Destinos Exportados")
    
    # Diccionario de lat/lon aproximados de países más frecuentes
    lat_lon = {
        "Venezuela": (6.4238, -66.5897),
        "Brasil": (-14.2350, -51.9253),
        "Colombia": (4.5709, -74.2973),
        "Estados Unidos": (37.0902, -95.7129),
        "México": (23.6345, -102.5528),
        # Agrega más destinos según sea necesario
    }
    
    if 'DESTINO' in df_filtrado.columns:
        df_map = df_filtrado.copy()
        df_map["latitud"] = df_map["DESTINO"].map(lambda x: lat_lon.get(x, 0))
        df_map["longitud"] = df_map["DESTINO"].map(lambda x: lat_lon.get(x, 0))
        df_map = df_map[df_map["latitud"] != 0]  # eliminar destinos sin coordenadas
        
        if not df_map.empty:
            fig_map = px.scatter_geo(
                df_map,
                lat="latitud",
                lon="longitud",
                hover_name="DESTINO",
                size="peso neto exportado (t)" if "peso neto exportado (t)" in df_map.columns else None,
                projection="natural earth",
                title="Destinos de Exportación"
            )
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("No hay coordenadas válidas para los destinos en el mapa 3D.")
