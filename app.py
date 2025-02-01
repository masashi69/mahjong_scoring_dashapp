from dash import Dash, html, dcc, callback, Output, Input, dash_table
import plotly.express as px
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import dash_ag_grid as dag
import os 
import summary

currentpath = os.getcwd()
filelist = list()

for f in os.scandir(currentpath):
    if 'csv' in f.name:
        filelist.append(f.name)

#todo select dropdown
fileinput = dcc.Dropdown(filelist, id='dropdown-data')


def create_tscore_table(file):
    df = pd.read_csv(file)
    df_tscore = summary.CalculateScore(df)
    headers = ['名前','対局数','平均スコア','最高スコア', \
            '平均順位','雀力偏差値']

    result_tscore = pd.DataFrame(df_tscore, columns=headers)

    return result_tscore

app = Dash()
server = app.server

@callback(
    Output('player-data', 'options'),
    Input('dropdown-data', 'value'),
    prevent_initial_call=True
)
def players(value):
    df = pd.read_csv(value)
    return df['player'].unique()

@callback(
    Output('score-table', 'children'),
    Input('dropdown-data', 'value'),
    prevent_initial_call=True
)
def display_score_table(value):
    df = pd.read_csv(value)
    score_table = dash_table.DataTable(df.to_dict('records'),
                    [{"name": i, "id": i} for i in df.columns],
                    style_cell={'textAlign': 'left'}, style_header={'fontWeight': 'bold'},
                    page_size=12)

    return score_table

@callback(
    Output('tscore-table', 'children'),
    Input('dropdown-data', 'value'),
    prevent_initial_call=True
)
def create_grid_tscore(value):
    tscore = create_tscore_table(value)

    grid_tscore = dag.AgGrid(
        rowData=tscore.to_dict("records"),
        columnDefs=[{"field": i} for i in tscore.columns],
        defaultColDef={"width": 125}
    )

    return grid_tscore

app.layout = [
    html.H1(children=f'Jong-Crew スコア結果'),
    html.H2(children='対局結果スコア'),
    html.Div(children='検索したい年のファイルを選択してください'),
    html.Div(children='各結果は検索後出力されます'),
    html.Br(),
    fileinput,
    html.H3(children='スコア一覧'),
    html.Div(children='対局ID=日付_卓_対局回数_対局種別  例) 0518_1_1_T: 5/18の卓1 1回戦 東風'),
    html.Br(),
    html.Div(id='score-table'),
    html.H2(children='個人スコアグラフ'),
    html.Div(children='スコア経緯を検索したいプレイヤーを選択してください'),
    html.Br(),
    dcc.Dropdown(id='player-data'),
    dcc.Graph(id='graph-content'),
    html.H2(children='個人スコアサマリー'),
    html.Div(children='タイトル行クリックでソートできます'),
    html.Div(children='偏差値: 平均スコア+平均順位を合わせた偏差'),
    html.Br(),
    html.Div(id='tscore-table')
]

@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-data', 'value'),
    Input('player-data', 'value'),
    prevent_initial_call=True
)
def display_score_graph(file, player):
    df = pd.read_csv(file)
    dff = df[df.player==player]
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
