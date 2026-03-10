# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import os

def run(BASE_DIR):
    st.markdown("<h2 style='text-align:center; color:#4B7BE5'>Analisis de Operaciones</h2>", unsafe_allow_html=True)

    # Ruta del Excel
    ruta_excel = os.path.join(BASE_DIR, "data", "datos.xlsx")
    if not os.path.exists(ruta_excel):
        st.error(f"No se encontro el archivo Excel: {ruta_excel}")
        return

    # Cargar datos
    df = pd.read_excel(ruta_excel)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ","_")

    # Detectar columnas
    peso_exportado_col = next((c for c in df.columns if "export" in c), None)
    peso_importado_col = next((c for c in df.columns if "import" in c), None)
    tipo_col = next((c for c in df.columns if "tipo" in c), None)
    fecha_col = next((c for c in df.columns if "fecha" in c), None)

    if not peso_exportado_col or not peso_importado_col:
        st.error("Faltan columnas de peso exportado o importado.")
        return

    # Convertir a numérico
    df[peso_exportado_col] = pd.to_numeric(df[peso_exportado_col], errors="coerce")
    df[peso_importado_col] = pd.to_numeric(df[peso_importado_col], errors="coerce")

    # Convertir columna de fecha
    if fecha_col:
        df[fecha_col] = pd.to_datetime(df[fecha_col], errors="coerce")
        min_fecha = df[fecha_col].min().date()
        max_fecha = df[fecha_col].max().date()
    else:
        df["fecha_temp"] = pd.Timestamp.today()
        fecha_col = "fecha_temp"
        min_fecha = max_fecha = df[fecha_col].iloc[0].date()

    # Sidebar filtros
    st.sidebar.markdown("### Filtros")
    tipos = st.sidebar.multiselect(
        "Tipo de Carga",
        options=df[tipo_col].dropna().unique() if tipo_col else [],
        default=df[tipo_col].dropna().unique() if tipo_col else []
    )
    fechas = st.sidebar.date_input(
        "Rango de Fechas",
        [min_fecha, max_fecha]
    )

    # Filtrar datos
    df_filtrado = df.copy()
    if tipo_col: 
        df_filtrado = df_filtrado[df_filtrado[tipo_col].isin(tipos)]
    df_filtrado = df_filtrado[
        (df_filtrado[fecha_col].dt.date >= fechas[0]) &
        (df_filtrado[fecha_col].dt.date <= fechas[1])
    ]

    # KPIs con diseño corporativo
    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(
        f"<div style='background-color:#4B7BE5; padding:15px; border-radius:10px; text-align:center; color:white'>"
        f"<h4>Operaciones Totales</h4><h2>{len(df_filtrado):,}</h2></div>", unsafe_allow_html=True
    )
    col2.markdown(
        f"<div style='background-color:#F5A623; padding:15px; border-radius:10px; text-align:center; color:white'>"
        f"<h4>Peso Neto Exportado (kg)</h4><h2>{df_filtrado[peso_exportado_col].sum():,}</h2></div>", unsafe_allow_html=True
    )
    col3.markdown(
        f"<div style='background-color:#34C759; padding:15px; border-radius:10px; text-align:center; color:white'>"
        f"<h4>Peso Neto Importado (kg)</h4><h2>{df_filtrado[peso_importado_col].sum():,}</h2></div>", unsafe_allow_html=True
    )
    col4.markdown(
        f"<div style='background-color:#888888; padding:15px; border-radius:10px; text-align:center; color:white'>"
        f"<h4>Peso Total (kg)</h4><h2>{df_filtrado[peso_exportado_col].sum() + df_filtrado[peso_importado_col].sum():,}</h2></div>", unsafe_allow_html=True
    )

    # Grafico Tipo de Carga
    if tipo_col:
        df_tipo = df_filtrado[tipo_col].value_counts().reset_index()
        df_tipo.columns = ["Tipo de Carga","Cantidad"]
        fig = px.bar(
            df_tipo, x="Tipo de Carga", y="Cantidad", text="Cantidad",
            color="Tipo de Carga", color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig.update_layout(title_text="Operaciones por Tipo de Carga", title_x=0.5)
        st.plotly_chart(fig, use_container_width=True)