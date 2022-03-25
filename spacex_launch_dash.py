# Import required libraries
import numpy as np
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input
from dash.dependencies import Output
import plotly.express as px
from plotly.graph_objects import Layout

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")

print(spacex_df.head())

max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash( __name__ )

launch_sites = list(set(spacex_df['Launch Site']))

options = []

options.append({'label': 'All sites', 'value': 'ALL'})

for item in launch_sites:
    options.append({'label':item,'value':item})

min_value = spacex_df['Payload Mass (kg)'].min()
max_value = spacex_df['Payload Mass (kg)'].max()

# Create an app layout
app.layout = html.Div(
    children=[
        html.H1(
            'SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}
        ),
        # TASK 1: Add a dropdown list to enable Launch Site selection
        # The default select value is for ALL sites
        dcc.Dropdown(
            id='site-dropdown',
            options=options,
            placeholder='Select a Launch Site here',
            searchable=True,
            value='ALL',
        ),
        html.Br(),

        # TASK 2: Add a pie chart to show the total successful launches count for all sites
        # If a specific launch site was selected, show the Success vs. Failed counts for the site
        html.Div(
            dcc.Graph(id='success-pie-chart')
        ),
        html.Br(),

        html.P("Payload range (Kg):"),
        # TASK 3: Add a slider to select payload range
        dcc.RangeSlider(
            id='payload-slider',
            min=0,
            max=10000,
            step=1000,
            marks={
                0: '0',
                2500: '2500',
                5000: '5000',
                7500: '7500',
                10000: '10000',
            },
            value=[min_value, max_value]
        ),

        # TASK 4: Add a scatter chart to show the correlation between payload and launch success
        html.Div(
            dcc.Graph(id='success-payload-scatter-chart')
        ),
    ]
)

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# add callback decorator
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value'),
)
# Add computation to callback function and return graph
def update_pie_chart( site ):
    df = spacex_df
    df['count']=np.zeros(len(df['Launch Site']))
    df = df.groupby(['Launch Site','class']).count().reset_index()
    df = df[['Launch Site', 'class', 'count']]

    # Successful launches for all sites
    if site == 'ALL':
        fig = px.pie(
            df[df['class']==1],
            values = 'count',
            names = 'Launch Site',
            title = 'Total Success Launches By Site'
        )
    # Launches for a specific site
    elif site in launch_sites:
        fig = px.pie(
            df[df['Launch Site']==site],
            values = 'count',
            names = 'class',
            title = f'Total Success Launches for site {site}'
        )
    else:
        return

    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def update_scatter(site, payload):
    df = spacex_df

    df = df[
        (df['Payload Mass (kg)'] >= payload[0])&
        (df['Payload Mass (kg)'] <= payload[1])
    ]

    if site in launch_sites:
        df = df[df['Launch Site'] == site]

    fig = px.scatter(
        data_frame = df,
        x = 'Payload Mass (kg)',
        y = 'class',
        color = 'Booster Version Category',
        title = f'Correlation between Payload and Success for {site} Site(s)'
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
