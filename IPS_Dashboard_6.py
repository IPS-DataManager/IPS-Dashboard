# -*- coding: utf-8 -*-
"""
Created on Fri Mar 11 09:09:48 2022

@author: IPSMX-L7NRKD03
"""
#Core Packages
import streamlit as st
from PIL import Image
import streamlit_authenticator as stauth

#EDA
import pandas as pd 
import numpy as np

#Graphers
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.graph_objs as go

pd.options.mode.chained_assignment = None  # default='warn'
pd.options.display.float_format = '{:,.2f}'.format
def format_float(value):
    return f'{value:,.2f}'
pd.options.display.float_format = format_float

######################################## Page Config ########################################
APP_TITLE = "IPS Dashboard"
img=Image.open('Imagenes//IPS.png')
st.set_page_config(
    page_title = APP_TITLE,
    page_icon = img,
    layout = "wide")

img_sidebar= st.sidebar.columns(3)
img_sidebar[1].image(img,width=100)

######################################## CONVERTION FACTORS ########################################
# Metros cubicos a barriles (aceite)
bbls = 6.29
# Metros cubicos a pies cubicos (gas)
ft3 = 35.3147
#Meses a días
days = 30.5
# Miles
#M = 1000
# Millones
#MM = 1000000

######################################## Authentication ########################################
users = pd.read_csv('Usuarios//Usuarios.csv', encoding='utf-8')
users['pass'] = users['pass'].astype(str)
users['pass'] = '000' + users['pass']
hashed_passwords = stauth.hasher(users['pass']).generate()
authenticator = stauth.authenticate(users['nombre_c'], users['usuario'], hashed_passwords, 'IPS_Dashboard','key_1', cookie_expiry_days=30)

name, authentication_status = authenticator.login('Login','main')

################################################################################################################################################################
if st.session_state['authentication_status']:
    st.write('Bienvenido *%s*' % (st.session_state['name']))
    st.title('Tablero de Campos Maduros - Proyecto Sitio Grande')
################################################################################################################################################################
    @st.cache
    def data():
        prod = pd.read_csv('Data//Production.csv')
        prod['fecha'] = pd.to_datetime(prod['fecha']).dt.strftime('%d-%m-%Y')
        
        press_pr = pd.read_csv('Data//RPFC-Plano de referencia.csv')
        press_nmd = pd.read_csv('Data//RPFC-NMD.csv')
        coords = pd.read_csv('Data//Coords.csv')
        raa_rga = pd.read_csv('Data//RAA-RGA.csv')
        raa_rga['fecha'] = pd.to_datetime(raa_rga['fecha']).dt.strftime('%d-%m-%Y')
        
        return prod, press_pr, press_nmd, coords, raa_rga
    prod, press_pr, press_nmd, coords, raa_rga = data()
    
######################################## DASHBOARD ########################################
    with st.container():
        with st.expander('DATOS DUROS'):
            if st.checkbox('Ver Coordenadas de los Pozos') == True:
                coords
            if st.checkbox('Ver Datos de Producción') == True:
                prod
            if st.checkbox('Ver Datos de Registro de Presión de Fondo Cerrado al Plano de Referencia') == True:
                press_pr
            if st.checkbox('Ver Datos de Registro de Presión de Fondo Cerrado al Nivel Medio de los Disparos') == True:
                press_nmd
            if st.checkbox('Ver Datos de Productividad (RAA/RGA)') == True:
                raa_rga
        with st.expander('RESUMEN DE POZO'):
            prod
            
    with st.sidebar.expander('Selector de pozos'):
        pozos = prod['pozo'].unique()
        filt_pozos = st.selectbox('Seleccione un pozo', pozos)
        pozo = prod[prod['pozo'] == filt_pozos]
        
################################################################################################################################################################
elif st.session_state['authentication_status'] == False:
    st.error('Username/password is incorrect')
elif st.session_state['authentication_status'] == None:
    st.warning('Please enter your username and password')
