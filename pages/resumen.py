#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  5 08:27:47 2026

@author: jerson-lebron
"""
from data import data_loader
import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts, JsCode, Map
from data import colors


COLORES = colors.COLORES
COLORES_TIPOS_AVERIA = colors.COLORES_TIPOS_AVERIA

# Carga de los datos
# -------------------------------------------------------
datos = data_loader.load_data()
averias = datos["averias"]
geo = datos["geo"]
bajas = datos["bajas"]
serie_edeeste = datos["serie_edeeste"]
energia = datos["energia"]

geo["fecha"] = pd.to_datetime(
    geo['mes'].astype(str) + '-' + geo['anio'].astype(str),
    format='%m-%Y'
)

averias["fecha"] = pd.to_datetime(averias["fecha"], format="%Y-%m-%d")
geo["fecha"] = pd.to_datetime(geo["fecha"], format="%Y-%m-%d")
bajas["fecha"] = pd.to_datetime(bajas["fecha"], format="%Y-%m-%d")
energia["fecha"] = pd.to_datetime(energia["fecha"], format="%Y-%m-%d")
serie_edeeste["fecha"] = pd.to_datetime(serie_edeeste["fecha"], format="%Y-%m-%d")

min_date = serie_edeeste["fecha"].min()
max_date = serie_edeeste["fecha"].max()

st.header(":material/bar_chart: Dashboard de Eficiencia de Distribución - :yellow[EDEESTE]", divider="gray")
st.markdown(f"Análisis integral de averías, pérdidas y bajas de servicio | **Periodo de Análisis:** {min_date.strftime('%d-%m-%Y')} - {max_date.strftime('%d-%m-%Y')}")
st.caption("***Actualizado: 5/7/2026***")

# Filtros
# --------------------------------------------------------
with st.sidebar:
    selected_period = st.selectbox(
        "Período de Análisis",
        ["1 Mes", "3 Meses", "6 Meses", "12 Meses", "Todo"],
        index=3,
        key="period",
        bind="query-params", 
    )
    
    if selected_period:
        selected_provincias = st.multiselect(
            "Provincia",
            options=sorted(list(geo["provincia"].unique())),
            default=[],
            key="provincia",
            bind="query-params",
        )
    
    if selected_provincias:
        tipo_options = sorted(
            list(averias[averias["provincia"].isin(selected_provincias)]["tipo de averia y emergencia"]
            .unique())
        )
    else:
        tipo_options = sorted(list(averias["tipo de averia y emergencia"].unique()))
    
    selected_tipos = st.multiselect(
        "Tipo de Avería",
        options=tipo_options,
        default=[],
        key="tipo_averia",
        bind="query-params",
    )

period_offsets = {
    "1 Mes": 1,
    "3 Meses": 3,
    "6 Meses": 6,
    "12 Meses": 12,
    "24 Meses": 24,
}

fecha_fin = max_date 

if selected_period == "1 Mes":
    fecha_inicio = pd.to_datetime("2025-12-01")
    meses = period_offsets[selected_period]
    fecha_inicio_anterior = fecha_inicio - pd.DateOffset(months=meses)
    fecha_fin_anterior = fecha_inicio - pd.DateOffset(days=1)
elif selected_period in period_offsets:
    meses = period_offsets[selected_period]
    fecha_inicio = fecha_fin - pd.DateOffset(months=meses)
    fecha_inicio_anterior = fecha_inicio - pd.DateOffset(months=meses)
    fecha_fin_anterior = fecha_inicio - pd.DateOffset(days=1)
else:
    fecha_inicio = min_date
    fecha_inicio_anterior = None
    fecha_fin_anterior = None

def apply_filters(df, fecha_inicio, fecha_fin, provincias, tipos):
    mask = (df['fecha'] >= fecha_inicio) & (df['fecha'] <= fecha_fin)
    if provincias:
        mask = mask & df['provincia'].isin(provincias)
    if tipos:
        mask = mask & df["tipo de averia y emergencia"].isin(tipos)
    return df[mask].copy()

current_averias = apply_filters(averias, fecha_inicio, fecha_fin, selected_provincias, selected_tipos)
if fecha_inicio_anterior is not None:
    prev_averias = apply_filters(averias, fecha_inicio_anterior, fecha_fin_anterior, selected_provincias, selected_tipos)
else:
    prev_averias = None 

current_bajas = apply_filters(bajas, fecha_inicio, fecha_fin, selected_provincias, False)
if fecha_inicio_anterior is not None:
    prev_bajas = apply_filters(bajas, fecha_inicio_anterior, fecha_fin_anterior, selected_provincias, False)
else:
    prev_bajas = None 

current_geo = apply_filters(geo, fecha_inicio, fecha_fin, selected_provincias, False)
if fecha_inicio_anterior is not None:
    prev_geo = apply_filters(geo, fecha_inicio_anterior, fecha_fin_anterior, selected_provincias, False)
else:
    prev_geo = None 

current_energia = apply_filters(energia, fecha_inicio, fecha_fin, selected_provincias, False)
if fecha_inicio_anterior is not None:
    prev_energia = apply_filters(energia, fecha_inicio_anterior, fecha_fin_anterior, selected_provincias, False)
else:
    prev_energia = None 

current_serie_edeeste = apply_filters(serie_edeeste, fecha_inicio, fecha_fin, False, False)
if fecha_inicio_anterior is not None:
    prev_serie_edeeste = apply_filters(serie_edeeste, fecha_inicio_anterior, fecha_fin_anterior, False, False)
else:
    prev_serie_edeeste = None 
    
# Datos para los KPIs
# ----------------------------------------------------
current_kpis = {
    "total_averias": current_averias["averias"].sum(),
    "total_bajas": current_bajas["bajas"].sum(),
    "perdida_pct": current_serie_edeeste["perdida_pct"].mean(),
    "total_energia": current_geo["energia_entregada_GWh"].sum()
}

prev_kpis = {
    "total_averias": prev_averias["averias"].sum() if prev_averias is not None else 0,
    "total_bajas": prev_bajas["bajas"].sum() if prev_bajas is not None else 0,
    "perdida_pct": prev_serie_edeeste["perdida_pct"].mean() if prev_serie_edeeste is not None else 0,
    "total_energia": prev_geo["energia_entregada_GWh"].sum() if prev_geo is not None else 0
}

def get_delta(curr, prev, is_pct=False):
    if prev is None or prev == 0:
        return None
    if is_pct:
        return f"{curr - prev:+.1f}%"
    return f"{(curr - prev) / prev * 100:+.1f}%"

def get_sparkline_data(df, columna):
    if df.empty:
        return None
    df_mensual = df.groupby(pd.Grouper(key='fecha', freq='M'))[columna].sum().reset_index()
    return df_mensual[columna].tolist()

spark_averias = get_sparkline_data(current_averias, "averias")
spark_bajas = get_sparkline_data(current_bajas, "bajas")
spark_perdida = get_sparkline_data(current_serie_edeeste, "perdida_GWh")
spark_energia = get_sparkline_data(current_geo, "energia_entregada_GWh")

# Graficos de los KPIs
# -----------------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    val = current_kpis['total_averias']
    delta = get_delta(val, prev_kpis['total_averias']) if prev_kpis else None
    st.metric(
        "Total Averías",
        f"{val:,.0f}",
        delta=delta,
        delta_color="inverse",
        border=True,
        chart_data=spark_averias if spark_averias else 0,
        chart_type="area",
    )

with col2:
    val = current_kpis['total_bajas']
    delta = get_delta(val, prev_kpis['total_bajas'])
    st.metric(
        "Total Bajas",
        f"{val:,.0f}",
        delta=delta,
        delta_color="inverse",
        border=True,
        chart_data=spark_bajas if spark_bajas else 0, 
        chart_type="area",
    )
    
with col3:
    val = current_kpis['perdida_pct']
    delta = get_delta(val, prev_kpis['perdida_pct'])
    st.metric(
        "Perdida Promedio",
        f"{val:,.0f}%",
        delta=delta,
        delta_color="inverse",
        border=True,
            chart_data=spark_perdida if spark_perdida else 0,
            chart_type="area",
        )
        
st.caption("**Nota:** El KPI de pérdida no se filtra por provincia ni por tipo de averías. El KPI de total de bajas no se fitra por tipo de averías")

with col4:
    val = current_kpis["total_energia"]
    delta = get_delta(val, prev_kpis["total_energia"])
    st.metric(
        "Total Energia Entregada",
        f"{val:,.0f} GWh",
        delta=delta,
        border=True,
        chart_data=spark_energia if spark_energia else 0,
        chart_type="area"
    )

# Seccion 1: Evolucion de la eficiencia energetica
# ---------------------------------------------------------------------
st.subheader(":material/trending_up: ¿Cómo está evolucionando nuestra eficiencia energética?")
st.caption("""
**Evolución y composición energética:** Analiza la tendencia de la energía comprada, facturada y cobrada, 
y visualiza la proporción entre pérdidas y energía facturada para identificar desviaciones y patrones de eficiencia.
""")

row1_1, row1_2 = st.columns([1.8, 1])

# Grafico de lineas: Comprada, cobrada, perdida y facturada en GWh
# ------------------------------------------------------------------

with row1_1:
    datos = current_serie_edeeste
    fechas = datos["fecha"].dt.strftime("%b %Y").to_list()
    comprada = datos["comprada_GWh"].to_list()
    cobrada = datos["cobrada_GWh"].to_list()
    perdida = datos["perdida_GWh"].to_list()
    facturada = datos["facturada_GWh"].to_list()
    
    trend_opts = {
        "title": {
            "text": "Evolución de Indicadores Energéticos",
            "left": "center",
            "top": 5
        },
        "toolbox": {
            "feature": {
                "saveAsImage": {},
                "dataView": {"readOnly": True},
                "restore": {},
                "magicType": {"type": ["line", "bar"]},
            }
        },
        "tooltip": {
            "trigger": "axis",
            "valueFormatter": JsCode(
                "function(v){return v.toLocaleString('es-MX')  + ' GWh'}"
            )
        },
        "legend": {
            "data": ["Comprada", "Facturada", "Cobrada", "Pérdida"],
            "bottom": "0"
        },
        "xAxis": {
            "type": "category",
            "data": fechas,
            "axisLabel": {"rotate": 45}
        },
        "yAxis": {
            "type": "value",
            "name": "GWh",
            "axisLabel": {"formatter": "{value}"}
        },
        "dataZoom": [
            {"type": "inside", "start": 0, "end": 100},
            {"type": "slider", "start": 0, "end": 100, "height": 20, "bottom": 30}
        ],
        "grid": {
            "left": "4%", "right": "5%",
            "bottom": "18%",
            "containLabel": True
        },
        "series": [
            {
                "name": "Comprada",
                "type": "line",
                "smooth": True,
                "areaStyle": {"opacity": 0.1},
                "data": comprada,
                "itemStyle": {"color": COLORES["comprada"]},
            },
            {
                "name": "Facturada",
                "type": "line",
                "smooth": True,
                "areaStyle": {"opacity": 0.1},
                "data": facturada,
                "itemStyle": {"color": COLORES["facturada"]},
            },
            {
                "name": "Cobrada",
                "type": "line",
                "smooth": True,
                "areaStyle": {"opacity": 0.1},
                "data": cobrada,
                "itemStyle": {"color": COLORES["cobrada"]},
            },
            {
                "name": "Pérdida",
                "type": "line",
                "smooth": True,
                "areaStyle": {"opacity": 0.1},
                "data": perdida,
                "itemStyle": {"color": COLORES["perdida"]},
            }
        ]
    }

    st_echarts(options=trend_opts, height="400px", key="trend_energy", theme="streamlit")
    
# Grafico de Donut: Distribucion de energía comprada
# ----------------------------------------------------
with row1_2:
    total_comprada = current_serie_edeeste["comprada_GWh"].sum()
    total_facturada = current_serie_edeeste["facturada_GWh"].sum()
    total_perdida = current_serie_edeeste["perdida_GWh"].sum()
    
    pie_data = [
        {"name": "Energía Facturada", "value": round(total_facturada, 2)},
        {"name": "Pérdida de Energía", "value": round(total_perdida, 2)}
    ]
    
    pie_opts = {
        "title": {
            "text": "Distribución de Energía Comprada",
            "left": "center"
        },
        "tooltip": {
            "trigger": "item",
            "formatter": "{b}<br/>Energía: {c} GWh<br/>Porcentaje: {d}%"
        },
        "legend": {
            "bottom": "0",
            "orient": "horizontal",
            "left": "center"
        },
        "series": [{
            "type": "pie",
            "radius": ["45%", "70%"],
            "avoidLabelOverlap": True,
            "itemStyle": {
                "borderRadius": 10,
                "borderColor": "#fff",
                "borderWidth": 2
            },
            "label": {
                "show": True,
                "formatter": "{b}\n{d}%",
                "fontSize": 12
            },
            "emphasis": {
                "label": {
                    "show": True,
                    "fontSize": 14,
                    "fontWeight": "bold"
                },
                "itemStyle": {
                    "shadowBlur": 10,
                    "shadowOffsetX": 0,
                    "shadowColor": "rgba(0, 0, 0, 0.5)"
                }
            },
            "data": pie_data,
            "color": [COLORES["facturada"], COLORES["perdida"]]
        }]
    }

    st_echarts(options=pie_opts, height="400px", key="pie_perdidas", theme="streamlit")
    
st.caption("**Nota:** Los gráficos de esta sección muestran datos agregados de EDEESTE y no se filtran por provincia ni por tipo de averías.")

# Seccion 2: Averias por provincia
# ----------------------------------------------------------
st.subheader(":material/map_search: Panorama de Averías: Ubicación y Tipología")
st.caption("Distribución geográfica de averías por provincia y composición por tipo de avería en barras apiladas.")

row2_1, row2_2 = st.columns(2)

# Mapa de coropletas de averias
# -------------------------------------------------------------
with row2_1:
    geojson_data = data_loader.load_geojson()

    for feature in geojson_data["features"]:
        feature["properties"]["name"] = feature["properties"]["adm2_name"]

    mapa_datos = data_loader.transform_data_map(current_averias)

    if not mapa_datos:
        st.warning("No hay datos para mostrar en el mapa con este filtro.")
    else:
        nombres_con_datos = [item["name"] for item in mapa_datos]

        features_con_datos = [
            f for f in geojson_data["features"]
            if f["properties"]["name"] in nombres_con_datos
        ]

        if not features_con_datos:
            st.warning("Los nombres de mapa_datos no coinciden con el GeoJSON.")
        else:
            lats = [f["properties"]["center_lat"] for f in features_con_datos]
            lons = [f["properties"]["center_lon"] for f in features_con_datos]
            centro_lat = sum(lats) / len(lats)
            centro_lon = sum(lons) / len(lons)

            valores = [item["value"] for item in mapa_datos]
            val_min = 0
            val_max = max(valores)

            mapa_datos_final = [
                {"name": item["name"], "value": item["value"]}
                for item in mapa_datos
                if item["value"] is not None and item["value"] > 0
                ]
            
            color_escala = ["#f7f7f7", "#fdcc8a", "#fc8d59", "#d73027"]
            
            titulo = "Distribución de Averías"
            map_opts = {
                "title": {
                    "text": titulo,
                    "subtext": "Haz clic en una provincia para ver detalle",
                    "left": "center", "top": 5,
                    "textStyle": {"fontSize": 14, "fontWeight": "bold"},
                    "subtextStyle": {"fontSize": 10, "color": "#888"}
                },
                "tooltip": {
                    "trigger": "item",
                    "formatter": JsCode(
                        f"""
                        function(params) {{
                            if (!params.data) return params.name + ': Sin datos';
                            return '<strong>' + params.name + '</strong><br/>' +
                                   'Averías: ' + params.data.value.toLocaleString();
                        }}
                        """
                    )
                },
                "visualMap": {
                    "min": val_min,
                    "max": val_max,
                    "calculable": True,
                    "orient": "horizontal",
                    "left": "center",
                    "bottom": "5%",
                    "text": ["Alto", "Bajo"],
                    "inRange": {"color": color_escala}
                },
                "series": [{
                    "name": titulo,
                    "type": "map",
                    "map": "rd_provinces",
                    "roam": True,
                    "aspectScale": 0.8,
                    "zoom": 2.2,
                    "center": [centro_lon, centro_lat],
                    "data": mapa_datos_final,
                    "itemStyle": {"borderColor": "#fff", "borderWidth": 1},
                    "emphasis": {
                        "label": {"show": True, "fontSize": 12, "fontWeight": "bold"},
                        "itemStyle": {"shadowBlur": 10, "shadowColor": "rgba(0,0,0,0.4)"}
                    },
                    "label": {"show": False}
                }]
            }

            st_echarts(options=map_opts, map=Map("rd_provinces", geojson_data), height="400px", key="mapa_averias", theme="streamlit")

# Barras apiladas por tipo de averia y provincia
# ---------------------------------------------------------------------
with row2_2:
    stacked_datos = current_averias.groupby(["provincia", "tipo de averia y emergencia"])["averias"].sum().reset_index()
    provincias_ordenadas = stacked_datos.groupby('provincia')["averias"].sum().sort_values(ascending=False).index.tolist()
    
    tipos_averia = sorted(stacked_datos["tipo de averia y emergencia"].unique().tolist())
    
    series_data = []
    for tipo in tipos_averia:
        tipo_data = stacked_datos[stacked_datos["tipo de averia y emergencia"] == tipo]
        valores = []
        for provincia in provincias_ordenadas:
            valor = tipo_data[tipo_data['provincia'] == provincia]['averias'].sum()
            valores.append(float(valor) if not pd.isna(valor) else 0)
        
        color = COLORES_TIPOS_AVERIA.get(tipo, COLORES["otro"])
        
        series_data.append({
            "name": tipo,
            "type": "bar",
            "stack": "total",
            "data": valores,
            "itemStyle": {"color": color},
            "emphasis": {"focus": "series"}
        })
    
    stacked_opts = {
        "title": {
            "text": "Averías por Tipo y Provincia",
            "left": "center",
            "top": 5,
            "textStyle": {"fontSize": 16, "fontWeight": "bold"}
        },
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {"type": "shadow"},
            "formatter": JsCode(
                """
                function(params) {
                    var total = 0;
                    var html = '<strong>' + params[0].name + '</strong><br/>';
                    params.forEach(function(p) {
                        if (p.value > 0) {
                            html += p.marker + ' ' + p.seriesName + ': ' + p.value.toLocaleString() + '<br/>';
                            total += p.value;
                        }
                    });
                    html += '<strong>Total: ' + total.toLocaleString() + '</strong>';
                    return html;
                }
                """
            )
        },
        "legend": {
            "bottom": "0",
            "type": "scroll",
            "textStyle": {"fontSize": 11}
        },
        "grid": {
            "left": "3%",
            "right": "4%",
            "bottom": "15%",
            "top": "10%",
            "containLabel": True
        },
        "xAxis": {
            "type": "category",
            "data": provincias_ordenadas,
            "axisLabel": {"rotate": 30, "fontSize": 10, "interval": 0}
        },
        "yAxis": {
            "type": "value",
            "name": "Averías",
            "nameTextStyle": {"fontSize": 12}
        },
        "series": series_data
    }

    st_echarts(
        options=stacked_opts,
        height="500px",
        key="stacked_averias",
        theme="streamlit"
    )

# Seccion 3: Bajas/Cancelaciones
# -------------------------------------------------------------------------
st.subheader(":material/assessment: Análisis de Bajas")
st.caption("""
**Visualiza la evolución temporal de las bajas**, su composición por estado y provincia, 
y la distribución general de estados para identificar patrones y áreas críticas.
""")

if not current_bajas.empty:
    row3_1, row3_2, row3_3 = st.columns(3)

    current_bajas_temp = current_bajas.copy()

    current_bajas_temp["mes_str"] = pd.to_datetime(
        current_bajas_temp["anio"].astype(str) + "-" +
        current_bajas_temp["mes"].astype(str).str.zfill(2) + "-01"
    ).dt.strftime("%b %Y")

    COLOR_FORZADA = COLORES["forzada"]
    COLOR_VOLUNTARIA = COLORES["voluntaria"]
    COLOR_TOTAL = COLORES["bajas"]
    
    # Grafico de Lineas: Bajas por estado (baja forzada, baja voluntaria)
    # ___________________________________________________________________
    with row3_1:
        temporal_total = (
            current_bajas_temp
            .groupby(["anio", "mes", "mes_str"])["bajas"]
            .sum()
            .reset_index()
            .sort_values(["anio", "mes"])
            .reset_index(drop=True)
        )

        temporal_estado = (
            current_bajas_temp
            .groupby(["anio", "mes", "mes_str", "estado"])["bajas"]
            .sum()
            .reset_index()
            .sort_values(["anio", "mes"])
            .reset_index(drop=True)
        )

        fechas = temporal_total["mes_str"].tolist()

        def serie_estado(estado, color):
            df_e = temporal_estado[temporal_estado["estado"] == estado]
            merged = temporal_total[["anio", "mes", "mes_str"]].merge(
                df_e[["anio", "mes", "bajas"]], on=["anio", "mes"], how="left"
            ).fillna(0)
            return {
                "name": estado,
                "type": "line",
                "smooth": True,
                "symbolSize": 5,
                "lineStyle": {"color": color, "width": 2},
                "itemStyle": {"color": color},
                "areaStyle": {"opacity": 0.08},
                "data": [int(v) for v in merged["bajas"].tolist()],
            }

        promedio = float(round(temporal_total["bajas"].mean(), 0))
        maximo = float(temporal_total["bajas"].max())

        line_opts = {
            "title": {
                "text": "Evolución de Bajas de Servicio",
                "subtext": "Total mensual · Forzada vs Voluntaria",
                "left": "center", "top": 5,
                "textStyle": {"fontSize": 15, "fontWeight": "bold"},
                "subtextStyle": {"fontSize": 11, "color": "#888"}
            },
            "tooltip": {"trigger": "axis"},
            "legend": {
                "data": ["Total", "baja forzada", "baja voluntaria"],
                "bottom": 0, "type": "scroll"
            },
            "xAxis": {
                "type": "category",
                "data": fechas,
                "axisLabel": {"rotate": 40, "fontSize": 10}
            },
            "yAxis": {
                "type": "value",
                "name": "Bajas",
                "nameTextStyle": {"fontSize": 11}
            },
            "grid": {
                "left": "3%",
                "right": "4%",
                "bottom": "15%",
                "top": "12%",
                "containLabel": True
            },
            "dataZoom": [
                {"type": "inside", "start": 0, "end": 100},
                {"type": "slider", "start": 0, "end": 100, "height": 18, "bottom": 28}
            ],
            "series": [
                {
                    "name": "Total",
                    "type": "line",
                    "smooth": True,
                    "symbolSize": 5,
                    "lineStyle": {"color": COLOR_TOTAL, "width": 3},
                    "itemStyle": {"color": COLOR_TOTAL},
                    "areaStyle": {"opacity": 0.06},
                    "data": [int(v) for v in temporal_total["bajas"].tolist()],
                    "markLine": {
                        "silent": True,
                        "symbol": "none",
                        "data": [
                            {
                                "yAxis": promedio,
                                "lineStyle": {"color": COLORES["meta"], "type": "dashed", "width": 2},
                                "label": {
                                    "formatter": f"Prom: {int(promedio):,}",
                                    "color": COLORES["meta"],
                                    "position": "insideEndTop"
                                }
                            },
                            {
                                "yAxis": maximo,
                                "lineStyle": {"color": COLORES["perdida"], "type": "dashed", "width": 2},
                                "label": {
                                    "formatter": f"Máx: {int(maximo):,}",
                                    "color": COLORES["perdida"],
                                    "position": "insideEndTop"
                                }
                            }
                        ]
                    }
                },
                serie_estado("baja forzada", COLOR_FORZADA),
                serie_estado("baja voluntaria", COLOR_VOLUNTARIA),
            ]
        }

        st_echarts(options=line_opts, height="420px", key="bajas_linea")
        
    # Barras apiladas por estado y provincia
    # _______________________________________
    with row3_2:
        comp = (
            current_bajas
            .groupby(["provincia", "estado"])["bajas"]
            .sum()
            .reset_index()
            )
        
        orden_prov = (
            comp.groupby("provincia")["bajas"]
            .sum()
            .sort_values(ascending=False)
            .index.tolist()
            )

        def serie_barras(estado, color):
            df_e = comp[comp["estado"] == estado]
            valores = []
            for prov in orden_prov:
                fila = df_e[df_e["provincia"] == prov]["bajas"]
                valores.append(int(fila.sum()) if not fila.empty else 0)
            return {
                "name": estado,
                "type": "bar",
                "stack": "total",
                "data": valores,
                "itemStyle": {"color": color},
                "emphasis": {"focus": "series"},
                "label": {
                    "show": True,
                    "position": "inside",
                    "fontSize": 10,
                    "fontWeight": "bold",
                    "formatter": JsCode(
                        "function(v){return v.value.toLocaleString();}"
                        )
                    }
                }

        bar_opts = {
            "title": {
                "text": "Composición de Bajas por Provincia",
                "subtext": "Forzada vs Voluntaria",
                "left": "center", "top": 5,
                "textStyle": {"fontSize": 15, "fontWeight": "bold"},
                "subtextStyle": {"fontSize": 11, "color": "#888"}
                },
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {"type": "shadow"},
                "formatter": JsCode(
                    """
                    function(params) {
                        var total = 0;
                        var html = '<strong>' + params[0].name + '</strong><br/>';
                        params.forEach(function(p) {
                            if (p.value > 0) {
                                    html += p.marker + ' ' + p.seriesName + ': ' + p.value.toLocaleString('es-MX') + '<br/>';
                                    total += p.value;
                                    }
                            });
                        html += '<strong>Total: ' + total.toLocaleString('es-MX') + '</strong>';
                        return html;
                    }
                    """
                    )
                },
            "legend": {
                "data": ["baja forzada", "baja voluntaria"],
                "bottom": 0
                },
            "grid": {
                "left": "3%", "right": "4%",
                "bottom": "15%", "top": "18%",
                "containLabel": True
                },
            "xAxis": {
                "type": "category",
                "data": orden_prov,
                "axisLabel": {"rotate": 30, "fontSize": 10, "interval": 0}
                },
            "yAxis": {
                "type": "value",
                "name": "Bajas",
                "nameTextStyle": {"fontSize": 11},
                "axisLabel": {
                    "formatter": JsCode(
                        "function(v){return v.toLocaleString('es-MX');}"
                        )
                    }
                },
            "series": [
                serie_barras("baja forzada", COLOR_FORZADA),
                serie_barras("baja voluntaria", COLOR_VOLUNTARIA),
                ]
            }

        st_echarts(options=bar_opts, height="420px", key="bajas_barras")
    
    # Grafico de Donut: Distribucion de las bajas
    # __________________________________
    with row3_3:
        totales = (
            current_bajas
            .groupby("estado")["bajas"]
            .sum()
            .reset_index()
        )

        data_donut = []
        for estado, color in [("baja forzada", COLOR_FORZADA), ("baja voluntaria", COLOR_VOLUNTARIA)]:
            fila = totales[totales["estado"] == estado]["bajas"]
            val = int(fila.sum()) if not fila.empty else 0
            data_donut.append({
                "name": estado,
                "value": val,
                "itemStyle": {"color": color}
            })

        total_global = sum(d["value"] for d in data_donut)

        donut_opts = {
            "title": {
                "text": "Proporción de Bajas",
                "subtext": f"Total: {total_global:,}",
                "left": "center", "top": 5,
                "textStyle": {"fontSize": 15, "fontWeight": "bold"},
                "subtextStyle": {"fontSize": 12, "color": "#555"}
            },
            "tooltip": {"trigger": "item"},
            "legend": {
                "orient": "horizontal",
                "bottom": 0,
                "data": ["Forzada", "Voluntaria"]
            },
            "series": [
                {
                    "name": "Bajas",
                    "type": "pie",
                    "radius": ["42%", "70%"],
                    "center": ["50%", "52%"],
                    "avoidLabelOverlap": True,
                    "itemStyle": {"borderRadius": 6, "borderColor": "#fff", "borderWidth": 2},
                    "label": {
                        "show": True,
                        "formatter": "{b}\n{d}%",
                        "fontSize": 12
                    },
                    "emphasis": {
                        "label": {"show": True, "fontSize": 14, "fontWeight": "bold"},
                        "itemStyle": {"shadowBlur": 10, "shadowOffsetX": 0, "shadowColor": "rgba(0,0,0,0.2)"}
                    },
                    "data": data_donut
                }
            ]
        }

        st_echarts(options=donut_opts, height="420px", key="bajas_donut")

else:
    st.warning("""
               **No se encontraron datos disponibles**  
               La fuente de datos *Estadísticas de Bajas o Cancelaciones de Contratos de Servicios 2017 - 2026* no contiene registros para los filtros seleccionados.  
               Por favor, ajusta los filtros o verifica la disponibilidad de información en el período consultado.
               """)