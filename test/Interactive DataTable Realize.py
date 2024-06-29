from dash import Dash, dash_table, dcc, html, Input, Output, callback
import pandas as pd
import plotly.express as px

# 读取项目中的癌症数据文件
df = pd.read_csv('dataset/Cleaned_BRCA_Merged_Data_test.csv')  # 替换为你实际的数据文件路径

# 删除第一列并重新排列数据框列顺序，将与可视化相关的列放在前面显示
columns_to_display = ['Hugo_Symbol', 'One_Consequence', 'age_at_initial_pathologic_diagnosis', 'vital_status'] + \
                     [col for col in df.columns if
                      col not in ['Unnamed: 0', 'Hugo_Symbol', 'One_Consequence', 'age_at_initial_pathologic_diagnosis',
                                  'vital_status']]
df = df[columns_to_display]

# 创建工具提示数据
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

app = Dash(__name__)

app.layout = html.Div([
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
        # tooltip_data=[
        #     {column: {'value': str(value), 'type': 'markdown'} for column, value in row.items()} for row in
        #     df.to_dict('records')
        # ],
        tooltip_duration=None,  # 保持工具提示一直可见
    ),
    html.Div(id='datatable-interactivity-container')
])


@callback(
    Output('datatable-interactivity', 'style_data_conditional'),
    Input('datatable-interactivity', 'selected_columns')
)
def update_styles(selected_columns):
    return [{
        'if': {'column_id': i},
        'background_color': '#D2F3FF'
    } for i in selected_columns]


@callback(
    Output('datatable-interactivity-container', "children"),
    Input('datatable-interactivity', "derived_virtual_data"),
    Input('datatable-interactivity', "derived_virtual_selected_rows"))
def update_graphs(rows, derived_virtual_selected_rows):
    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []

    dff = df if rows is None else pd.DataFrame(rows)

    top_genes = dff['Hugo_Symbol'].value_counts().head(20).index
    filtered_df = dff[dff['Hugo_Symbol'].isin(top_genes)]
    waterfall_data = filtered_df.groupby(['Hugo_Symbol', 'One_Consequence']).size().reset_index(name='Count')
    waterfall_fig = px.bar(waterfall_data, x='Hugo_Symbol', y='Count', color='One_Consequence',
                           title='BRCA Gene Mutation Waterfall Plot')
    waterfall_fig.update_layout(xaxis_title='Gene', yaxis_title='Count')

    return [
        dcc.Graph(
            id='brca_waterfall',
            figure=waterfall_fig
        )
    ]


if __name__ == '__main__':
    app.run(debug=True)
