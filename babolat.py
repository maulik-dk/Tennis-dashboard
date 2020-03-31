import dash
import datetime
import dash_core_components as dcc
import dash_html_components as html
import flask
import werkzeug
import plotly.graph_objs as go
import pandas as pd
import plotly
import os
import base64
import numpy as np
from dash.dependencies import Input, Output, State
import dash_table
import dash_auth
import dash_table.FormatTemplate as FormatTemplate
from dash_table.Format import Sign
import io
from flask import send_file,request, redirect
import urllib.parse
import gspread
from oauth2client.service_account import ServiceAccountCredentials

"""
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)
# Find a workbook by name and open the first sheet
# Make sure you use the right name here.
log = client.open("Tennis Shipment User Authentication").sheet1
# Extract and print all of the values
list_of_hashes = log.get_all_records()
babolatlog=[d for d in list_of_hashes if d['brand'] =='babolat']
babolatsecurity = {x['username']:x['password']for x in babolatlog}
wilsonlog=[d for d in list_of_hashes if d['brand'] =='wilson']
wilsonsecurity={x['username']:x['password']for x in wilsonlog}

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app=dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.scripts.config.serve_locally = True # needed to upload images
app.config.suppress_callback_exceptions = True # needed to create multiple pages
server=app.server
auth = dash_auth.BasicAuth(
    app,
    babolatsecurity)
"""
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app=dash.Dash(__name__, external_stylesheets=external_stylesheets)  

url='https://github.com/Saahil28/babolat/blob/master/Tennis5.xlsx?raw=true'
xl=pd.ExcelFile(url)
Total=xl.parse('DATA')# taking each excel tab and putting it into its own dataframe



def set_half(row):
    if row["Quarter"] == "Q1":
        return str(row["Annual"])+'-06-30'
    elif row["Quarter"] == "Q2":
        return str(row["Annual"])+ '-06-30'
    else:
        return str(row["Annual"])+ '-12-31'

Total= Total.assign(Half=Total.apply(set_half, axis=1))

def set_quarter(row):
    if row["Quarter"] == "Q1":
        return str(row["Annual"])+"-03-31"
    elif row["Quarter"] == "Q2":
        return str(row["Annual"])+"-06-30"
    elif row["Quarter"] == "Q3":
        return str(row["Annual"])+"-09-30"
    else:
        return str(row["Annual"])+"-12-31"

Total=Total.assign(Quarters=Total.apply(set_quarter, axis=1))

#Creating lists for dropdowns
Country=Total['Country_Name'].unique()
Continent=Total['Region_Name'].unique()
Equipment=Total['Equipment_Type'].unique()
Year=Total['Annual'].unique()
Quarter=Total['Quarter'].unique()
Equipment_Category=Total['Equipment_Category'].unique()
Brand=Total['Manufacturer_Name'].unique()

#Creating Hierarchies from Lists
Region={'Americas': ['Argentina', 'Brazil', 'Canada', 'USA'],
'Europe':['Austria', 'Belgium', 'Czech Republic', 'Denmark', 'Finland', 'France', 'Germany', 'Italy', 'Netherlands', 'Norway', 'Poland', 'Russia', 'Spain', 'Sweden', 'Switzerland', 'UK', 'Total Europe'],
'Australasia': ['Australia', 'China', 'Hong Kong', 'India', 'Japan', 'South Korea'],'Other':['Total Europe', 'Total Primary Markets','Total Primary Markets With Japan','South Africa']}

Equipments={'Tennis Balls': ['Total Balls','Premium (Dozens)','Standard (Dozens)','Total Transition Balls','Red Foam Balls','Red Felt Balls','Orange Balls','Green Balls'],
'Tennis Racquets': ['Adult Racquets','Junior Racquets','Total Value','Recreational','Performance','Adult Value','Junior Value','Recreational 1','Recreational 2','Total Racquets'],
'Tennis String': ['Sets (Total)','Polyester','Synthetic','Multifilament','Natural Gut','Hybrid']}

Time_Frame={"Annual","Half","Quarters"}

Measures={'Units','Value','Currency_Share_Percentage','Unit_Share_Percentage','Average_Price'}

Currency={'USD($)','Euros','Local_Currency'}


colors={'background':'#EDEDED','text':'#000000'}
colors['text']

image_filename2 = 'smsusa.jpg'
image_filename3='TIA.jpg'
encoded_image2 = base64.b64encode(open(image_filename2, 'rb').read()) #encoding images into the app layout
encoded_image3 = base64.b64encode(open(image_filename3, 'rb').read())


#setTabs

