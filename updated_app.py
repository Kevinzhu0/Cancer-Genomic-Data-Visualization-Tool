import pandas as pd
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px

# 初始化Dash应用程序
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# 读取项目中的癌症数据文件
df = pd.read_csv('dataset/Cleaned_BRCA_Merged_Data.csv')  # 替换为你实际的数据文件路径

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Cancer Genomic Data Visualization Tool", className="text-center"), className="mb-5 mt-5")
    ]),
    dbc.Row([
        dbc.Col([
            html.Label('Select Visualization:'),
            dcc.Dropdown(
                id='visualization-dropdown',
                options=[
                    {'label': 'Age Distribution at Initial Diagnosis', 'value': 'age_dist'},
                    {'label': 'Vital Status vs. Age', 'value': 'vital_status_vs_age'},
                    {'label': 'Age at Initial Diagnosis vs. Mutation Type and Vital Status', 'value': 'mutation_vs_age_vs_status'},
                    {'label': 'Top 10 Mutation Type Distribution in BRCA Patients', 'value': 'mutation_type_dist'}
                ],
                value='age_dist',
                multi=False,
                className='mt-3'
            ),
        ], width=6),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='visualization-output'), width=12),
    ])
])

# 生成图像的回调函数
@app.callback(
    Output('visualization-output', 'figure'),
    Input('visualization-dropdown', 'value')
)
def update_graph(selected_vis):
    if df.empty:
        return {}

    if 'age_at_initial_pathologic_diagnosis' not in df.columns or 'vital_status' not in df.columns or 'One_Consequence' not in df.columns:
        return {}

    if selected_vis == 'age_dist':
        # Age Distribution at Initial Pathologic Diagnosis bar chart
        hist_fig = px.histogram(df, x='age_at_initial_pathologic_diagnosis', nbins=30,
                                title='Age Distribution at Initial Pathologic Diagnosis')
        hist_fig.update_layout(xaxis_title='Age', yaxis_title='Frequency')
        return hist_fig

    elif selected_vis == 'vital_status_vs_age':
        # 生成Vital Status vs. Age图像
        box_fig = px.box(df, x='vital_status', y='age_at_initial_pathologic_diagnosis', color='vital_status',
                         title='Vital Status vs. Age')
        box_fig.update_layout(xaxis_title='Vital Status', yaxis_title='Age at Initial Pathologic Diagnosis')
        return box_fig

    elif selected_vis == 'mutation_vs_age_vs_status':
        # 生成Age at Initial Diagnosis vs. Mutation Type and Vital Status图像
        box_fig = px.box(df, x='One_Consequence', y='age_at_initial_pathologic_diagnosis', color='vital_status',
                         title='Age at Initial Diagnosis vs. Mutation Type and Vital Status')
        box_fig.update_layout(xaxis_title='Mutation Type', yaxis_title='Age at Initial Pathologic Diagnosis')
        return box_fig

    elif selected_vis == 'mutation_type_dist':
        # 生成Top 10 Mutation Type Distribution in BRCA Patients图像
        mutation_type_counts = df['One_Consequence'].value_counts().head(10)
        bar_fig = px.bar(mutation_type_counts, x=mutation_type_counts.index, y=mutation_type_counts.values,
                         title='Top 10 Mutation Type Distribution in BRCA Patients')
        bar_fig.update_layout(xaxis_title='Mutation Type', yaxis_title='Count')
        return bar_fig

    return {}

if __name__ == '__main__':
    app.run_server(debug=True)
