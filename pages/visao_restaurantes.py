# ----------------------------------------
# Importação de bibliotecas
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import numpy as np
from haversine import haversine
from datetime import datetime, date
from PIL import Image

st.set_page_config( page_title='Visão Restaurantes', page_icon='👩‍🍳', layout='wide')

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

def mean_distance(df1):

    cols = ['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']
    df1['distance'] = df1.loc[:,cols].apply(lambda x: 
                                            haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                      (x['Delivery_location_latitude'], x['Delivery_location_longitude']))
                                            , axis=1)
    distance = np.round(df1['distance'].mean(),2)

    return distance

def avg_std_festivais(df1,parametro,festival):

    cols = ['Time_taken(min)','Festival']
    df_6 = df1.loc[:,cols].groupby('Festival').agg({'Time_taken(min)':['mean','std']})
    df_6.columns = ['avg_time','std_time']
    df_6 = df_6.reset_index()
    df_6 = df_6.loc[df_6['Festival'] == festival,:]
    avg_time = np.round(df_6['avg_time'],2)
    std_time = np.round(df_6['std_time'],2)

    if parametro == 'std':
        return std_time
    elif parametro == 'avg':
        return avg_time
    
def tempo_cidade_media(df1):
    cols = ['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']
    df1['distance'] = df1.loc[:,cols].apply(lambda x: haversine((x['Restaurant_latitude'],x['Restaurant_longitude']),
                                                        (x['Delivery_location_latitude'],x['Delivery_location_longitude'])),axis=1)
    df1['distance'].mean()
    avg_distance = df1.loc[:,['City','distance']].groupby('City').mean().reset_index()
    fig = go.Figure( data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0,0.15,0])])

    return fig

def tempo_cidade_desvio(df1):
    cols = ['City','Time_taken(min)']
    df_3 = df1.loc[:,cols].groupby('City').agg({'Time_taken(min)':['mean','std']})
    df_3.columns = ['avg_time','std_time']
    df_3 = df_3.reset_index()

    fig = go.Figure()
    fig.add_trace( go.Bar( name='Control',x=df_3['City'],y=df_3['avg_time'],error_y=dict( type='data', array=df_3['std_time'])))
    fig.update_layout(barmode='group')

    return fig

def avg_std_cidade_trafego(df1):
    cols = ['City','Time_taken(min)','Road_traffic_density']
    df_5 = df1.loc[:,cols].groupby(['City','Road_traffic_density']).agg({'Time_taken(min)':['mean','std']})
    df_5.columns = ['avg_time','std_time']
    df_5 = df_5.reset_index()
    fig = px.sunburst(df_5, path=['City', 'Road_traffic_density'], values='avg_time',
          color='std_time', color_continuous_scale='RdBu',
          color_continuous_midpoint=np.average(df_5['std_time']) )

    return fig

def distribuicao_distancia(df1):
    cols = ['City','Time_taken(min)','Type_of_order']
    df_4 = df1.loc[:,cols].groupby(['City','Type_of_order']).agg({'Time_taken(min)':['mean','std']})
    df_4.columns = ['avg_time','std_time']
    df_4 = df_4.reset_index()
    
    return df_4

# --------------------------------- Início da estrutura lógica do código ---------------------------
# ----------------------------------------
# Importação do dataset
# ----------------------------------------
df = pd.read_csv('dataset/train.csv')

# ----------------------------------------
# Limpeza dos dados
# ----------------------------------------
df1 = clean_code(df)

# ---------- Visão Entregadores ----------

# ----------------------------------------
# Sidebar
# ----------------------------------------

#image_path='C:/Users/Phelipe Pachler/Documents/REPOS/ftc_python_analise_dados/notebooks/'
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

#st.header(date_slider)
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

st.header('Marketplace - Visão Restaurantes')

with st.container():
    st.title('Overall Metrics')

    col1,col2,col3,col4,col5,col6 = st.columns(6)

    with col1:
        delivery_unique = df1.loc[:,'Delivery_person_ID'].nunique()
        col1.metric('Entregadores',delivery_unique)

    with col2:            
        col2.metric('Distância Média', mean_distance(df1))

    with col3:            
        col3.metric('Tempo Festivais',avg_std_festivais(df1,parametro='avg',festival='Yes'))

    with col4:
        col4.metric('Desvio Festivais',avg_std_festivais(df1,'std','Yes'))

    with col5:
        col5.metric('Tempo S/ Festivais',avg_std_festivais(df1,'avg','No'))

    with col6:
        col6.metric('Desvio S/ Festivais',avg_std_festivais(df1,'std','No'))

with st.container():
    st.markdown('---')
    st.title('Distribuição do Tempo Por Cidade')

    col1,col2 = st.columns(2,gap='large')

    with col1:
        fig = tempo_cidade_media(df1)
        st.markdown('#### Média')        
        st.plotly_chart(fig)

    with col2:
        fig = tempo_cidade_desvio(df1)
        st.markdown('#### Desvio Padrão')        
        st.plotly_chart(fig)

with st.container():
    st.markdown('---')
    fig = avg_std_cidade_trafego(df1)
    st.title('AVG e STD de Entrega por Cidade e Tipo de Tráfego')
    st.plotly_chart(fig) 

with st.container():
    df_4 = distribuicao_distancia(df1)
    st.markdown('---')
    st.title('Distribuição da Distância')
    st.dataframe(df_4)
