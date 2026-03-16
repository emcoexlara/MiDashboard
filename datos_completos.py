# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

def run(BASE_DIR):
    st.markdown("## 🗂 Datos Completos")

    # Subida de archivo dinámico
    archivo = st.sidebar.file_uploader("Actualizar datos (Excel)", type=["xlsx"])
    if archivo:
        df = pd.read_excel(archivo)
    else:
        df = pd.read_excel(BASE_DIR / "datos.xlsx")

    # Normalizar nombres de columnas
    df.columns = df.columns.str.strip().str.lower()

    # Convertir a numérico
    df["peso manejado"] = pd.to_numeric(df.get("peso manejado", 0), errors="coerce").fillna(0)
    df["peso neto exportado"] = pd.to_numeric(df.get("peso neto exportado", 0), errors="coerce").fillna(0)

    # Nueva columna: Peso Total en toneladas
    df["peso total (t)"] = (df["peso manejado"] + df["peso neto exportado"]) / 1000

    # Crear un estilo visual llamativo
    def highlight_peso(val):
        color = "#FFD700"  # Dorado para pesos altos
        return f"background-color: {color}; font-weight: bold;"

    # Aplicar estilo solo a columnas de peso
    styler = df.style.format({
        "peso manejado": "{:,.2f}",
        "peso neto exportado": "{:,.2f}",
        "peso total (t)": "{:,.2f}"
    }).applymap(highlight_peso, subset=["peso manejado", "peso neto exportado", "peso total (t)"])\
      .set_table_styles([
          {"selector": "th", "props": [("background-color", "#1f77b4"),
                                       ("color", "white"),
                                       ("font-size", "14px")]}
      ])

    st.dataframe(styler, use_container_width=True)
