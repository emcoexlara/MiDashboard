import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64

st.set_page_config(layout="wide")

# ------------------------------
# DISEÑO (FONDO + LOGO)
# ------------------------------
def get_base64(file):
    with open(file, "rb") as f:
        return base64.b64encode(f.read()).decode()

try:
    fondo = get_base64("assets/fondo.jpg")
    logo = get_base64("assets/logo.png")

    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{fondo}");
        background-size: cover;
    }}
    .card {{
        background-color: rgba(255,255,255,0.9);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.3);
    }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f'<center><img src="data:image/png;base64,{logo}" width="180"></center>', unsafe_allow_html=True)

except:
    pass

# ------------------------------
# CARGA
# ------------------------------
archivo = st.file_uploader("Cargar Excel", type=["xlsx"])

if archivo is None:
    st.stop()

df = pd.read_excel(archivo)
df.columns = df.columns.str.strip().str.upper()

df['FECHA'] = pd.to_datetime(df['FECHA'], errors='coerce')

for col in ['PESO NETO EXPORTADO', 'PESO NETO IMPORTADO']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df['PESO TOTAL'] = df['PESO NETO EXPORTADO'].fillna(0) + df['PESO NETO IMPORTADO'].fillna(0)

# ------------------------------
# FILTROS
# ------------------------------
st.sidebar.title("Filtros")

df_filtrado = df.copy()

rango = st.sidebar.date_input("Fecha", (df['FECHA'].min(), df['FECHA'].max()))
if isinstance(rango, tuple):
    df_filtrado = df_filtrado[
        (df_filtrado['FECHA'] >= pd.to_datetime(rango[0])) &
        (df_filtrado['FECHA'] <= pd.to_datetime(rango[1]))
    ]

destinos = st.sidebar.multiselect("Destino", df['DESTINO'].dropna().unique())
if destinos:
    df_filtrado = df_filtrado[df_filtrado['DESTINO'].isin(destinos)]

contenidos = st.sidebar.multiselect("Contenido", df['CONTENIDO'].dropna().unique())
if contenidos:
    df_filtrado = df_filtrado[df_filtrado['CONTENIDO'].isin(contenidos)]

# ------------------------------
# KPI AVANZADOS
# ------------------------------
col1, col2, col3, col4 = st.columns(4)

def variacion(actual, anterior):
    if anterior == 0:
        return 0
    return ((actual - anterior) / anterior) * 100

df_ordenado = df.sort_values('FECHA')

mitad = len(df_ordenado) // 2
df_old = df_ordenado.iloc[:mitad]
df_new = df_ordenado.iloc[mitad:]

ops_var = variacion(len(df_new), len(df_old))
exp_var = variacion(df_new['PESO NETO EXPORTADO'].sum(), df_old['PESO NETO EXPORTADO'].sum())

def card(t, v, var):
    color = "green" if var >= 0 else "red"
    st.markdown(f"""
    <div class="card">
        <h4>{t}</h4>
        <h2>{v}</h2>
        <p style='color:{color};'>{var:.2f}%</p>
    </div>
    """, unsafe_allow_html=True)

with col1:
    card("Operaciones", len(df_filtrado), ops_var)

with col2:
    card("Exportado", f"{df_filtrado['PESO NETO EXPORTADO'].sum():,.0f}", exp_var)

with col3:
    card("Importado", f"{df_filtrado['PESO NETO IMPORTADO'].sum():,.0f}", 0)

with col4:
    card("Total", f"{df_filtrado['PESO TOTAL'].sum():,.0f}", 0)

# ------------------------------
# RANKING DESTINOS
# ------------------------------
ranking = df_filtrado.groupby('DESTINO').size().reset_index(name='OPS').sort_values(by='OPS', ascending=False)
fig_rank = px.bar(ranking.head(10), x='DESTINO', y='OPS', title="Top Destinos")
st.plotly_chart(fig_rank, use_container_width=True)

# ------------------------------
# MAPA CON RUTAS
# ------------------------------
st.subheader("Rutas de Exportación")

origen = [8.0, -66.0]  # Venezuela

coords = {
    "USA": [37, -95],
    "ESPAÑA": [40, -3],
    "BRASIL": [-14, -51],
    "COLOMBIA": [4, -74]
}

fig = go.Figure()
for destino in df_filtrado['DESTINO'].dropna().unique():
    if destino.upper() in coords:
        lat2, lon2 = coords[destino.upper()]
        fig.add_trace(go.Scattergeo(
            locationmode='ISO-3',
            lon=[origen[1], lon2],
            lat=[origen[0], lat2],
            mode='lines',
            line=dict(width=2)
        ))

fig.update_layout(
    geo=dict(showland=True),
    margin=dict(l=0, r=0, t=0, b=0)
)

st.plotly_chart(fig, use_container_width=True)

# ------------------------------
# GRÁFICO TEMPORAL
# ------------------------------
df_time = df_filtrado.groupby('FECHA')['PESO NETO EXPORTADO'].sum().reset_index()
fig_time = px.line(df_time, x='FECHA', y='PESO NETO EXPORTADO', title="Tendencia Exportaciones")
st.plotly_chart(fig_time, use_container_width=True)

# ------------------------------
# TABLA
# ------------------------------
st.dataframe(df_filtrado)