tabs_styles = {
    'height': '44px'
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '6px'
}

app.layout =html.Div(children=[
html.H1('Global Tennis Shipments Dashboard', style={'textAlign': 'center', 'fontSize': 20, 'font-family': 'Arial'}),
html.Div([html.Img(src='data:image/png;base64,{}'.format(encoded_image2.decode()))], style={'textAlign': 'center'}),
html.Div([
    dcc.Tabs(id="tabs", children=[
        dcc.Tab(label='Master', children=[
            html.Div([
                html.H3('Region:', style={'paddingRight': '30px','fontSize':16,'font-family': 'Arial',}), #labeling dropdowns
                dcc.Dropdown(
                id='continent',
                options=[
                {'label': i, 'value': i} for i in Region.keys()],
                value='Europe'
                ),
                dcc.Dropdown(
                    id='country', #setting up the id to connect to the dash callback ( connecting checklist to figure)
                )],style={'width':'12%','display':'inline-block','font-family': 'Arial'}),
            html.Div([
                html.H3('Equipment:', style={'fontSize':16,'font-family': 'Arial'}),
                dcc.Dropdown(
                id='Equipment_Type', #setting up the id to connect to the dash callback ( connecting checklist to figure)
                options=[
                {'label': i, 'value': i} for i in Equipments.keys()],
                value='Tennis Balls'#default checked items
                ),
                dcc.Dropdown(
                    id='Equipment_Sub_Category',
                )], style={'width':'12%','display':'inline-block','font-family': 'Arial'}),
            html.Div([
                html.H3('Measure:', style={'fontSize':16,'font-family': 'Arial'}),
                dcc.Dropdown(
                id='Currency',
                options=[{'label': 'Local Currency', 'value': 'Local_Currency'},
                {'label': 'Euros', 'value': 'Euros'},
                {'label': 'USD ($)', 'value': 'USD ($)'}],
                value='Euros'#default checked items
                ),
                dcc.Dropdown(
                id='Measure',
                options=[{'label': 'Units', 'value': 'Units'},
                {'label': 'Value', 'value': 'Value'},
                {'label': 'Average Price', 'value': 'Average_Price'},
                {'label': 'Currency Share Percentage', 'value': 'Currency_Share'},
                {'label': 'Unit Share Percentage', 'value': 'Unit_Share'}],
                value='Value'#default checked items
                )
                ], style={'width':'15%','display':'inline-block','font-family': 'Arial'}),
            html.Div([
                html.H3('Time Frame:', style={'fontSize':16,'font-family': 'Arial'}),
                dcc.Dropdown(
                id='Time',
                options=sorted([
                {'label': i, 'value': i} for i in Time_Frame], key = lambda x: x['label']),
                value='Quarters'#default checked items
                ),
                dcc.Dropdown(
                    id='brand',
                    options=[{'label': 'Brand and Market', 'value':'Market'},
                            {'label': 'Brand', 'value':'Brand'}],
                    value='Market'
                    )], style={'display':'inline-block','width':'15%','font-family': 'Arial'}),
            html.Div([
                    html.H3('Last Period Change', style={'textAlign': 'center','paddingRight': '30px','fontSize':16,'font-family': 'Arial'}),
                    dash_table.DataTable(id='upload',data=[],
                    columns=[{'name':'Industry','id':'Industry'},
                            {'name':'Units','id':'Units'},
                            {'name':'Value','id':'Value'},
                            {'name':'Avg Price','id':'Average Price'},
                            {'name':'Unit Share','id':'Unit Share'},
                            {'name':'Value Share','id':'Value Share'}],
                    style_cell={'font-family': 'Arial','minWidth': '97px', 'width': '97px', 'maxWidth': '97px','textAlign': 'center'},
                    style_header={'font-family': 'Arial'})],style={'display':'inline-block','font-family': 'Arial'}),
            html.Div([
                dcc.Graph(id='linear',config={'modeBarButtonsToRemove':['pan2d', 'lasso2d','zoom2d','zoomIn2d','zoomOut2d','autoScale2d','resetScale2d','select2d','hoverClosestCartesian','hoverCompareCartesian','sendDataToCloud','toggleSpikelines']})
                ]),
            html.Div([dcc.RangeSlider(
                id='my-range-slider',
                min=2010,
                max=2019,
                marks={2010: 2010,
                2011: 2011,
                2012: 2012,
                2013: 2013,
                2014: 2014,
                2015: 2015,
                2016: 2016,
                2017: 2017,
                2018: 2018,
                2019: 2019
                },
                value=[2018,2019],
                step=1,
                )],style={'width':'80%','padding-left':'10%','padding-right':'10%'}),
                html.Div([html.A(html.Button("CSV", id='download-button'), id='download-link')],
                style={'font-family': 'Arial','textAlign': 'right','display':'inline-block'})], style=tab_style, selected_style=tab_selected_style),
    dcc.Tab(label='Country Comparison',
    children=[
        html.Div([
            html.H3('Region:', style={'paddingRight': '30px','fontSize':18}), #labeling dropdowns
            dcc.Dropdown(
            id='continent2',
            options=[
            {'label': i, 'value': i} for i in Region.keys()],
            value='Europe'
            ),
            dcc.Dropdown(
                id='country2',
                value=['Austria','Spain'],
                multi=True
            )],style={'width':'14%','display':'inline-block'}),
        html.Div([
            html.H3('Equipment:', style={'paddingRight': '30px','fontSize':18}),
            dcc.Dropdown(
            id='Equipment_Type2', #setting up the id to connect to the dash callback ( connecting checklist to figure)
            options=[
            {'label': i, 'value': i} for i in Equipments.keys()],
            value='Tennis String'#default checked items
            ),
            dcc.Dropdown(
                id='Equipment_Sub_Category2',
            )], style={'width':'14%','display':'inline-block'}),
        html.Div([
            html.H3('Time Frame:', style={'paddingRight': '30px','fontSize':18}),
            dcc.Dropdown(
            id='Time2',
            options=[
            {'label': i, 'value': i} for i in Time_Frame],
            value='Quarters'#default checked items
            )], style={'width':'14%','display':'inline-block'}),
        html.Div([
            html.H3('Currency:', style={'paddingRight': '30px','fontSize':18}),
            dcc.Dropdown(
            id='Currency2',
            options=[{'label': 'Local Currency', 'value': 'Local_Currency'},
            {'label': 'Euros', 'value': 'Euros'},
            {'label': 'USD ($)', 'value': 'USD ($)'}],
            value='Euros'#default checked items
            )], style={'width':'14%','display':'inline-block'}),
        html.Div([
            html.H3('Measure:', style={'paddingRight': '30px','fontSize':18}),
            dcc.Dropdown(
            id='Measure2',
            options=[{'label': 'Units', 'value':'Units'},
            {'label': 'Value', 'value':'Value'},
            {'label': 'Average Price', 'value': 'Average_Price'},
            {'label': 'Currency Share Percentage', 'value':'Currency_Share'},
            {'label': 'Unit Share Percentage', 'value':'Unit_Share'}],
            value='Value'#default checked items
            )
            ], style={'width':'20%','display':'inline-block'}),
        html.Div([
            dcc.Graph(id='linear2',config={'modeBarButtonsToRemove':['pan2d', 'lasso2d','zoom2d','zoomIn2d','zoomOut2d','autoScale2d','resetScale2d','select2d','hoverClosestCartesian','hoverCompareCartesian','sendDataToCloud','toggleSpikelines']})]),
        html.Div([dcc.RangeSlider(
            id='my-range-slider2',
            min=2010,
            max=2019,
            marks={2010: 2010,
            2011: 2011,
            2012: 2012,
            2013: 2013,
            2014: 2014,
            2015: 2015,
            2016: 2016,
            2017: 2017,
            2018: 2018,
            2019: 2019
            },
            step=1,
            value=[2018,2019])],style={'width':'80%','padding-left':'10%','padding-right':'10%'}),
            html.Div([html.A(html.Button("CSV", id='download-button2'), id='download-link2')], style={'font-family': 'Arial','textAlign': 'right','display':'inline-block'})
        ], style=tab_style, selected_style=tab_selected_style)])])])

