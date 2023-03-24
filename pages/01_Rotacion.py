import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from pandas.io.json import json_normalize

ventas_mkp = pd.read_csv('https://raw.githubusercontent.com/jamesllamo/Sharwinn_dashboard/main/ventas_mkp.csv')
productos = pd.read_csv('https://raw.githubusercontent.com/jamesllamo/Sharwinn_dashboard/main/productos.csv')

# CAMBIOS A VENTAS MKP
# Cambio de variables fecha
ventas_mkp['date_created'] = pd.to_datetime(ventas_mkp['date_created'])
# Cambio de variables INT
ventas_mkp['id_order'] = ventas_mkp['id_order'].astype(int)
ventas_mkp['product_id'] = ventas_mkp['product_id'].astype(int)
ventas_mkp['variation_id'] = ventas_mkp['variation_id'].astype(int)
ventas_mkp['quantity'] = ventas_mkp['quantity'].astype(int)
# Cambio de variables FLOAT
ventas_mkp['subtotal'] = ventas_mkp['subtotal'].astype(float)
ventas_mkp['subtotal_tax'] = ventas_mkp['subtotal_tax'].astype(float)
ventas_mkp['price'] = ventas_mkp['price'].astype(float)
# Cambio de variables STRING
ventas_mkp['status'] = ventas_mkp['status'].astype(str)
ventas_mkp['status'] = ventas_mkp['status'].astype(str)
ventas_mkp['name'] = ventas_mkp['name'].astype(str)
ventas_mkp['register_name'] = ventas_mkp['register_name'].astype(str)

# CAMBIOS A PRODUCTOS
# Convertir la columna date_created en un objeto datetime
productos['date_created'] = pd.to_datetime(productos['date_created'])

# Cambio de variables INT
productos['product_id'] = productos['product_id'].fillna(0).astype(int)
#productos['stock_quantity'] = productos['stock_quantity'].fillna(0).astype(int)
#productos['total_sales'] = productos['total_sales'].fillna(0).astype(int)

# Cambio de variables FLOAT
productos['price'] = productos['price'].replace('', 0.0).fillna(0.0).astype(float)
#productos['regular_price'] = productos['regular_price'].replace('','nan').fillna(productos['price']).astype(float)

# Cambio de variables STR
productos['name'] = productos['name'].fillna('').astype(str)
#productos['type'] = productos['type'].fillna('').astype(str)
productos['status'] = productos['status'].fillna('').astype(str)
#productos['sku'] = productos['sku'].fillna('').astype(str)

#____________________________________________________________________________________________
# PRIMERA VENTA
########################################
# Primera venta desde su lanzamiento
primer_venta=ventas_mkp.copy()
creacion_productos=productos.copy()
# Se agrupa por id_producto y se aplica la función de agregación min() a la columna venta
fecha_primera_venta= primer_venta.groupby('product_id')['date_created'].agg(min).reset_index(name='Fecha_Primera_Venta')
fecha_Creacion= creacion_productos.groupby('product_id')['date_created'].agg(min).reset_index(name='Fecha_Creacion_producto')
# Unir los dataframe resultantes
primer_venta_fechas=pd.merge(fecha_primera_venta, fecha_Creacion, on='product_id')

# Calculamos la diferencias de días
primer_venta_fechas['diferencia_en_dias'] = (primer_venta_fechas['Fecha_Primera_Venta'] - primer_venta_fechas['Fecha_Creacion_producto']).dt.days
primer_venta_fechas_sorted=primer_venta_fechas.sort_values('diferencia_en_dias', ascending=True)
# Agregamos el Nombre del producto
primer_venta_fechas_nombre = primer_venta.loc[:, ['product_id', 'name']]
df_sin_duplicados = primer_venta_fechas_nombre.drop_duplicates(subset=['product_id'])
# Juntamos el dataframe
primer_venta_completo=pd.merge(primer_venta_fechas_sorted, df_sin_duplicados, on='product_id')

# Generación de DataFrame "Lista Completa" Por Días
rotacion_primera_venta = primer_venta_completo.loc[:, ['product_id', 'name', 'Fecha_Creacion_producto', 'diferencia_en_dias']]

st.title('ROTACIÓN')
st.markdown('## PRIMERA COMPRA')
st.subheader('Tiempo en Días transccurridos desde la primera compra')

