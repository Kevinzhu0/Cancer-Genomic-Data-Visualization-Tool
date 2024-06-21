import pandas as pd
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px
import io
import base64

# 初始化Dash应用程序
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Cancer Genomic Data Visualization Tool", className="text-center"), className="mb-5 mt-5")
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Upload(
                id='upload-data',
                children=html.Div(['Drag and Drop or ', html.A('Select Data File')]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                multiple=False
            ),
            dcc.ConfirmDialog(
                id='upload-confirm',
                message='File uploaded successfully. Please click "Visualize" to generate the graph.',
            ),
            html.Button('Visualize', id='visualize-button', n_clicks=0, className='mt-4 mb-4'),
        ], width=6),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='age-distribution-hist'), width=12),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='vital-status-vs-age'), width=12),
    ])
])


# 处理文件上传的回调函数
@app.callback(
    Output('upload-confirm', 'displayed'),
    Input('upload-data', 'contents')
)
def show_confirm_dialog(contents):
    if contents is not None:
        return True
    return False


# 生成图像的回调函数
@app.callback(
    [Output('age-distribution-hist', 'figure'),
     Output('vital-status-vs-age', 'figure')],
    Input('visualize-button', 'n_clicks'),
    State('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_graphs(n_clicks, contents, filename):
    if n_clicks > 0 and contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        try:
            if 'csv' in filename:
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            else:
                return {}, {}  # 如果不是CSV文件，则返回空图像

            if 'age_at_initial_pathologic_diagnosis' not in df.columns or 'vital_status' not in df.columns:
                return {}, {}  # 如果数据集中没有所需的列，则返回空图像

            # 生成初诊年龄分布直方图
            hist_fig = px.histogram(df, x='age_at_initial_pathologic_diagnosis', nbins=30,
                                    title='Age Distribution at Initial Pathologic Diagnosis')
            hist_fig.update_layout(xaxis_title='Age', yaxis_title='Frequency')

            # 生成Vital Status vs. Age图像
            box_fig = px.box(df, x='vital_status', y='age_at_initial_pathologic_diagnosis', color='vital_status',
                             title='Vital Status vs. Age')
            box_fig.update_layout(xaxis_title='Vital Status', yaxis_title='Age at Initial Pathologic Diagnosis')

            return hist_fig, box_fig
        except Exception as e:
            print(e)
            return {}, {}
    return {}, {}


if __name__ == '__main__':
    app.run_server(debug=True)
