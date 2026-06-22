"""
Dashboard de Control Operacional de Comercio Exterior - Lara
==============================================================
Requiere: streamlit, pandas, plotly, openpyxl
Instalación: pip install streamlit pandas plotly openpyxl

Estructura de carpetas esperada (relativa a este archivo):
    data/datos.xlsx
    assets/logo_empresa.png
    assets/fondo_comercio.jpg

Ejecución:
    streamlit run dashboard_comercio_exterior.py
"""

import os
from pathlib import Path
import base64

import streamlit as st
import pandas as pd
import plotly.express as px

# ============================================================
# CONFIGURACIÓN GENERAL DE LA PÁGINA
# ============================================================
st.set_page_config(
    page_title="Comercio Exterior - Lara",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CONSTANTES Y ESTILO CORPORATIVO
# ============================================================
COLOR_TITULO = "#1F4E79"
COLOR_PRIMARIO = "#0A1F44"    # azul marino corporativo
COLOR_SECUNDARIO = "#2E75B6"  # azul medio
COLOR_ACENTO = "#FFD700"      # dorado

NOMBRE_EMPRESA = "EMCOEX"
SUBTITULO_DASHBOARD = "Panel de Indicadores en Tiempo Real"

ASSETS_DIR = Path("assets")
DATA_PATH = Path("data/datos.xlsx")

COLUMNAS_NUMERICAS = ["Peso Neto Exportado", "Peso Neto Importado", "Peso Neto Manejado"]
COLUMNAS_REQUERIDAS = ["DESTINO", "FECHA", "TIPO DE CARGA"] + COLUMNAS_NUMERICAS


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================
def set_background(image_path: Path) -> None:
    """Aplica una imagen de fondo a la app, si el archivo existe."""
    if not image_path.exists():
        return
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    ext = image_path.suffix.replace(".", "") or "jpg"
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/{ext};base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def cargar_datos(file_path: str, last_modified: float) -> pd.DataFrame:
    """Carga y limpia los datos del Excel.

    El parámetro `last_modified` se usa solo para invalidar el caché
    de Streamlit automáticamente cuando el archivo cambia en disco.
    """
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()
    return df


def formato_numero(valor: float) -> str:
    """Formatea un número al estilo latino: punto como separador de miles."""
    return f"{valor:,.0f}".replace(",", ".")


def aplicar_fondo_blanco(fig):
    """Aplica un fondo blanco semitransparente a un gráfico de Plotly."""
    fig.update_layout(
        paper_bgcolor="rgba(255,255,255,0.90)",
        plot_bgcolor="rgba(255,255,255,0.80)",
        font=dict(family="Arial", size=14, color="black"),
    )
    return fig


def marca_de_agua(fig, texto: str):
    """Agrega una marca de agua discreta y centrada a un gráfico."""
    fig.add_annotation(
        text=texto,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=40, color="rgba(0,0,0,0.05)"),
        align="center",
    )
    return fig


# ============================================================
# CARGA DE DATOS
# ============================================================
if not DATA_PATH.exists():
    st.error(f"❌ No se encontró el archivo de datos en: {DATA_PATH}")
    st.stop()

df = cargar_datos(str(DATA_PATH), os.path.getmtime(DATA_PATH))

faltantes = [c for c in COLUMNAS_REQUERIDAS if c not in df.columns]
if faltantes:
    st.error(f"❌ Faltan columnas en el Excel: {faltantes}")
    st.stop()

for col in COLUMNAS_NUMERICAS:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
df["FECHA"] = pd.to_datetime(df["FECHA"], errors="coerce")

# Eliminar duplicados reales (mismo destino + fecha + tipo de carga)
id_unico = (
    df["DESTINO"].astype(str) + "_" + df["FECHA"].astype(str) + "_" + df["TIPO DE CARGA"].astype(str)
)
df = df.assign(_id_unico=id_unico).drop_duplicates(subset="_id_unico").drop(columns="_id_unico")

