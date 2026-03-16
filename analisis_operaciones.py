import streamlit as st
import pandas as pd
import plotly.express as px

COLOR_LOGO = "#1f77b4"

def run(BASE_DIR):
    st.markdown("## 📈 Análisis de Operaciones")

    archivo = st.sidebar.file_uploader("Actualizar datos (Excel)", type=["xlsx"])
    df = pd.read_excel(archivo) if archivo else pd.read_excel(BASE_DIR / "datos.xlsx")
    df.columns = df.columns.str.strip().str.lower()

    for col in ["peso neto manejado", "peso neto exportado", "peso neto importado"]:
        if col not in df.columns:
            st.error(f"No se encontró la columna '{col}' en el Excel.")
            return

    df["peso neto manejado"] = pd.to_numeric(df["peso neto manejado"], errors="coerce").fillna(0)
    df["peso neto exportado"] = pd.to_numeric(df["peso neto exportado"], errors="coerce").fillna(0)
    df["peso neto importado"] = pd.to_numeric(df["peso neto importado"], errors="coerce").fillna(0)
    df["peso total (t)"] = (df["peso neto manejado"] + df["peso neto exportado"]) / 1000

    paises = ["Todos"] + list(df["destino"].unique())
    pais_sel = st.sidebar.selectbox("Filtrar por País", paises)
    if pais_sel != "Todos":
        df = df[df["destino"] == pais_sel]

    st.subheader("Distribución Peso Neto Exportado (t)")
    fig1 = px.histogram(df, x="peso neto exportado" / 1000, nbins=30, color_discrete_sequence=[COLOR_LOGO])
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Distribución Peso Neto Importado (t)")
    fig2 = px.histogram(df, x="peso neto importado" / 1000, nbins=30, color_discrete_sequence=[COLOR_LOGO])
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Distribución Peso Total (t)")
    fig3 = px.histogram(df, x="peso total (t)", nbins=30, color_discrete_sequence=[COLOR_LOGO])
    st.plotly_chart(fig3, use_container_width=True)
