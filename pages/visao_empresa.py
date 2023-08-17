# ----------------------------------------
# Importação de bibliotecas
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import folium
from haversine import haversine
from datetime import datetime, date
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config( page_title='Visão Empresa', page_icon='📈', layout='wide')

# ----------------------------------------
# Funções
def clean_code(df1):
    """ Esta função tem a responsabilidade de limpar o dataframe
    
        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formataçã das colunas de datas
        5. Limpeza da coluna de tempo - remoção do texto da variável numérica
        
        Input: dataframe
        Output: dataframe
    """
    df1['ID'] = df1.loc[:,'ID'].str.strip()
    df1['Delivery_person_ID'] = df1.loc[:,'Delivery_person_ID'].str.strip()
    df1['Delivery_person_Age'] = df1.loc[:,'Delivery_person_Age'].str.strip()
    df1['Delivery_person_Ratings'] = df1.loc[:,'Delivery_person_Ratings'].str.strip()
    df1['multiple_deliveries'] = df1.loc[:,'multiple_deliveries'].str.strip()
    df1['Type_of_order'] = df1.loc[:,'Type_of_order'].str.strip()
    df1['Type_of_vehicle'] = df1.loc[:,'Type_of_vehicle'].str.strip()
    df1['City'] = df1.loc[:,'City'].str.strip()
    df1['Festival'] = df1.loc[:,'Festival'].str.strip()
    df1['Road_traffic_density'] = df1.loc[:,'Road_traffic_density'].str.strip()

    df1 = df1.loc[df1['Road_traffic_density'] != 'NaN']

    df1 = df1.loc[df1['Delivery_person_Age'] != 'NaN']
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype('int64')

    df1 = df1.loc[df1['Delivery_person_Ratings'] != 'NaN']
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype('float64')

    df1 = df1.loc[df1['City'] != 'NaN']
    df1['City'] = df1['City'].astype(str)

    df1 = df1.loc[df1['Festival'] != 'NaN']
    df1['Festival'] = df1['Festival'].astype(str)

    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

    df1 = df1.loc[df1['multiple_deliveries'] != 'NaN']
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype('int64')

    df1 = df1.reset_index(drop=True)

    df1['Time_taken(min)'] =  df1['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1]).astype(int)

    return df1

def order_metric(df1):
    df_1 = df1.loc[:,['ID','Order_Date']].groupby('Order_Date').count().reset_index()
    graph1 = px.bar(df_1, x='Order_Date', y='ID')

    return graph1

def traffic_order_share(df1):
    
    df_3 = df1.loc[:,['ID','Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    df_3 = df_3.loc[df_3['Road_traffic_density'] != 'NaN',:]
    df_3[ 'entrega_erc'] = df_3['ID'] / df_3[ 'ID'].sum()
    graph2 = px.pie( df_3, values='entrega_erc', names='Road_traffic_density')

    return graph2

def traffic_order_city(df1):
    
    df_4 = df1.loc[:,['ID','City','Road_traffic_density']].groupby(['City','Road_traffic_density']).count().reset_index()
    df_4 = df_4.loc[df_4['City'] != 'NaN',:]
    df_4 = df_4.loc[df_4['Road_traffic_density'] != 'NaN',:]
    graph3 = px.scatter(df_4,x='City',y='Road_traffic_density',size='ID', color='City')
    
    return graph3

def order_by_week(df1):
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    df_2 = df1.loc[:,['ID','week_of_year']].groupby('week_of_year').count().reset_index()
    graph4 = px.line( df_2, x='week_of_year',y='ID')

    return graph4

def order_share_by_week(df1):
    df_51 = df1.loc[:,['ID','week_of_year']].groupby('week_of_year').count().reset_index()
    df_52 = df1.loc[:,['Delivery_person_ID','week_of_year']].groupby('week_of_year').nunique().reset_index()

    df_5 = pd.merge(df_51, df_52, how='inner')
    df_5['order_by_deliver'] = df_5['ID'] / df_5['Delivery_person_ID']

    graph5 = px.line(df_5,x='week_of_year',y='order_by_deliver')

    return graph5

def country_maps(df1):
    cols = ['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']
    df_6 = df1.loc[:,cols].groupby( ['City','Road_traffic_density'] ).median().reset_index()
    map = folium.Map()
    for index, location in df_6.iterrows():
        folium.Marker( [location['Delivery_location_latitude'],location['Delivery_location_longitude']],
                      popup = location[['City','Road_traffic_density']]).add_to(map)
    folium_static( map, width=1024, height=600)

    return None

# --------------------------------- Início da estrutura lógica do código ---------------------------
# ----------------------------------------
# Importação do dataset
# ----------------------------------------
df = pd.read_csv('../dataset/train.csv')

# ----------------------------------------
# Limpeza dos dados
# ----------------------------------------
df1 = clean_code(df)

# ---------- Visão Empresa ---------------

# ----------------------------------------
# Sidebar
# ----------------------------------------

#image_path = 'C:/Users/Phelipe Pachler/Documents/REPOS/ftc_python_analise_dados/notebooks/logo.png'

image = Image.open('logo.png')
st.sidebar.image(image, width=300)

st.sidebar.markdown('# Pachler Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown('---')
st.sidebar.markdown('## Selecione uma data limite')

min_date = df1['Order_Date'].min().date()
max_date = df1['Order_Date'].max().date()

date_slider = st.sidebar.slider(
    'Até qual data?', value=date(2022,4,13),
    min_value=min_date,
    max_value=max_date,
    format='DD/MM/YYYY')

st.sidebar.markdown('---')

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito?',
    list(df1['Road_traffic_density'].unique()),
    default=list(df1['Road_traffic_density'].unique()))

st.sidebar.markdown('---')
st.sidebar.markdown('### Powered by Comunidade DS')

# filtro de data
linhas_selecionadas = df1['Order_Date'].apply(lambda x: x.date()) < date_slider

df1 = df1.loc[linhas_selecionadas,:]

# filtro de trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas,:]

# ----------------------------------------
# Layout Dashboard
# ----------------------------------------

st.header('Marketplace - Visão Cliente')

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica' ])

with tab1:
    with st.container():
        graph1 = order_metric(df1)
        st.markdown('# Orders by Day')
        st.plotly_chart(graph1, use_container_width=True)
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            graph2 = traffic_order_share(df1)
            st.markdown('## Traffic Order Share')
            st.plotly_chart(graph2, use_container_width=True)        

        with col2:
            graph3 = traffic_order_city(df1)
            st.markdown('## Traffic Order City')
            st.plotly_chart(graph3, use_container_width=True)
        
with tab2:
    with st.container():
        graph4 = order_by_week(df1)
        st.markdown('## Order By Week')
        st.plotly_chart(graph4, use_container_width=True)
        
    with st.container():
        graph5 = order_share_by_week(df1)
        st.markdown('## Order Share By Week')
        st.plotly_chart(graph5, use_container_width=True)            
        
with tab3:
    st.markdown('# Country Maps')
    country_maps(df1)
    
