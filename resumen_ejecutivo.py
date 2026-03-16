import streamlit as st
import pandas as pd

def run(BASE_DIR):
    st.markdown("## 📊 Resumen Ejecutivo")

    archivo = st.sidebar.file_uploader("Actualizar datos (Excel)", type=["xlsx"])
    df = pd.read_excel(archivo) if archivo else pd.read_excel(BASE_DIR / "datos.xlsx")

    df.columns = df.columns.str.strip().str.lower()

    # Validar columnas
    for col in ["peso neto manejado", "peso neto exportado", "peso neto importado"]:
        if col not in df.columns:
            st.error(f"No se encontró la columna '{col}' en el Excel.")
            return

    # Convertir a numérico
    df["peso neto manejado"] = pd.to_numeric(df["peso neto manejado"], errors="coerce").fillna(0)
    df["peso neto exportado"] = pd.to_numeric(df["peso neto exportado"], errors="coerce").fillna(0)
    df["peso neto importado"] = pd.to_numeric(df["peso neto importado"], errors="coerce").fillna(0)

    # Pesos en toneladas
    df["peso total (t)"] = (df["peso neto manejado"] + df["peso neto exportado"]) / 1000
    peso_exportado_t = df["peso neto exportado"].sum() / 1000
    peso_importado_t = df["peso neto importado"].sum() / 1000
    peso_total_t = df["peso total (t)"].sum()
    operaciones_totales = len(df)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Operaciones Totales", operaciones_totales)
    col2.metric("Peso Neto Exportado (t)", f"{peso_exportado_t:,.2f}")
    col3.metric("Peso Neto Importado (t)", f"{peso_importado_t:,.2f}")
    col4.metric("Peso Total (t)", f"{peso_total_t:,.2f}")
