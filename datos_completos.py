# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

def run(BASE_DIR):
    st.markdown("## Datos Completos")

    ruta_excel = BASE_DIR / "datos.xlsx"
    if not ruta_excel.exists():
        st.error(f"No se encontró el archivo Excel: {ruta_excel}")
        return

    df = pd.read_excel(ruta_excel)
    df.columns = df.columns.str.strip().str.lower()

    st.subheader("Tabla completa de operaciones")
    st.dataframe(df, use_container_width=True)

    st.download_button(
        label="Descargar datos en CSV",
        data=df.to_csv(index=False),
        file_name="datos_comercio_exterior.csv",
        mime="text/csv"
    )
