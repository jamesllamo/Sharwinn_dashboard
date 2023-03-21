#.\sw_env\Scripts\activate
#streamlit run .\Sharwinn_intro.py
#pip freeze > requirements.txt
# git add .
# git commit -m "Mensaje de confirmación"
# git push origin main


import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from pandas.io.json import json_normalize


st.image('https://www.sharwinn.com/wp-content/uploads/2022/05/Logo-Editable-Sharwin-700x300-1.jpg')
st.title('DashBoard Sharwinn')
st.markdown('***')

st.sidebar.markdown('## ¿Qué son los Gráficos?')
st.markdown('''
Cada gráfico hace referencia a un determinado comportamiento de las variables. 
La información presentada se actualiza en tiempo real.
''')

st.write('## Info Complementaria')
st.markdown('[Ver más de Sharwinn](https://www.sharwinn.com/)')

if st.button('Actualizar Base de datos'):

    # HABILITAR REPO
    from git import Repo
    from github import Github
    # Autenticar con el token de acceso personal
    g = Github("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")
    # Obtener la referencia al repositorio
    repo = g.get_repo("jamesllamo/Sharwinn_dashboard")
    
    # EXTRACCION DE VENTAS
    #____________________________________________________________________________________________
    url = 'https://www.sharwinn.com/wp-json/wc/v3/orders'                   # url
    params = {
        'consumer_key': 'ck_e88ed88e0a1684cd729a37dee41c2a3cb503b0ec',      # CK
        'consumer_secret': 'cs_0cc67c5057e588a91ba99b38271729baeb83dc56',   # CS
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

    df_expanded = df_agrupada.explode('line_items')
    df_expanded = pd.concat([df_expanded.drop(['line_items'], axis=1), df_expanded['line_items'].apply(pd.Series)], axis=1)

    # Expande los datos de la columna 'yith_pos_data' utilizando json_normalize
    df_normalized = json_normalize(df_expanded['yith_pos_data'])
    # Concatenar
    df_expanded1=df_expanded.copy()
    df_normalized1=df_normalized.copy()
    df_expanded1 = df_expanded1.reset_index()
    df_normalized1 = df_normalized1.reset_index()
    df_combined = pd.concat([df_expanded1, df_normalized1], axis=1)

    # Selección de Columnas útiles
    ventas = df_combined.loc[:, ['id', 'status', 'date_created','payment_method_title',
                                'name', 'product_id', 'variation_id', 'quantity',
                                'subtotal', 'subtotal_tax', 'price', 'register_name']]
    # Elimina columna redundante en el nombre
    ventas.columns.values[0] = 'id_order'
    ventas = ventas.drop(ventas.columns[1], axis=1)

    # Cambio de tipo de datos en las columnas
    ventas['date_created'] = pd.to_datetime(ventas['date_created'])
    # Formatear la columna date_created en YYYY-MM-DD
    ventas['date_created'] = ventas['date_created'].apply(lambda x: datetime.strftime(x, '%Y-%m-%d'))
    ventas['date_created'] = pd.to_datetime(ventas['date_created'])

    # Cambio de variables INT
    ventas['id_order'] = ventas['id_order'].astype(int)
    ventas['product_id'] = ventas['product_id'].astype(int)
    ventas['variation_id'] = ventas['variation_id'].astype(int)
    ventas['quantity'] = ventas['quantity'].astype(int)
    # Cambio de variables FLOAT
    ventas['subtotal'] = ventas['subtotal'].astype(float)
    ventas['subtotal_tax'] = ventas['subtotal_tax'].astype(float)
    ventas['price'] = ventas['price'].astype(float)
    # Cambio de variables STRING
    ventas['status'] = ventas['status'].astype(str)
    ventas['status'] = ventas['status'].astype(str)
    ventas['name'] = ventas['name'].astype(str)
    ventas['register_name'] = ventas['register_name'].astype(str)

    # Levantamiento de ventas
    ventas_mkp = ventas[ventas['register_name'].str.contains('Caja 2')]
    # Generamos la cadena de texto
    ventas_mkp_string = ventas_mkp.to_csv(index=False)
    # Crear un archivo en el repositorio
    contents = repo.create_file("ventas_mkp.csv", "ventas_mkp_string", ventas_mkp_string)


    # EXTRACCION DE PRODUCTOS
    #____________________________________________________________________________________________
    # Importación de Productos
    url = 'https://www.sharwinn.com/wp-json/wc/v3/products'                 # url
    params = {
        'consumer_key': 'ck_e88ed88e0a1684cd729a37dee41c2a3cb503b0ec',      # CK
        'consumer_secret': 'cs_0cc67c5057e588a91ba99b38271729baeb83dc56',   # CS
        'per_page': 100,                                                    # número de pedidos por página
    }
    products = []                                                             # lista para almacenar los pedidos
    response = requests.get(url, params=params)                             # Consulta para extraer el número de páginas
    npages_p=round(int(response.headers['X-WP-Total'])/100)+2                 # Conseguimos el número de Páginas
    npages_pc=response.headers['X-WP-Total']
    for page in range(1, npages_p):                                           # Ciclo For para extraer la data
        params['page'] = page
        response = requests.get(url, params=params)
        products += response.json()

    p_agrupada = pd.DataFrame(products)                                     # Convertimos en DataFrame

    products=p_agrupada.copy()

    # Selección de productos a Trabajar para Productos
    products.rename(columns={'id': 'product_id'}, inplace=True)
    productos = products.loc[:, ['product_id', 'name', 'date_created', 'type',
                                'status', 'sku', 'price', 'regular_price','total_sales',
                                'stock_quantity','categories']]

    # Convertir la columna date_created en un objeto datetime
    productos['date_created'] = pd.to_datetime(productos['date_created'])
    # Formatear la columna date_created en YYYY-MM-DD
    productos['date_created'] = productos['date_created'].apply(lambda x: datetime.strftime(x, '%Y-%m-%d'))
    # Convertir la columna date_created en un objeto datetime
    productos['date_created'] = pd.to_datetime(productos['date_created'])

    # Cambio de variables INT
    productos['product_id'] = productos['product_id'].fillna(0).astype(int)
    productos['stock_quantity'] = productos['stock_quantity'].fillna(0).astype(int)
    productos['total_sales'] = productos['total_sales'].fillna(0).astype(int)

    # Cambio de variables FLOAT
    productos['price'] = productos['price'].replace('', 0.0).fillna(0.0).astype(float)
    productos['regular_price'] = productos['regular_price'].replace('','nan').fillna(productos['price']).astype(float)

    # Cambio de variables STR
    productos['name'] = productos['name'].fillna('').astype(str)
    productos['type'] = productos['type'].fillna('').astype(str)
    productos['status'] = productos['status'].fillna('').astype(str)
    productos['sku'] = productos['sku'].fillna('').astype(str)

    # Generamos la cadena de texto
    productos_string = ventas_mkp.to_csv(index=False)
    # Crear un archivo en el repositorio
    contents = repo.create_file("productos.csv", "productos_string", productos_string)

    st.write('Base de datos Actualizada')
    st.write('Órdenes: ',npages_oc)
    st.write('Productos: ', npages_pc)
else:
    st.write('Este proceso tardará 5 a 10 minutos')