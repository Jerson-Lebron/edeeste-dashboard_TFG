#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  5 08:46:29 2026

@author: jerson-lebron
"""
import streamlit as st
import pandas as pd
from data import data_loader
from streamlit_echarts import st_echarts, Map, JsCode
from data import colors

COLORES = colors.COLORES
COLORES_TIPOS_AVERIA = colors.COLORES_TIPOS_AVERIA

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

st.header(" :material/map: Inteligencia Geográfica", divider="gray")
st.caption("""
           **Compara el comportamiento** de las provincias en múltiples dimensiones.  
           **Detecta anomalías geográficas** y **explora relaciones** entre indicadores clave del sistema de distribución.
           """)
st.caption("***Actualizado: 5/7/2026***")

# Filtros
# ----------------------------------------------------------------
with st.sidebar:
    st.header("Filtros")
    
    anios_disp = sorted(averias["anio"].unique().tolist())
    anio_sel = st.multiselect(
        "Año", 
        anios_disp, 
        default=anios_disp,
        key="anio_geo"
    )
    
    provs_disp = sorted(averias["provincia"].unique().tolist())
    prov_sel = st.multiselect(
        "Provincia", 
        provs_disp, 
        default=[],
        key="provincia_geo"
    )
    
    if prov_sel:
        tipos_disp = sorted(
            list(averias[averias["provincia"].isin(prov_sel)]["tipo de averia y emergencia"].unique())
        )
    else:
        tipos_disp = sorted(averias["tipo de averia y emergencia"].unique().tolist())
    
    tipo_sel = st.multiselect(
        "Tipo de Avería", 
        tipos_disp, 
        default=[],
        key="tipo_geo"
    )

    metrica_mapa = st.selectbox(
        "Métrica en el mapa",
        ["Averías", "Bajas"],
        index=0,
        key="metrica_mapa"
    )


current_averias = averias[
    (averias["anio"].isin(anio_sel)) &
    (averias["provincia"].isin(prov_sel) if prov_sel else True) &
    (averias["tipo de averia y emergencia"].isin(tipo_sel) if tipo_sel else True)
].copy()

df_correlacion = geo[
    (geo["anio"].isin(anio_sel)) &
    (geo["provincia"].isin(prov_sel) if prov_sel else True)
].copy()

row1_1, row1_2 = st.columns([1.2, 1])
row2_1, row2_2 = st.columns([1, 1])

# Mapa de averias por provincia
# --------------------------------------------------------
with row1_1:
    st.subheader("Distribución Geográfica")

    geojson_data = data_loader.load_geojson()

    for feature in geojson_data["features"]:
        feature["properties"]["name"] = feature["properties"]["adm2_name"]

    if metrica_mapa == "Averías":
        mapa_datos = data_loader.transform_data_map(current_averias)
        titulo_metrica = "Averías"
        color_escala = ["#f7f7f7", "#fdcc8a", "#fc8d59", "#d73027"]
    elif metrica_mapa == "Bajas":
        bajas_agg = bajas[
            (bajas["anio"].isin(anio_sel)) &
            (bajas["provincia"].isin(prov_sel))
        ].groupby("provincia")["bajas"].sum().reset_index()
        bajas_agg.columns = ["provincia", "valor"]
        mapa_datos = [{"name": f"Provincia {row['provincia']}", "value": row["valor"]} 
                     for _, row in bajas_agg.iterrows()]
        titulo_metrica = "Bajas"
        color_escala = ["#f7f7f7", "#fdcc8a", "#fc8d59", "#d73027"]
    else:
        mapa_datos = []
        titulo_metrica = "Pérdida %"
        color_escala = ["#f7fcfd", "#bfd3e6", "#8c96c6", "#88419d"]

    if not mapa_datos:
        st.warning("No hay datos para mostrar con este filtro.")
    else:
        nombres_con_datos = [item["name"] for item in mapa_datos]
        features_con_datos = [
            f for f in geojson_data["features"]
            if f["properties"]["name"] in nombres_con_datos
        ]

        if not features_con_datos:
            st.warning("Los nombres no coinciden con el GeoJSON.")
        else:
            lats = [f["properties"]["center_lat"] for f in features_con_datos]
            lons = [f["properties"]["center_lon"] for f in features_con_datos]
            centro_lat = sum(lats) / len(lats)
            centro_lon = sum(lons) / len(lons)
            valores = [item["value"] for item in mapa_datos]
            
            val_min = 0
            val_max = max(valores) if valores else 1

            map_opts = {
                "title": {
                    "text": f"Distribución de {titulo_metrica}",
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
                                   '{titulo_metrica}: ' + params.data.value.toLocaleString('es-MX');
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
                    "name": titulo_metrica,
                    "type": "map",
                    "map": "rd_provinces",
                    "roam": True,
                    "aspectScale": 0.8,
                    "zoom": 2.2,
                    "center": [centro_lon, centro_lat],
                    "data": mapa_datos,
                    "itemStyle": {"borderColor": "#fff", "borderWidth": 1},
                    "emphasis": {
                        "label": {"show": True, "fontSize": 12, "fontWeight": "bold"},
                        "itemStyle": {"shadowBlur": 10, "shadowColor": "rgba(0,0,0,0.4)"}
                    },
                    "label": {"show": False}
                }]
            }

            st_echarts(
                options=map_opts,
                map=Map("rd_provinces", geojson_data),
                height="420px",
                key="mapa_averias_exp"
            )

# Matriz de correlacion: Bajas, energia entregada y averias
# ---------------------------------------------------------
with row1_2:
    st.subheader("Matriz de Correlación")
    
    if not df_correlacion.empty:
        columnas_corr = ['averias', 'bajas', 'energia_entregada_GWh']
        columnas_existentes = [col for col in columnas_corr if col in df_correlacion.columns]
        
        if len(columnas_existentes) < 2:
            st.info("No hay suficientes variables numéricas para calcular correlaciones")
        else:
            corr_df = df_correlacion[columnas_corr].corr().astype(float)
                
            corr_data = []
            for i in range(len(corr_df)):
                for j in range(len(corr_df)):
                    corr_data.append([i, j, round(float(corr_df.iloc[i, j]), 2)])
                        
            nombres_map = {
                'averias': 'Averías',
                'bajas': 'Bajas',
                'energia_entregada_GWh': 'Energía'
            }
            etiquetas = [nombres_map.get(col, col) for col in corr_df.columns]
                        
            heatmap_corr_opts = {
                "title": {
                    "text": "Relación entre Indicadores",
                    "subtext": "Correlación por provincia",
                    "left": "center", "top": 5,
                    "textStyle": {"fontSize": 14, "fontWeight": "bold"},
                    "subtextStyle": {"fontSize": 10, "color": "#888"}
                },
                "tooltip": {
                    "position": "top",
                    "formatter": JsCode(
                        """
                        function(params) {
                            return '<strong>' + params.value[0] + ' vs ' + params.value[1] + '</strong><br/>' +
                                   'Correlación: ' + params.value[2].toFixed(2);
                        }
                        """
                    )
                },
                "grid": {
                    "left": "10%", "right": "15%",
                    "top": "15%", "bottom": "15%",
                    "containLabel": True
                },
                "xAxis": {
                    "type": "category",
                    "data": etiquetas,
                    "splitArea": {"show": True},
                    "axisLabel": {"fontSize": 10}
                },
                "yAxis": {
                    "type": "category",
                    "data": etiquetas,
                    "splitArea": {"show": True},
                    "axisLabel": {"fontSize": 10}
                },
                "visualMap": {
                    "min": -1.0,
                    "max": 1.0,
                    "calculable": True,
                    "orient": "vertical",
                    "right": "2%",
                    "top": "center",
                    "inRange": {"color": ["#ee6666", "#fac858", "#91cc75"]}
                },
                "series": [{
                    "name": "Correlación",
                    "type": "heatmap",
                    "data": corr_data,
                    "label": {
                        "show": True,
                        "color": "#333",
                        "fontSize": 11,
                        "fontWeight": "bold",
                        "formatter": "{@[2]}"
                    },
                    "itemStyle": {"borderColor": "#fff", "borderWidth": 2}
                }]
            }
                    
            st_echarts(
                options=heatmap_corr_opts,
                height="420px",
                key="corr_heatmap",
                theme="streamlit"
            )
    else: 
        st.warning("No hay datos para mostrar con este filtro.")  

# Barras apiladas por tipo de averia y provincia
# ----------------------------------------------------
with row2_1:
    st.subheader("Averías por Tipo y Provincia")

    comp = (
        current_averias
        .groupby(["provincia", "tipo de averia y emergencia"])["averias"]
        .sum()
        .reset_index()
    )

    orden_prov = (
        comp.groupby("provincia")["averias"]
        .sum()
        .sort_values(ascending=False)
        .index.tolist()
    )

    tipos = sorted(comp["tipo de averia y emergencia"].unique().tolist())

    series_barras = []
    for tipo in tipos:
        df_t = comp[comp["tipo de averia y emergencia"] == tipo]
        vals = []
        for prov in orden_prov:
            fila = df_t[df_t["provincia"] == prov]["averias"]
            vals.append(round(float(fila.sum()), 1) if not fila.empty else 0)
        
        color = COLORES_TIPOS_AVERIA.get(tipo, COLORES["otros"])
        
        series_barras.append({
            "name": tipo,
            "type": "bar",
            "stack": "total",
            "data": vals,
            "itemStyle": {"color": color},
            "emphasis": {"focus": "series"},
            "label": {"show": False}
        })

    bar_opts = {
        "title": {
            "text": "Composición por Tipo de Avería",
            "left": "center", "top": 5,
            "textStyle": {"fontSize": 14, "fontWeight": "bold"}
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
        "legend": {"type": "scroll", "bottom": 0, "textStyle": {"fontSize": 10}},
        "grid": {
            "left": "3%", "right": "4%",
            "bottom": "3%", "top": "13%",
            "containLabel": True
        },
        "xAxis": {
            "type": "category",
            "data": orden_prov,
            "axisLabel": {"rotate": 35, "fontSize": 10, "interval": 0}
        },
        "yAxis": {
            "type": "value",
            "name": "Averías",
            "nameTextStyle": {"fontSize": 11},
            "axisLabel": {
                "formatter": JsCode(
                    "function(v){return v.toLocaleString('es-MX');}"
                )
            }
        },
        "series": series_barras
    }

    st_echarts(options=bar_opts, height="400px", key="barras_tipo_prov")
    
# Mapa de calor de averias (Mes por Provincia)
#---------------------------------------------------------
with row2_2:
    st.subheader("Mapa de Calor (Mes por Provincia)")

    heat = (
        current_averias
        .groupby(["mes", "provincia"])["averias"]
        .sum()
        .reset_index()
    )

    MESES_LABEL = {
        1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr",
        5: "May", 6: "Jun", 7: "Jul", 8: "Ago",
        9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"
    }

    prov_heat = (
        heat.groupby("provincia")["averias"]
        .sum()
        .sort_values(ascending=False)
        .index.tolist()
    )
    meses_label = [MESES_LABEL[m] for m in range(1, 13)]

    heat_data = []
    for _, row in heat.iterrows():
        if row["provincia"] in prov_heat:
            x = prov_heat.index(row["provincia"])
            y = int(row["mes"]) - 1
            heat_data.append([x, y, round(float(row["averias"]), 1)])

    max_heat = max([d[2] for d in heat_data]) if heat_data else 1

    heatmap_opts = {
        "title": {
            "text": "Intensidad de Averías por Mes y Provincia",
            "left": "center", "top": 5,
            "textStyle": {"fontSize": 14, "fontWeight": "bold"}
        },
        "tooltip": {
            "position": "top",
            "formatter": JsCode(
                """
                function(params) {
                    return '<strong>' + params.name + '</strong><br/>' +
                           'Mes: ' + params.value[1] + '<br/>' +
                           'Averías: ' + params.value[2].toLocaleString('es-MX');
                }
                """
            )
        },
        "grid": {
            "left": "5%", "right": "5%",
            "bottom": "28%", "top": "7%",
            "containLabel": False
        },
        "xAxis": {
            "type": "category",
            "data": prov_heat,
            "splitArea": {"show": True},
            "axisLabel": {"rotate": 35, "fontSize": 9, "interval": 0}
        },
        "yAxis": {
            "type": "category",
            "data": meses_label,
            "splitArea": {"show": True},
            "axisLabel": {"fontSize": 10}
        },
        "visualMap": {
           "min": 0,
           "max": max_heat,
           "calculable": True,
           "orient": "horizontal",
           "left": "center",
           "bottom": "0%",
           "inRange": {"color": color_escala}
       },
        "series": [{
            "name": "Averías",
            "type": "heatmap",
            "data": heat_data,
            "label": {
                "show": True,
                "fontSize": 9,
                "fontWeight": "bold",
                "formatter": JsCode(
                    "function(v){return v.value[2].toLocaleString('es-MX');}"
                )
            },
            "emphasis": {
                "itemStyle": {"shadowBlur": 10, "shadowColor": "rgba(0,0,0,0.5)"}
            }
        }]
    }

    st_echarts(options=heatmap_opts, height="400px", key="heatmap_averias")