# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

def run(BASE_DIR):
    st.markdown("## 📊 Resumen Ejecutivo")

    archivo = st.sidebar.file_uploader("Actualizar datos (Excel)", type=["xlsx"])
    if archivo:
        df = pd.read_excel(archivo)
    else:
        df = pd.read_excel(BASE_DIR / "datos.xlsx")

    df.columns = df.columns.str.strip().str.lower()
    df["peso neto exportado"] = pd.to_numeric(df.get("peso neto exportado", 0), errors="coerce").fillna(0)
    df["peso neto importado"] = pd.to_numeric(df.get("peso neto importado", 0), errors="coerce").fillna(0)

    operaciones_totales = len(df)
    peso_exportado_total = df["peso neto exportado"].sum()
    peso_importado_total = df["peso neto importado"].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Operaciones Totales", operaciones_totales, delta_color="inverse")
    col2.metric("Peso Neto Exportado (kg)", f"{peso_exportado_total:,.2f}", delta_color="normal")
    col3.metric("Peso Neto Importado (kg)", f"{peso_importado_total:,.2f}", delta_color="normal")
