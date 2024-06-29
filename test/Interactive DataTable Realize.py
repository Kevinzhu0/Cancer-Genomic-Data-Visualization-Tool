from dash import Dash, dash_table, dcc, html, Input, Output, callback
import pandas as pd
import plotly.express as px

# 读取项目中的癌症数据文件
df = pd.read_csv('dataset/Cleaned_BRCA_Merged_Data_test.csv')  # 替换为你实际的数据文件路径

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
