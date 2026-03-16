import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px

# Base de datos
BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "datos.xlsx"
COLOR_LOGO = "#1f77b4"

# Función para cargar datos
@st.cache_data
def cargar_datos(archivo=None):
    if archivo:
        df = pd.read_excel(archivo)
    else:
        df = pd.read_excel(DATA_FILE)
    df.columns = df.columns.str.strip().str.lower()
    for col in ["peso neto manejado", "peso neto exportado", "peso neto importado"]:
        if col not in df.columns:
            st.error(f"No se encontró la columna '{col}' en el Excel.")
            return pd.DataFrame()
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    df["peso total (t)"] = (df["peso neto manejado"] + df["peso neto exportado"]) / 1000
    return df

# Sidebar: subir archivo
archivo_excel = st.sidebar.file_uploader("Actualizar datos (Excel)", type=["xlsx"])
df = cargar_datos(archivo_excel)
if df.empty:
    st.stop()

# Tabs principales
tabs = st.tabs(["Resumen Ejecutivo", "Operaciones", "Países", "Datos Completos"])

# ------------------------------
# 1️⃣ Resumen Ejecutivo
# ------------------------------
with tabs[0]:
    st.markdown("## 📊 Resumen Ejecutivo")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Operaciones Totales", len(df))
    col2.metric("Peso Neto Exportado (t)", f"{df['peso neto exportado'].sum()/1000:,.2f}")
    col3.metric("Peso Neto Importado (t)", f"{df['peso neto importado'].sum()/1000:,.2f}")
    col4.metric("Peso Total (t)", f"{df['peso total (t)'].sum():,.2f}")

# ------------------------------
# 2️⃣ Análisis de Operaciones
# ------------------------------
with tabs[1]:
    st.markdown("## 📈 Análisis de Operaciones")
    paises = ["Todos"] + list(df["destino"].unique())
    pais_sel = st.selectbox("Filtrar por País", paises)
    df_ops = df if pais_sel == "Todos" else df[df["destino"] == pais_sel]

    st.subheader("Distribución Peso Neto Exportado (t)")
    fig1 = px.histogram(df_ops, x=df_ops["peso neto exportado"]/1000, nbins=30, color_discrete_sequence=[COLOR_LOGO])
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Distribución Peso Neto Importado (t)")
    fig2 = px.histogram(df_ops, x=df_ops["peso neto importado"]/1000, nbins=30, color_discrete_sequence=[COLOR_LOGO])
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Distribución Peso Total (t)")
    fig3 = px.histogram(df_ops, x=df_ops["peso total (t)"], nbins=30, color_discrete_sequence=[COLOR_LOGO])
    st.plotly_chart(fig3, use_container_width=True)

# ------------------------------
# 3️⃣ Análisis por Países
# ------------------------------
with tabs[2]:
    st.markdown("## 🌍 Análisis por Países")
    df_paises = df.groupby("destino")[["peso neto exportado", "peso neto importado", "peso total (t)"]].sum().reset_index()

    st.subheader("Exportaciones por País (t)")
    fig_exp = px.bar(df_paises, x=df_paises["destino"], y=df_paises["peso neto exportado"]/1000, color_discrete_sequence=[COLOR_LOGO])
    st.plotly_chart(fig_exp, use_container_width=True)

    st.subheader("Importaciones por País (t)")
    fig_imp = px.bar(df_paises, x=df_paises["destino"], y=df_paises["peso neto importado"]/1000, color_discrete_sequence=[COLOR_LOGO])
    st.plotly_chart(fig_imp, use_container_width=True)

    st.subheader("Peso Total por País (t)")
    fig_total = px.bar(df_paises, x=df_paises["destino"], y=df_paises["peso total (t)"], color_discrete_sequence=[COLOR_LOGO])
    st.plotly_chart(fig_total, use_container_width=True)

    st.subheader("Mapa de Exportaciones (t)")
    fig_map = px.choropleth(
        df_paises,
        locations=df_paises["destino"],
        locationmode="country names",
        color=df_paises["peso neto exportado"]/1000,
        color_continuous_scale=[COLOR_LOGO, "#ffffff"],
        title="Exportaciones por País"
    )
    st.plotly_chart(fig_map, use_container_width=True)
    # ------------------------------
# 4️⃣ Datos Completos
# ------------------------------
with tabs[3]:
    st.markdown("## 🗂 Datos Completos")
    df_display = df.copy()
    df_display["peso manejado + exportado (t)"] = df_display["peso total (t)"]

    def color_gradiente(s):
        max_val = s.max() if s.max() > 0 else 1
        return [f"background-color: rgba(255,215,0,{v/max_val}); font-weight: bold; border: 1px solid {COLOR_LOGO};" for v in s]

    styler = (
        df_display.style.format({
            "peso neto manejado": "{:,.2f}",
            "peso neto exportado": "{:,.2f}",
            "peso total (t)": "{:,.2f}",
            "peso manejado + exportado (t)": "{:,.2f}"
        })
        .apply(color_gradiente, subset=["peso neto manejado", "peso neto exportado", "peso total (t)", "peso manejado + exportado (t)"])
        .set_table_styles([{"selector": "th",
                            "props": [("background-color", COLOR_LOGO),
                                      ("color", "white"),
                                      ("font-size", "14px"),
                                      ("border", f"2px solid {COLOR_LOGO}"),
                                      ("text-align", "center")]}])
        .set_properties(**{"border": f"1px solid {COLOR_LOGO}", "text-align": "center", "font-size": "13px"})
    )

    st.dataframe(styler, use_container_width=True)
