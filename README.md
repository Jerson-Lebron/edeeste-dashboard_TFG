# Dashboard de Eficiencia de Distribución - EDEESTE

## Trabajo Final de Grado

Este proyecto es el trabajo final de grado para la carrera de **Analítica y Ciencia de Datos**. El dashboard permite analizar la eficiencia de distribución eléctrica de EDEESTE en la región Este de República Dominicana.

---

## Descripción

El dashboard muestra indicadores clave de EDEESTE como averías, bajas de servicio, pérdidas energéticas y energía entregada. La herramienta permite filtrar por provincia, período y tipo de avería, y visualizar los datos en gráficos interactivos y mapas geográficos.

**Periodo de análisis:** 2017 - 2025

---

## Funcionalidades

## Página 1: Resumen Ejecutivo
- KPIs principales (total averías, total bajas, pérdida % y energía entregada)
- Evolución temporal de energía comprada, facturada, cobrada y pérdidas
- Distribución de energía facturada vs pérdidas
- Mapa coroplético de averías por provincia
- Barras apiladas de averías por tipo y provincia
- Evolución temporal de bajas (total y por estado)
- Barras verticales de bajas por estado y provincia
- Donut de proporción de bajas (forzada vs voluntaria)
- Filtros por período, provincia y tipo de avería

## Página 2: Inteligencia Geográfica
- Mapa coroplético de averías o bajas por provincia (seleccionable)
- Matriz de correlación entre indicadores (averías, bajas, energía entregada)
- Barras apiladas de averías por tipo y provincia
- Mapa de calor de averías por mes y provincia
- Filtros por año, provincia, tipo de avería y métrica del mapa

## Página 3: Flujo y Eficiencia Energética
- Líneas temporales de energía comprada, facturada, cobrada y pérdidas
- Gauge de pérdida actual con promedio anual
- Barras de brecha energética (entregada vs facturada por año)
- KPIs de pérdida actual y promedio anual
- Filtros por año 

---
## Tecnologías

- **Python 3.10+** — Lenguaje base.
- **Streamlit** — Framework del dashboard.
- **Pandas** — Procesamiento de datos.
- **ECharts + PyEcharts** — Gráficos interactivos y mapas.
- **GeoJSON** — Mapas.
- **Plotly** — Visualizaciones complementarias.

---

## Estructura del Proyecto

```
dashboard-edeeste/
├── app.py
├── pages/
│   ├── resumen.py                
│   ├── energia.py                 
│   └── inteligencia_geo.py        
├── data/
│   ├── data_loader.py             
│   ├── colors.py                  
│   ├── rd_provincias.geojson      
│   ├── datos_averias.csv          
│   ├── datos_energia_entregada.csv 
│   ├── datos_bajas_servicio.csv   
│   ├── geo_unificado.csv          
│   └── serie_edeeste.csv          
├── assets/
│   └── logos/
│       ├── edeeste.png            
│       └── mem_logo.png           
├── requirements.txt               
└── README.md                      
```

---

## Instalación y Ejecución

### Requisitos
- Python 3.10 o superior

### Pasos

1. Clonar o descargar el repositorio:

```bash
git clone https://github.com/tu-usuario/dashboard-edeeste.git
cd dashboard-edeeste
```

2. Crear entorno virtual:

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

4. Ejecutar el dashboard:

```bash
streamlit run app.py
```

5. Abrir en el navegador:

```
http://localhost:8501
```
