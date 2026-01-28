# ------------------- Import Libraries -------------------
import requests
import io
import pandas as pd

from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# ------------------- Load Data -------------------
URL = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/d51iMGfp_t0QpO30Lym-dw/automobile-sales.csv"

response = requests.get(URL)
response.raise_for_status()

csv_content = io.StringIO(response.text)
df = pd.read_csv(csv_content)

print("Data downloaded and loaded successfully!")

# ------------------- Year List -------------------
year_list = sorted(df['Year'].unique())

# ------------------- Initialize App -------------------
app = Dash(__name__)
app.title = "Automobile Sales Statistics Dashboard"

# ------------------- Layout -------------------
app.layout = html.Div([

    html.H1(
        "Automobile Sales Statistics Dashboard",
        style={
            'textAlign': 'center',
            'color': '#503D36',
            'fontSize': 24
        }
    ),

    # -------- Dropdown Section --------
    html.Div([

        dcc.Dropdown(
            id='dropdown-statistics',
            options=[
                {'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
                {'label': 'Recession Period Statistics', 'value': 'Recession Period Statistics'}
            ],
            placeholder='Select a report type',
            style={'width': '70%', 'fontSize': '18px'}
        ),

        dcc.Dropdown(
            id='select-year',
            options=[{'label': year, 'value': year} for year in year_list],
            placeholder='Select Year',
            disabled=True,
            style={'width': '70%', 'fontSize': '18px'}
        )

    ], style={
        'display': 'flex',
        'justifyContent': 'space-between',
        'width': '90%',
        'margin': '20px auto'
    }),

    # -------- Output Section --------
    html.Div(
        id='output-container',
        style={'display': 'flex', 'flexDirection': 'column'}
    )

])

# ------------------- Callback: Enable / Disable Year Dropdown -------------------
@app.callback(
    Output('select-year', 'disabled'),
    Input('dropdown-statistics', 'value')
)
def toggle_year_dropdown(selected_statistics):
    return selected_statistics != 'Yearly Statistics'

# ------------------- Callback: Update Graphs -------------------
@app.callback(
    Output('output-container', 'children'),
    [
        Input('dropdown-statistics', 'value'),
        Input('select-year', 'value')
    ]
)
def update_output_container(selected_report, selected_year):

    # -------- Recession Period Statistics --------
    if selected_report == 'Recession Period Statistics':

        recession_data = df[df['Recession'] == 1]

        chart1 = dcc.Graph(
            figure=px.line(
                recession_data.groupby('Year')['Automobile_Sales'].mean().reset_index(),
                x='Year',
                y='Automobile_Sales',
                title='Average Automobile Sales During Recession'
            ),
            style={'width': '48%'}
        )

        chart2 = dcc.Graph(
            figure=px.bar(
                recession_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index(),
                x='Vehicle_Type',
                y='Automobile_Sales',
                title='Average Sales by Vehicle Type (Recession)'
            ),
            style={'width': '48%'}
        )

        chart3 = dcc.Graph(
            figure=px.pie(
                recession_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index(),
                names='Vehicle_Type',
                values='Advertising_Expenditure',
                title='Advertising Expenditure Share (Recession)'
            ),
            style={'width': '48%'}
        )

        chart4 = dcc.Graph(
            figure=px.bar(
                recession_data.groupby(
                    ['unemployment_rate', 'Vehicle_Type']
                )['Automobile_Sales'].mean().reset_index(),
                x='unemployment_rate',
                y='Automobile_Sales',
                color='Vehicle_Type',
                title='Unemployment Rate vs Automobile Sales'
            ),
            style={'width': '48%'}
        )

        return [
            html.Div([chart1, chart2], style={'display': 'flex', 'justifyContent': 'space-between'}),
            html.Div([chart3, chart4], style={'display': 'flex', 'justifyContent': 'space-between'})
        ]

    # -------- Yearly Statistics --------
    elif selected_report == 'Yearly Statistics' and selected_year is not None:

        yearly_data = df[df['Year'] == selected_year]

        chart1 = dcc.Graph(
            figure=px.line(
                df.groupby('Year')['Automobile_Sales'].mean().reset_index(),
                x='Year',
                y='Automobile_Sales',
                title='Yearly Average Automobile Sales'
            ),
            style={'width': '48%'}
        )

        chart2 = dcc.Graph(
            figure=px.line(
                yearly_data.groupby('Month')['Automobile_Sales'].sum().reset_index(),
                x='Month',
                y='Automobile_Sales',
                title=f'Monthly Automobile Sales in {selected_year}'
            ),
            style={'width': '48%'}
        )

        chart3 = dcc.Graph(
            figure=px.bar(
                yearly_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index(),
                x='Vehicle_Type',
                y='Automobile_Sales',
                title=f'Average Sales by Vehicle Type in {selected_year}'
            ),
            style={'width': '48%'}
        )

        chart4 = dcc.Graph(
            figure=px.pie(
                yearly_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index(),
                names='Vehicle_Type',
                values='Advertising_Expenditure',
                title=f'Advertising Expenditure in {selected_year}'
            ),
            style={'width': '48%'}
        )

        return [
            html.Div([chart1, chart2], style={'display': 'flex', 'justifyContent': 'space-between'}),
            html.Div([chart3, chart4], style={'display': 'flex', 'justifyContent': 'space-between'})
        ]

    # -------- Default Message --------
    return html.Div(
        "Please select a report type and year.",
        style={
            'textAlign': 'center',
            'fontSize': '18px',
            'marginTop': '20px'
        }
    )

# ------------------- Run App -------------------
if __name__ == '__main__':
    app.run(port=8054)