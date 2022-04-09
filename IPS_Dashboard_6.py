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
MM = 1000000

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
    #@st.cache
    def data():
        prod = pd.read_csv('Data//Production.csv')
        prod['fecha'] = pd.to_datetime(prod['fecha']).dt.date
        prod.columns = [x.capitalize() for x in prod.columns]
        
        press_pr = pd.read_csv('Data//RPFC-Plano de referencia.csv')
        press_pr['fecha'] = pd.to_datetime(press_pr['fecha']).dt.strftime('%d-%m-%Y')
        press_pr.columns = [x.capitalize() for x in press_pr.columns]
                
        press_nmd = pd.read_csv('Data//RPFC-NMD.csv')
        press_nmd['fecha'] = pd.to_datetime(press_nmd['fecha']).dt.strftime('%d-%m-%Y')
        press_nmd.columns = [x.capitalize() for x in press_nmd.columns]
        
        coords = pd.read_csv('Data//Coords.csv')
        coords.columns = [x.lower() for x in coords.columns]
        
        raa_rga = pd.read_csv('Data//RAA-RGA.csv')
        raa_rga['fecha'] = pd.to_datetime(raa_rga['fecha']).dt.strftime('%d-%m-%Y')
        raa_rga['gor'] = raa_rga['gor'].astype(float)
        raa_rga['wor'] = raa_rga['wor'].astype(float)
        raa_rga['wc'] = raa_rga['wc'].astype(float)
        raa_rga.columns = [x.capitalize() for x in raa_rga.columns]
        
        well_sum = pd.read_excel('Data//Resumen de pozos.xlsx')
        well_sum['fecha de terminacion'] = pd.to_datetime(well_sum['fecha de terminacion']).dt.strftime('%d-%m-%Y')
        well_sum.columns = [x.capitalize() for x in well_sum.columns]
        
        shots = pd.read_excel('Data//Zones.xlsx', sheet_name='INTERVALOS')
        shots['FECHA DE DISPARO'] = pd.to_datetime(shots['FECHA DE DISPARO']).dt.strftime('%d-%m-%Y')
        shots['FECHA DE CIERRE'] = pd.to_datetime(shots['FECHA DE CIERRE']).dt.strftime('%d-%m-%Y')
        shots.columns = [x.capitalize() for x in shots.columns]
        shots = shots.fillna('NO DISPONIBLE')

        return prod, press_pr, press_nmd, coords, raa_rga, well_sum, shots
    prod, press_pr, press_nmd, coords, raa_rga, well_sum, shots = data()
    
