# ----------------------------------------
# Importação de bibliotecas
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import math
from datetime import datetime, date
from PIL import Image

st.set_page_config( page_title='Visão Entregadores', page_icon='🛵', layout='wide')

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

vazio_zero = lambda x: 0 if math.isnan(x) else x

def top_delivers(df1,top_asc):

    df_6 = ( df1.loc[:,['Delivery_person_ID','City','Time_taken(min)']]
            .groupby(['City','Delivery_person_ID']).mean()
            .sort_values(['City','Time_taken(min)'],ascending=top_asc).reset_index() )

    cidades = list(df_6.City.unique())

    if len(cidades) == 0:
        col1.markdown('No Data')

    else:
        df_aux01 = df_6.loc[df_6['City'] == cidades[0],:].head(10)
        df_aux02 = df_6.loc[df_6['City'] == cidades[1],:].head(10)
        df_aux03 = df_6.loc[df_6['City'] == cidades[2],:].head(10)
        df_6 = pd.concat( [df_aux01, df_aux02, df_aux03]).reset_index(drop=True)

    return df_6

# --------------------------------- Início da estrutura lógica do código ---------------------------
# ----------------------------------------
# Importação do dataset
# ----------------------------------------
df = pd.read_csv('../dataset/train.csv')

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

st.header('Marketplace - Visão Entregadores')

with st.container():
    st.title('Overall Metrics')

    col1,col2,col3,col4 = st.columns(4,gap='large')

    with col1:
        mais_velho = df1.loc[:,'Delivery_person_Age'].max()
        mais_velho = vazio_zero(mais_velho)
        col1.metric('Mais Velho', mais_velho)

    with col2:
        mais_novo = df1.loc[:,'Delivery_person_Age'].min()
        mais_novo = vazio_zero(mais_novo)
        col2.metric('Mais Novo', mais_novo)

    with col3:
        melhor_cond = df1.loc[:,'Vehicle_condition'].max()
        melhor_cond = vazio_zero(melhor_cond)
        col3.metric('Melhor Condição',melhor_cond)

    with col4:
        pior_cond = df1.loc[:,'Vehicle_condition'].min()
        pior_cond = vazio_zero(pior_cond)
        col4.metric('Pior Condição',pior_cond)

with st.container():
    st.markdown('---')
    st.title('Avaliações')

    col1, col2 = st.columns(2)

    with col1:
        st.subheader('Avaliação Média por Entregador')
        df_3 = df1.loc[:,['Delivery_person_ID','Delivery_person_Ratings']].groupby('Delivery_person_ID').mean().reset_index()
        st.dataframe(df_3)

    with col2:
        st.subheader('Avaliação Média por Trânsito')
        df_4 = ( df1.loc[:, ['Delivery_person_Ratings','Road_traffic_density']]
                .groupby('Road_traffic_density')
                .agg({'Delivery_person_Ratings':['mean','std']}).reset_index() )

        df_4.columns = ['Road_traffic_density','delivery_mean','delivery_std']

        st.dataframe(df_4)

        st.subheader('Avaliação Média por Clima')
        df_5 = ( df1.loc[:, ['Delivery_person_Ratings','Weatherconditions']].groupby('Weatherconditions')
                .agg({'Delivery_person_Ratings':['mean','std']}).reset_index() )

        df_5.columns = ['Weatherconditions','delivery_mean','delivery_std']

        st.dataframe(df_5)

with st.container():
    st.markdown('---')
    st.title('Velocidade de Entrega')

    col1, col2 = st.columns(2)

    with col1:
        fast_delivers = top_delivers(df1,True)
        st.subheader('Top Entregadores Mais Rápidos')
        st.dataframe(fast_delivers)

    with col2:
        slow_delivers = top_delivers(df1,False)
        st.subheader('Top Entregadores Mais Lentos')
        st.dataframe(slow_delivers)

    st.markdown('---')