@app.callback(
    dash.dependencies.Output('country', 'options'),
    [dash.dependencies.Input('continent', 'value')])

def selected_continent_options(selected_continent):
    return [{'label': i, 'value': i} for i in Region[selected_continent]]

@app.callback(
    dash.dependencies.Output('country', 'value'),
    [dash.dependencies.Input('country', 'options')])
def set_cities_value(available_options):
    return available_options[0]['value']

    # These first two callbacks link the continent dropdown to Area for the first tab


@app.callback(
    dash.dependencies.Output('country2', 'options'),
    [dash.dependencies.Input('continent2', 'value')])
def selected_continent_options(selected_continent):
    return [{'label': i, 'value': i} for i in Region[selected_continent]]

@app.callback(
    dash.dependencies.Output('country2', 'value'),
    [dash.dependencies.Input('country2', 'options')])
def set_cities_value(available_options):
    return available_options[0]['value']

    # These second two callbacks link the continent dropdown to Area for the second tab

@app.callback(
    dash.dependencies.Output('Equipment_Sub_Category', 'options'),
    [dash.dependencies.Input('Equipment_Type', 'value')])
def selected_equipment_options(selected_equipment):
    return [{'label': i, 'value': i} for i in Equipments[selected_equipment]]

@app.callback(
    dash.dependencies.Output('Equipment_Sub_Category', 'value'),
    [dash.dependencies.Input('Equipment_Sub_Category', 'options')])
