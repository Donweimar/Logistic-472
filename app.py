import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Configuración de la página
st.set_page_config(
    page_title="Gestión Logística Nacional 4-72", 
    page_icon="🚚",
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Estilos CSS adaptables tanto a Modo Claro como a Modo Oscuro
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    
    /* Tarjetas KPI adaptables */
    div[data-testid="stMetric"] {
        background-color: var(--secondary-background-color);
        padding: 14px;
        border-radius: 10px;
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
    
    /* Color de texto responsive */
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

    # Normalización de columnas de texto (incluyendo conductor)
    text_cols = ['AÑO', 'RUTA', 'OPERADOR', 'PLACA', 'HORA', 'NOMBRE_CONDUCTOR', 'CONDUCTOR']
    for text_col in text_cols:
        if text_col in df.columns:
            df[text_col] = df[text_col].astype(str).str.strip()
        else:
            if text_col == 'NOMBRE_CONDUCTOR' and 'CONDUCTOR' in df.columns:
                df['NOMBRE_CONDUCTOR'] = df['CONDUCTOR'].astype(str).str.strip()
            elif text_col == 'CONDUCTOR' and 'NOMBRE_CONDUCTOR' in df.columns:
                df['CONDUCTOR'] = df['NOMBRE_CONDUCTOR'].astype(str).str.strip()
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

conductores_disponibles = sorted([c for c in df_raw['NOMBRE_CONDUCTOR'].unique() if c not in ['nan', 'N/A']])
selected_conductores = st.sidebar.multiselect("Conductor(es)", conductores_disponibles)


# 4. Aplicación de Filtros
df_filtered = df_raw.copy()

if selected_anos:
    df_filtered = df_filtered[df_filtered['AÑO'].isin(selected_anos)]

if selected_operadores:
    df_filtered = df_filtered[df_filtered['OPERADOR'].isin(selected_operadores)]

if selected_rutas:
    df_filtered = df_filtered[df_filtered['RUTA'].isin(selected_rutas)]

if selected_conductores:
    df_filtered = df_filtered[df_filtered['NOMBRE_CONDUCTOR'].isin(selected_conductores)]

if df_filtered.empty:
    st.error("No se encontraron registros con los filtros seleccionados.")
    st.stop()


# 5. Encabezado e Indicadores Clave (KPIs)
header_col1, header_col2 = st.columns([4, 1])

with header_col1:
    st.title("🚚 Gestión Logística Nacional 4-72 ")
    st.markdown("Visualización estratégica del flujo operativo, capacidad y eficiencia.")

with header_col2:
    if uploaded_logo is not None:
        st.image(uploaded_logo, width=150)
    elif os.path.exists("logo.png"):
        st.image("logo.png", width=150)

# Alertas de Capacidad Subutilizada
viajes_subutilizados = df_filtered[df_filtered['CAPACIDAD'] < 30].shape[0]
total_viajes = df_filtered.shape[0]
pct_sub = (viajes_subutilizados / total_viajes) * 100 if total_viajes > 0 else 0

if pct_sub > 15:
    st.warning(f"⚠️ **Alerta de Capacidad:** El **{pct_sub:.1f}%** de los viajes registrados ({viajes_subutilizados} despachos) salieron con menos del 30% de ocupación.")

# Tarjetas KPI (5 métricas)
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
    'VOLUME': 'mean',
    'PIEZAS': 'sum',
    'CAPACIDAD': 'mean'
}).reset_index()


# 7. Organización en Pestañas (Tabs)
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Métricas Anuales", 
    "👨‍✈️ Conductores y Rutas", 
    "⏱️ Operación y Eficiencia", 
    "📋 Datos Auditables"
])

# --- PESTAÑA 1: MÉTRICAS ANUALES ---
with tab1:
    st.subheader("Evolución y Totales Anuales")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("##### 📦 Total de PESO Movilizado por Año (kg)")
        fig_peso_ano = px.bar(
            df_annual, x='AÑO', y='PESO',
            text_auto='.2s', template='plotly_white',
            color_discrete_sequence=['#f59e0b']
        )
        fig_peso_ano.update_layout(xaxis_title="Año", yaxis_title="Peso Total (kg)", margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_peso_ano, use_container_width=True)

    with col_b:
        st.markdown("##### 🧩 Total de PIEZAS Transportadas por Año")
        fig_piezas_ano = px.bar(
            df_annual, x='AÑO', y='PIEZAS',
            text_auto='.2s', template='plotly_white',
            color_discrete_sequence=['#10b981']
        )
        fig_piezas_ano.update_layout(xaxis_title="Año", yaxis_title="Piezas Totales", margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_piezas_ano, use_container_width=True)

    col_c, col_d = st.columns(2)
    with col_c:
        st.markdown("##### 📄 Envíos Totales (Manifiestos por Año)")
        fig_envios = px.bar(
            df_annual, x='AÑO', y='MANIFIESTOS',
            text_auto='.2s', template='plotly_white',
            color_discrete_sequence=['#2563eb']
        )
        fig_envios.update_layout(xaxis_title="Año", yaxis_title="Manifiestos Sumados", margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_envios, use_container_width=True)

    with col_d:
        st.markdown("##### 📈 Evolución Comparativa Peso vs Volumen")
        fig_peso_vol = px.line(
            df_annual, x='AÑO', y=['PESO', 'VOLUME'],
            markers=True, template='plotly_white',
            labels={'value': 'Cantidad Acumulada', 'variable': 'Métrica'},
            color_discrete_sequence=['#f59e0b', '#06b6d4']
        )
        fig_peso_vol.update_layout(xaxis_title="Año", yaxis_title="Total Acumulado", margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_peso_vol, use_container_width=True)


