# Core Packages
import streamlit as st
from PIL import Image
#import streamlit_authenticator as stauth

#EDA
import pandas as pd 

#Graphers
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.graph_objs as go

pd.options.mode.chained_assignment = None  # default='warn'
pd.options.display.float_format = '{:,.2f}'.format

def format_float(value):
    return f'{value:,.2f}'
pd.options.display.float_format = format_float

#################### Convertion Units ####################

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
# Billones (Americanos)
B = 1000000000

#################### PAGE CONFIG ####################

APP_TITLE = "IPS Dash"
img=Image.open('Imagenes\IPS.png')
st.set_page_config(
    page_title = APP_TITLE,
    page_icon = img,
    layout = "wide")

img_sidebar= st.sidebar.columns(3)
img_sidebar[1].image(img,width=100)

#################### Authentication ####################


#################### Data ####################

@st.cache
def data():
    prod = pd.read_csv('Data//PRODUCTION.csv')
    prod.columns = [x.lower() for x in prod.columns]
    prod.columns = [x.capitalize() for x in prod.columns]
    prod['Fecha'] = pd.to_datetime(prod['Fecha']).dt.date
    prod['Pozo'] = prod['Pozo'].str.replace('SG-','SITIO GRANDE ')
    
    press_pr = pd.read_csv('Data//RPFC-PLANO DE REFERENCIA.csv')
    press_pr['fecha'] = pd.to_datetime(press_pr['fecha']).dt.date
    press_pr.columns = [x.capitalize() for x in press_pr.columns]
            
    press_nmd = pd.read_csv('Data//RPFC-NMD.csv')
    press_nmd['fecha'] = pd.to_datetime(press_nmd['fecha']).dt.date
    press_nmd.columns = [x.capitalize() for x in press_nmd.columns]
    
    coords = pd.read_csv('Data//COORDS.csv')
    coords.columns = [x.lower() for x in coords.columns]
    
    salinity = pd.read_csv('Data//SALINITY.csv')
    salinity['Fecha'] = pd.to_datetime(salinity['Fecha']).dt.date
    salinity.columns = [x.capitalize() for x in salinity.columns]
    salinity['Pozo'] = salinity['Pozo'].str.replace('SITIO_GDE_','SITIO GRANDE ')
    salinity = salinity.sort_values(by='Fecha')
    
    raa_rga = pd.read_csv('Data//RAA-RGA.csv')
    raa_rga['fecha'] = pd.to_datetime(raa_rga['fecha']).dt.date
    raa_rga['gor'] = raa_rga['gor'].astype(float)
    raa_rga['wor'] = raa_rga['wor'].astype(float)
    raa_rga['wc'] = raa_rga['wc'].astype(float)
    raa_rga.columns = [x.capitalize() for x in raa_rga.columns]
    
    well_sum = pd.read_csv('Data//SUMMARY.csv')
    well_sum['Fecha de terminacion'] = pd.to_datetime(well_sum['Fecha de terminacion']).dt.date
    well_sum.columns = [x.upper() for x in well_sum.columns]
    
    completions = pd.read_csv('Data//RESUMEN DE POZOS Y LITOLOGÍA.csv')
    completions.columns = [x.capitalize() for x in completions.columns]

    return prod, press_pr, press_nmd, coords, raa_rga, well_sum, completions, salinity
prod, press_pr, press_nmd, coords, raa_rga, well_sum, completions, salinity = data()

#################### Dashboard ####################

with st.sidebar.expander('Selector de pozos'):
    pozos = prod['Pozo'].unique()
    filt_pozos = st.selectbox('Seleccione un Pozo', pozos)
    pozo = prod[prod['Pozo'] == filt_pozos]
    
