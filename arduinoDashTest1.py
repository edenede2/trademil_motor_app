import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import serial
import time

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# Serial connection to Arduino
# ser = serial.Serial('/dev/cu.usbmodem1301', 9600)

app.layout = html.Div([
    html.H1("Motor Control Dashboard"),

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
        ]),
    ]),
    
    dbc.Row([
        dbc.Col([
            html.H2("Motor Control"),
            html.Button('Start Motor', id='start-button', n_clicks=0),
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
    dcc.Store(id='motor-state', data=False),
    dcc.Store(id='history-state', data={}),
    dcc.Store(id='motor-duration', data=0),  # Store the duration for the motor run
])

@app.callback(
    Output('interval-component', 'disabled'),
    Output('interval-component', 'n_intervals'),
    Output('control-output', 'children'),
    Output('motor-state', 'data'),
    Output('motor-duration', 'data'),
    [Input('start-button', 'n_clicks')],
    State('motor-state', 'data'),
    State('speed-slider', 'value'),
    State('motor-duration', 'data')
)
def control_motor(start_clicks, motor_state, speed, motor_duration):
    if start_clicks > 0 and not motor_state:
        # Start motor logic
        # ser.write(f"SPEED:{speed}\n".encode('utf-8'))
        # ser.write("START\n".encode())

        # Example motor run duration; you can adjust this as needed.
        motor_duration = 10  # Assume the motor runs for 10 seconds

        return False, 0, "Motor started.", True, motor_duration
    
    return True, dash.no_update, "Motor stopped.", motor_state, motor_duration

@app.callback(
    Output('timer-output', 'children'),
    Output('motor-state', 'data', allow_duplicate=True),
    Input('interval-component', 'n_intervals'),
    State('interval-component', 'disabled'),
    State('motor-duration', 'data'),
    State('motor-state', 'data'),
    prevent_initial_call=True
)
def update_timer(n_intervals, disabled, motor_duration, motor_state):
    if not disabled:
        if n_intervals >= motor_duration:
            # ser.write("STOP\n".encode())
            return "Motor stopped.", False  # Reset motor state after stop
        return f"Motor running for {n_intervals} seconds.", motor_state
    return "Motor stopped.", motor_state

@app.callback(
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

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8050, debug=True)