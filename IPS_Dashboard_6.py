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
M = 1000
# Millones
MM = 1000000

######################################## DATA ########################################
prod = pd.read_csv('Data//Production.csv')

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
    @st.cache
################################################################################################################################################################
    def data():
        production = pd.read_csv('Data\Production.csv')
        pressure_pr = pd.read_csv('Data\RPFC-Plano de referencia.csv')
        pressure_nmd = pd.read_csv('Data\RPFC-NMD.csv')
        well_coords = pd.read_csv('Coords.csv')
        raa_rga = pd.read_csv('RAA-RGA.csv)
        return production, pressure_pr, pressure_nmd, well_coords, raa_rga
######################################## DASHBOARD ########################################
    with st.container():
        with st.expander('DATOS DUROS'):
            if st.checkbox('Ver Datos de Producción') == True:
                st.write('Datos de Producción')
                prod
            if st.checkbox('Ver Datos de Presión') == True:
                st.write('Datos de Presión')
            if st.checkbox('Ver Datos de Salinidad') == True:
                st.write('Datos de Salinidad')
        with st.expander('RESUMEN DE POZO'):
            prod
    
################################################################################################################################################################
elif st.session_state['authentication_status'] == False:
    st.error('Username/password is incorrect')
elif st.session_state['authentication_status'] == None:
    st.warning('Please enter your username and password')
