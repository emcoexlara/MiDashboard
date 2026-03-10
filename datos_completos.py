# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os

def run(BASE_DIR):
    st.markdown("<h2 style='text-align:center; color:#4B7BE5'>Datos Completos</h2>", unsafe_allow_html=True)

    ruta_excel = os.path.join(BASE_DIR, "data", "datos.xlsx")
    if not os.path.exists(ruta_excel):
        st.error(f"No se encontro el archivo Excel: {ruta_excel}")
        return

    df = pd.read_excel(ruta_excel)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ","_")

    st.dataframe(df, use_container_width=True)