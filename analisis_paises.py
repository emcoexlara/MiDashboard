import streamlit as st
import pandas as pd
import plotly.express as px

COLOR_LOGO = "#1f77b4"

def run(BASE_DIR):
    st.markdown("## 🌍 Análisis por Países")

    archivo = st.sidebar.file_uploader("Actualizar datos (Excel)", type=["xlsx"])
    df = pd.read_excel(archivo) if archivo else pd.read_excel(BASE_DIR / "datos.xlsx")
    df.columns = df.columns.str.strip().str.lower()

    for col in ["peso neto manejado", "peso neto exportado", "peso neto importado", "destino"]:
        if col not in df.columns:
            st.error(f"No se encontró la columna '{col}' en el Excel.")
            return

    df["peso neto manejado"] = pd.to_numeric(df["peso neto manejado"], errors="coerce").fillna(0)
    df["peso neto exportado"] = pd.to_numeric(df["peso neto exportado"], errors="coerce").fillna(0)
    df["peso neto importado"] = pd.to_numeric(df["peso neto importado"], errors="coerce").fillna(0)
    df["peso total (t)"] = (df["peso neto manejado"] + df["peso neto exportado"]) / 1000

    paises = df.groupby("destino")[["peso neto exportado", "peso neto importado", "peso total (t)"]].sum().reset_index()

    st.subheader("Exportaciones por País (t)")
    fig_exp = px.bar(paises, x="destino", y="peso neto exportado" / 1000, color_discrete_sequence=[COLOR_LOGO])
    st.plotly_chart(fig_exp, use_container_width=True)

    st.subheader("Importaciones por País (t)")
    fig_imp = px.bar(paises, x="destino", y="peso neto importado" / 1000, color_discrete_sequence=[COLOR_LOGO])
    st.plotly_chart(fig_imp, use_container_width=True)

    st.subheader("Peso Total por País (t)")
    fig_total = px.bar(paises, x="destino", y="peso total (t)", color_discrete_sequence=[COLOR_LOGO])
    st.plotly_chart(fig_total, use_container_width=True)

    st.subheader("Mapa de Exportaciones (t)")
    fig_map = px.choropleth(
        paises,
        locations="destino",
        locationmode="country names",
        color="peso neto exportado" / 1000,
        color_continuous_scale=[COLOR_LOGO, "#ffffff"],
        title="Exportaciones por País"
    )
    st.plotly_chart(fig_map, use_container_width=True)
