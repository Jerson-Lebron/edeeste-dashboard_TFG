#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  5 07:59:00 2026

@author: jerson-lebron
"""
import pandas as pd 
import streamlit as st
import json

@st.cache_data
def load_data() -> dict[str, pd.DataFrame]:
    """
    Carga los dataset desde los archivos .csv resultantes de la asignacion S6 y 
    retorna un diccionario de DataFrames
    
    Returns
    ---------
    dict[str, pd.Dataframe] 
            Diccionario con todos los datos preparados
    """
    
    datos_averias = pd.read_csv("data/datos_averias.csv")
    datos_bajas = pd.read_csv("data/datos_bajas_servicio.csv")
    datos_energia = pd.read_csv("data/datos_energia_entregada.csv")
    serie_edeeste = pd.read_csv("data/serie_edeeste.csv")
    geo_unificado = pd.read_csv("data/geo_unificado.csv")
    
    return {"averias": datos_averias,
            "bajas": datos_bajas,
            "energia": datos_energia,
            "serie_edeeste": serie_edeeste,
            "geo" : geo_unificado}

@st.cache_data
def load_geojson() -> [dict, None]:
    """
    Carga el archivo GeoJSON de las provincias de RD
    
    Returns
    ---------
    dict 
        Un diccionario con los datos del GeoJSON
    """
    ruta = "data/rd_provincias.geojson"
    
    with open(ruta, "r", encoding="utf-8") as f:
        geojson = json.load(f)
            
        return geojson
    return None


def transform_data_map(datos: pd.DataFrame, columna : str ="averias" ) -> dict:
    """
    Transforma los datos de un DataFrame para que pasarlo al mapa de coropletas

    Parameters
    ----------
    datos : pd.DataFrame
        DataFrame que almacena los datos
    columna :  str, optional
        La columna con los datos a mostrar

    Returns
    -------
    dict
        Un diccionario con los datos ya adaptados a lo requerido por el grafico
        de mapa de Streamlit-Echarts
    """
    mapa_datos = datos.groupby("provincia")[columna].sum().reset_index()

    mapa_datos["provincia"] = mapa_datos["provincia"].str.strip()
    mapa_datos["provincia"] = mapa_datos["provincia"].apply(lambda x: f"Provincia {x}" if x != "Distrito Nacional" else x)

    mapa_datos = mapa_datos.rename(columns={"provincia": "name", columna: "value"})
    mapa_datos["value"] = mapa_datos["value"].astype(float)

    return mapa_datos[["name", "value"]].to_dict("records")



