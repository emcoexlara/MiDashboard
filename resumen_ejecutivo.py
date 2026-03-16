# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
from pathlib import Path


def run(BASE_DIR):

    st.markdown("## Resumen Ejecutivo")

    # Ruta del archivo Excel
    ruta_excel = BASE_DIR / "datos.xlsx"

    # Verificar si el archivo existe
    if not ruta_excel.exists():
        st.error(f"No se encontró el archivo Excel: {ruta_excel}")
        return

    # Cargar datos
    df = pd.read_excel(ruta_excel)

    # Normalizar nombres de columnas
    df.columns = df.columns.str.strip().str.lower()

    # Convertir a valores numéricos
    if "peso neto exportado" in df.columns:
        df["peso neto exportado"] = pd.to_numeric(
            df["peso neto exportado"], errors="coerce"
        ).fillna(0)

    if "peso neto importado" in df.columns:
        df["peso neto importado"] = pd.to_numeric(
            df["peso neto importado"], errors="coerce"
        ).fillna(0)

    # Indicadores principales
    operaciones_totales = len(df)
    peso_exportado_total = df["peso neto exportado"].sum()
    peso_importado_total = df["peso neto importado"].sum()

    # Mostrar indicadores
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Operaciones Totales",
        f"{operaciones_totales:,}"
    )

    col2.metric(
        "Peso Neto Exportado Total",
        f"{peso_exportado_total:,.2f}"
    )

    col3.metric(
        "Peso Neto Importado Total",
        f"{peso_importado_total:,.2f}"
    )
