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

# 定义可视化选项
visualization_options = [
    {'label': 'Age Distribution at Initial Diagnosis', 'value': 'age_dist'},
    {'label': 'Vital Status vs. Age', 'value': 'vital_status_vs_age'},
    {'label': 'Age at Initial Diagnosis vs. Mutation Type and Vital Status', 'value': 'mutation_vs_age_vs_status'},
    {'label': 'Top 10 Mutation Type Distribution in BRCA Patients', 'value': 'mutation_type_dist'}
]

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.Img(src='assets/logo.png', height='60px'), width="auto"),
        dbc.Col(html.H1("Cancer Genomic Data Visualization Tool", className="text-center"), className="mb-5 mt-3")
    ], align="center"),
    dbc.Row([
        dbc.Col([
            html.Label('Select Visualization:', style={'margin-bottom': '15px'}),
            dcc.Dropdown(
                id='visualization-dropdown',
                options=visualization_options,
                value=[option['value'] for option in visualization_options],  # 默认全选
                multi=True,
                className='mt-3',
                style={'margin-bottom': '30px'}
            ),
            html.Label('Number of figures per row:', style={'margin-bottom': '15px'}),
            dcc.Dropdown(
                id='figures-per-row-dropdown',
                options=[
                    {'label': '1', 'value': 1},
                    {'label': '2', 'value': 2}
                ],
                value=2,
                multi=False,
                className='mt-3',
                style={'margin-bottom': '30px'}
            ),
        ], width=3),
        dbc.Col([
            dbc.Row(id='visualization-rows')
        ], width=9)
    ])
])


# 生成图像的回调函数
@app.callback(
    Output('visualization-rows', 'children'),
    [Input('visualization-dropdown', 'value'),
     Input('figures-per-row-dropdown', 'value')]
)
def update_graphs(selected_vis, figures_per_row):
    if df.empty:
        return []

    if 'age_at_initial_pathologic_diagnosis' not in df.columns or 'vital_status' not in df.columns or 'One_Consequence' not in df.columns:
        return []

    figs = []
    for vis in selected_vis:
        if vis == 'age_dist':
            # Age Distribution at Initial Pathologic Diagnosis bar chart
            hist_fig = px.histogram(df, x='age_at_initial_pathologic_diagnosis', nbins=30,
                                    title='Age Distribution at Initial Pathologic Diagnosis')
            hist_fig.update_layout(xaxis_title='Age', yaxis_title='Frequency')
            figs.append(hist_fig)

        elif vis == 'vital_status_vs_age':
            # 生成Vital Status vs. Age图像
            box_fig = px.box(df, x='vital_status', y='age_at_initial_pathologic_diagnosis', color='vital_status',
                             title='Vital Status vs. Age')
            box_fig.update_layout(xaxis_title='Vital Status', yaxis_title='Age at Initial Pathologic Diagnosis')
            figs.append(box_fig)

        elif vis == 'mutation_vs_age_vs_status':
            # 生成Age at Initial Diagnosis vs. Mutation Type and Vital Status图像
            box_fig = px.box(df, x='One_Consequence', y='age_at_initial_pathologic_diagnosis', color='vital_status',
                             title='Age at Initial Diagnosis vs. Mutation Type and Vital Status')
            box_fig.update_layout(xaxis_title='Mutation Type', yaxis_title='Age at Initial Pathologic Diagnosis')
            figs.append(box_fig)

        elif vis == 'mutation_type_dist':
            # 生成Top 10 Mutation Type Distribution in BRCA Patients图像
            mutation_type_counts = df['One_Consequence'].value_counts().head(10)
            bar_fig = px.bar(mutation_type_counts, x=mutation_type_counts.index, y=mutation_type_counts.values,
                             title='Top 10 Mutation Type Distribution in BRCA Patients')
            bar_fig.update_layout(xaxis_title='Mutation Type', yaxis_title='Count')
            figs.append(bar_fig)

    # 根据图像数量和用户选择生成行和列布局
    rows = []
    for i in range(0, len(figs), figures_per_row):
        row = dbc.Row([
            dbc.Col(dcc.Graph(figure=figs[i]), width=int(12 / figures_per_row)) if i < len(figs) else None,
            dbc.Col(dcc.Graph(figure=figs[i + 1]), width=int(12 / figures_per_row)) if i + 1 < len(
                figs) and figures_per_row > 1 else None
        ])
        rows.append(row)

    return rows


if __name__ == '__main__':
    app.run_server(debug=True)