st.markdown('***')
diferencia_en_dias_rango=st.slider('Definir el Max de Días',0,100,5)
if st.checkbox('Montrar Tabla Completa'):
    st.dataframe(rotacion_primera_venta.loc[rotacion_primera_venta['diferencia_en_dias'] <=diferencia_en_dias_rango])
st.markdown('***')

########################################
# Generación de DataFrame "Lista Completa" Por Fecha
Fecha_Creacion_producto_rango='2023-03-01'
rotacion_primera_venta = primer_venta_completo.loc[:, ['product_id', 'name', 'Fecha_Creacion_producto', 'diferencia_en_dias']]


st.subheader('Tiempo transccurrido (anterior) desde una fecha')

Fecha_Creacion_producto_rango = st.text_input('Ingresa una fecha similar al ejemplo: 2023-03-01')
if Fecha_Creacion_producto_rango=='':
    print('')
else:
    st.dataframe(rotacion_primera_venta.loc[rotacion_primera_venta['Fecha_Creacion_producto'] >=Fecha_Creacion_producto_rango])
st.markdown('***')

########################################
# Graficar por Precio de venta
venta_promedio_id = ventas_mkp.groupby('product_id')['price'].mean().reset_index(name='precio_promedio')
venta_promedio=pd.merge(rotacion_primera_venta, venta_promedio_id, on='product_id')
venta_promedio_precio = venta_promedio.loc[:, ['product_id', 'diferencia_en_dias','precio_promedio']]

st.subheader('Cantidad de ordenes rango de precio')
st.markdown('***')
# Crear gráfico de dispersión
dias_limite = st.number_input('Insert un número de diferencia de días')
if dias_limite==0.00:
    st.write('Ingresa un valor distinto de ', dias_limite)
else:
    fig=plt.figure()
    sns.histplot(data=venta_promedio_precio[venta_promedio_precio['diferencia_en_dias']<dias_limite], x="precio_promedio", color='red', bins=30, kde=True, linewidth=0)
    plt.xlabel('Precio Promedio')
    plt.ylabel('Frecuencia de cantidad de órdenes')
    plt.title('Cantidad de ordenes x Precio')
    st.pyplot(fig)

st.markdown('***')
########################################

st.subheader('Cantidad de ordenes rango de Días')

precio_limite = st.number_input('Inserta un número de días')
if precio_limite==0.00:
    st.write('Ingresa un valor distinto de ', precio_limite)
else:
    st.write('El número ingresado es ', precio_limite)
    fig=plt.figure()
    sns.histplot(data=venta_promedio_precio[venta_promedio_precio['precio_promedio']<precio_limite], x="diferencia_en_dias", color='red', bins=30, kde=True, linewidth=0)
    plt.xlabel('Diferencia en Día')
    plt.ylabel('Frecuencia de cantidad de órdenes')
    plt.title('Cantidad de ordenes x Días de la Primera')
    st.pyplot(fig)

st.markdown('***')
########################################
#Generar Dataframe con la información importante
flujo_semanal=ventas_mkp.copy()
df_semanal = flujo_semanal.loc[:, ['id_order','date_created', 'quantity', 'price', 'subtotal']]
df_semanal['nombre_dia_semana'] = df_semanal['date_created'].dt.day_name()
df_semanal['numero_mes'] = df_semanal['date_created'].dt.month
df_semanal['numero_ano'] = df_semanal['date_created'].dt.year

# PARETO POR CANTIDAD
# Filtrar por cantidad
st.markdown('## HISTOGRAMAS')
filtro_mes_IS = st.selectbox(
    'Seleciona el Mes',
    (1,2,3,4,5,6,7,8,9,10,11,12))
st.write('Selecionaste:', filtro_mes_IS)

filtro_ano_IS = st.selectbox(
    'Seleciona el Mes',
    (2020,2021,2022,2023,2024,2025))
st.write('Selecionaste:', filtro_ano_IS)


# Agrupar los datos por día de la semana y sumar las ventas
df_semanal_mes_filtrado = df_semanal[(df_semanal['numero_mes'] ==filtro_mes_IS) & (df_semanal['numero_ano'] == filtro_ano_IS)]
ventas_por_dia = df_semanal_mes_filtrado.groupby('nombre_dia_semana')['quantity'].sum().reset_index(name='cantidad_productos_dia_semana')

# Ordenar los datos por frecuencia
ventas_por_dia = ventas_por_dia.sort_values('cantidad_productos_dia_semana', ascending=False)

