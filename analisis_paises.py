# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px

def run(BASE_DIR):
    st.markdown("## Análisis por Países")

    archivo = st.sidebar.file_uploader("Actualizar datos (Excel)", type=["xlsx"])
    if archivo:
        df = pd.read_excel(archivo)
    else:
        df = pd.read_excel(BASE_DIR / "datos.xlsx")

    df.columns = df.columns.str.strip().str.lower()

    required_cols = ["destino", "peso neto exportado", "peso neto importado"]
    for col in required_cols:
        if col not in df.columns:
            st.error(f"No existe la columna: {col}")
            return

    df["peso neto exportado"] = pd.to_numeric(df["peso neto exportado"], errors="coerce").fillna(0)
    df["peso neto importado"] = pd.to_numeric(df["peso neto importado"], errors="coerce").fillna(0)

    paises = df.groupby("destino")[["peso neto exportado", "peso neto importado"]].sum().reset_index()

    st.subheader("Exportaciones por País")
    fig_export = px.bar(paises, x="destino", y="peso neto exportado", title="Peso Neto Exportado por País")
    st.plotly_chart(fig_export, use_container_width=True)

    st.subheader("Importaciones por País")
    fig_import = px.bar(paises, x="destino", y="peso neto importado", title="Peso Neto Importado por País")
    st.plotly_chart(fig_import, use_container_width=True)

    # Mapa mundial de exportaciones
    st.subheader("Mapa de Exportaciones por País")
    fig_mapa = px.choropleth(
        paises,
        locations="destino",
        locationmode="country names",
        color="peso neto exportado",
        title="Exportaciones por País (kg)",
    )
    st.plotly_chart(fig_mapa, use_container_width=True)