def set_equipment_value(available_options):
    return available_options[0]['value']

    # these next two callbacks link equipment to equipment sub category for the first tab

@app.callback(
    dash.dependencies.Output('Equipment_Sub_Category2', 'options'),
    [dash.dependencies.Input('Equipment_Type2', 'value')])
def selected_equipment_options(selected_equipment):
    return [{'label': i, 'value': i} for i in Equipments[selected_equipment]]

@app.callback(
    dash.dependencies.Output('Equipment_Sub_Category2', 'value'),
    [dash.dependencies.Input('Equipment_Sub_Category2', 'options')])
def set_equipment_value(available_options):
    return available_options[0]['value']

    # these next two callbacks link equipment to equipment sub category for the second tab


@app.callback(dash.dependencies.Output('linear','figure'),
    [dash.dependencies.Input('country','value'),
    dash.dependencies.Input('Equipment_Sub_Category','value'),
    dash.dependencies.Input('Time','value'),
    dash.dependencies.Input('Currency','value'),
    dash.dependencies.Input('my-range-slider','value'),
    dash.dependencies.Input('brand','value'),
    dash.dependencies.Input('Measure','value'),
    ])

def update_graph(country_name,category_name,time_name,currency_name,year_name,brand_name,measure_name):
        Total1=Total[Total['Country_Name'] == country_name]
        Total2=Total1[Total1['Equipment_Category'] ==category_name]
        year_range=list(range(year_name[0],year_name[1]+1, 1))
        Total3=Total2[Total2.Annual.isin(year_range)]
        Total4=Total3[Total3['Currency'] ==currency_name]
        Total5=Total4[Total4['Manufacturer_Name'] =='Babolat']
        Total5=Total5.groupby(time_name).sum().reset_index()
        Total5['Average_Price']=Total5['Value']/Total5['Units']
        Total5['Average_Price'] = Total5['Average_Price'].astype(float).round(1)
        AllBrandsUnits=Total4.groupby(time_name)['Units'].sum().reset_index()
        AllBrandsValues=Total4.groupby(time_name)['Value'].sum().reset_index()
        AllBrandsUnits.rename(columns={"Units": "Units1"},inplace=True)
        AllBrandsValues.rename(columns={"Value": "Value1"},inplace=True)
        Total5=pd.merge(Total5,AllBrandsUnits, on=time_name)
        Total5=pd.merge(Total5,AllBrandsValues, on=time_name)
        Total5['Average_Price1']=Total5['Value1']/Total5['Units1']
        Total5['Average_Price1'] = Total5['Average_Price1'].astype(float).round(1)
        Total5['Unit_Share']=Total5['Units']/Total5['Units1']
        Total5['Currency_Share']=Total5['Value']/Total5['Value1']
        Total5['Unit_Share']=Total5['Units']/Total5['Units1']
        Total5['Currency_Share']=Total5['Value']/Total5['Value1']
        xdata=Total5[time_name]
        ydata=Total5[measure_name]
        xvalue=xdata
        yvalue=ydata
        xlist=xdata.tolist()
        ylist=ydata.tolist()
        traces=[]
        trace1=go.Scatter(x=xvalue,y=yvalue,
                    mode='lines+markers',
                    marker=dict(
                    color='rgb(0,191,255)', # code for sky blue 0,191,255
                    ),opacity=0.6,name='Babolat',
                    line={'width':4})
        if (measure_name=='Units') & (brand_name=='Market'):
            y2=Total5[measure_name + '1']
            trace2=go.Scatter(x=xvalue,y=y2,
                    mode='lines+markers',
                    opacity=0.6,name='Market',
                    line={'width':4})
            traces.append(trace1)
            traces.append(trace2)
        elif (measure_name=='Value') & (brand_name=='Market'):
            y2=Total5[measure_name + '1']
            trace2=go.Scatter(x=xvalue,y=y2,
                    mode='lines+markers',
                    opacity=0.6,name='Market',
                    line={'width':4})
            traces.append(trace1)
            traces.append(trace2)
        elif (measure_name=='Average_Price') & (brand_name=='Market'):
            y2=Total5[measure_name + '1']
            trace2=go.Scatter(x=xvalue,y=y2,
                    mode='lines+markers',
                    opacity=0.6,name='Market')
            traces.append(trace1)
            traces.append(trace2)
        else:
            traces.append(trace1)

        if measure_name =='Unit_Share':
            layout=go.Layout(xaxis={'title':'Time Frame','tickvals':xlist,'tickfont':{'size':14}},
                                    yaxis={'title':'Unit Share Percentage','tickformat':',.0%','tickfont':{'size':14}},
                                    hovermode='closest')
        elif measure_name =='Currency_Share':
            layout=go.Layout(xaxis={'title':'Time Frame','tickvals':xlist,'tickfont':{'size':14}},
                                    yaxis={'title':'Currency Share Percentage','tickformat':',.0%','tickfont':{'size':14}},
                                    hovermode='closest')

        elif measure_name =='Average_Price':
            layout=go.Layout(xaxis={'title':'Time Frame','tickvals':xlist,'tickfont':{'size':14}},
                                    yaxis={'title':'Average Price','tickformat':'$','dtick':'10','tickfont':{'size':14}},
                                    hovermode='closest')

        else:
            layout=go.Layout(xaxis={'title':'Time Frame','tickvals':xlist,'tickfont':{'size':14}},
                                yaxis={'title': measure_name,'tickfont':{'size':14}},
                                hovermode='closest')
        figure={'data':traces,'layout':layout}
        return figure


