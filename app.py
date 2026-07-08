#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  5 08:27:47 2026

@author: jerson-lebron
"""

import streamlit as st 
from pathlib import Path

# Configuacion de la app (Streamlit)
# -----------------------------------------------------------
st.set_page_config(
    page_title="EDEESTE Dashboard",
    layout="wide",
)

# Barra de navegacion
# ------------------------------------------------------------
pg = st.navigation([
    st.Page("pages/resumen.py",
            title=":material/browse: Resumen Ejecutivo",
            default=True),
    st.Page("pages/inteligencia_geo.py",
            title=" :material/map: Inteligencia Geográfica"),
    st.Page("pages/energia.py",
            title=":material/bolt: Flujo y Eficiencia Energética")
    ]
    )

pg.run()

# Pie de pagina 
# ----------------------------------------------------------
st.header("", divider="gray")

st.markdown("""
    <style>
    .footer-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 20px;
    }
    .footer-text {
        text-align: center;
        flex: 1;
    }
    .footer-text strong {
        color: #1a5276;
    }
    .footer-text small {
        color: #666;
    }
    .footer-logo {
        opacity: 0.8;
        transition: opacity 0.3s;
    }
    .footer-logo:hover {
        opacity: 1;
    }
    </style>
    """, unsafe_allow_html=True)
    
st.markdown("""
               <div class="footer-text">
               <strong>Fuente de datos:</strong><br>
               Este dashboard se realizó con datos extraídos de los datos abiertos proporcionados en:
               <a href="https://datos.gob.do/organization/empresa-distribuidora-de-electricidad-del-este-edeeste" target="_blank">Datos.gob.do</a>
               y
               <a href="https://mem.gob.do/category/sector-electrico/informe-de-desempeno/2026-informe-de-desempeno/" target="_blank">MEM - Informes de Desempeño</a><br>
               <small>EDEEste (Direcciones Técnica Operativa, Comercial y de Regulación) vía Datos.gob.do · Ministerio de Energía y Minas</small>
               </div>
               """, unsafe_allow_html=True)
        
col_1, col_2, col_3, col_4, col_5, col_6 = st.columns(6)

with col_1:
    st.write(" ")

with col_3:
    st.image(
        Path("assets/logos/edeeste.png"),
        use_container_width=None,
        output_format="PNG",
        link="https://edeeste.com.do/"
        )
    
with col_4:
    st.image(
        Path("assets/logos/mem_logo.png"),
        use_container_width=None,
        link="https://mem.gob.do/"
        )

with col_6:
    st.write(" ")
                
             
                

                

    

