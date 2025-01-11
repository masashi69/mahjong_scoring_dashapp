from dash import Dash, html, dcc, callback, Output, Input, dash_table
import plotly.express as px
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import dash_ag_grid as dag
import summary

#todo select dropdown
df = pd.read_csv('2024_majong_score.csv')

def create_tscore_table():
    df_tscore = summary.CalculateScore(df)
    headers = ['名前','対局数','平均スコア','最高スコア', \
            '平均順位','雀力偏差値']

    result_tscore = pd.DataFrame(df_tscore, columns=headers)

    return result_tscore

app = Dash()

score_table = dash_table.DataTable(df.to_dict('records'),
                [{"name": i, "id": i} for i in df.columns],
                style_cell={'textAlign': 'left'}, style_header={'fontWeight': 'bold'},
                page_size=10)

tscore = create_tscore_table()

grid_tscore = dag.AgGrid(
    id="tscore-table",
    rowData=tscore.to_dict("records"),
    columnDefs=[{"field": i} for i in tscore.columns],
    defaultColDef={"width": 150}
)

app.layout = [
    html.H1(children=f'Jong-Crew2024 結果'),
    html.H2(children='対局結果'),
    html.H3(children='対局ID=日付_卓_対局回数_対局種別  例) 0518_1_1_T: 5/18の卓1 1回戦 東風'),
    score_table,
    dash_table.DataTable(id='tbldata'),
    html.H2(children='個人スコアグラフ'),
    dcc.Dropdown(df.player.unique(), id='dropdown-selection'),
    dcc.Graph(id='graph-content'),
    html.H2(children='個人スコアサマリー'),
    grid_tscore
]

@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value')
)
def display_score_graph(value):
    dff = df[df.player==value]
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    fig.add_trace(
        go.Scatter(x=dff['gameid'], y=dff['score'], name="スコア",),
    )
    fig.add_trace(
        go.Scatter(x=dff['gameid'], y=dff['rank'], name="順位"),
        secondary_y=True
    )

    # Reverse rank value for axes
    fig.update_yaxes(autorange="reversed", secondary_y=True)
    # Add figure title
    fig.update_layout(title_text="スコア&順位")
    fig.update_xaxes(title_text="対局ID")
    fig.update_yaxes(title_text="スコア", secondary_y=False, dtick=10)
    fig.update_yaxes(title_text="順位", secondary_y=True, dtick=1)

    return fig

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
