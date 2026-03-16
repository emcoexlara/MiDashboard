# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px

def run(BASE_DIR):
    st.markdown("## Análisis de Operaciones")

    ruta_excel = BASE_DIR / "datos.xlsx"
    if not ruta_excel.exists():
        st.error(f"No se encontró el archivo Excel: {ruta_excel}")
        return

    df = pd.read_excel(ruta_excel)
    df.columns = df.columns.str.strip().str.lower()

    df["peso neto exportado"] = pd.to_numeric(df.get("peso neto exportado", 0), errors="coerce").fillna(0)
    df["peso neto importado"] = pd.to_numeric(df.get("peso neto importado", 0), errors="coerce").fillna(0)

    st.subheader("Distribución Peso Neto Exportado")
    fig_export = px.histogram(df, x="peso neto exportado", nbins=30, title="Distribución del Peso Neto Exportado")
    st.plotly_chart(fig_export, use_container_width=True)

    st.subheader("Distribución Peso Neto Importado")
    fig_import = px.histogram(df, x="peso neto importado", nbins=30, title="Distribución del Peso Neto Importado")
    st.plotly_chart(fig_import, use_container_width=True)