@app.callback(
    dash.dependencies.Output('linear2','figure'),
    [dash.dependencies.Input('country2','value'),
    dash.dependencies.Input('Equipment_Sub_Category2','value'),
    dash.dependencies.Input('Time2','value'),
    dash.dependencies.Input('Currency2','value'),
    dash.dependencies.Input('my-range-slider2','value'),
    dash.dependencies.Input('Measure2','value'),
    ])

def update_graph(country_name2,category_name2,time_name2,currency_name2,year_name2,measure_name2):
        traces=[]
        Total1=Total[Total['Equipment_Category'] ==category_name2]
        columns=list(range(year_name2[0],year_name2[1]+1, 1))
        Total2=Total1[Total1.Annual.isin(columns)]
        Total3=Total2[Total2['Currency'] ==currency_name2]
        for country_name2 in country_name2:
            Total4=Total3[Total3['Country_Name'] == country_name2]
            Total5=Total4[Total4['Manufacturer_Name'] =='Babolat']
            Total5=Total5.groupby(time_name2).sum().reset_index()
            Total5['Average_Price']=Total5['Value']/Total5['Units']
            AllBrandsUnits=Total4.groupby(time_name2)['Units'].sum().reset_index()
            AllBrandsValues=Total4.groupby(time_name2)['Value'].sum().reset_index()
            AllBrandsUnits.rename(columns={"Units": "Units1"},inplace=True)
            AllBrandsValues.rename(columns={"Value": "Value1"},inplace=True)
            Total5=pd.merge(Total5,AllBrandsUnits, on=time_name2)
            Total5=pd.merge(Total5,AllBrandsValues, on=time_name2)
            x=Total5[time_name2]
            y=Total5[measure_name2]
            trace=go.Scatter(x=x,y=y,
                        mode='lines+markers',
                        name=country_name2,
                        opacity=0.6,
                        line={'width':4})
            traces.append(trace)
            xlist=x.tolist()
            ylist=y.tolist()
        if measure_name2 =='Unit_Share':
            layout=go.Layout(xaxis={'title':'Time Frame','tickvals':xlist,'tickfont':{'size':14}},
                                    yaxis={'title':'Unit Share Percentage','tickformat':',.0%','tickfont':{'size':14}},
                                    hovermode='closest')
        elif measure_name2 =='Currency_Share':
            layout=go.Layout(xaxis={'title':'Time Frame','tickvals':xlist,'tickfont':{'size':14}},
                                    yaxis={'title':'Currency Share Percentage','tickformat':',.0%','tickfont':{'size':14}},
                                    hovermode='closest')

        elif measure_name2 =='Average_Price':
            layout=go.Layout(xaxis={'title':'Time Frame','tickvals':xlist,'tickfont':{'size':14}},
                                    yaxis={'title':'Average Price','tickformat':'$','tickfont':{'size':14}},
                                    hovermode='closest')
        else:
            layout=go.Layout(xaxis={'title':'Time Frame','tickvals':xlist,'tickfont':{'size':14}},
                                yaxis={'title': measure_name2,'tickfont':{'size':14}},
                                hovermode='closest')
        return {'data':traces,
                'layout':layout}

