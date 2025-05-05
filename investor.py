import dash
from dash import dcc, html, Input, Output, State, ctx, MATCH, ALL
import dash_bootstrap_components as dbc
import pandas as pd
import base64
import io
import re

# Define expected schemas
EXPECTED_SCHEMAS = {
    'file1': {
        'customer_id': int,
        'order_date': 'datetime64[ns]',
        'amount': float
    },
    'file2': {
        'product_id': int,
        'product_name': str,
        'price': float,
        'category': str,
        'stock': int
    }
}

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    html.H3("Multi-Stage File Upload and Validation"),
    dbc.Row([
        dbc.Col([
            html.H5("Upload File 1"),
            dcc.Upload(
                id='upload-file1',
                children=html.Div(['Click to Upload File 1']),
                accept='.csv,.xls,.xlsx',
                multiple=False,
                style={'border': '1px dashed black', 'padding': '20px', 'textAlign': 'center'}
            ),
            html.Div(id='file1-preview'),
            html.Div(id='mapping-form-file1'),
            html.Div(id='validation-results-file1'),
        ]),
        dbc.Col([
            html.H5("Upload File 2"),
            dcc.Upload(
                id='upload-file2',
                children=html.Div(['Click to Upload File 2']),
                accept='.csv,.xls,.xlsx',
                multiple=False,
                style={'border': '1px dashed black', 'padding': '20px', 'textAlign': 'center'}
            ),
            html.Div(id='file2-preview'),
            html.Div(id='mapping-form-file2'),
            html.Div(id='validation-results-file2'),
        ])
    ]),
    html.Hr(),
    html.Button("Load Files", id='load-btn', n_clicks=0, disabled=True),
    html.Div(id='final-status'),

    # Store components
    dcc.Store(id='store-file1'),
    dcc.Store(id='store-file2'),
    dcc.Store(id='store-validations')
])

def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            return None, 'Unsupported file format'
        return df, None
    except Exception as e:
        return None, str(e)

@app.callback(
    Output('file1-preview', 'children'),
    Output('store-file1', 'data'),
    Input('upload-file1', 'contents'),
    State('upload-file1', 'filename')
)
def handle_file1(contents, filename):
    if contents:
        df, err = parse_contents(contents, filename)
        if err:
            return html.Div(f"Error: {err}"), None
        return html.Div([
            html.H6("File 1 Preview"),
            dbc.Table.from_dataframe(df.head(), striped=True, bordered=True, hover=True)
        ]), df.to_json(date_format='iso', orient='split')
    return None, None

@app.callback(
    Output('file2-preview', 'children'),
    Output('store-file2', 'data'),
    Input('upload-file2', 'contents'),
    State('upload-file2', 'filename')
)
def handle_file2(contents, filename):
    if contents:
        df, err = parse_contents(contents, filename)
        if err:
            return html.Div(f"Error: {err}"), None
        return html.Div([
            html.H6("File 2 Preview"),
            dbc.Table.from_dataframe(df.head(), striped=True, bordered=True, hover=True)
        ]), df.to_json(date_format='iso', orient='split')
    return None, None

@app.callback(
    Output('mapping-form-file1', 'children'),
    Input('store-file1', 'data')
)
def show_mapping_form_file1(file1_data):
    if file1_data:
        df = pd.read_json(file1_data, orient='split')
        uploaded_cols = [col.lower() for col in df.columns]
        expected_cols = EXPECTED_SCHEMAS['file1']
        unmatched = [col for col in expected_cols if col.lower() not in uploaded_cols]
        if unmatched:
            return html.Div([
                html.H5("Manual Mapping for File 1"),
                html.Div([
                    html.Div([
                        html.Label(f"Map '{expected_col}' to: "),
                        dcc.Dropdown(
                            options=[{'label': col, 'value': col} for col in df.columns],
                            id={'type': 'col-map', 'index': f"file1:{expected_col}"},
                            placeholder="Select column"
                        )
                    ]) for expected_col in unmatched
                ])
            ])
    return None

@app.callback(
    Output('mapping-form-file2', 'children'),
    Input('store-file2', 'data')
)
def show_mapping_form_file2(file2_data):
    if file2_data:
        df = pd.read_json(file2_data, orient='split')
        uploaded_cols = [col.lower() for col in df.columns]
        expected_cols = EXPECTED_SCHEMAS['file2']
        unmatched = [col for col in expected_cols if col.lower() not in uploaded_cols]
        if unmatched:
            return html.Div([
                html.H5("Manual Mapping for File 2"),
                html.Div([
                    html.Div([
                        html.Label(f"Map '{expected_col}' to: "),
                        dcc.Dropdown(
                            options=[{'label': col, 'value': col} for col in df.columns],
                            id={'type': 'col-map', 'index': f"file2:{expected_col}"},
                            placeholder="Select column"
                        )
                    ]) for expected_col in unmatched
                ])
            ])
    return None

