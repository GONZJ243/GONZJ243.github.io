import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'Sidebar Navigation App'

# -------------------------------
# Screen layouts
# -------------------------------

home_layout = dbc.Container([
    html.H3("🏠 Home", className="mb-4"),
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Welcome!"),
            dbc.CardBody("This is the home page of your app. Use the sidebar to navigate.")
        ]), width=6),
        dbc.Col(dbc.Card([
            dbc.CardHeader("Quick Tip"),
            dbc.CardBody("Dash apps are great for interactive analytics and dashboards!")
        ]), width=6)
    ])
], fluid=True)

dashboard_layout = dbc.Container([
    html.H3("📊 Dashboard", className="mb-4"),
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Sales Summary"),
            dbc.CardBody("Total revenue, growth rate, and key product insights.")
        ]), width=6),
        dbc.Col(dbc.Card([
            dbc.CardHeader("Inventory Overview"),
            dbc.CardBody("Stock levels, turnover rate, and restocking alerts.")
        ]), width=6)
    ])
], fluid=True)

metrics_layout = dbc.Container([
    html.H3("📈 Metrics", className="mb-4"),
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Customer KPIs"),
            dbc.CardBody([
                html.Ul([
                    html.Li("On-Time Delivery: 94%"),
                    html.Li("Order Fill Rate: 89%"),
                    html.Li("Return Rate: 1.3%")
                ])
            ])
        ]), width=6),
        dbc.Col(dbc.Card([
            dbc.CardHeader("Operational KPIs"),
            dbc.CardBody([
                html.Ul([
                    html.Li("Cycle Time: 2.4 days"),
                    html.Li("Forecast Accuracy: 87%"),
                    html.Li("Inventory Accuracy: 97%")
                ])
            ])
        ]), width=6)
    ])
], fluid=True)

# -------------------------------
# App layout with sidebar
# -------------------------------

app.layout = html.Div([
    dcc.Store(id='page-store', data='home'),

    dbc.Row([
        # Sidebar
        dbc.Col([
            html.H2("Navigation", className="display-6"),
            html.Hr(),
            dbc.Button("Home", id="btn-home", color="primary", className="mb-2", n_clicks=0, style={"width": "100%"}),
            dbc.Button("Dashboard", id="btn-dashboard", color="primary", className="mb-2", n_clicks=0, style={"width": "100%"}),
            dbc.Button("Metrics", id="btn-metrics", color="primary", className="mb-2", n_clicks=0, style={"width": "100%"})
        ], width=2, style={"background-color": "#f8f9fa", "height": "100vh", "padding": "20px"}),

        # Content area
        dbc.Col(html.Div(id='page-content', style={"padding": "20px"}), width=10)
    ], className="g-0")
])

# -------------------------------
# Callbacks
# -------------------------------

@app.callback(
    Output('page-store', 'data'),
    [Input('btn-home', 'n_clicks'),
     Input('btn-dashboard', 'n_clicks'),
     Input('btn-metrics', 'n_clicks')],
    prevent_initial_call=True
)
def update_page(n_home, n_dash, n_metrics):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    return {
        'btn-home': 'home',
        'btn-dashboard': 'dashboard',
        'btn-metrics': 'metrics'
    }.get(button_id, 'home')

@app.callback(
    Output('page-content', 'children'),
    Input('page-store', 'data')
)
def render_page(screen):
    if screen == 'dashboard':
        return dashboard_layout
    elif screen == 'metrics':
        return metrics_layout
    return home_layout

# -------------------------------

if __name__ == '__main__':
    app.run_server(debug=True)
