import dash
from dash import dcc, html, Dash, dependencies, dash_table, Input, Output, State, Patch, MATCH, ALL, callback
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import serial
import pyfirmata
import time
import os
import polars as pl
import pandas as pd



dash.register_page(__name__, name='Trial')


# app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])



# board = pyfirmata.Arduino('COM3')
ser = serial.Serial('/dev/cu.usbmodem1301', 9600)

history_path = r'/Users/edeneldar/arduino/pages/history/trial_history.parquet'

if not os.path.exists(history_path):
    history = pl.DataFrame({'index': [],'R_speed': [],'L_speed': []})
    history.write_parquet(history_path)
else:
    history = pl.read_parquet(history_path)

columns_def = [
    {
        'headerName': c, 'field': c} for c in history.columns
        ]

ag_table = dag.AgGrid(
    id='settings-table',
    columnDefs=columns_def,
    rowData=history.to_pandas().to_dict('records'),
    defaultColDef={
        'resizable': True,
        'sortable': True,
        'filter': True,
    },
    columnSize='autoSize',
    dashGridOptions={'pagination': True, 'paginationPageSize': 10, 'undoRedoCellEditing': True, 'rowSelection': 'multiple'},
)
        
        

layout = html.Div([
    html.H1("Motor Control Dashboard"),


    dbc.Row([
        dbc.Col([
            html.H2("Trial Settings Table"),
            html.Div(id='trial-settings-input-table', children=[ag_table]),
            html.Br(),
            html.H2("Left Motor Speed RPM"),
            dbc.Input(id='L_speed', type='number', placeholder='L_speed', min=-10000, step=1),
            html.Br(),
            html.H2("Right Motor Speed RPM"),
            dbc.Input(id='R_speed', type='number', placeholder='R_speed', min=-10000, step=1),
            html.Br(),
            html.H2("Duration (seconds)"),
            dbc.Input(id='duration', type='number', placeholder='Duration (s)', min=1, step=1),
            html.Br(),
            dbc.Button("Add Row", id='add-row-button', n_clicks=0),
            dbc.Button("Delete Row", id='delete-row-button', n_clicks=0),
            dbc.Button("Save", id='save-button', n_clicks=0),
            html.Br(),
            html.Div(id='settings-output', style={'margin-top': 20}),
        ]),
    ]),

    dbc.Row([
        dbc.Col([
            html.H2("Trial execution"),
            html.Button('Start', id='start-button-trial', n_clicks=0),
            html.Div(id='control-output-trial', style={'margin-top': 20}),
        ])
    ]),
    dbc.Row([
        dbc.Col([
            html.H2("History"),
            dbc.Button('Show History', id='show-history-button-trial', n_clicks=0),
        ]),
    ]),
        dcc.Store(id='motor-state-trial', data=False) ,
        dcc.Store(id='history-state-trial', data={}),
        dcc.Store(id='motor-speed-trial', data=0),
        dcc.Store(id='motor-duration-trial', data=0),  

])

@callback(
    Output('settings-table', 'rowData'),
    Input('add-row-button', 'n_clicks'),
    State('L_speed', 'value'),
    State('R_speed', 'value'),
    State('duration', 'value'),
    State('settings-table', 'rowData')
)
def update_settings_table(n_clicks, L_speed, R_speed, duration, rows):
    
    if n_clicks ==0:
        return dash.no_update
    
    if n_clicks:

        if rows == []:
            rows = pl.DataFrame({'L_speed': pl.Series([],dtype=pl.Int64), 'R_speed': pl.Series([],dtype=pl.Int64), 'duration': pl.Series([],dtype=pl.Int64)})
        else:
            rows = pl.DataFrame(rows).select('L_speed','R_speed','duration')

        new_row = pl.DataFrame({'L_speed': [L_speed], 'R_speed': [R_speed], 'duration': [duration]})
        print(new_row)
        rows = pl.concat([rows, new_row]).select('L_speed','R_speed','duration').with_row_index('index')
        

    return rows.to_pandas().to_dict('records')

@callback(
    Output('settings-table', 'rowData', allow_duplicate=True),
    Input('delete-row-button', 'n_clicks'),
    State('settings-table', 'selectedRows'),
    State('settings-table', 'rowData'),
    prevent_initial_call=True
)
def delete_row(n_clicks, selected_rows, rows):
    if n_clicks == 0:
        return dash.no_update
    
    if n_clicks:
        if 'index' not in rows[0]:
            rows = pl.DataFrame(rows).with_row_index('index')
        new_rows = (
            pl.DataFrame(rows)
            .select('index','L_speed','R_speed','duration')
            .filter(
                ~pl.col('index').is_in(selected_rows[0]['index']))
            .drop('index')
            .with_row_index('index')
        )
        return new_rows.to_pandas().to_dict('records')
    return rows

@callback(
    Output('history-state-trial', 'data'),
    Output('settings-output', 'children'),
    Input('save-button', 'n_clicks'),
    State('settings-table', 'rowData')
)
def save_settings(n_clicks, rows):
    if n_clicks == 0:
        return dash.no_update, dash.no_update
    
    if n_clicks:
        df = pl.DataFrame(rows)
        df.write_parquet(history_path)
        

        settings_output = f"Current settings: Right Motor Speed: {rows['R_speed']} RPM, Duration: {rows['duration']} seconds."

        return rows, settings_output

    return dash.no_update, dash.no_update

@callback(
    Output('control-output-trial', 'children'),
    Input('start-button-trial', 'n_clicks'),
    State('settings-table', 'rowData')
)
def start_motor(n_clicks,rows):
    if n_clicks == 0:
        return dash.no_update
    
    if n_clicks:
        for row in rows:
            time.sleep(1)
            ser.write(f"SPEED:{row['R_speed']}\n".encode('utf-8'))
            print(row['R_speed'])
            time.sleep(1)
            ser.write(f"DELAY:{row['duration']*1000}\n".encode('utf-8'))
            print(row['duration'])
            time.sleep(1)
            ser.write("START\n".encode('utf-8'))
            print('Motor started')
            time.sleep(row['duration']+1)
        
        return ['Motor started']