# ============================================================
# ENCABEZADO / LOGO — banner "hero" con gradiente corporativo
# ============================================================
set_background(ASSETS_DIR / "fondo_comercio.jpg")

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}

    .hero-banner {{
        background: linear-gradient(135deg, {COLOR_PRIMARIO} 0%, {COLOR_TITULO} 55%, {COLOR_SECUNDARIO} 100%);
        border-radius: 20px;
        padding: 28px 36px;
        margin-bottom: 28px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.18);
        display: flex;
        align-items: center;
        gap: 24px;
    }}
    .hero-logo {{
        height: 56px;
        border-radius: 10px;
        background: rgba(255,255,255,0.9);
        padding: 6px;
    }}
    .hero-title {{
        color: white;
        font-size: 30px;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.3px;
    }}
    .hero-subtitle {{
        color: rgba(255,255,255,0.78);
        font-size: 14px;
        margin-top: 4px;
        font-weight: 400;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

logo_path = ASSETS_DIR / "logo_empresa.png"
logo_html = ""
if logo_path.exists():
    logo_b64 = base64.b64encode(logo_path.read_bytes()).decode()
    logo_html = f'<img class="hero-logo" src="data:image/png;base64,{logo_b64}" />'

st.markdown(
    f"""
    <div class="hero-banner">
        {logo_html}
        <div>
            <p class="hero-title">Control Operacional de Comercio Exterior de Lara</p>
            <p class="hero-subtitle">{NOMBRE_EMPRESA} · {SUBTITULO_DASHBOARD}</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# FILTROS (SIDEBAR)
# ============================================================
st.sidebar.markdown("## 🔎 Filtros")

fecha_min, fecha_max = df["FECHA"].min(), df["FECHA"].max()
rango_fecha = st.sidebar.date_input("Rango de Fecha", [fecha_min, fecha_max])

destinos_disponibles = sorted(df["DESTINO"].dropna().unique())
destinos = st.sidebar.multiselect("Destino", destinos_disponibles, default=destinos_disponibles)

tipos_disponibles = sorted(df["TIPO DE CARGA"].dropna().unique())
tipos_carga = st.sidebar.multiselect("Tipo de Carga", tipos_disponibles, default=tipos_disponibles)

# ============================================================
# APLICAR FILTROS — ÚNICA FUENTE DE VERDAD: df_filtrado
# Todo lo que sigue (KPIs y gráficos) usa SIEMPRE df_filtrado.
# ============================================================
df_filtrado = df.copy()

if isinstance(rango_fecha, (list, tuple)) and len(rango_fecha) == 2:
    inicio, fin = pd.to_datetime(rango_fecha[0]), pd.to_datetime(rango_fecha[1])
    df_filtrado = df_filtrado[(df_filtrado["FECHA"] >= inicio) & (df_filtrado["FECHA"] <= fin)]

if destinos:
    df_filtrado = df_filtrado[df_filtrado["DESTINO"].isin(destinos)]

if tipos_carga:
    df_filtrado = df_filtrado[df_filtrado["TIPO DE CARGA"].isin(tipos_carga)]

if df_filtrado.empty:
    st.warning("⚠️ No hay datos para los filtros seleccionados.")
    st.stop()

# ============================================================
# KPIs — calculados sobre df_filtrado (esto es lo que estaba roto)
# ============================================================
total_operaciones = len(df_filtrado)
total_exportado = df_filtrado["Peso Neto Exportado"].sum()
total_importado = df_filtrado["Peso Neto Importado"].sum()
total_total = df_filtrado["Peso Neto Manejado"].sum()

exportado_fmt = formato_numero(total_exportado)
importado_fmt = formato_numero(total_importado)
total_fmt = formato_numero(total_total)

# Métricas comparativas (le dan contexto analítico a cada KPI)
pct_exportado = (total_exportado / total_total * 100) if total_total else 0
pct_importado = (total_importado / total_total * 100) if total_total else 0
promedio_operacion = (total_total / total_operaciones) if total_operaciones else 0

st.markdown(
    """
    <style>
    .kpi-box {
        background: linear-gradient(160deg, rgba(10,31,68,0.94), rgba(31,78,121,0.88));
        border-radius: 16px;
        padding: 22px 20px;
        text-align: left;
        color: white;
        box-shadow: 0 6px 20px rgba(0,0,0,0.16);
        border-top: 4px solid var(--accent);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        height: 100%;
    }
    .kpi-box:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 28px rgba(0,0,0,0.24);
    }
    .kpi-icon { font-size: 22px; }
    .kpi-title {
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        opacity: 0.85;
        margin-top: 10px;
    }
    .kpi-value { font-size: 32px; font-weight: 800; margin-top: 4px; line-height: 1.1; }
    .kpi-sub { font-size: 12px; opacity: 0.72; margin-top: 6px; }
    </style>
    """,
    unsafe_allow_html=True,
)

kpis = [
    ("🚢", "Operaciones", f"{total_operaciones}", f"Promedio {formato_numero(promedio_operacion)} kg/op.", "#00BFFF"),
    ("🌍", "Exportado (kg)", exportado_fmt, f"{pct_exportado:.1f}% del total manejado", "#28A745"),
    ("📦", "Importado (kg)", importado_fmt, f"{pct_importado:.1f}% del total manejado", "#FFC107"),
    ("⚖️", "Total manejado (kg)", total_fmt, f"{len(destinos)} destino(s) seleccionados", "#DC3545"),
]

cols = st.columns(4)
for col, (icono, titulo, valor, sub, color) in zip(cols, kpis):
    with col:
        st.markdown(
            f"""
            <div class="kpi-box" style="--accent: {color};">
                <div class="kpi-icon">{icono}</div>
                <div class="kpi-title">{titulo}</div>
                <div class="kpi-value">{valor}</div>
                <div class="kpi-sub">{sub}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# CONTENIDO PRINCIPAL — organizado en pestañas (estilo empresarial)
# ============================================================
tab_resumen, tab_logistica, tab_mapa, tab_datos = st.tabs(
    ["📊 Exportaciones por País", "📦 Contenedores vs Toneladas", "🗺️ Mapa Global", "📋 Datos"]
)

with tab_resumen:
    df_paises = df_filtrado.groupby("DESTINO", as_index=False)["Peso Neto Exportado"].sum()
    fig1 = px.bar(df_paises, x="DESTINO", y="Peso Neto Exportado", text="Peso Neto Exportado")
    fig1.update_traces(texttemplate="%{text:,.0f}", textposition="outside", marker_line_width=1.5)
    fig1.update_layout(title="Exportaciones por País", title_x=0.5, font=dict(size=14, family="Arial"))
    fig1 = aplicar_fondo_blanco(fig1)
    fig1 = marca_de_agua(fig1, "COMERCIO EXTERIOR")
    st.plotly_chart(fig1, use_container_width=True)

with tab_logistica:
    if "CONTENIDO" in df_filtrado.columns and "LLENOS RECIBIDOS (EXPORTADOS)" in df_filtrado.columns:
        df_cont = df_filtrado.groupby("CONTENIDO", as_index=False)[
            ["LLENOS RECIBIDOS (EXPORTADOS)", "Peso Neto Exportado"]
        ].sum()
        fig2 = px.bar(
            df_cont,
            x="CONTENIDO",
            y=["LLENOS RECIBIDOS (EXPORTADOS)", "Peso Neto Exportado"],
            barmode="group",
        )
        fig2.update_layout(
            title="Contenedores vs Toneladas", title_x=0.5, font=dict(size=14, family="Arial")
        )
        fig2 = aplicar_fondo_blanco(fig2)
        fig2 = marca_de_agua(fig2, "LOGÍSTICA INTERNACIONAL")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info(
            "ℹ️ Esta vista requiere las columnas 'CONTENIDO' y "
            "'LLENOS RECIBIDOS (EXPORTADOS)' en el Excel."
        )

with tab_mapa:
    df_map = df_filtrado.groupby(["DESTINO", "TIPO DE CARGA"], as_index=False)[
        "Peso Neto Exportado"
    ].sum()
    fig_map = px.scatter_geo(
        df_map,
        locations="DESTINO",
        locationmode="country names",
        size="Peso Neto Exportado",
        color="TIPO DE CARGA",
        hover_name="DESTINO",
        size_max=45,
        projection="natural earth",
    )
    fig_map.update_layout(
        title=dict(
            text="Mapa de Exportaciones por País y Tipo de Carga",
            x=0.5,
            font=dict(family="Arial", size=20, color="black"),
        ),
        paper_bgcolor="rgba(255,255,255,0.95)",
        geo=dict(
            bgcolor="rgba(255,255,255,0.95)",
            showland=True,
            landcolor="#F4F6F7",
            showocean=True,
            oceancolor="#D6EAF8",
            showcountries=True,
            countrycolor="#A6ACAF",
        ),
        legend=dict(title="Tipo de Carga", orientation="h", y=-0.1),
    )
    fig_map = marca_de_agua(fig_map, "EXPORTACIONES")
    st.plotly_chart(fig_map, use_container_width=True)

with tab_datos:
    st.dataframe(df_filtrado, use_container_width=True)
    csv = df_filtrado.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Descargar datos filtrados (CSV)",
        data=csv,
        file_name="comercio_exterior_filtrado.csv",
        mime="text/csv",
    )

st.markdown(
    f"""
    <hr style='margin-top:40px; margin-bottom:10px; border:none; border-top:1px solid #E0E0E0;'>
    <div style='text-align:center; color:#8A8F98; font-size:12px;'>
        {NOMBRE_EMPRESA} · Control Operacional de Comercio Exterior ·
        Actualizado {pd.Timestamp.now():%Y-%m-%d %H:%M}
    </div>
    """,
    unsafe_allow_html=True,
)
