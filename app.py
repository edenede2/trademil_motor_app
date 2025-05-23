import dash
from dash import dcc, html, Dash, dependencies, dash_table, Input, Output, State, Patch, MATCH, ALL, callback
from flask import Flask
import dash_bootstrap_components as dbc
import webview


flask_app = Flask(__name__)

app = dash.Dash(__name__, server=flask_app, external_stylesheets=[dbc.themes.DARKLY], use_pages=True)

window = webview.create_window('Motor Control App', flask_app, width=800, height=600, resizable=True, fullscreen=False)

app.layout = html.Div(
    [
        html.Div([
            dcc.Link(page['name'] + ' | ', href=page['path'])

        
            for page in dash.page_registry.values()
        ]),
        html.Hr(),

        dash.page_container

    ]
)

if __name__ == '__main__':
    webview.start()
