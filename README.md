# 📦 Dashboard Operativo 4-72 Colombia

Dashboard profesional para análisis de operaciones de distribución urbana.

## 🚀 Instalación y Ejecución

### 1. Requisitos previos
- Python 3.9 o superior
- pip actualizado

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Ejecutar el dashboard

```bash
# Coloca el archivo Urbanas.csv en la misma carpeta que dashboard_472.py
streamlit run dashboard_472.py
```

El dashboard se abrirá automáticamente en tu navegador en: **http://localhost:8501**

---

## 📊 Funcionalidades

| Funcionalidad | Descripción |
|---|---|
| 📂 Importar CSV | Carga masiva de datos desde el panel lateral |
| 📤 Exportar CSV | Descarga la base de datos completa o filtrada |
| ➕ Nuevo Registro | Formulario para agregar registros en línea |
| 📊 KPIs | Tarjetas con métricas clave (envíos, devoluciones, productividad, efectividad) |
| 📈 Análisis anual | Gráficos de envíos, devoluciones y crecimiento por año |
| 🛣️ Por Ruta & Tarea | Comparativas por ruta y tipo de tarea |
| 🔍 Filtros | Selección múltiple por Ruta No. y Tarea Asignada |
| 📋 Tabla interactiva | Vista y búsqueda en la base de datos filtrada |

## 🏗️ Arquitectura

```
Python
├── Pandas          → Lectura, limpieza y procesamiento del CSV
├── Plotly          → Gráficos interactivos (barras, torta, anillo, líneas)
└── Streamlit       → Interfaz web con panel lateral y pestañas
```

## 📁 Estructura de archivos

```
📁 Tu proyecto/
├── dashboard_472.py    ← Aplicación principal
├── requirements.txt    ← Dependencias Python
├── Urbanas.csv         ← Base de datos (debe estar en la misma carpeta)
└── README.md
```

## 💡 Uso

1. **Filtros**: Usa el panel lateral para filtrar por Ruta, Tarea y Año
2. **Importar**: Arrastra un nuevo CSV en el panel lateral para actualización masiva
3. **Exportar**: Descarga los datos filtrados desde la pestaña "Tabla de Datos"
4. **Nuevo registro**: Ve a la pestaña "Nuevo Registro" y llena el formulario

---
*Dashboard desarrollado con Python + Streamlit + Plotly para 4-72 Colombia*