@app.callback(
    Output('validation-results-file1', 'children'),
    Output('store-validations', 'data', allow_duplicate=True),
    Input({'type': 'col-map', 'index': ALL}, 'value'),
    State('store-file1', 'data'),
    prevent_initial_call='initial_duplicate'
)
def validate_file1(mapping_values, file1_data):
    ctx_ids = [i['index'] for i in ctx.inputs_list[0] if i['index'].startswith('file1:')]
    mapping_dict = dict(zip(ctx_ids, mapping_values))

    messages = []
    status = {}

    if file1_data:
        df = pd.read_json(file1_data, orient='split')
        expected_schema = EXPECTED_SCHEMAS['file1']
        uploaded_cols = {col.lower(): col for col in df.columns}

        mapped_cols = {}
        for expected_col in expected_schema:
            key = f"file1:{expected_col}"
            if expected_col.lower() in uploaded_cols:
                mapped_cols[expected_col] = uploaded_cols[expected_col.lower()]
            elif key in mapping_dict and mapping_dict[key]:
                mapped_cols[expected_col] = mapping_dict[key]
            else:
                messages.append(f"file1: Missing column mapping for {expected_col}")

        for expected_col, actual_col in mapped_cols.items():
            try:
                series = df[actual_col]
                expected_type = expected_schema[expected_col]
                if expected_type == int and not pd.api.types.is_integer_dtype(series):
                    messages.append(f"file1: Column '{actual_col}' is not integer")
                elif expected_type == float and not pd.api.types.is_float_dtype(series):
                    messages.append(f"file1: Column '{actual_col}' is not float")
                elif expected_type == str and not pd.api.types.is_string_dtype(series):
                    messages.append(f"file1: Column '{actual_col}' is not string")
                elif expected_type == 'datetime64[ns]' and not pd.api.types.is_datetime64_any_dtype(series):
                    messages.append(f"file1: Column '{actual_col}' is not datetime")
            except Exception as e:
                messages.append(f"file1: Error checking column '{actual_col}': {e}")

    valid = len(messages) == 0
    status['file1_valid'] = valid

    return html.Div([html.P(m) for m in messages] if messages else "File 1: All validations passed!"), status

@app.callback(
    Output('validation-results-file2', 'children'),
    Output('store-validations', 'data', allow_duplicate=True),
    Input({'type': 'col-map', 'index': ALL}, 'value'),
    State('store-file2', 'data'),
    prevent_initial_call='initial_duplicate'
)
def validate_file2(mapping_values, file2_data):
    ctx_ids = [i['index'] for i in ctx.inputs_list[0] if i['index'].startswith('file2:')]
    mapping_dict = dict(zip(ctx_ids, mapping_values))

    messages = []
    status = {}
    date_like_pattern = re.compile(r"\d{1,2}[A-Za-z]{3}\d{4}")

    if file2_data:
        df = pd.read_json(file2_data, orient='split')
        expected_schema = EXPECTED_SCHEMAS['file2']
        uploaded_cols = {col.lower(): col for col in df.columns}

        mapped_cols = {}
        for expected_col in expected_schema:
            key = f"file2:{expected_col}"
            if expected_col.lower() in uploaded_cols:
                mapped_cols[expected_col] = uploaded_cols[expected_col.lower()]
            elif key in mapping_dict and mapping_dict[key]:
                mapped_cols[expected_col] = mapping_dict[key]
            else:
                messages.append(f"file2: Missing column mapping for {expected_col}")

        for expected_col, actual_col in mapped_cols.items():
            try:
                series = df[actual_col]
                expected_type = expected_schema[expected_col]
                if expected_type == int and not pd.api.types.is_integer_dtype(series):
                    messages.append(f"file2: Column '{actual_col}' is not integer")
                elif expected_type == float and not pd.api.types.is_float_dtype(series):
                    messages.append(f"file2: Column '{actual_col}' is not float")
                elif expected_type == str and not pd.api.types.is_string_dtype(series):
                    messages.append(f"file2: Column '{actual_col}' is not string")
            except Exception as e:
                messages.append(f"file2: Error checking column '{actual_col}': {e}")

        date_like_cols = [col for col in df.columns if date_like_pattern.match(str(col))]
        status['file2_date_columns'] = date_like_cols

    valid = len(messages) == 0
    status['file2_valid'] = valid

    return html.Div([html.P(m) for m in messages] if messages else "File 2: All validations passed!"), status

@app.callback(
    Output('load-btn', 'disabled'),
    Input('store-validations', 'data')
)
def toggle_load_button(validations):
    if validations:
        return not (validations.get('file1_valid') and validations.get('file2_valid'))
    return True

@app.callback(
    Output('final-status', 'children'),
    Input('load-btn', 'n_clicks'),
    State('store-validations', 'data')
)
def load_data(n_clicks, validations):
    if n_clicks > 0 and validations and validations.get('file1_valid') and validations.get('file2_valid'):
        return html.Div([
            html.P("Files successfully loaded into memory or database."),
            html.P(f"Detected date-like columns in file2: {validations.get('file2_date_columns', [])}")
        ])
    return ""

if __name__ == '__main__':
    app.run_server(debug=True)