# --- PESTAÑA 2: CONDUCTORES Y RUTAS ---
with tab2:
    st.subheader("Análisis de Conductores y Rutas")
    col_cond, col_rutas = st.columns(2)

    with col_cond:
        st.markdown("##### 🏆 Top 10 Conductores con Más Viajes")
        df_cond = df_filtered.groupby('NOMBRE_CONDUCTOR').size().reset_index(name='VIAJES')
        df_cond = df_cond[df_cond['NOMBRE_CONDUCTOR'] != 'N/A']
        df_top_cond = df_cond.sort_values(by='VIAJES', ascending=False).head(10)

        if not df_top_cond.empty:
            fig_cond = px.bar(
                df_top_cond, x='VIAJES', y='NOMBRE_CONDUCTOR', orientation='h',
                template='plotly_white', color_discrete_sequence=['#6366f1'],
                text_auto=True
            )
            fig_cond.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                xaxis_title="Cantidad de Viajes Realizados", yaxis_title="",
                margin=dict(l=10, r=10, t=30, b=10)
            )
            st.plotly_chart(fig_cond, use_container_width=True)
        else:
            st.info("No hay información de conductores disponible en el archivo cargado.")

    with col_rutas:
        st.markdown("##### 📍 Top 10 Rutas de Mayor Impacto (Por Peso)")
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


# --- PESTAÑA 3: OPERACIÓN Y EFICIENCIA ---
with tab3:
    st.subheader("Eficiencia Operativa y Terceros")
    col_op1, col_op2 = st.columns(2)

    with col_op1:
        st.markdown("##### 📉 Ocupación Promedio (%) por Año")
        fig_ocupacion = px.line(
            df_annual, x='AÑO', y='CAPACIDAD',
            markers=True, template='plotly_white',
            color_discrete_sequence=['#ef4444']
        )
        fig_ocupacion.update_layout(xaxis_title="Año", yaxis_title="Promedio Capacidad (%)", margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_ocupacion, use_container_width=True)

    with col_op2:
        st.markdown("##### ⏰ Distribución de Horarios de Despacho (Horas Pico)")
        df_hora = df_filtered.groupby('HORA_SIMPLE')['MANIFIESTOS'].sum().reset_index()
        fig_hora = px.bar(
            df_hora, x='HORA_SIMPLE', y='MANIFIESTOS',
            template='plotly_white', color_discrete_sequence=['#8b5cf6']
        )
        fig_hora.update_layout(xaxis_title="Hora del Día", yaxis_title="Despachos Totales", margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_hora, use_container_width=True)

    st.markdown("##### 🤝 Participación por Operador Logístico")
    df_op = df_filtered.groupby('OPERADOR')['MANIFIESTOS'].sum().reset_index()
    df_op = df_op[df_op['MANIFIESTOS'] > 0]
    
    fig_operador = px.pie(
        df_op, names='OPERADOR', values='MANIFIESTOS',
        hole=0.45, template='plotly_white'
    )
    fig_operador.update_traces(textposition='inside', textinfo='percent+label')
    fig_operador.update_layout(showlegend=True, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_operador, use_container_width=True)


# --- PESTAÑA 4: DATOS AUDITABLES ---
with tab4:
    st.subheader("🔍 Tabla de Datos Auditables")
    
    csv_data = df_filtered.to_csv(index=False, sep=";").encode('latin1')
    st.download_button(
        label="📥 Descargar Reporte Filtrado en CSV",
        data=csv_data,
        file_name="Reporte_Logistico_Filtrado.csv",
        mime="text/csv"
    )

    cols_a_mostrar = [c for c in ['AÑO', 'FECHA', 'HORA', 'RUTA', 'OPERADOR', 'NOMBRE_CONDUCTOR', 'PLACA', 'MANIFIESTOS', 'PESO', 'PIEZAS', 'CAPACIDAD'] if c in df_filtered.columns]
    st.dataframe(df_filtered[cols_a_mostrar], use_container_width=True)