with st.container():
    with st.expander('BASE DE DATOS'):
        if st.checkbox('Ver Coordenadas de los Pozos') == True:
            coords
        if st.checkbox('Ver Producción de Pozos') == True:
            prod
        if st.checkbox('Ver Registro de Presión de Fondo Cerrado al Plano de Referencia') == True:
            press_pr
        if st.checkbox('Ver Registro de Presión de Fondo Cerrado al Nivel Medio de los Disparos') == True:
            press_nmd
                        
    with st.expander('RESUMEN DE POZOS'):
        st.write('Consultar expedientes - http://187.157.54.226:5000/d/s/678868682763449491/cZDf3kcwj06VPeCKpffcSo_zjQMX_uD0-7bmgbazTawk_')
        map_pozos_loc = px.scatter_mapbox(well_sum, lat="LATITUD", lon="LONGITUD", hover_name='POZO', zoom=12, color='ESTADO')
        map_pozos_loc.update_layout(mapbox_style="stamen-terrain", height=550, width=1380, margin={"r":0,"t":100,"l":0,"b":0}, legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=0.9), showlegend=True, autosize=True)
        map_pozos_loc
        well_sum
        
    with st.expander('HISTORIAL DE INTERVALOS DISPARADOS POR POZO'):
        completions_pozo = completions[completions['Pozo'] == filt_pozos]
        mapa = st.columns(3)
        mapa[1].image('Mapas\MAPA SG.png', width=700)
        st.subheader('Historial de Terminaciones del Campo')
        completions
        st.subheader('Historial de Terminaciones del Pozo')
        completions_pozo
        
    with st.expander('DATOS DINAMICOS'):
        st.subheader(f'{filt_pozos}')
       
       ### PRESION ###
        press_field = pd.read_csv('Data//RPFC-PR-ANUAL.csv')
        press_field['Fecha'] = pd.to_datetime(press_field['Fecha']).dt.date
        press_field.columns = [x.capitalize() for x in press_field.columns]
        
        press_pozo = press_pr[press_pr['Pozo'] == filt_pozos]
        press_pr_plot = make_subplots(specs=[[{"secondary_y": False}]])
        press_pr_plot.add_trace(go.Scatter(x=press_field['Fecha'], y=press_field['Presion de fondo cerrado'], mode='lines', marker_line_width=.5, marker=dict(size=3.5,color='black'),name='Presión de Yacimiento'),secondary_y=False)
        press_pr_plot.add_trace(go.Scatter(x=press_pozo['Fecha'], y=press_pozo['De fondo cerrado gradiente de yacimiento (kg/cm2)'], mode='markers', marker_line_width=.5, marker=dict(size=3.5,color='red'),name=f'Presión al gradiente de Yacimiento {filt_pozos}'),secondary_y=False)
        press_pr_plot.add_trace(go.Scatter(x=press_pozo['Fecha'], y=press_pozo['De fondo cerrado gradiente de pozo (kg/cm2)'], mode='markers', marker_line_width=.5, marker=dict(size=3.5,color='blue'), name=f'Presión al gradiente de Pozo {filt_pozos}'),secondary_y=False)
        press_pr_plot.update_layout(title_text = 'HISTORICO DE PRESIONES AL PLANO DE REFERENCIA', margin={"r":110,"t":100,"l":120,"b":50}, hovermode="x unified", font=dict(family="sans-serif", size=10, color="black"), legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1), width=1380, height=450)
        press_pr_plot.update_yaxes(title_text="Presión (kg/cm2)", secondary_y=False, nticks=10)
        press_pr_plot.update_xaxes(title_text="<b>Año</b>", nticks=25)
        press_pr_plot.update_yaxes(rangemode="tozero")
        press_pr_plot.update_xaxes(range=['1970', '2022'])
        st.plotly_chart(press_pr_plot)
        
        ### PRODUCCION ###
        well_prod = go.Figure()
        well_prod.add_trace(go.Scatter(x=pozo['Fecha'], y=pozo['Aceite diario (bpd)'], name="Aceite", mode='markers+lines', marker_line_width=.3, marker=dict(size=4,color='green')))
        well_prod.add_trace(go.Scatter(x=pozo['Fecha'], y=pozo['Agua diario (bpd)'], name="Agua", mode='markers+lines', marker_line_width=.3, marker=dict(size=4,color='blue'), yaxis="y2"))
        well_prod.add_trace(go.Scatter(x=pozo['Fecha'], y=pozo['Gas diario (ft3/d)']/MM, name="Gas", mode='markers+lines', marker_line_width=.3, marker=dict(size=4,color='red'), yaxis="y3"))
        well_prod.update_layout(title_text='HISTÓRICO DE PRODUCCIÓN', margin={"r":10,"t":50,"l":50,"b":50}, height=400, width=1380, font=dict(family="sans-serif", size=10, color="black"), legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=0.93))
        well_prod.update_layout(hovermode="x unified", xaxis=dict(title_text="<b>Año</b>", nticks=25, domain=[0.047, 0.93]),
            yaxis=dict(nticks=15, exponentformat='none', title="Aceite [SBPD]", titlefont=dict(color="black", size=12), tickfont=dict(color="black", size=9), position=0),
            yaxis2=dict(nticks=15, exponentformat='none', title="Agua [SBPD]", titlefont=dict(color="black", size=12), tickfont=dict(color="black", size=9),
                    anchor="free",
                    overlaying="y",
                    side="left",
                    position=0.047),
            yaxis3=dict(nticks=15, exponentformat='none', title="Gas [MMPCPD]", titlefont=dict(color="black", size=12), tickfont=dict(color="black", size=9),
                    anchor="x",
                    overlaying="y",
                    side="right",
                    position = 0.93))
        well_prod.update_yaxes(rangemode="tozero")
        well_prod.update_xaxes(range=['1970', '2022'])
        st.plotly_chart(well_prod)
        
        well_prod_2 = go.Figure()
        well_prod_2.add_trace(go.Scatter(x=pozo['Fecha'], y=pozo['Aceite diario (bpd)'], name="Aceite", mode='markers', marker_line_width=.3, marker=dict(size=4,color='green')))
        well_prod_2.add_trace(go.Scatter(x=pozo['Fecha'], y=pozo['Agua diario (bpd)'], name="Agua", mode='markers', marker_line_width=.3, marker=dict(size=4,color='blue'), yaxis="y2"))
        well_prod_2.add_trace(go.Scatter(x=pozo['Fecha'], y=pozo['Gas diario (ft3/d)']/MM, name="Gas", mode='markers', marker_line_width=.3, marker=dict(size=4,color='red'), yaxis="y3"))
        well_prod_2.update_layout(title_text='HISTÓRICO DE PRODUCCIÓN', margin={"r":0,"t":50,"l":50,"b":50}, height=400, width=1380, font=dict(family="sans-serif", size=10, color="black"), legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=0.93))
        well_prod_2.update_layout(hovermode="x unified", xaxis=dict(title_text="<b>Año</b>", nticks=25, domain=[0.07, 0.93]),
            yaxis=dict(nticks=15, exponentformat='none', title="Aceite [SBPD]", titlefont=dict(color="black", size=12), tickfont=dict(color="black", size=9), position=0),
            yaxis2=dict(nticks=15, exponentformat='none', title="Agua [SBPD]", titlefont=dict(color="black", size=12), tickfont=dict(color="black", size=9),
                    anchor="free",
                    overlaying="y",
                    side="left",
                    position=0.07),
            yaxis3=dict(nticks=15, exponentformat='none', title="Gas [MMPCPD]", titlefont=dict(color="black", size=12), tickfont=dict(color="black", size=9),
                    anchor="x",
                    overlaying="y",
                    side="right",
                    position = 0.93))
        well_prod_2.update_yaxes(type='log', rangemode="tozero")
        well_prod_2.update_xaxes(range=['1970', '2022'])
        if st.checkbox('Producción en Escala Semilogarítmica') == True:
            well_prod_2
        
        rga_plot = go.Figure()
        rga_plot.add_trace(go.Scatter(x=pozo['Fecha'], y=pozo['Rga'], name="RGA", mode='markers', marker_line_width=.3, marker=dict(size=4,color='orange')))
        rga_plot.update_layout(title_text = 'RELACIÓN GAS-ACEITE', margin={"r":110,"t":120,"l":120,"b":50}, hovermode="x unified", font=dict(family="sans-serif", size=10, color="black"), legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1), width=1380, height=450)
        rga_plot.update_yaxes(title_text="RGA [sm3/sm3]", exponentformat='none', nticks=10)
        # rga_plot.update_yaxes(rangemode="tozero")
        rga_plot.update_yaxes(range=[0, 70000])
        rga_plot.update_xaxes(range=['1970', '2022'])
        rga_plot.update_xaxes(title_text="<b>Año</b>", nticks=25)
        st.plotly_chart(rga_plot)
        
        rga_plot_2 = go.Figure()
        rga_plot_2.add_trace(go.Scatter(x=pozo['Fecha'], y=pozo['Rga'], name="RGA", mode='markers', marker_line_width=.3, marker=dict(size=4,color='orange')))
        rga_plot_2.update_layout(title_text = 'RELACIÓN GAS-ACEITE', margin={"r":110,"t":120,"l":120,"b":50}, hovermode="x unified", font=dict(family="sans-serif", size=10, color="black"), legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1), width=1380, height=450)
        rga_plot_2.update_yaxes(title_text="RGA [scf/stb]", exponentformat='none', nticks=10)
        rga_plot_2.update_yaxes(rangemode="tozero", type='log')
        rga_plot_2.update_xaxes(range=['1970', '2022'])
        rga_plot_2.update_xaxes(title_text="<b>Año</b>", nticks=25)
        if st.checkbox('RGA en Escala Semilogarítmica') == True:
            rga_plot_2

        ### RAA/RGA/WC ###
        well_salinity = salinity[salinity['Pozo'] == filt_pozos]
        sal_raa_plot = go.Figure()
        sal_raa_plot.add_trace(go.Scatter(x=well_salinity['Fecha'], y=well_salinity['Salinidad'], name="Salinidad", mode='markers', marker_line_width=.3, marker=dict(size=4,color='magenta')))
        sal_raa_plot.add_trace(go.Scatter(x=pozo['Fecha'], y=pozo['Raa'], name="RAA", mode='markers+lines', marker_line_width=.3, marker=dict(size=4,color='skyblue'), yaxis="y4"))
        sal_raa_plot.add_trace(go.Scatter(x=pozo['Fecha'], y=pozo['Corte de agua (%)'], name="Corte de Agua", mode='markers+lines', marker_line_width=.3, marker=dict(size=4,color='blue'), yaxis="y3"))
        sal_raa_plot.update_layout(title_text='SALINIDAD / RELACIÓN AGUA-ACEITE / CORTE DE AGUA', height=400, width=1380, font=dict(family="sans-serif", size=10, color="black"), legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1))
        sal_raa_plot.update_layout(hovermode="x unified", margin={"r":0,"t":100,"l":120,"b":50}, xaxis=dict(title_text="<b>Año</b>", nticks=25, domain=[0, 0.95]),
            yaxis=dict(nticks=15, exponentformat='none', title="Salinidad [PPM]", titlefont=dict(
                    color="black", size=12), range=[0,200000], tickfont=dict(color="black", size=9)),
            yaxis3=dict(nticks=15, exponentformat='none', title="Corte de Agua [%]", titlefont=dict(color="black", size=12), tickfont=dict(color="black", size=9),
                anchor="x",
                overlaying="y",
                side="right",
                position= 1),
            yaxis4=dict(nticks=15,exponentformat='none', title="RAA [sm3/sm3]", titlefont=dict(color="black", size=12), tickfont=dict(color="black", size=9),
                anchor="free",
                overlaying="y",
                side="right",
                position=1))
        sal_raa_plot.update_yaxes(rangemode="tozero")
        sal_raa_plot.update_xaxes(range=['1970', '2022'])
        st.plotly_chart(sal_raa_plot)
        
        sal_raa_plot_2 = go.Figure()
        sal_raa_plot_2.add_trace(go.Scatter(x=well_salinity['Fecha'], y=well_salinity['Salinidad'], name="Salinidad", mode='markers', marker_line_width=.3, marker=dict(size=4,color='magenta')))
        sal_raa_plot_2.add_trace(go.Scatter(x=pozo['Fecha'], y=pozo['Raa'], name="RAA", mode='markers+lines', marker_line_width=.3, marker=dict(size=4,color='skyblue'), yaxis="y4"))
        sal_raa_plot_2.add_trace(go.Scatter(x=pozo['Fecha'], y=pozo['Corte de agua (%)'], name="Corte de Agua", mode='markers+lines', marker_line_width=.3, marker=dict(size=4,color='blue'), yaxis="y3"))
        sal_raa_plot_2.update_layout(title_text='SALINIDAD / RELACIÓN AGUA-ACEITE / CORTE DE AGUA', height=400, width=1380, font=dict(family="sans-serif", size=10, color="black"), legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1))
        sal_raa_plot_2.update_layout(hovermode="x unified", margin={"r":0,"t":100,"l":120,"b":50}, xaxis=dict(title_text="<b>Año</b>", nticks=25, domain=[0, 0.95]),
            yaxis=dict(nticks=15, exponentformat='none', title="Salinidad [PPM]", titlefont=dict(
                    color="black", size=12), type='log', tickfont=dict(color="black", size=9)),
            yaxis3=dict(nticks=15, exponentformat='none', title="Corte de Agua [%]", titlefont=dict(color="black", size=12), tickfont=dict(color="black", size=9),
                anchor="x",
                overlaying="y",
                side="right",
                position= 1),
            yaxis4=dict(nticks=15,exponentformat='none', title="RAA [sm3/sm3]", titlefont=dict(color="black", size=12), tickfont=dict(color="black", size=9),
                anchor="free",
                overlaying="y",
                side="right",
                position=1))
        sal_raa_plot_2.update_yaxes(rangemode="tozero")
        sal_raa_plot_2.update_xaxes(range=['1970', '2022'])
        if st.checkbox('Salinidad en Escala Semilogarítmica') == True:
            sal_raa_plot_2
        
        ### Acumuladas ###
        cum_prod = st.columns(3)
        cum_oil_plot = px.ecdf(pozo, x="Fecha", y="Aceite mensual (bpm)", ecdfnorm=None)
        cum_oil_plot.update_layout(font=dict(family="sans-serif", size=10, color="black"), hovermode="x unified", title=f'Producción Acumulada de Aceite {filt_pozos}', legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1), margin={"r":0,"t":100,"l":0,"b":0}, height=300, width=350)
        cum_oil_plot.update_traces(marker=dict(color='green'))
        cum_oil_plot.update_yaxes(title_text="<b>Aceite [bbls]</b>", nticks=10)
        cum_oil_plot.update_xaxes(title_text="<b>Año</b>", nticks=10)
        cum_prod[0].plotly_chart(cum_oil_plot)
        cum_water_plot = px.ecdf(pozo, x="Fecha", y="Agua mensual (bpm)", ecdfnorm=None)
        cum_water_plot.update_layout(font=dict(family="sans-serif", size=10, color="black"), hovermode="x unified", title=f'Producción Acumulada de Agua {filt_pozos}', legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1), margin={"r":0,"t":100,"l":0,"b":0}, height=300, width=350)
        cum_water_plot.update_traces(marker=dict(color='blue'))
        cum_water_plot.update_yaxes(title_text="<b>Agua [bbls]</b>", nticks=10)
        cum_water_plot.update_xaxes(title_text="<b>Año</b>", nticks=10)
        cum_prod[1].plotly_chart(cum_water_plot)
        cum_gas_plot = px.ecdf(pozo, x="Fecha", y="Gas mensual (ft3/m)", ecdfnorm=None)
        cum_gas_plot.update_layout(font=dict(family="sans-serif", size=10, color="black"), hovermode="x unified", title=f'Producción Acumulada de Gas {filt_pozos}', legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1), margin={"r":0,"t":100,"l":0,"b":0}, height=300, width=350)
        cum_gas_plot.update_traces(marker=dict(color='red'))
        cum_gas_plot.update_yaxes(title_text="<b>Gas [MMPCPD]</b>", nticks=10)
        cum_gas_plot.update_xaxes(title_text="<b>Año</b>", nticks=10)
        cum_prod[2].plotly_chart(cum_gas_plot)
        
        st.subheader('Descripción de pozo')
        st.caption("Ultima medición de producción: " + str(pozo['Fecha'].iloc[-1]))
        st.caption("Qo Inicial: " + str(round(pozo['Aceite diario (bpd)'].iloc[0],1)))
        st.caption("Qo Final: " + str(round(pozo['Aceite diario (bpd)'].iloc[-1],1)))
        st.caption("Qw Inicial: " + str(round(pozo['Agua diario (bpd)'].iloc[0],4)))
        st.caption("Qw Final: " + str(round(pozo['Agua diario (bpd)'].iloc[-1],4)))
        st.caption("Qg Inicial: " + str(round(pozo['Gas diario (ft3/d)'].iloc[0],4))) 
        st.caption("Qg Final: " + str(round(pozo['Gas diario (ft3/d)'].iloc[-1],4)))
        st.caption("Producción acumulada de aceite: " + str(round(pozo['Aceite mensual (bpm)'].sum()/MM,2)) + " Millones de Barriles")
        st.caption("Producción acumulada de agua: " + str(round(pozo['Agua mensual (bpm)'].sum()/MM,2)) + " Millones de Barriles")
        st.caption("Producción acumulada de gas: " + str(round(pozo['Gas mensual (ft3/m)'].sum()/B,2)) + " Billones (10^9) de Pies Cúbicos")
        
    with st.expander('GRÁFICADOR MULTIPOZO'):
        # multiselector_pozos = st.multiselect('Pozos a gráficar', pozos)
        # multiplot_prod = prod[prod['Pozo'] == multiselector_pozos]
        # multiplot_prod      
        # multiselector_pozos
        def plot():

            df = prod.copy()
        
            wlist = df["Pozo"].unique().tolist()
        
            wells = st.multiselect("Select well", wlist)
            # st.header("You selected: {}".format(", ".join(wells)))
        
            dfs = {well: df[df["Pozo"] == wells] for well in wells}
        
            fig = go.Figure()
            for country, df in dfs.items():
                fig = fig.add_trace(go.Scatter(x=df["Fecha"], y=df["Aceite diario (bpd)"], name=wells))
        
            st.plotly_chart(fig)
        
        
        plot()
            
################################################################################################################################################################
