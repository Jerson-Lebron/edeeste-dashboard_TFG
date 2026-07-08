#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 16:00:55 2026

@author: jerson-lebron
"""
import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts, JsCode
from data import data_loader
from data import colors

COLORES = colors.COLORES

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

st.header(":material/bolt: Flujo y Eficiencia Energética", divider="gray")
st.markdown("""
            **Analiza la evolución de la energía comprada, facturada y cobrada**, 
            y visualiza la composición de pérdidas para identificar desviaciones y oportunidades de mejora.
            """)

# Filtros
#--------------------------------------------------
with st.sidebar:
    st.header("Filtros")
    anios_disp = sorted(serie_edeeste["anio"].astype(int).unique().tolist())
    anio_sel = st.multiselect("Año", anios_disp, default=anios_disp)

current_serie = serie_edeeste[
    serie_edeeste["anio"].astype(int).isin(anio_sel)
].copy().sort_values("fecha").reset_index(drop=True)

current_energia = energia[
    (energia["anio"].isin(anio_sel))
].copy()

row1_1, row1_2 = st.columns([1.8, 1])
row2_1, = st.columns([1])

# Grafico de lineas: Comprada, cobrada, perdida y facturada en GWh
#--------------------------------------------------
with row1_1:
    st.subheader("Flujo Energético en GWh")
    if not current_serie.empty:
        fechas = current_serie["fecha"].dt.strftime("%b %Y").tolist()

        SERIES_ENERGIA = [
            ("comprada_GWh", "Comprada", COLORES["comprada"], "solid"),
            ("facturada_GWh", "Facturada", COLORES["facturada"], "solid"),
            ("cobrada_GWh", "Cobrada", COLORES["cobrada"], "solid"),
            ("perdida_GWh", "Pérdida", COLORES["perdida"], "dashed"),
            ]   

        series_flujo = []
        for col, nombre, color, dash in SERIES_ENERGIA:
            vals = [round(float(v), 2) for v in current_serie[col].tolist()]
            series_flujo.append({
                "name": nombre,
                "type": "line",
                "smooth": True,
                "symbol": "none",
                "lineStyle": {"color": color, "width": 2, "type": dash},
                "itemStyle": {"color": color},
                "areaStyle": {"opacity": 0.04} if dash == "solid" else None,
                "data": vals
                })

        flujo_opts = {
            "title": {
                "text": "Energía Comprada · Facturada · Cobrada · Pérdida",
                "left": "center", "top": 5,
                "textStyle": {"fontSize": 14, "fontWeight": "bold"}
                },
            "tooltip": {
                "trigger": "axis",
                "formatter": JsCode(
                    """
                    function(params) {
                        var html = '<strong>' + params[0].name + '</strong><br/>';
                        params.forEach(function(p) {
                            html += p.marker + ' ' + p.seriesName + ': ' + p.value.toFixed(2) + ' GWh<br/>';
                            });
                        return html;
                    }
                    """
                    )
                },
            "legend": {"data": ["Comprada", "Facturada", "Cobrada", "Pérdida"], "bottom": 0},
            "grid": {
                "left": "4%", "right": "5%",
                "bottom": "18%", "top": "15%",
                "containLabel": True
                },
            "xAxis": {
                "type": "category",
                "data": fechas,
                "axisLabel": {"rotate": 40, "fontSize": 9}
                },
            "yAxis": {
                "type": "value",
                "name": "GWh",
                "nameTextStyle": {"fontSize": 11},
                "axisLabel": {
                    "formatter": JsCode(
                        "function(v){return v.toLocaleString('es-MX');}"
                        )
                    },
                "splitLine": {"lineStyle": {"type": "dashed", "color": "#e8e8e8"}}
                },
            "dataZoom": [
                {"type": "inside", "start": 0, "end": 100},
                {"type": "slider", "start": 0, "end": 100, "height": 18, "bottom": 28}
                ],
            "series": series_flujo
            }
        
        st_echarts(options=flujo_opts, height="420px", key="flujo_energia")
        
    else:
        st.warning("No hay datos para mostrar con este filtro.")

# Grafico de Gauge: Nivel de perdida 
# ---------------------------------
with row1_2:
    st.subheader(f"Nivel de Pérdida en {str(int(current_serie['anio'].max())) if not current_serie.empty else '-'}", text_alignment="center")

    pct_actual = round(float(current_serie["perdida_pct"].iloc[-1]), 2) if len(current_serie) > 0 else 0
    pct_movil = round(float(current_serie["perdida_ano_movil_pct"].dropna().iloc[-1]), 2) \
                if current_serie["perdida_ano_movil_pct"].notna().any() else 0

    COLOR_GAUGE_BAJO = "#4CAF50"
    COLOR_GAUGE_MEDIO = "#FFC107"
    COLOR_GAUGE_ALTO = "#F44336"

    if pct_actual < 20:
        COLOR_AGUJA = COLOR_GAUGE_BAJO
    elif pct_actual < 35:
        COLOR_AGUJA = COLOR_GAUGE_MEDIO
    else:
        COLOR_AGUJA = COLOR_GAUGE_ALTO

    gauge_opts = {
        "title": {
            "text": f"% Pérdida Energética",
            "left": "center", "top": 5,
            "textStyle": {
                "fontSize": 14,
                "fontWeight": "bold",
                "fontFamily": "Work Sans"
            }
        },
        "tooltip": {
            "formatter": "{a}: {c}%",
            "textStyle": {"fontFamily": "Work Sans"}
        },
        "series": [
            {
                "name": "Pérdida actual",
                "type": "gauge",
                "radius": "80%",
                "startAngle": 200,
                "endAngle": -20,
                "min": 0,
                "max": 60,
                "splitNumber": 6,
                "axisLine": {
                    "lineStyle": {
                        "width": 18,
                        "color": [
                            [0.33, COLOR_GAUGE_BAJO],
                            [0.58, COLOR_GAUGE_MEDIO],
                            [1, COLOR_GAUGE_ALTO]
                        ]
                    }
                },
                "pointer": {
                    "length": "65%",
                    "width": 5,
                    "itemStyle": {"color": COLOR_AGUJA}
                },
                "axisTick": {
                    "length": 10,
                    "lineStyle": {"color": "#aaa", "width": 1.5}
                },
                "splitLine": {
                    "length": 16,
                    "lineStyle": {"color": "#666", "width": 2}
                },
                "axisLabel": {"fontWeight": "bold",
                    "fontSize": 14,
                    "fontFamily": "Work Sans",
                    "color": "#555"
                },
                "detail": {
                    "valueAnimation": True,
                    "formatter": "{value}%",
                    "fontSize": 24,
                    "fontWeight": "bold",
                    "fontFamily": "Work Sans",
                    "color": COLOR_AGUJA,
                    "offsetCenter": [0, "70%"]
                },
                "title": {
                    "offsetCenter": [0, "90%"],
                    "fontSize": 11,
                    "fontFamily": "Work Sans",
                    "color": "#888"
                },
                "data": [{"value": pct_actual, "name": "Pérdida actual"}]
            },
            {
                "name": "Móvil anual",
                "type": "gauge",
                "radius": "80%",
                "startAngle": 200,
                "endAngle": -20,
                "min": 0,
                "max": 60,
                "axisLine": {"show": False},
                "axisTick": {"show": False},
                "splitLine": {"show": False},
                "axisLabel": {"show": False},
                "pointer": {
                    "length": "50%",
                    "width": 3,
                    "itemStyle": {"color": "#2196F3"}
                },
                "detail": {
                    "formatter": f"Promedio Anual: {pct_movil}%",
                    "fontSize": 11,
                    "fontFamily": "Work Sans",
                    "fontWeight": "bold",
                    "color": "#2196F3",
                    "offsetCenter": [0, "110%"]
                },
                "data": [{"value": pct_movil, "name": "Promedio Anual"}]
            }
        ]
    }

    st_echarts(options=gauge_opts, height="380px", key="gauge_perdida")

    col_a, col_b = st.columns(2, border=True)
    col_a.metric("Pérdida actual", f"{pct_actual:.1f}%")
    col_b.metric("Promedio Anual", f"{pct_movil:.1f}%",
                 delta=f"{pct_actual - pct_movil:+.1f}%" if not current_serie.empty else None,
                 delta_color="inverse")
    
# Barras comparativas
# ----------------------------------------------
with row2_1:
    st.subheader("Brecha Energética: Entregada vs Facturada por Año")

    if not current_serie.empty:
        anual_df = current_serie.groupby('anio').agg({
            'energia entregada': 'sum',
            'facturada_GWh': 'sum'
        }).reset_index()

        anual_df = anual_df.sort_values('anio', ascending=True)
        
        years = anual_df['anio'].astype(int).tolist()
        vals_entregada = anual_df['energia entregada'].round(2).tolist()
        vals_facturada = anual_df['facturada_GWh'].round(2).tolist()
        vals_perdida = [round(e - f, 2) for e, f in zip(vals_entregada, vals_facturada)]
        
        vals_perdida_pct = [
            round((e - f) / e * 100, 1) if e > 0 else 0 
            for e, f in zip(vals_entregada, vals_facturada)
        ]
        
        barra_brecha_opts = {
            "title": {
                "text": "Brecha entre Energía Entregada y Facturada",
                "subtext": f"Pérdida total: {sum(vals_perdida):,.2f} GWh | Promedio: {sum(vals_perdida_pct)/len(vals_perdida_pct):.1f}%",
                "left": "center",
                "top": 5,
                "textStyle": {"fontSize": 14, "fontWeight": "bold"},
                "subtextStyle": {"fontSize": 10, "color": "#888"}
            },
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {"type": "shadow"},
                "formatter": JsCode(
                    """
                    function(params) {
                        var html = '<strong>' + params[0].name + '</strong><br/>';
                        var entregada = 0, facturada = 0;
                        params.forEach(function(p) {
                            html += p.marker + ' ' + p.seriesName + ': ' + p.value.toLocaleString('es-MX') + ' GWh<br/>';
                            if (p.seriesName === 'Entregada') entregada = p.value;
                            if (p.seriesName === 'Facturada') facturada = p.value;
                        });
                        var perdida = entregada - facturada;
                        var pct = (perdida / entregada * 100).toLocaleString('es-MX');
                        html += '<strong>Pérdida: ' + perdida.toLocaleString('es-MX') + ' GWh (' + pct + '%)</strong>';
                        return html;
                    }
                    """
                )
            },
            "legend": {
                "data": ["Entregada", "Facturada", "Pérdida"],
                "bottom": 0
            },
            "grid": {
                "left": "4%",
                "right": "4%",
                "bottom": "15%",
                "top": "18%",
                "containLabel": True
            },
            "xAxis": {
                "type": "category",
                "data": [str(y) for y in years],
                "axisLabel": {"fontSize": 12, "fontWeight": "bold"}
            },
            "yAxis": {
                "type": "value",
                "name": "GWh",
                "nameTextStyle": {"fontSize": 11},
                "axisLabel": {
                    "formatter": JsCode(
                        "function(v){return v.toLocaleString('es-MX');}"
                    )
                }
            },
            "series": [
                {
                    "name": "Entregada",
                    "type": "bar",
                    "data": vals_entregada,
                    "itemStyle": {"color": COLORES["entregada"], "borderRadius": [4, 4, 0, 0]},
                    "barMaxWidth": 40,
                    "label": {"show": False}
                },
                {
                    "name": "Facturada",
                    "type": "bar",
                    "data": vals_facturada,
                    "itemStyle": {"color": COLORES["facturada"], "borderRadius": [4, 4, 0, 0]},
                    "barMaxWidth": 40,
                    "label": {"show": False}
                },
                {
                    "name": "Pérdida",
                    "type": "bar",
                    "data": vals_perdida,
                    "itemStyle": {"color": COLORES["perdida"], "borderRadius": [4, 4, 0, 0]},
                    "barMaxWidth": 40,
                    "label": {
                        "show": True,
                        "position": "top",
                        "formatter": JsCode(
                            """
                            function(params) {
                                return params.value.toLocaleString('es-MX');
                            }
                            """
                        ),
                        "fontSize": 12,
                        "fontWeight": "bold",
                        "color": COLORES["perdida"]
                    }
                }
            ]  
        }
        
        st_echarts(
            options=barra_brecha_opts,
            height="400px",
            key="barras_brecha_anual"
        )
    else:
        st.warning("No hay datos para mostrar con este filtro.")