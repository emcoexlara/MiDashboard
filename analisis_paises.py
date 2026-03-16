# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px

def run(BASE_DIR):
    st.markdown("## 🌍 Análisis por Países")

    archivo = st.sidebar.file_uploader("Actualizar datos (Excel)", type=["xlsx"])
    if archivo:
        df = pd.read_excel(archivo)
    else:
        df = pd.read_excel(BASE_DIR / "datos.xlsx")

    df.columns = df.columns.str.strip().str.lower()
    df["peso neto exportado"] = pd.to_numeric(df.get("peso neto exportado", 0), errors="coerce").fillna(0)
    df["peso neto importado"] = pd.to_numeric(df.get("peso neto importado", 0), errors="coerce").fillna(0)

    if "destino" not in df.columns:
        st.error("No se encontró la columna 'destino'.")
        return

    paises = df.groupby("destino")[["peso neto exportado","peso neto importado"]].sum().reset_index()

    st.subheader("Exportaciones por País")
    fig_exp = px.bar(paises, x="destino", y="peso neto exportado", title="Peso Neto Exportado por País", color="peso neto exportado")
    st.plotly_chart(fig_exp, use_container_width=True)

    st.subheader("Importaciones por País")
    fig_imp = px.bar(paises, x="destino", y="peso neto importado", title="Peso Neto Importado por País", color="peso neto importado")
    st.plotly_chart(fig_imp, use_container_width=True)

    st.subheader("Mapa de Exportaciones")
    fig_map = px.choropleth(
        paises,
        locations="destino",
        locationmode="country names",
        color="peso neto exportado",
        title="Exportaciones por País"
    )
    st.plotly_chart(fig_map, use_container_width=True)