@app.callback(dash.dependencies.Output('upload','data'),
    [dash.dependencies.Input('country','value'),
    dash.dependencies.Input('Equipment_Sub_Category','value'),
    dash.dependencies.Input('Time','value'),
    dash.dependencies.Input('Currency','value'),
    dash.dependencies.Input('brand','value'),
    dash.dependencies.Input('Measure','value'),
    ])

def update_table(country_name,category_name,time_name,currency_name,brand_name,measure_name):
        Total1=Total[Total['Country_Name'] == country_name]
        Total2=Total1[Total1['Equipment_Category'] ==category_name]
        Total3=Total2[Total2['Currency'] ==currency_name]
        Total4=Total3[(Total3['Annual']==2018) | (Total3['Annual']==2019)]
        Total5=Total4[Total4['Manufacturer_Name'] =='Babolat']
        Total5=Total5.groupby(time_name).sum().reset_index()
        Total5['Average_Price']=Total5['Value']/Total5['Units']
        Total5['Average_Price'] = Total5['Average_Price'].astype(float).round(2)
        AllBrandsUnits=Total4.groupby(time_name)['Units'].sum().reset_index()
        AllBrandsValues=Total4.groupby(time_name)['Value'].sum().reset_index()
        AllBrandsUnits.rename(columns={"Units": "Units1"},inplace=True)
        AllBrandsValues.rename(columns={"Value": "Value1"},inplace=True)
        Total5=pd.merge(Total5,AllBrandsUnits, on=time_name)
        Total5=pd.merge(Total5,AllBrandsValues, on=time_name)
        Total5['Unit_Share']=Total5['Units']/Total5['Units1']
        Total5['Currency_Share']=Total5['Value']/Total5['Value1']
        Total5['Unit_Share']=Total5['Units']/Total5['Units1']
        Total5['Currency_Share']=Total5['Value']/Total5['Value1']
        if time_name=='Annual':
            unitsdata=Total5.groupby(time_name)['Units'].sum().reset_index()
            data_table_units=(unitsdata['Units'].iloc[-1] - unitsdata['Units'].iloc[0])/ unitsdata['Units'].iloc[-1]
            valuedata=Total5.groupby(time_name)['Value'].sum().reset_index()
            data_table_value=(valuedata['Value'].iloc[-1] - valuedata['Value'].iloc[0])/ valuedata['Value'].iloc[-1]
            unitsharedata=Total5.groupby(time_name)['Unit_Share'].sum().reset_index()
            data_table_unitshare=(unitsharedata['Unit_Share'].iloc[-1] - unitsharedata['Unit_Share'].iloc[0])/ unitsharedata['Unit_Share'].iloc[-1]
            valuesharedata=Total5.groupby(time_name)['Currency_Share'].sum().reset_index()
            data_table_valueshare=(valuesharedata['Currency_Share'].iloc[-1] - valuesharedata['Currency_Share'].iloc[0])/ valuesharedata['Currency_Share'].iloc[-1]
            pricedata=Total5.groupby(time_name)['Average_Price'].mean().reset_index()
            data_table_average=(pricedata['Average_Price'].iloc[-1] - pricedata['Average_Price'].iloc[0])/ pricedata['Average_Price'].iloc[-1]

            #market data table data
            AllBrands=Total4.groupby(time_name).sum().reset_index()
            AllBrands['Average_Price']=AllBrands['Value']/AllBrands['Units']
            AllBrands['Average_Price'] = AllBrands['Average_Price'].astype(float).round(2)
            data_table_market_value=(AllBrands['Value'].iloc[-1] - AllBrands['Value'].iloc[0])/ AllBrands['Value'].iloc[-1]
            data_table_market_units=(AllBrands['Units'].iloc[-1] - AllBrands['Units'].iloc[0])/ AllBrands['Units'].iloc[-1]
            data_table_market_price=(AllBrands['Average_Price'].iloc[-1] - AllBrands['Average_Price'].iloc[0])/ AllBrands['Average_Price'].iloc[-1]

        else:
            Total5[time_name]=pd.to_datetime(Total5[time_name])
            Total5['Month'] = Total5[time_name].map(lambda x: x.strftime('%m'))
            Total6= Total5.groupby('Month')['Units'].diff().fillna(0)
            data_table_units=Total6.iloc[-1]/Total5['Units'].iloc[-1]
            Total6=Total5.groupby('Month')['Value'].diff().fillna(0)
            data_table_value=Total6.iloc[-1]/Total5['Value'].iloc[-1]
            Total6=Total5.groupby('Month')['Unit_Share'].diff().fillna(0)
            data_table_unitshare=Total6.iloc[-1]/Total5['Unit_Share'].iloc[-1]
            Total6=Total5.groupby('Month')['Currency_Share'].diff().fillna(0)
            data_table_valueshare=Total6.iloc[-1]/Total5['Currency_Share'].iloc[-1]
            Total6=Total5.groupby('Month')['Average_Price'].diff().fillna(0)
            data_table_average=Total6.iloc[-1]/Total5['Average_Price'].iloc[-1]

            AllBrands=Total4.groupby(time_name).sum().reset_index()
            AllBrands['Average_Price']=AllBrands['Value']/AllBrands['Units']
            AllBrands['Average_Price'] = AllBrands['Average_Price'].astype(float).round(2)
            AllBrands[time_name]=pd.to_datetime(AllBrands[time_name])
            AllBrands['Month'] = AllBrands[time_name].map(lambda x: x.strftime('%m'))
            Total6= AllBrands.groupby('Month')['Units'].diff().fillna(0)
            data_table_market_units=Total6.iloc[-1]/AllBrands['Units'].iloc[-1]
            Total6= AllBrands.groupby('Month')['Average_Price'].diff().fillna(0)
            data_table_market_price=Total6.iloc[-1]/AllBrands['Average_Price'].iloc[-1]
            Total6= AllBrands.groupby('Month')['Value'].diff().fillna(0)
            data_table_market_value=Total6.iloc[-1]/AllBrands['Value'].iloc[-1]

        d=[{"Industry": "Your Brand","Units": data_table_units, "Value": data_table_value, "Average Price": data_table_average, "Unit Share": data_table_unitshare , "Value Share":data_table_valueshare},
           {"Industry": "Market","Units": data_table_market_units, "Value": data_table_market_value, "Average Price": data_table_market_price}]
        new_data_table=pd.DataFrame(d,index=["Brand","Market"])
        new_data_table=new_data_table[["Industry","Units","Value","Average Price","Unit Share","Value Share"]]
        data=new_data_table.to_dict('rows')
        columns=[{'id': c, 'name': c, 'type': 'numeric', 'format': FormatTemplate.percentage(1).sign(Sign.positive)} for c in new_data_table.columns]
        return data


