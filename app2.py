import streamlit as st
import pandas as pd

# Ejemplo de df_filtrado con columnas necesarias
# df_filtrado = pd.read_excel("data/datos.xlsx")

# Cálculos de métricas
operaciones = len(df_filtrado) if 'FECHA' in df_filtrado.columns else 0
peso_exportado = df_filtrado['Peso Neto Exportado'].sum() if 'Peso Neto Exportado' in df_filtrado.columns else 0
peso_importado = df_filtrado['Peso Neto Importado'].sum() if 'Peso Neto Importado' in df_filtrado.columns else 0
peso_total = peso_exportado + peso_importado

# ------------------------------
# CONTENEDORES DE METRICAS CON ICONOS
# ------------------------------
st.markdown(
    """
    <style>
    .metric-container {
        display: flex;
        justify-content: space-between;
        margin-bottom: 20px;
    }
    .metric-box {
        background-color: #FFFFFF;
        border-radius: 15px;
        padding: 20px;
        flex: 1;
        margin: 0 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        text-align: center;
    }
    .metric-box h3 {
        color: #000000;
        margin: 10px 0;
    }
    .metric-icon {
        font-size: 40px;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="metric-container">', unsafe_allow_html=True)

# Operaciones
st.markdown(f'''
    <div class="metric-box">
        <div class="metric-icon">📦</div>
        <h3>Operaciones</h3>
        <p style="font-size:24px;font-weight:bold;">{operaciones}</p>
    </div>
''', unsafe_allow_html=True)

# Exportaciones
st.markdown(f'''
    <div class="metric-box">
        <div class="metric-icon">🌎</div>
        <h3>Exportado</h3>
        <p style="font-size:24px;font-weight:bold;">{peso_exportado:,.2f} t</p>
    </div>
''', unsafe_allow_html=True)

# Importaciones
st.markdown(f'''
    <div class="metric-box">
        <div class="metric-icon">🛬</div>
        <h3>Importado</h3>
        <p style="font-size:24px;font-weight:bold;">{peso_importado:,.2f} t</p>
    </div>
''', unsafe_allow_html=True)

# Total
st.markdown(f'''
    <div class="metric-box">
        <div class="metric-icon">⚖️</div>
        <h3>Peso Total</h3>
        <p style="font-size:24px;font-weight:bold;">{peso_total:,.2f} t</p>
    </div>
''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
