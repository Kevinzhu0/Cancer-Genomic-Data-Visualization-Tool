import pandas as pd
import dash
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px
import os

# 初始化Dash应用程序并设置标题
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "GenoVAI"

# 读取项目中的癌症数据文件
# df = pd.read_csv('../dataset/Cleaned_BRCA_Merged_Data_test.csv')  # 替换为你实际的数据文件路径

data_path = os.path.join(os.path.dirname(__file__), 'dataset/Cleaned_BRCA_Merged_Data_test.csv')
if os.path.exists(data_path):
    df = pd.read_csv(data_path)
    # 删除第一列并重新排列数据框列顺序，将与可视化相关的列放在前面显示
    columns_to_display = ['Hugo_Symbol', 'One_Consequence', 'age_at_initial_pathologic_diagnosis', 'vital_status'] + \
                         [col for col in df.columns if
                          col not in ['Unnamed: 0', 'Hugo_Symbol', 'One_Consequence',
                                      'age_at_initial_pathologic_diagnosis',
                                      'vital_status']]
    df = df[columns_to_display]
else:
    df = pd.DataFrame()
# 定义可视化选项
visualization_options = [
    {'label': 'Age Distribution at Initial Diagnosis', 'value': 'age_dist'},
    {'label': 'Vital Status vs. Age', 'value': 'vital_status_vs_age'},
    {'label': 'Age at Initial Diagnosis vs. Mutation Type and Vital Status', 'value': 'mutation_vs_age_vs_status'},
    {'label': 'Top 10 Mutation Type Distribution in BRCA Patients', 'value': 'mutation_type_dist'},
    {'label': 'Gene Mutation Frequency by Chromosome', 'value': 'mutation_by_chr'},
    {'label': 'Age at Initial Diagnosis by Gender', 'value': 'age_by_gender'},
    {'label': 'Number of Mutations per Gene', 'value': 'mutations_per_gene'},
    {'label': 'Number of Mutations per Patient', 'value': 'mutations_per_patient'}
    # {'label': 'BRCA Gene Mutation Waterfall Plot', 'value': 'brca_waterfall'}
]
prediction_metrics_options = [
    {'label': 'a', 'value': 'A'},
    {'label': 'b', 'value': 'B'},
    {'label': 'c', 'value': 'C'},
    {'label': 'd', 'value': 'D'},
    {'label': 'e', 'value': 'E'},
    {'label': 'BRCA Gene Mutation Waterfall Plot', 'value': 'brca_waterfall'}
]  # label: brca_wplot&mucnt_byage, value: Brca_wplot&mucnt_byage
# 定义任务选项
task_options = [
    {'label': 'Genomic Data Analysis', 'value': 'data_analysis'},
    {'label': 'brca_wplot&mucnt_byage', 'value': 'Brca_wplot&mucnt_byage'},
    # {'label': 'Tabular', 'value': 'tabular'},
    {'label': 'Vision', 'value': 'vision'},
    {'label': 'NLP', 'value': 'nlp'},
    # {'label': 'Timeseries', 'value': 'timeseries'}
]

# 创建datatable tooltips工具提示数据
tooltips = []
for i in range(len(df)):
    tooltips.append({
        'Hugo_Symbol': {
            'value': f"Barcode: {df.loc[i, 'bcr_patient_barcode']}, "
                     f"Hugo_Symbol: {df.loc[i, 'Hugo_Symbol']},"
                     f"One_Consequence: {df.loc[i, 'One_Consequence']}, "
                     f"Age: {df.loc[i, 'age_at_initial_pathologic_diagnosis']}, "
                     f"Vital Status: {df.loc[i, 'vital_status']}, "
                     f"Gender: {df.loc[i, 'gender']}",
            'type': 'markdown'
        }
    })

app.layout = dbc.Container([
    # 顶部Logo和标题区域
    dbc.Row([
        dbc.Col(html.Img(src=app.get_asset_url('GENOVAI Logo.png'), height='80px'), width="auto"),
        dbc.Col(html.H1("Cancer Genomic Data Visualization Tool", style={'fontSize': '18px', 'margin': '0'}), width=9),
    ], align="center", className="mb-4"),

    # 主体内容区域
    dbc.Row([
        # 左侧功能区
        dbc.Col([
            html.Label('Select Task:', style={'margin-bottom': '15px'}),
            dcc.Dropdown(
                id='task-dropdown',
                options=task_options,
                value='data_analysis',
                multi=False,
                className='mt-3',
                style={'margin-bottom': '30px'}
            ),
            html.Div(id='task-content')
        ], width=3, style={'border-right': '1px solid #ddd', 'padding-right': '15px'}),

        # 右侧可视化图像生成区域
        dbc.Col([
            html.Div([
                # dash table_Construction
                dash_table.DataTable(
                    id='datatable-interactivity',
                    columns=[
                        {"name": i, "id": i, "deletable": True, "selectable": True} for i in df.columns
                    ],
                    data=df.to_dict('records'),
                    editable=True,
                    filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    column_selectable="single",
                    row_selectable="multi",
                    row_deletable=True,
                    selected_columns=[],
                    selected_rows=[],
                    page_action="native",
                    page_current=0,
                    page_size=10,
                    tooltip_data=tooltips,
                    tooltip_duration=None,  # 保持工具提示一直可见
                ),
                # brca_waterfall plotting && Linechart plotting
                html.Div(id='datatable-interactivity-container')
            ]),
            # visualization_plots_container
            dbc.Row(id='visualization-rows')
        ], width=9)
    ])
], fluid=True)


