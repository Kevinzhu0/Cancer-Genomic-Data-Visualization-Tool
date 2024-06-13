import pandas as pd
import dash
# import dash_core_components as dcc
from dash import dcc
# import dash_html_components as html
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objs as go
from lifelines import KaplanMeierFitter
from sklearn.decomposition import PCA
import networkx as nx
import numpy as np
import io
import base64

# 初始化Dash应用程序
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# 初始化全局变量
merged_df = pd.DataFrame()

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Cancer Genomic Data Visualization Tool", className="text-center"), className="mb-5 mt-5")
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Upload(
                id='upload-merged-data',
                children=html.Div(['Drag and Drop or ', html.A('Select Merged Data File')]),
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
            html.Label('Select Gene(s):'),
            dcc.Dropdown(
                id='gene-dropdown',
                options=[],
                value=[],
                multi=True
            )
        ], width=6),
    ], className="mb-4"),
    dbc.Row([
        dbc.Col(dcc.Graph(id='mutation-frequency-bar'), width=6),
        dbc.Col(dcc.Graph(id='age-distribution-hist'), width=6),
    ]),
    # dbc.Row([
    #     # dbc.Col(dcc.Graph(id='survival-analysis'), width=6),
    #     # dbc.Col(dcc.Graph(id='pca-analysis'), width=6),
    # ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='co-occurrence-network'), width=6),
        dbc.Col(dcc.Graph(id='mutation-type-vs-age'), width=6),
    ])
])

# 处理文件上传的回调函数
@app.callback(
    Output('gene-dropdown', 'options'),
    Output('gene-dropdown', 'value'),
    Input('upload-merged-data', 'contents'),
    State('upload-merged-data', 'filename')
)
def update_dropdown(merged_contents, merged_filename):
    global merged_df  # 声明为全局变量
    if merged_contents is not None:
        merged_df = parse_contents(merged_contents, merged_filename)

        # 打印列名以检查数据
        print(merged_df.columns)

        gene_options = [{'label': gene, 'value': gene} for gene in merged_df['Hugo_Symbol'].unique()]
        return gene_options, []

    return [], []


def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            return pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        else:
            return pd.DataFrame()
    except Exception as e:
        print(e)
        return pd.DataFrame()


# 更新图表的回调函数
@app.callback(
    Output('mutation-frequency-bar', 'figure'),
    Output('age-distribution-hist', 'figure'),
    # Output('survival-analysis', 'figure'),
    # Output('pca-analysis', 'figure'),
    Output('co-occurrence-network', 'figure'),
    Output('mutation-type-vs-age', 'figure'),
    Input('gene-dropdown', 'value')
)
def update_graphs(selected_genes):
    global merged_df  # 声明为全局变量
    if merged_df.empty or not selected_genes:
        return {}, {}, {}, {}, {}, {}

    # 检查'days_to_death'列是否存在
    # if 'days_to_death' not in merged_df.columns:
    #     print("Error: 'days_to_death' column not found in the dataset.")
    #     return {}, {}, {}, {}, {}, {}

    # 突变基因频率条形图
    gene_mutation_counts = merged_df['Hugo_Symbol'].value_counts().head(20)
    bar_fig = px.bar(gene_mutation_counts, x=gene_mutation_counts.index, y=gene_mutation_counts.values,
                     title='Top 20 Gene Mutation Frequency')
    bar_fig.update_layout(xaxis_title='Gene', yaxis_title='Mutation Count')

    # 初诊年龄分布直方图
    hist_fig = px.histogram(merged_df, x='age_at_initial_pathologic_diagnosis', nbins=30,
                            title='Age Distribution at Initial Pathologic Diagnosis')
    hist_fig.update_layout(xaxis_title='Age', yaxis_title='Frequency')

    # 生存分析Kaplan-Meier曲线
    # kmf = KaplanMeierFitter()
    # km_fig = go.Figure()
    #
    # for gene in selected_genes:
    #     gene_mutants = merged_df[merged_df['Hugo_Symbol'] == gene]
    #     if not gene_mutants.empty:
    #         kmf.fit(gene_mutants['days_to_death'], event_observed=gene_mutants['vital_status'] == 'Dead', label=gene)
    #         km_fig.add_trace(
    #             go.Scatter(x=kmf.survival_function_.index, y=kmf.survival_function_['KM_estimate'], mode='lines', name=gene)
    #         )
    # km_fig.update_layout(title='Survival Analysis', xaxis_title='Days', yaxis_title='Survival Probability')

    # 多变量PCA分析图
    # pca = PCA(n_components=2)
    # clinical_vars = merged_df[['age_at_initial_pathologic_diagnosis', 'days_to_death']].dropna()
    # principal_components = pca.fit_transform(clinical_vars)
    # pca_fig = px.scatter(x=principal_components[:, 0], y=principal_components[:, 1],
    #                      color=clinical_vars['days_to_death'], title='PCA of Clinical Variables')
    # pca_fig.update_layout(xaxis_title='Principal Component 1', yaxis_title='Principal Component 2',
    #                       coloraxis_colorbar=dict(title='Days to Death'))

    # 突变基因共现网络图
    co_occurrence_matrix = pd.crosstab(merged_df['bcr_patient_barcode'], merged_df['Hugo_Symbol'])
    co_occurrence_matrix = co_occurrence_matrix.T.dot(co_occurrence_matrix)
    co_occurrence_matrix.values[[np.arange(co_occurrence_matrix.shape[0])] * 2] = 0
    G = nx.from_pandas_adjacency(co_occurrence_matrix)
    pos = nx.spring_layout(G)
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)
    edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=0.5, color='#888'), hoverinfo='none', mode='lines')
    node_x = []
    node_y = []
    for node in pos:
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
    node_trace = go.Scatter(x=node_x, y=node_y, mode='markers+text', text=[str(node) for node in G.nodes()],
                            hoverinfo='text', marker=dict(size=10, color='#1f78b4'))
    network_fig = go.Figure(data=[edge_trace, node_trace],
                            layout=go.Layout(title='Co-occurrence Network of Gene Mutations', showlegend=False,
                                             hovermode='closest'))

    # 突变类型和临床变量关系的箱线图
    box_fig = px.box(merged_df, x='One_Consequence', y='age_at_initial_pathologic_diagnosis', color='vital_status',
                     title='Age at Initial Diagnosis vs. Mutation Type and Vital Status')
    box_fig.update_layout(xaxis_title='Mutation Type', yaxis_title='Age at Initial Pathologic Diagnosis')

    return bar_fig, hist_fig, km_fig, pca_fig, network_fig, box_fig


if __name__ == '__main__':
    app.run_server(debug=True)