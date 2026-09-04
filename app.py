import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Configuración de la página
st.set_page_config(
    page_title="Gestión Logística Nacional", 
    page_icon="🚚",
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Estilos CSS adaptables tanto a Modo Claro como a Modo Oscuro
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    
    /* Selector adaptable para tarjetas KPI en Modo Claro / Oscuro */
    div[data-testid="stMetric"] {
        background-color: var(--secondary-background-color);
        padding: 14px;
        border-radius: 10px;
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
    
    /* Forzar que el texto de las métricas responda al tema activo */
    div[data-testid="stMetricValue"], div[data-testid="stMetricLabel"] {
        color: var(--text-color) !important;
    }
    </style>
""", unsafe_allow_html=True)


# 2. Función de Carga y Limpieza de Datos
@st.cache_data(show_spinner=False)
def process_data(file_source):
    try:
        df = pd.read_csv(file_source, sep=";", encoding="latin1")
    except Exception:
        df = pd.read_csv(file_source, sep=",", encoding="utf-8", errors="ignore")
    
    df.columns = df.columns.str.strip()
    
    def clean_numeric(x):
        if pd.isna(x):
            return 0.0
        x_str = str(x).replace('%', '').strip()
        if not x_str or x_str in ['-', '--', ' - ', ' -', 'NaN', 'nan', 'None']:
            return 0.0
        try:
            if '.' in x_str and ',' not in x_str:
                parts = x_str.split('.')
                if len(parts[-1]) == 3:
                    x_str = x_str.replace('.', '')
            elif ',' in x_str:
                x_str = x_str.replace('.', '').replace(',', '.')
            return float(x_str)
        except (ValueError, TypeError):
            return 0.0

    cols_numericas = ['MANIFIESTOS', 'PIEZAS', 'PESO', 'VOLUME', 'CAPACIDAD']
    for col in cols_numericas:
        if col in df.columns:
            df[col] = df[col].apply(clean_numeric)
        else:
            df[col] = 0.0

    for text_col in ['AÑO', 'RUTA', 'OPERADOR', 'PLACA', 'HORA']:
        if text_col in df.columns:
            df[text_col] = df[text_col].astype(str).str.strip()
        else:
            df[text_col] = "N/A"

    if 'HORA' in df.columns:
        df['HORA_SIMPLE'] = df['HORA'].str.split(':').str[0].str.zfill(2) + ":00"
    
    return df


# 3. Sidebar: Logo, Carga de Datos y Filtros
st.sidebar.title("⚙️ Configuración")

# --- SECCIÓN DEL LOGO ---
st.sidebar.subheader("🖼️ Logo Corporativo")
uploaded_logo = st.sidebar.file_uploader("Cargar Logo (PNG/JPG)", type=["png", "jpg", "jpeg"])

if uploaded_logo is not None:
    st.sidebar.image(uploaded_logo, use_container_width=True)
elif os.path.exists("logo.png"):
    st.sidebar.image("logo.png", use_container_width=True)
else:
    st.sidebar.caption("💡 *Puedes subir tu logo o guardar una imagen 'logo.png' en la carpeta.*")

st.sidebar.markdown("---")

# --- CARGA DE ARCHIVO CSV ---
uploaded_file = st.sidebar.file_uploader("Importar archivo CSV", type=["csv"])

if uploaded_file is not None:
    df_raw = process_data(uploaded_file)
    st.sidebar.success("✅ Datos cargados correctamente")
elif os.path.exists("RutaNacional.csv"):
    df_raw = process_data("RutaNacional.csv")
    st.sidebar.info("ℹ️ Usando 'RutaNacional.csv'")
else:
    st.warning("⚠️ Por favor sube un archivo `.csv` en la barra lateral.")
    st.stop()

# --- FILTROS DINÁMICOS MULTI-SELECCIÓN ---
st.sidebar.subheader("Filtros de Operación")

anos_disponibles = sorted([a for a in df_raw['AÑO'].unique() if a not in ['nan', 'N/A']])
selected_anos = st.sidebar.multiselect("Año(s)", anos_disponibles)

operadores_disponibles = sorted([op for op in df_raw['OPERADOR'].unique() if op not in ['nan', 'N/A']])
selected_operadores = st.sidebar.multiselect("Operador(es) Logístico(s)", operadores_disponibles)

rutas_disponibles = sorted([r for r in df_raw['RUTA'].unique() if r not in ['nan', 'N/A']])
selected_rutas = st.sidebar.multiselect("Ruta(s)", rutas_disponibles)


# 4. Aplicación de Filtros
df_filtered = df_raw.copy()

if selected_anos:
    df_filtered = df_filtered[df_filtered['AÑO'].isin(selected_anos)]

if selected_operadores:
    df_filtered = df_filtered[df_filtered['OPERADOR'].isin(selected_operadores)]

if selected_rutas:
    df_filtered = df_filtered[df_filtered['RUTA'].isin(selected_rutas)]

if df_filtered.empty:
    st.error("No se encontraron registros con los filtros seleccionados.")
    st.stop()


# 5. Encabezado e Indicadores Clave (KPIs)
header_col1, header_col2 = st.columns([4, 1])

with header_col1:
    st.title("🚚 Gestión Logística Nacional 4-72 ")
    st.markdown("Visualización estratégica del flujo operativo, capacidad y eficiencia.")

#with header_col2:
    if uploaded_logo is not None:
        st.image(uploaded_logo, width=150)
    elif os.path.exists("logo.png"):
        st.image("logo.png", width=150)

# Alertas de Eficiencia
viajes_subutilizados = df_filtered[df_filtered['CAPACIDAD'] < 30].shape[0]
total_viajes = df_filtered.shape[0]
pct_sub = (viajes_subutilizados / total_viajes) * 100 if total_viajes > 0 else 0

if pct_sub > 15:
    st.warning(f"⚠️ **Alerta de Capacidad:** El **{pct_sub:.1f}%** de los viajes registrados ({viajes_subutilizados} despachos) salieron con menos del 30% de ocupación.")

# Métricas Principales (5 KPIs)
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("Viajes Realizados", f"{len(df_filtered):,}")
kpi2.metric("Envíos Totales (Manifiestos)", f"{int(df_filtered['MANIFIESTOS'].sum()):,}")
kpi3.metric("Peso Total Movilizado", f"{df_filtered['PESO'].sum():,.0f} kg")
kpi4.metric("Piezas Transportadas", f"{int(df_filtered['PIEZAS'].sum()):,}")
kpi5.metric("Ocupación Promedio", f"{df_filtered['VOLUME'].mean():.1f}%")

st.markdown("---")


# 6. Preparación de Agregación Anual
df_annual = df_filtered.groupby('AÑO').agg({
    'MANIFIESTOS': 'sum',
    'PESO': 'sum',
    'VOLUME': 'sum',
    'PIEZAS': 'sum',
    'CAPACIDAD': 'mean'
}).reset_index()

df_annual['RATIO_PIEZAS_PESO'] = df_annual['PIEZAS'] / df_annual['PESO'].replace(0, 1)


# 7. Gráficos Interactivos

# FILA 1: Producción y Capacidad
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Envíos Totales (Manifiestos por Año)")
    fig_envios = px.bar(
        df_annual, x='AÑO', y='MANIFIESTOS',
        text_auto='.2s', template='plotly_white',
        color_discrete_sequence=['#2563eb']
    )
    fig_envios.update_layout(xaxis_title="Año", yaxis_title="Manifiestos Sumados", margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_envios, use_container_width=True)

with col2:
    st.subheader("2. Evolución Peso vs Volumen")
    fig_peso_vol = px.line(
        df_annual, x='AÑO', y=['PESO', 'VOLUME'],
        markers=True, template='plotly_white',
        labels={'value': 'Cantidad Acumulada', 'variable': 'Métrica'},
        color_discrete_sequence=['#f59e0b', '#10b981']
    )
    fig_peso_vol.update_layout(xaxis_title="Año", yaxis_title="Total Acumulado", margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_peso_vol, use_container_width=True)

st.markdown("---")

# FILA 2: Eficiencia y Horas Pico
col3, col4 = st.columns(2)

with col3:
    st.subheader("3. Ocupación Promedio (%)")
    fig_ocupacion = px.line(
        df_annual, x='AÑO', y='CAPACIDAD',
        markers=True, template='plotly_white',
        color_discrete_sequence=['#ef4444']
    )
    fig_ocupacion.update_layout(xaxis_title="Año", yaxis_title="Promedio Capacidad (%)", margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_ocupacion, use_container_width=True)

with col4:
    st.subheader("4. Distribución de Horarios de Despacho (Horas Pico)")
    df_hora = df_filtered.groupby('HORA_SIMPLE')['MANIFIESTOS'].sum().reset_index()
    fig_hora = px.bar(
        df_hora, x='HORA_SIMPLE', y='MANIFIESTOS',
        template='plotly_white', color_discrete_sequence=['#8b5cf6']
    )
    fig_hora.update_layout(xaxis_title="Hora del Día", yaxis_title="Despachos Totales", margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_hora, use_container_width=True)

st.markdown("---")

# FILA 3: Gestión de Terceros y Rutas
col5, col6 = st.columns(2)

with col5:
    st.subheader("5. Participación por Operador Logístico")
    df_op = df_filtered.groupby('OPERADOR')['MANIFIESTOS'].sum().reset_index()
    df_op = df_op[df_op['MANIFIESTOS'] > 0]
    
    fig_operador = px.pie(
        df_op, names='OPERADOR', values='MANIFIESTOS',
        hole=0.45, template='plotly_white'
    )
    fig_operador.update_traces(textposition='inside', textinfo='percent+label')
    fig_operador.update_layout(showlegend=False, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_operador, use_container_width=True)

with col6:
    st.subheader("6. Top 10 Rutas de Mayor Impacto (Por Peso)")
    df_rutas = df_filtered.groupby('RUTA')['PESO'].sum().reset_index()
    df_top_rutas = df_rutas.sort_values(by='PESO', ascending=False).head(10)
    
    fig_rutas = px.bar(
        df_top_rutas, x='PESO', y='RUTA', orientation='h',
        template='plotly_white', color_discrete_sequence=['#06b6d4'],
        text_auto='.2s'
    )
    fig_rutas.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        xaxis_title="Peso Total Movilizado (kg)", yaxis_title="",
        margin=dict(l=10, r=10, t=30, b=10)
    )
    st.plotly_chart(fig_rutas, use_container_width=True)


# 8. Exportación de Datos Filtrados
st.markdown("---")
st.subheader("🔍 Tabla de Datos Auditables")

csv_data = df_filtered.to_csv(index=False, sep=";").encode('latin1')
st.download_button(
    label="📥 Descargar Reporte Filtrado en CSV",
    data=csv_data,
    file_name="Reporte_Logistico_Filtrado.csv",
    mime="text/csv"
)

st.dataframe(df_filtered[['AÑO', 'FECHA', 'HORA', 'RUTA', 'OPERADOR', 'PLACA', 'MANIFIESTOS', 'PESO', 'PIEZAS', 'CAPACIDAD']], use_container_width=True)