#connecting the column formatting of the datatable from the data collected
@app.callback(dash.dependencies.Output('upload','columns'),
             [dash.dependencies.Input('upload','data')])
def update_column(data_name):
    new_data_table=pd.DataFrame.from_dict(data_name)
    new_data_table=new_data_table[["Industry","Units","Value","Average Price","Unit Share","Value Share"]]
    columns=[{'id': c, 'name': c, 'type': 'numeric', 'format': FormatTemplate.percentage(1).sign(Sign.positive)} for c in new_data_table.columns]
    return columns


@app.callback(
    dash.dependencies.Output('download-link', 'href'),
    [dash.dependencies.Input('country','value'),
      dash.dependencies.Input('Equipment_Sub_Category','value'),
      dash.dependencies.Input('Time','value'),
      dash.dependencies.Input('Currency','value'),
      dash.dependencies.Input('my-range-slider','value'),
      dash.dependencies.Input('brand','value'),
      dash.dependencies.Input('Measure','value'),
      ])

def update_link(country_name,category_name,time_name,currency_name,year_name,brand_name,measure_name):
    return '/dash/urlToDownload?value={}/{}/{}/{}/{}/{}/{}'.format((country_name),(category_name),(time_name),
                                                                  (currency_name),(str(year_name[0])),(str(year_name[1]))
                                                                  ,(measure_name))
@app.server.route('/dash/urlToDownload')
def download_csv():
    value = flask.request.args.get('value')
#here is where I split the value
    value = value.split('/')
    country_name=value[0]
    category_name=value[1]
    time_name=value[2]
    currency_name=value[3]
    yearvalue=value[4]
    print(time_name)
    print(yearvalue)
    yearvalue=int(yearvalue)
    yearvalue2=value[5]
    yearvalue2=int(yearvalue2)
    measure_name=value[6]
