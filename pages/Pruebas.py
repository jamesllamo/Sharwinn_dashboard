import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from pandas.io.json import json_normalize
# HABILITAR REPO
from git import Repo
from github import Github
import os

# EXTRACCION DE VENTAS
#____________________________________________________________________________________________
# Obtener credenciales desde las variables de entorno
consumer_key = os.environ.get('consumer_key')
consumer_secret = os.environ.get('consumer_secret')
url = 'https://www.sharwinn.com/wp-json/wc/v3/orders'                   # url
params = {
    'consumer_key': consumer_key,      # CK
    'consumer_secret': consumer_secret,   # CS
    'per_page': 100,                                                    # número de pedidos por página
    'meta_data': ['_yith_pos_cashier', '[P] _alg_wc_cog_cost']     # Metadata
}
orders = []                                                             # lista para almacenar los pedidos
response = requests.get(url, params=params)                             # Consulta para extraer el número de páginas
npages_o=round(int(response.headers['X-WP-Total'])/100)+1                 # Conseguimos el número de Páginas
npages_oc=response.headers['X-WP-Total']
for page in range(1, npages_o):                                           # Ciclo For para extraer la data
    params['page'] = page
    response = requests.get(url, params=params)
    orders += response.json()

df_agrupada = pd.DataFrame(orders)                                               # Convertimos en DataFrame