# 任务选项内容
@app.callback(
    Output('task-content', 'children'),
    Input('task-dropdown', 'value')
)
def update_task_content(selected_task):
    # if there is no value in 'task-dropdown' there is no update
    if selected_task == '':
        return dash.no_update
    elif selected_task == 'data_analysis':
        return html.Div([
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
        ])
    elif selected_task == 'Brca_wplot&mucnt_byage':
        return html.Div([
            html.Label('Select Visualization:', style={'margin-bottom': '15px'}),
            dcc.Dropdown(
                id='visualization-dropdown',
                options=prediction_metrics_options,
                value=[option['value'] for option in prediction_metrics_options],  # 默认全选
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
                value=1,
                multi=False,
                className='mt-3',
                style={'margin-bottom': '30px'}
            ),
        ])
    elif selected_task == 'vision':
        return html.Div([
            html.Label('Select Visualization:', style={'margin-bottom': '15px'}),
            dcc.Dropdown(
                id='visualization-dropdown',
                # options=visualization_options,
                value=[],  # 默认值为空
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
                value=1,
                multi=False,
                className='mt-3',
                style={'margin-bottom': '30px'}
            ),
        ])
    elif selected_task == 'nlp':
        return html.Div([
            html.Label('Select Visualization:', style={'margin-bottom': '15px'}),
            dcc.Dropdown(
                id='visualization-dropdown',
                # options=visualization_options,
                value=[],  # 默认值为空
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
                value=1,
                multi=False,
                className='mt-3',
                style={'margin-bottom': '30px'}
            ),
        ])
    return html.Div([
        html.Label('Select Visualization:', style={'margin-bottom': '15px'}),
        dcc.Dropdown(
            id='visualization-dropdown',
            # options=visualization_options,
            value=[],  # 默认值为空
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
            value=1,
            multi=False,
            className='mt-3',
            style={'margin-bottom': '30px'}
        ),
    ])


@app.callback(
    Output('datatable-interactivity', 'style_data_conditional'),
    Input('datatable-interactivity', 'selected_columns')
)
def update_styles(selected_columns):
    return [{
        'if': {'column_id': i},
        'background_color': '#D2F3FF'
    } for i in selected_columns]