######################################## DASHBOARD ########################################
    with st.sidebar.expander('Selector de pozos'):
        pozos = prod['Pozo'].unique()
        filt_pozos = st.selectbox('Seleccione un Pozo', pozos)
        pozo = prod[prod['Pozo'] == filt_pozos]
        
    with st.container():
        with st.expander('DATOS DUROS - PRODUCTIVIDAD'):
            if st.checkbox('Ver Coordenadas de los Pozos') == True:
                coords
            if st.checkbox('Ver Producción de Pozos') == True:
                prod
            if st.checkbox('Ver Registro de Presión de Fondo Cerrado al Plano de Referencia') == True:
                press_pr
            if st.checkbox('Ver Registro de Presión de Fondo Cerrado al Nivel Medio de los Disparos') == True:
                press_nmd
            if st.checkbox('Ver Datos RAA/RGA') == True:
                raa_rga
                
        with st.expander('RESUMEN DE POZOS'):
            st.write('Consultar expedientes - http://187.157.54.226:5000/d/s/678868682763449491/cZDf3kcwj06VPeCKpffcSo_zjQMX_uD0-7bmgbazTawk_')
            st.map(coords)
            well_sum
            
        with st.expander('HISTORIAL DE INTERVALOS DISPARADOS POR POZO'):
            shots
            
        with st.expander('GRÁFICOS DE PRODUCTIVIDAD'):
            w_prod_plot = make_subplots(specs=[[{"secondary_y": True}]])
            w_prod_plot.add_trace(go.Scatter(x=pozo['Fecha'], y=pozo['Aceite_bpd'], mode='lines', marker_line_width=.5, marker=dict(size=5,color='green'),name='Aceite'),secondary_y=False)
            w_prod_plot.add_trace(go.Scatter(x=pozo['Fecha'], y=pozo['Agua_bpd'], mode='lines', marker_line_width=.5, marker=dict(size=5,color='blue'), name='Agua'), secondary_y=False)
            w_prod_plot.add_trace(go.Scatter(x=pozo['Fecha'], y=pozo['Gas_mmcfpd'], mode='lines', marker_line_width=.5, marker=dict(size=5,color='red'),name='Gas'),secondary_y=True)
            w_prod_plot.update_layout(title_text = f'Histórico de producción {filt_pozos}', hovermode="x unified", font=dict(family="sans-serif", size=10, color="black"), legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1), margin={"r":0,"t":100,"l":100,"b":0}, height=350, width=1020)
            w_prod_plot.update_yaxes(title_text="<b> Aceite [SBPD] / Agua [SBPD] </b> ", secondary_y=False, nticks=10)
            w_prod_plot.update_yaxes(title_text="<b> Gas [MMSPCD]</b>", secondary_y=True, nticks=10)
            w_prod_plot.update_xaxes(title_text="<b>Año</b>", nticks=25)
            st.plotly_chart(w_prod_plot)
                
            raa_rga_plot = go.Figure()
            raa_rga_plot.add_trace(go.Scatter(x=pozo['Fecha'], y=pozo['Gor'], name="RGA", mode='lines', marker_line_width=.3, marker=dict(size=5,color='red')))
            raa_rga_plot.add_trace(go.Scatter(x=pozo['Fecha'], y=pozo['Wc'], name="Corte de Agua", mode='lines', marker_line_width=.3, marker=dict(size=5,color='blue'), yaxis="y3"))
            raa_rga_plot.add_trace(go.Scatter(x=pozo['Fecha'], y=pozo['Wor'], name="RAA", mode='lines', marker_line_width=.3, marker=dict(size=5,color='skyblue'), yaxis="y4"))
            raa_rga_plot.update_layout(title_text=f'RGA/RAA {filt_pozos}', height=350, width=1000, font=dict(family="sans-serif", size=10, color="black"), legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1))
            raa_rga_plot.update_layout(hovermode="x unified", margin={"r":0,"t":100,"l":100,"b":0}, xaxis=dict(title_text="<b>Año</b>", nticks=25, domain=[0, 0.95]),
                yaxis=dict(nticks=20, exponentformat='none', title="<b>RGA [sm3/sm3]</b>", titlefont=dict(
                        color="black", size=9), tickfont=dict(color="black", size=9)),
                yaxis3=dict(nticks=20, exponentformat='none', title="<b>Corte de Agua [%]</b>", titlefont=dict(color="black", size=10), tickfont=dict(color="black", size=9),
                    anchor="x",
                    overlaying="y",
                    side="right",
                    position=0.95),
                yaxis4=dict(nticks=20,exponentformat='none', title="<b>RAA [sm3/sm3]</b>", titlefont=dict(color="black", size=10), tickfont=dict(color="black", size=9),
                    anchor="free",
                    overlaying="y",
                    side="right",
                    position=1))
            raa_rga_plot.update_yaxes(rangemode="tozero")
            st.plotly_chart(raa_rga_plot)
            
            cum_prod = st.columns(3)
            cum_oil_plot = px.ecdf(pozo, x="Fecha", y="Aceite_bpm", ecdfnorm=None)
            cum_oil_plot.update_layout(font=dict(family="sans-serif", size=10, color="black"), hovermode="x unified", title=f'Producción de Aceite Acumulado {filt_pozos}', legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1), margin={"r":0,"t":50,"l":0,"b":0}, height=200, width=350)
            cum_oil_plot.update_traces(marker=dict(color='green'))
            cum_oil_plot.update_yaxes(title_text="<b>Aceite [bbls]</b>", nticks=10)
            cum_oil_plot.update_xaxes(title_text="<b>Años</b>", nticks=10)
            cum_prod[0].plotly_chart(cum_oil_plot)
            cum_water_plot = px.ecdf(pozo, x="Fecha", y="Agua_bpm", ecdfnorm=None)
            cum_water_plot.update_layout(font=dict(family="sans-serif", size=10, color="black"), hovermode="x unified", title=f'Producción de Agua Acumulada {filt_pozos}', legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1), margin={"r":0,"t":50,"l":0,"b":0}, height=200, width=350)
            cum_water_plot.update_traces(marker=dict(color='blue'))
            cum_water_plot.update_yaxes(title_text="<b>Agua [bbls]</b>", nticks=10)
            cum_water_plot.update_xaxes(title_text="<b>Años</b>", nticks=10)
            cum_prod[1].plotly_chart(cum_water_plot)
            cum_gas_plot = px.ecdf(pozo, x="Fecha", y="Gas_mmcfpm", ecdfnorm=None)
            cum_gas_plot.update_layout(font=dict(family="sans-serif", size=10, color="black"), hovermode="x unified", title=f'Producción de Gas Acumulado {filt_pozos}', legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1), margin={"r":0,"t":50,"l":0,"b":0}, height=200, width=350)
            cum_gas_plot.update_traces(marker=dict(color='red'))
            cum_gas_plot.update_yaxes(title_text="<b>Gas [MMPCPD]</b>", nticks=10)
            cum_gas_plot.update_xaxes(title_text="<b>Años</b>", nticks=10)
            cum_prod[2].plotly_chart(cum_gas_plot)
            
            st.subheader('Descripción de pozo')
            st.caption("Producción acumulada de aceite: " + str(round(pozo['Aceite_bpm'].sum()/MM,2)) + " Millones de Barriles")
            st.caption("Producción acumulada de agua: " + str(round(pozo['Agua_bpm'].sum()/MM,2)) + " Millones de Barriles")
            st.caption("Producción acumulada de gas: " + str(round(pozo['Gas_mmcfpm'].sum(),2)) + " Millones de Pies Cúbicos")
                        
            if st.button(f'Exportar Gráfico de Producción Histórica {filt_pozos}') == True:
                w_prod_plot.write_html(f'{filt_pozos} Histórico de Producción.html')
            if st.button(f'Exportar Gráfico de RAA-RGA Histórica {filt_pozos}') == True:
                raa_rga_plot.write_html(f'{filt_pozos} WOR-GOR-WC% historico.html')
                
################################################################################################################################################################
elif st.session_state['authentication_status'] == False:
    st.error('Username/password is incorrect')
elif st.session_state['authentication_status'] == None:
    st.warning('Please enter your username and password')
