# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

def run(BASE_DIR):
    st.markdown("## Datos Completos")

    archivo = st.sidebar.file_uploader("Actualizar datos (Excel)", type=["xlsx"])
    if archivo:
        df = pd.read_excel(archivo)
    else:
        df = pd.read_excel(BASE_DIR / "datos.xlsx")

    df.columns = df.columns.str.strip().str.lower()

    st.subheader("Tabla completa de operaciones")
    st.dataframe(df, use_container_width=True)

    st.download_button(
        label="Descargar datos en CSV",
        data=df.to_csv(index=False),
        file_name="datos_comercio_exterior.csv",
        mime="text/csv"
    )
