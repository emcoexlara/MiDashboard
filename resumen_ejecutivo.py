# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os

def run(BASE_DIR):
    st.markdown("<h2 style='text-align:center; color:#4B7BE5'>Resumen Ejecutivo</h2>", unsafe_allow_html=True)

    ruta_excel = os.path.join(BASE_DIR, "data", "datos.xlsx")
    if not os.path.exists(ruta_excel):
        st.error(f"No se encontro el archivo Excel: {ruta_excel}")
        return

    df = pd.read_excel(ruta_excel)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ","_")

    peso_exportado_col = next((c for c in df.columns if "export" in c), None)
    peso_importado_col = next((c for c in df.columns if "import" in c), None)

    if not peso_exportado_col or not peso_importado_col:
        st.error("Faltan columnas de peso exportado o importado.")
        return

    df[peso_exportado_col] = pd.to_numeric(df[peso_exportado_col], errors="coerce")
    df[peso_importado_col] = pd.to_numeric(df[peso_importado_col], errors="coerce")

    # KPIs
    total_operaciones = len(df)
    total_exportado = df[peso_exportado_col].sum()
    total_importado = df[peso_importado_col].sum()

    KPI_COLORS = ["#4B7BE5", "#F5A623", "#34C759"]
    col1, col2, col3 = st.columns(3)
    col1.markdown(f"<div style='background-color:{KPI_COLORS[0]}; padding:20px; border-radius:10px; text-align:center'><h3 style='color:white'>Operaciones Totales</h3><h1 style='color:white'>{total_operaciones:,}</h1></div>", unsafe_allow_html=True)
    col2.markdown(f"<div style='background-color:{KPI_COLORS[1]}; padding:20px; border-radius:10px; text-align:center'><h3 style='color:white'>Peso Neto Exportado (kg)</h3><h1 style='color:white'>{total_exportado:,}</h1></div>", unsafe_allow_html=True)
    col3.markdown(f"<div style='background-color:{KPI_COLORS[2]}; padding:20px; border-radius:10px; text-align:center'><h3 style='color:white'>Peso Neto Importado (kg)</h3><h1 style='color:white'>{total_importado:,}</h1></div>", unsafe_allow_html=True)