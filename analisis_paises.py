# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px

COLOR_LOGO = "#1f77b4"

def run(BASE_DIR):
    st.markdown("## 🌍 Análisis por Países")

    archivo = st.sidebar.file_uploader("Actualizar datos (Excel)", type=["xlsx"])
    if archivo:
        df = pd.read_excel(archivo)
    else:
        df = pd.read_excel(BASE_DIR / "datos.xlsx")

    df.columns = df.columns.str.strip().str.lower()
    df["peso neto exportado"] = pd.to_numeric(df.get("peso neto exportado", 0), errors="coerce").fillna(0)/1000
    df["peso neto importado"] = pd.to_numeric(df.get("peso neto importado", 0), errors="coerce").fillna(0)/1000

    if "destino" not in df.columns:
        st.error("No se encontró la columna 'destino'.")
        return

    paises = df.groupby("destino")[["peso neto exportado","peso neto importado"]].sum().reset_index()

    st.subheader("Exportaciones por País (t)")
    fig_exp = px.bar(paises, x="destino", y="peso neto exportado", color="peso neto exportado",
                     color_discrete_sequence=[COLOR_LOGO])
    st.plotly_chart(fig_exp, use_container_width=True)

    st.subheader("Importaciones por País (t)")
    fig_imp = px.bar(paises, x="destino", y="peso neto importado", color="peso neto importado",
                     color_discrete_sequence=[COLOR_LOGO])
    st.plotly_chart(fig_imp, use_container_width=True)

    st.subheader("Mapa de Exportaciones (t)")
    fig_map = px.choropleth(
        paises,
        locations="destino",
        locationmode="country names",
        color="peso neto exportado",
        color_continuous_scale=[COLOR_LOGO, "#ffffff"],
        title="Exportaciones por País"
    )
    st.plotly_chart(fig_map, use_container_width=True)