# Calcular la frecuencia acumulada y el porcentaje acumulado
ventas_por_dia['Frecuencia_acumulada'] = ventas_por_dia['cantidad_productos_dia_semana'].cumsum()
ventas_por_dia['Porcentaje_acumulado'] = 100 * ventas_por_dia['Frecuencia_acumulada'] / ventas_por_dia['cantidad_productos_dia_semana'].sum()

# Crear el gráfico de barras
fig, ax = plt.subplots()
ax.bar(ventas_por_dia['nombre_dia_semana'], ventas_por_dia['cantidad_productos_dia_semana'], color='green')

# Agregar la línea de porcentaje acumulado
ax2 = ax.twinx()
ax2.plot(ventas_por_dia['nombre_dia_semana'], ventas_por_dia['Porcentaje_acumulado'], color='red', marker='o')
ax2.grid(False)

# Personalizar el gráfico
ax.set_xlabel('Día de la semana')
ax.set_ylabel('Frecuencia de pedidos')
ax2.set_ylabel('Porcentaje acumulado')
ax.tick_params(axis='x', rotation=90)
plt.title('Cantidad pedidos por día de la semana')
st.pyplot(fig)

st.markdown('***')
########################################
# PARETO POR MONTOS
# Filtrar por Ventas

filtro_mes_ISV = st.selectbox(
    'Seleciona el Mes de la venta',
    (1,2,3,4,5,6,7,8,9,10,11,12))
st.write('Selecionaste el mes de:', filtro_mes_IS)

filtro_ano_ISV = st.selectbox(
    'Seleciona el Mes de la venta',
    (2020,2021,2022,2023,2024,2025))
st.write('Selecionaste el año :', filtro_ano_IS)

# Agrupar los datos por día de la semana y sumar las ventas
df_semanal_mes_filtrado = df_semanal[(df_semanal['numero_mes'] == filtro_mes_ISV) & (df_semanal['numero_ano'] == filtro_ano_ISV)]
ventas_por_dia = df_semanal_mes_filtrado.groupby('nombre_dia_semana')['subtotal'].sum().reset_index(name='venta_dia_semana')

# Ordenar los datos por frecuencia
ventas_por_dia = ventas_por_dia.sort_values('venta_dia_semana', ascending=False)

# Calcular la frecuencia acumulada y el porcentaje acumulado
ventas_por_dia['Frecuencia_acumulada'] = ventas_por_dia['venta_dia_semana'].cumsum()
ventas_por_dia['Porcentaje_acumulado'] = 100 * ventas_por_dia['Frecuencia_acumulada'] / ventas_por_dia['venta_dia_semana'].sum()

# Crear el gráfico de barras
fig, ax = plt.subplots()
ax.bar(ventas_por_dia['nombre_dia_semana'], ventas_por_dia['venta_dia_semana'], color='green')

# Agregar la línea de porcentaje acumulado
ax2 = ax.twinx()
ax2.plot(ventas_por_dia['nombre_dia_semana'], ventas_por_dia['Porcentaje_acumulado'], color='red', marker='o')
ax2.grid(False)

# Personalizar el gráfico
ax.set_xlabel('Día de la semana')
ax.set_ylabel('Frecuencia de Montos')
ax2.set_ylabel('Porcentaje acumulado')
ax.tick_params(axis='x', rotation=90)
plt.title('Ventas por día de la semana')
st.pyplot(fig)

st.markdown('***')
st.markdown('## PARETO')
########################################
# PRODUCTOS POPULARES
# Copiar
ventas_populares=ventas_mkp.copy()
productos_populares=productos.copy()
# Extraer data
ventas = ventas_populares.groupby('product_id')['quantity'].sum().reset_index(name='cantidad_total')    # Extraemos la cantidad total de ventas
nombres = productos_populares.loc[:, ['product_id','name']]                                             # Extraer nombres
valores_populares=pd.merge(ventas, nombres, on='product_id')                                            # Unimos
populares = valores_populares.sort_values(by='cantidad_total', ascending=False)                         # Ordenar
df_populares = populares.loc[:, ['name','cantidad_total']]                                              # Seleccionamos columnas

filtro_populares_cantidad=st.slider('Cantidad de Productos a mostrar',0,60,10)
if st.checkbox('Montrar Lista completa'):
    st.dataframe(df_populares.head(filtro_populares_cantidad))

st.markdown('***')