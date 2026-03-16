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
    columnas_requeridas = ["peso neto manejado", "peso neto exportado"]
    for col in columnas_requeridas:
        if col not in df.columns:
            st.error(f"No se encontró la columna '{col}' en el Excel.")
            return

    # Convertir a numérico y manejar valores faltantes
    df["peso neto manejado"] = pd.to_numeric(df.get("peso neto manejado", 0), errors="coerce").fillna(0)
    df["peso neto exportado"] = pd.to_numeric(df.get("peso neto exportado", 0), errors="coerce").fillna(0)

    # Peso total en toneladas
    df["peso total (t)"] = (df["peso neto manejado"] + df["peso neto exportado"]) / 1000

    # Nueva columna: peso manejado + exportado en toneladas
    df["peso neto manejado + exportado (t)"] = df["peso total (t)"]  # se puede usar la misma que peso total

    # Formato visual llamativo
    COLOR_LOGO = "#1f77b4"

    # Función de degradado según valor máximo de la columna
    def color_gradiente(s):
        max_val = s.max() if s.max() > 0 else 1
        return [
            f"background-color: rgba(255,215,0,{v/max_val}); font-weight: bold; border: 1px solid {COLOR_LOGO};"
            for v in s
        ]

    styler = (
        df.style
        .format({
            "peso neto manejado": "{:,.2f}",
            "peso neto exportado": "{:,.2f}",
            "peso total (t)": "{:,.2f}",
            "peso neto manejado + exportado (t)": "{:,.2f}"
        })
        .apply(color_gradiente, subset=[
            "peso neto manejado", "peso neto exportado", "peso total (t)", "peso neto manejado + exportado (t)"
        ])
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
