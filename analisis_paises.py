# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
import plotly.express as px


def run(BASE_DIR):

    st.markdown("## Análisis por Países")

    ruta_excel = BASE_DIR / "datos.xlsx"

    if not ruta_excel.exists():
        st.error(f"No se encontró el archivo Excel: {ruta_excel}")
        return

    df = pd.read_excel(ruta_excel)

    df.columns = df.columns.str.strip().str.lower()

    # Validar columnas necesarias
    columnas = ["destino", "peso neto exportado", "peso neto importado"]

    for col in columnas:
        if col not in df.columns:
            st.error(f"No existe la columna: {col}")
            return

    # Convertir valores
    df["peso neto exportado"] = pd.to_numeric(
        df["peso neto exportado"], errors="coerce"
    ).fillna(0)

    df["peso neto importado"] = pd.to_numeric(
        df["peso neto importado"], errors="coerce"
    ).fillna(0)

    # Agrupar por país
    paises = df.groupby("destino")[
        ["peso neto exportado", "peso neto importado"]
    ].sum().reset_index()

    # Gráfico exportaciones
    st.subheader("Exportaciones por País")

    fig_export = px.bar(
        paises,
        x="destino",
        y="peso neto exportado",
        title="Peso Neto Exportado por País"
    )

    st.plotly_chart(fig_export, use_container_width=True)

    # Gráfico importaciones
    st.subheader("Importaciones por País")

    fig_import = px.bar(
        paises,
        x="destino",
        y="peso neto importado",
        title="Peso Neto Importado por País"
    )

    st.plotly_chart(fig_import, use_container_width=True)
