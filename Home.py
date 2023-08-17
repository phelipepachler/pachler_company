import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home',
    page_icon='🤡', 
    layout='wide'
)

#image_path='C:/Users/Phelipe Pachler/Documents/REPOS/ftc_python_analise_dados/notebooks/'
image = Image.open('logo.png')
st.sidebar.image(image, width=300)

st.sidebar.markdown('# Pachler Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown('---')

st.write('# Pachler Company Growth Dashboard')

st.markdown(
    """
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos entregadores e restaurantes.
    ### Como utilizar esse dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento
        - Visão Tática: Indicadores semanais de crescimento
        - Visão Geográfica: Insights de geolocalização
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento
    - Visão Restaurante:
        - Indicadores semanais de crescimento dos restaurantes
    ### Ask for help
    - Eu
        - @pachler
    """
)