# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

def run(BASE_DIR):
    st.markdown("## 🗂 Datos Completos - Estilo Corporativo")

    # Subida de archivo dinámico
    archivo = st.sidebar.file_uploader("Actualizar datos (Excel)", type=["xlsx"])
    if archivo:
        df = pd.read_excel(archivo)
    else:
        df = pd.read_excel(BASE_DIR / "datos.xlsx")

    # Normalizar nombres de columnas
    df.columns = df.columns.str.strip().str.lower()

    # Verificar columnas obligatorias
    columnas_requeridas = ["peso manejado", "peso neto exportado"]
    for col in columnas_requeridas:
        if col not in df.columns:
            st.error(f"No se encontró la columna '{col}' en el Excel.")
            return

    # Convertir a numérico
    df["peso manejado"] = pd.to_numeric(df.get("peso manejado", 0), errors="coerce").fillna(0)
    df["peso neto exportado"] = pd.to_numeric(df.get("peso neto exportado", 0), errors="coerce").fillna(0)

    # Nueva columna: Peso Total en toneladas
    df["peso total (t)"] = (df["peso manejado"] + df["peso neto exportado"]) / 1000

    # Formato visual llamativo
    COLOR_LOGO = "#1f77b4"

    def color_gradiente(s):
        max_val = s.max() if s.max() > 0 else 1
        return [
            f"background-color: rgba(255,215,0,{v/max_val}); font-weight: bold; border: 1px solid {COLOR_LOGO};"
            for v in s
        ]

    styler = (
        df.style
        .format({
            "peso manejado": "{:,.2f}",
            "peso neto exportado": "{:,.2f}",
            "peso total (t)": "{:,.2f}"
        })
        .apply(color_gradiente, subset=["peso manejado", "peso neto exportado", "peso total (t)"])
        .set_table_styles([
            {"selector": "th",
             "props": [("background-color", COLOR_LOGO),
                       ("color", "white"),
                       ("font-size", "14px"),
                       ("border", f"2px solid {COLOR_LOGO}"),
                       ("text-align", "center")]}
        ])
        .set_properties(**{
            "border": f"1px solid {COLOR_LOGO}",
            "text-align": "center",
            "font-size": "13px"
        })
    )

    st.dataframe(styler, use_container_width=True)
