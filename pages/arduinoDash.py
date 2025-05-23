import dash
from dash import dcc, html, Dash, dependencies, dash_table, Input, Output, State, Patch, MATCH, ALL, callback
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import serial
import pyfirmata
import time



dash.register_page(__name__, path='/')


# app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])



# board = pyfirmata.Arduino('COM3')
ser = serial.Serial('/dev/cu.usbmodem1301', 9600)


layout = html.Div([
    html.H1("Motor Control Dashboard Test"),


    dbc.Row([
        dbc.Col([
            html.H2("Speed Control RPM"),
            dcc.Slider(
                id='speed-slider',
                min=0,
                max=5000,
                step=100,
                value=1000,
                marks={i: str(i) for i in range(0, 5001, 500)},
            ),
            html.Div(id='slider-output', style={'margin-top': 20}),
            dbc.Button("Set Speed", id='set-speed-button', n_clicks=0),
            html.Br(),
            html.H2("Motor Duration (seconds)"),
            dcc.Input(id='motor-duration-input', type='number', placeholder='Motor duration (s)', min=1, step=1),
            dbc.Button("Set Duration", id='set-duration-button', n_clicks=0),

        ]),
        dbc.Col([
            html.H2("motor selection"),
            dcc.Dropdown(
                id='direction-dropdown',
                options=[
                    {'label': 'Both', 'value': 'B'},
                    {'label': 'Left', 'value': 'L'},
                    {'label': 'Right', 'value': 'R'}
                ],
                value='B',
                style={'color': '#000000'}

            ),
            html.Div(id='direction-output', style={'margin-top': 20}),
        ]),
    ]),
    dbc.Row([
        dbc.Col([
            html.H2("Motor Control"),
            html.Button('Start Motor', id='start-button', n_clicks=0),
            html.Button('Stop Motor', id='stop-button', n_clicks=0),
            html.Div(id='control-output', style={'margin-top': 20}),
        ]),
        dbc.Col([
            html.H2("Timer"),
            html.Div(id='timer-output', style={'fontSize': 24,'margin-top': 20}),
            dcc.Interval(id='interval-component', interval=1000, n_intervals=0, disabled=True)
        ]),
    ]),
    dbc.Row([
        dbc.Col([
            html.H2("History"),
            html.Pre(id='history-output', style={'fontSize': 18}),
        ]),
    ]),
        dcc.Store(id='motor-state', data=False) ,
        dcc.Store(id='history-state', data={}),
        dcc.Store(id='motor-speed', data=0),
        dcc.Store(id='motor-duration', data=0),  

])

@callback(
    Output('slider-output', 'children'),
    Input('speed-slider', 'value')
)
def update_speed_output(speed):
    return f"Selected Speed: {speed} RPM"

@callback(
    Output('direction-output', 'children'),
    Input('direction-dropdown', 'value')
)
def update_direction_output(direction):
    return f"Selected Motor: {direction}"

@callback(
    Output('motor-speed', 'data'),
    Output('control-output', 'children'),
    Input('set-speed-button', 'n_clicks'),
    State('speed-slider', 'value'),
    State('motor-speed', 'data')
)
def set_speed(n_clicks, speed, motor_speed):
    if n_clicks > 0:
        motor_speed = speed
        time.sleep(1)
        ser.write(f"SPEED:{speed}\n".encode('utf-8'))
        return motor_speed, f"Speed set to {speed} RPM."

    return dash.no_update, dash.no_update

@callback(
    Output('motor-duration', 'value'),
    Output('control-output', 'children', allow_duplicate=True),
    Input('set-duration-button', 'n_clicks'),
    State('motor-duration', 'data'),
    State('motor-duration-input', 'value'),
    prevent_initial_call=True
)
def set_motor_duration(n_clicks, motor_duration, duration):
    if n_clicks > 0:
        motor_duration = duration*1000
        time.sleep(1)
        ser.write(f"DELAY:{motor_duration}\n".encode('utf-8'))
        return motor_duration, f"Motor duration set to {motor_duration} seconds."
    
    return dash.no_update, dash.no_update



@callback(
    Output('interval-component', 'disabled', allow_duplicate=True),
    Output('interval-component', 'n_intervals', allow_duplicate=True),
    Output('control-output', 'children', allow_duplicate=True),
    [Input('start-button', 'n_clicks'), 
     Input('stop-button', 'n_clicks')],
     State('motor-state', 'data'),
    prevent_initial_call=True
)
def control_motor(start_clicks, stop_clicks, motor_state):
    
    if start_clicks > 0:
        # @pyfirmata code
        # board.digital[13].write(1)
        time.sleep(2)

        # @serial code
        # ser.write(f"SPEED:{speed}\n".encode('utf-8'))

        ser.write("START\n".encode())




        return False, 0, "Motor started."
    
    if stop_clicks > 0:
        # board.write("STOP\n".encode())
        return True, 0, "Motor stopped."

    return True, dash.no_update, "Motor stopped."


@callback(
    Output('history-state', 'data'),
    Output('history-output', 'children'),
    Input('start-button', 'n_clicks'),
    State('history-state', 'data'),
    State('speed-slider', 'value'),
    State('interval-component', 'n_intervals'),
    State('motor-state', 'data')
)
def update_history(start_clicks, history, speed, n_intervals, motor_state):
    if start_clicks > 0 and motor_state:
        history[len(history)] = [speed, n_intervals]

    history_str = ""
    for key, value in history.items():
        history_str += f"{key}: Speed={value[0]} RPM, Time={value[1]}s\n"

    return history, history_str


@callback(
    Output('timer-output', 'children'),
    Input('interval-component', 'n_intervals'),
    State('interval-component', 'disabled'),
)
def update_timer(n_intervals, disabled):
    if not disabled:
        return f"Motor running for {n_intervals} seconds."
    return "Motor stopped."

# @app.callback(
#     Output('history-state', 'data'),
#     Output('history-output', 'children'),
#     Input('stop-button', 'n_clicks'),
#     State('history-state', 'data'),
#     State('speed-slider', 'value'),
#     State('direction-dropdown', 'value'),
#     State('interval-component', 'n_intervals'),
#     State('motor-state', 'data')
# )
# def update_history(stop_clicks, history, speed, direction, n_intervals, motor_state):
#     if stop_clicks > 0 and not motor_state:
#         history[len(history)] = [direction, motor_state, n_intervals]

#     history_str = ""
#     for key, value in history.items():
#         history_str += f"{key}: {value}\n"

#     return history, history_str
    
    
