# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px

# Color del logo
COLOR_LOGO = "#1f77b4"  # Cambia esto por el color principal de tu logo

def run(BASE_DIR):
    st.markdown("## 📈 Análisis de Operaciones")

    archivo = st.sidebar.file_uploader("Actualizar datos (Excel)", type=["xlsx"])
    if archivo:
        df = pd.read_excel(archivo)
    else:
        df = pd.read_excel(BASE_DIR / "datos.xlsx")

    df.columns = df.columns.str.strip().str.lower()
    df["peso neto exportado"] = pd.to_numeric(df.get("peso neto exportado", 0), errors="coerce").fillna(0)/1000
    df["peso neto importado"] = pd.to_numeric(df.get("peso neto importado", 0), errors="coerce").fillna(0)/1000

    # Filtro por país
    paises = ["Todos"] + list(df["destino"].unique())
    pais_sel = st.sidebar.selectbox("Filtrar por País", paises)
    if pais_sel != "Todos":
        df = df[df["destino"] == pais_sel]

    st.subheader("Distribución Peso Neto Exportado (t)")
    fig1 = px.histogram(df, x="peso neto exportado", nbins=30, title="Peso Neto Exportado",
                        color_discrete_sequence=[COLOR_LOGO])
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Distribución Peso Neto Importado (t)")
    fig2 = px.histogram(df, x="peso neto importado", nbins=30, title="Peso Neto Importado",
                        color_discrete_sequence=[COLOR_LOGO])
    st.plotly_chart(fig2, use_container_width=True)