# 生成图像的回调函数
@app.callback(
    Output('visualization-rows', 'children'),
    [Input('visualization-dropdown', 'value'),
     Input('figures-per-row-dropdown', 'value'),
     Input('datatable-interactivity', "derived_virtual_data"),
     Input('datatable-interactivity', "derived_virtual_selected_rows")
     ],
    # prevent_initial_call=True
)
def update_graphs(selected_vis, figures_per_row, rows, derived_virtual_selected_rows):
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

        elif vis == 'mutation_by_chr':
            # 生成Gene Mutation Frequency by Chromosome图像
            mutation_by_chr = df['Chromosome'].value_counts()
            bar_fig = px.bar(mutation_by_chr, x=mutation_by_chr.index, y=mutation_by_chr.values,
                             title='Gene Mutation Frequency by Chromosome')
            bar_fig.update_layout(xaxis_title='Chromosome', yaxis_title='Mutation Count')
            figs.append(bar_fig)

        elif vis == 'age_by_gender':
            # 生成Age at Initial Diagnosis by Gender图像
            box_fig = px.box(df, x='gender', y='age_at_initial_pathologic_diagnosis', color='gender',
                             title='Age at Initial Diagnosis by Gender')
            box_fig.update_layout(xaxis_title='Gender', yaxis_title='Age at Initial Pathologic Diagnosis')
            figs.append(box_fig)

        elif vis == 'mutations_per_gene':
            # 生成Number of Mutations per Gene图像（堆积条形图）
            top_genes = df['Hugo_Symbol'].value_counts().head(10).index
            filtered_df = df[df['Hugo_Symbol'].isin(top_genes)]
            mutations_per_gene_fig = px.histogram(filtered_df, x='Hugo_Symbol', color='One_Consequence',
                                                  title='Number of Mutations per Gene',
                                                  category_orders={'One_Consequence': filtered_df[
                                                                                          'One_Consequence'].value_counts().index[
                                                                                      :5].tolist()},
                                                  labels={'Hugo_Symbol': 'Gene', 'count': 'Mutation Count'},
                                                  barmode='stack')
            mutations_per_gene_fig.update_layout(xaxis_title='Gene', yaxis_title='Mutation Count')
            figs.append(mutations_per_gene_fig)

        elif vis == 'mutations_per_patient':
            # 生成Number of Mutations per Patient图像
            mutations_per_patient = df['bcr_patient_barcode'].value_counts().head(10)
            max_value = mutations_per_patient.max()
            y_axis_max = max(10, max_value + 1)  # 动态调整Y轴范围
            mutations_per_patient_fig = px.bar(mutations_per_patient, x=mutations_per_patient.index,
                                               y=mutations_per_patient.values,
                                               title='Number of Mutations per Patient')
            mutations_per_patient_fig.update_layout(xaxis_title='Patient', yaxis_title='Mutation Count',
                                                    yaxis=dict(range=[0, y_axis_max]), xaxis={'tickangle': 45})
            figs.append(mutations_per_patient_fig)

        elif vis == 'brca_waterfall':
            #     # 生成BRCA基因突变的瀑布图
            #     top_genes = df['Hugo_Symbol'].value_counts().head(20).index
            #     filtered_df = df[df['Hugo_Symbol'].isin(top_genes)]
            #     waterfall_data = filtered_df.groupby(['Hugo_Symbol', 'One_Consequence']).size().reset_index(name='Count')
            #     waterfall_fig = px.bar(waterfall_data, x='Hugo_Symbol', y='Count', color='One_Consequence',
            #                            title='BRCA Gene Mutation Waterfall Plot')
            #     waterfall_fig.update_layout(xaxis_title='Gene', yaxis_title='Count')
            #     # 添加折线图
            #     line_data = df.groupby('age_at_initial_pathologic_diagnosis').size().reset_index(name='Mutation Count')
            #     line_fig = px.line(line_data, x='age_at_initial_pathologic_diagnosis', y='Mutation Count',
            #                        title='Mutation Count by Age at Initial Pathologic Diagnosis')
            #     line_fig.update_layout(xaxis_title='Age at Initial Pathologic Diagnosis', yaxis_title='Mutation Count')
            if derived_virtual_selected_rows is None:
                derived_virtual_selected_rows = []
            dff = df if rows is None else pd.DataFrame(rows)
            top_genes = dff['Hugo_Symbol'].value_counts().head(20).index
            filtered_df = dff[dff['Hugo_Symbol'].isin(top_genes)]
            waterfall_data = filtered_df.groupby(['Hugo_Symbol', 'One_Consequence']).size().reset_index(
                name='Count')
            waterfall_fig = px.bar(waterfall_data, x='Hugo_Symbol', y='Count', color='One_Consequence',
                                   title='BRCA Gene Mutation Waterfall Plot')
            waterfall_fig.update_layout(xaxis_title='Gene', yaxis_title='Count')
            # 添加折线图
            line_data = dff.groupby('age_at_initial_pathologic_diagnosis').size().reset_index(name='Mutation Count')
            line_fig = px.line(line_data, x='age_at_initial_pathologic_diagnosis', y='Mutation Count',
                               title='Mutation Count by Age at Initial Pathologic Diagnosis')
            line_fig.update_layout(xaxis_title='Age at Initial Pathologic Diagnosis', yaxis_title='Mutation Count')
            figs.append(waterfall_fig)
            figs.append(line_fig)
    # print "The visualization plots user chose"
    print(f"The plots user chose: {selected_vis}")
    # if there is no value in 'visualization-dropdown' there is no update
    if len(selected_vis) == 0:
        return dash.no_update
    # 根据图像数量和用户选择生成行和列布局
    rows = []
    for i in range(0, len(figs), figures_per_row):
        row = dbc.Row([
            dbc.Col(dcc.Graph(figure=figs[i]), width=int(12 / figures_per_row)) if i < len(figs) else None,
            dbc.Col(dcc.Graph(figure=figs[i + 1]), width=int(12 / figures_per_row)) if i + 1 < len(
                figs) and figures_per_row > 1 else None
        ], className="mb-4")
        rows.append(row)

    return rows


if __name__ == '__main__':
    app.run_server(debug=True)