#if you use Python 3, use io.StringIO()
    Total1=Total[Total['Country_Name'] == country_name]
    Total2=Total1[Total1['Equipment_Category'] ==category_name]
    year_range=list(range(yearvalue,yearvalue2+1, 1))
    Total3=Total2[Total2.Annual.isin(year_range)]
    Total4=Total3[Total3['Currency'] ==currency_name]
    Total5=Total4[Total4['Manufacturer_Name'] =='Babolat']
    Total5=Total5.groupby(time_name).sum().reset_index()
    Total5['Average_Price']=Total5['Value']/Total5['Units']
    Total5['Average_Price'] = Total5['Average_Price'].astype(float).round(2)
    AllBrandsUnits=Total4.groupby(time_name)['Units'].sum().reset_index()
    AllBrandsValues=Total4.groupby(time_name)['Value'].sum().reset_index()
    AllBrandsUnits.rename(columns={"Units": "Market_Units"},inplace=True)
    #rounding the values to decimal points of 2
    AllBrandsUnits['Market_Units']=pd.Series([round(val, 2) for val in AllBrandsUnits['Market_Units']], index = AllBrandsUnits.index)
    AllBrandsValues.rename(columns={"Value": "Market_Value"},inplace=True)
    AllBrandsValues['Market_Value']=pd.Series([round(val, 2) for val in AllBrandsValues['Market_Value']], index = AllBrandsValues.index)
    Total5=pd.merge(Total5,AllBrandsUnits, on=time_name)
    Total5=pd.merge(Total5,AllBrandsValues, on=time_name)
    Total5['Market_Average_Price']=Total5['Market_Value']/Total5['Market_Units']
    Total5['Market_Average_Price'] = Total5['Market_Average_Price'].astype(float).round(2)
    Total5['Unit_Share']=Total5['Units']/Total5['Market_Units']
    #formatting the numbers to percents in the column for the excel sheet
    Total5['Unit_Share']=pd.Series(["{0:.2f}%".format(val * 100) for val in Total5['Unit_Share']], index = Total5.index)
    Total5['Currency_Share']=Total5['Value']/Total5['Market_Value']
    Total5['Currency_Share']=pd.Series(["{0:.2f}%".format(val * 100) for val in Total5['Currency_Share']], index = Total5.index)
    print(Total5)
    # storing string io in a variable and assigning a dataframe to it
    str= io.StringIO()
    Total5.to_csv(str)
    mem = io.BytesIO()
    #converting string to bytes and adding the dataframe to it before closing
    mem.write(str.getvalue().encode('utf-8'))
    mem.seek(0)
    str.close()
    return flask.send_file(mem,
                       mimetype='text/csv',
                       attachment_filename='downloadFile.csv',
                       as_attachment=True)




@app.callback(
    dash.dependencies.Output('download-link2', 'href'),
    [dash.dependencies.Input('country2','value'),
    dash.dependencies.Input('Equipment_Sub_Category2','value'),
    dash.dependencies.Input('Time2','value'),
    dash.dependencies.Input('Currency2','value'),
    dash.dependencies.Input('my-range-slider2','value'),
    dash.dependencies.Input('Measure2','value'),
    ])

def update_link(country_name2,category_name2,time_name2,currency_name2,year_name2,measure_name2):
    return '/dash/urlToDownload2?value={}/{}/{}/{}/{}/{}/{}/{}'.format((country_name2[0]),(country_name2[1]),
                                                                  (category_name2),(time_name2),(currency_name2),
                                                                  (str(year_name2[0])),(str(year_name2[1])),
                                                                  (measure_name2))

@app.server.route('/dash/urlToDownload2')
def download_csv2():
        value = flask.request.args.get('value')
    #here is where I split the value
        value = value.split('/')
        country_name=value[0]
        country_name2=value[1]
        category_name=value[2]
        time_name=value[3]
        currency_name=value[4]
        yearvalue=value[5]
        print(time_name)
        print(yearvalue)
        yearvalue=int(yearvalue)
        yearvalue2=value[6]
        yearvalue2=int(yearvalue2)
        measure_name=value[7]
        Total1=Total[Total['Equipment_Category'] ==category_name]
        columns=list(range(yearvalue,yearvalue2+1, 1))
        Total2=Total1[Total1.Annual.isin(columns)]
        Total3=Total2[Total2['Currency'] ==currency_name]
        Total4=Total3[(Total3['Country_Name'] ==country_name2) | (Total3['Country_Name'] ==country_name)]
        Total5=Total4[Total4['Manufacturer_Name'] =='Babolat']
        Total5['Average_Price']=Total5['Value']/Total5['Units']
        str= io.StringIO()
        Total5.to_csv(str)
        mem = io.BytesIO()
        #converting string to bytes and adding the dataframe to it before closing
        mem.write(str.getvalue().encode('utf-8'))
        mem.seek(0)
        str.close()
        return flask.send_file(mem,
                           mimetype='text/csv',
                           attachment_filename='downloadFile.csv',
                           as_attachment=True)

if __name__=='__main__': app.run_server()
