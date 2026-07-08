#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 20:55:15 2026

@author: kaibo
"""

COLORES = {
    # --- Energía ---
    "comprada": "#1f77b4",          # Azul
    "facturada": "#2ca02c",         # Verde
    "cobrada": "#ff7f0e",           # Naranja
    "perdida": "#d62728",           # Rojo
    "entregada": "#17becf",         # Turquesa
    
    # --- Bajas ---
    "bajas": "#8c564b",             # Marrón
    "forzada": "#e6550d",           # Naranja oscuro
    "voluntaria": "#fdae6b",        # Naranja claro
    
    # --- Tipos de Avería (TODOS ÚNICOS) ---
    "alumbrado_publico": "#9467bd",          # Púrpura
    "falta_energia": "#1f77b4",              # Azul (igual que comprada, pero comparten contexto energético)
    "niveles_tension": "#2ca02c",            # Verde (igual que facturada)
    "otros": "#7f7f7f",                      # Gris
    "defecto_falla": "#ff7f0e",              # Naranja (igual que cobrada)
    "riesgo_vida": "#b2182b",                # Rojo oscuro (DIFERENTE a perdida)
    "sin_identificar": "#c49c94",            # Marrón claro (DIFERENTE a bajas)
    
    # --- General (TODOS ÚNICOS) ---
    "meta": "#7f7f7f",                       # Gris
    "tecnica": "#1f77b4",                    # Azul
    "red": "#2ca02c",                        # Verde
    "equipo": "#ff7f0e",                     # Naranja
    "externa": "#9467bd",                    # Púrpura
    "emergencia": "#b2182b",                 # Rojo oscuro (DIFERENTE)
    "morosidad": "#e6550d",                  # Naranja oscuro
    "cancelacion": "#fdae6b",                # Naranja claro
    "reconexion": "#2ca02c",                 # Verde
    "proceso": "#ffd700",                    # Amarillo
    "otro": "#c49c94"                        # Marrón claro
}

# --- Mapeo de tipos de avería a colores (para usar en gráficos) ---
COLORES_TIPOS_AVERIA = {
    "Alumbrado Público": COLORES["alumbrado_publico"],      # #9467bd - Púrpura
    "Falta de Energía": COLORES["falta_energia"],           # #1f77b4 - Azul
    "Niveles de Tensión": COLORES["niveles_tension"],       # #2ca02c - Verde
    "Otros": COLORES["otros"],                              # #7f7f7f - Gris
    "Probable Defecto o Falla": COLORES["defecto_falla"],   # #ff7f0e - Naranja
    "Riesgo de Vida": COLORES["riesgo_vida"],               # #d62728 - Rojo
    "Sin Identificar": COLORES["sin_identificar"],          # #c49c94 - Marrón claro
}