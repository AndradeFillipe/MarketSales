import dash
import pandas as pd
import numpy as np 
from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import plotly.express as px
import plotly.graph_objects as go

load_figure_template("minty")
app = dash.Dash(
                external_stylesheets=[dbc.themes.MINTY])
server = app.server

df = pd.read_csv('supermarket_sales.csv')

df.Date = pd.to_datetime(df.Date)

# =========  Layout  =========== #

app.layout = html.Div(children=[

    dbc.Row([
        dbc.Col(
            [
                dbc.Card([
                    html.H2("ASIMOV",style={"font-family":"Voltaire",
                                            "font-size":"50px"}),
                    html.Hr(),
                    html.H5("Cidades:"),
                    dcc.Checklist(
                    df.City.unique(),
                    df.City.unique(),
                    id= 'check-city',
                    inline=True,
                    inputStyle={"margin-right":"5px",
                                "margin-left":"20px"}
                    ),
                    html.H5("Variável de Análise:",
                            style={"margin-top":"30px"}),
                    dcc.RadioItems(
                        ["gross income", "Rating"],
                        "gross income",
                        id="main_variable",
                        inline=True,
                        inputStyle={"margin-right":"5px",
                                "margin-left":"20px"}
                    )
                ], style={"height":"90vh",
                          "margin":"20px",
                          "padding":"20px"})
            ], 
            sm=2
        ),
        dbc.Col(
            [
                dbc.Row([
                    dbc.Col([dcc.Graph(id='city-fig')], sm=4),
                    dbc.Col([dcc.Graph(id='gender-fig')], sm=4),
                    dbc.Col([dcc.Graph(id='pay-fig'),], sm=4)
                ]),
                dbc.Row([
                    dcc.Graph(id='income_per_date_fig')
                ]),
                dbc.Row([
                    dcc.Graph(id='income_per_product_fig')
                ])
            ],
            sm=10
        )
    ]),
    
    
])


# =========  Callbacks  =========== #

@app.callback(
    [
       Output('city-fig', 'figure'),
       Output('pay-fig', 'figure'),
       Output('gender-fig', 'figure'),
       Output('income_per_date_fig', 'figure'),
       Output('income_per_product_fig', 'figure')
    ],
    [
        Input('check-city', 'value'),
        Input('main_variable', 'value')
    ])
def render_graph(cities, main_variable):
    operation = np.sum if main_variable == 'gross income' else np.mean
    df_filtered = df[df.City.isin(cities)]
    df_city = df_filtered.groupby('City')[main_variable].apply(operation)\
        .to_frame().reset_index()
    df_payment = df_filtered.groupby('Payment')[main_variable].apply(operation)\
        .to_frame().reset_index()
    df_gender = df_filtered.groupby(['Gender','City'])[main_variable].apply(operation)\
        .to_frame().reset_index()
    df_product_income = df_filtered.groupby(['Product line','City'])[main_variable].apply(operation)\
        .to_frame().reset_index()
    df_date_income = df_filtered.groupby('Date')[main_variable].apply(operation)\
        .to_frame().reset_index()
    fig_city = px.bar(df_city, x='City', y=main_variable)
    fig_payment = px.bar(df_payment, x='Payment', y=main_variable, orientation='h')
    fig_gender = px.bar(df_gender, x='Gender', y=main_variable,color="City", barmode='group')
    fig_date = px.bar(df_date_income,y=main_variable, x='Date')
    fig_income = px.bar(df_product_income,x=main_variable, y='Product line',
                         color='City',orientation='h', barmode='group')
    
    for fig in [fig_city,fig_payment,fig_gender,fig_date]:
        fig.update_layout(margin=dict(l=0,r=0,t=20,b=20), height = 200, template="minty")
    fig_income.update_layout(margin=dict(l=0,r=0,t=20,b=20), height = 500)
    return fig_city,fig_payment,fig_gender,fig_date,fig_income


# =========  Run sever  =========== #
if __name__ == '__main__':
    app.run(port=8050, debug=True)