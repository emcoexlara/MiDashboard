# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import os

def run(BASE_DIR):
    st.markdown("<h2 style='text-align:center; color:#4B7BE5'>Analisis por Paises</h2>", unsafe_allow_html=True)

    ruta_excel = os.path.join(BASE_DIR, "data", "datos.xlsx")
    if not os.path.exists(ruta_excel):
        st.error(f"No se encontro el archivo Excel: {ruta_excel}")
        return

    df = pd.read_excel(ruta_excel)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ","_")

    peso_exportado_col = next((c for c in df.columns if "export" in c), None)
    peso_importado_col = next((c for c in df.columns if "import" in c), None)
    destino_col = next((c for c in df.columns if "destino" in c), None)

    if not peso_exportado_col or not peso_importado_col or not destino_col:
        st.error("Faltan columnas necesarias para el analisis por paises.")
        return

    df[peso_exportado_col] = pd.to_numeric(df[peso_exportado_col], errors="coerce")
    df[peso_importado_col] = pd.to_numeric(df[peso_importado_col], errors="coerce")

    df_paises = df.groupby(destino_col)[[peso_exportado_col,peso_importado_col]].sum().reset_index()

    # Grafico
    fig = px.bar(
        df_paises, x=destino_col, y=[peso_exportado_col,peso_importado_col],
        text_auto=True,
        title="Peso Neto Exportado e Importado por Pais",
        color_discrete_sequence=["#4B7BE5","#F5A623"]
    )
    fig.update_layout(title_x=0.5)
    st.plotly_chart(fig, use_container_width=True)