from dash import (
    Dash,
    html,
    dcc,
    callback,
    Output,
    Input,
    dash_table,
    clientside_callback,
)
import plotly.express as px
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import dash_ag_grid as dag
import os
import summary

currentpath = os.getcwd()
filelist = list()

# select a file from dropdown
for f in os.scandir(currentpath):
    if 'csv' in f.name:
        filelist.append(f.name)


def readfile(file, match=None):
    df = pd.read_csv(file)
    if match == 'hansou':
        hansou_df = df[df['gameid'].str.contains('H')]
        return hansou_df
    elif match == 'tonpu': 
        tonpu_df = df[df['gameid'].str.contains('T')]
        return tonpu_df
    else:
        return df


app = Dash()
server = app.server

@callback(
    Output('gamescore', 'children'),
    Input('gamematch', 'value'),
    prevent_initial_call=True
)
def display_kind_match(value):
    if value == 'hansou':
        return '半荘戦'
    elif value == 'tonpu': 
        return '東風戦'
    else:
        return '総合'

@callback(
    Output('player-data', 'options'),
    Input('dropdown-data', 'value'),
    prevent_initial_call=True  # Don't call at app launch
)
def players(value):
    df = readfile(value)
    return df['player'].unique()


@callback(
    Output('score-table', 'children'),
    Input('dropdown-data', 'value'),
    Input('gamematch', 'value'),
    prevent_initial_call=True
)
def display_score_table(value, match):
    df = readfile(value, match)
    score_table = dash_table.DataTable(
        df.to_dict('records'),
        [{"name": i, "id": i} for i in df.columns],
        style_header={'fontWeight': 'bold'},
        style_cell_conditional=[
            {'if': {'column_id': c}, 'textAlign': 'left'}
            for c in ['gameid', 'date', 'player']
        ],
        page_size=12
    )

    return score_table


@callback(
    Output('tscore-table', 'children'),
    Input('dropdown-data', 'value'),
    Input('gamematch', 'value'),
    prevent_initial_call=True
)
def create_grid_tscore(value, match):
    df = readfile(value, match)
    df_tscore = summary.CalculateScore(df)
    headers1 = ['名前', '対局数', '平均スコア', '最高スコア']
    headers2 = ['名前', '平均順位', '4位回避率(%)', '雀力偏差値']

    table1 = list()
    table2 = list()

    for t in df_tscore:
        table1.append(t[0:4])
        table2.append(t[0:1]+t[4:])

    sumscore = pd.DataFrame(table1, columns=headers1)
    tscore = pd.DataFrame(table2, columns=headers2)

    grid_sumscore = dag.AgGrid(
        rowData=sumscore.to_dict("records"),
        columnDefs=[{"field": i} for i in sumscore.columns],
        columnSize="responsiveSizeToFit"
        )

    grid_tscore = dag.AgGrid(
        rowData=tscore.to_dict("records"),
        columnDefs=[{"field": i} for i in tscore.columns],
        columnSize="responsiveSizeToFit"
        )

    return grid_sumscore, grid_tscore


app.layout = [
    html.H1(children=f'Jong-Crew スコア結果'),
    html.H2(children='対局結果スコア'),
    html.Div(children='検索したい年のファイルを選択してください'),
    html.Div(children='各結果は検索後出力されます'),
    html.Br(),
    dcc.Dropdown(filelist, id='dropdown-data'),
    dcc.RadioItems(
        options=[
            {'label': '総合スコア', 'value': ''},
            {'label': '半荘戦', 'value': 'hansou'},
            {'label': '東風戦', 'value': 'tonpu'},
        ],
        value='総合スコア',
        id='gamematch',
        inline=True,
    ),
    html.H2([html.Span(id='gamescore'), html.Span(' ' + '各種スコア')]),
    html.H2(children='スコア一覧'),
    html.Div(
        children='対局ID=日付_卓_対局回数_対局種別  例) 0518_1_1_T: 5/18の卓1 1回戦 東風'
    ),
    html.Br(),
    html.Div(id='score-table'),
    html.H2(children='個人スコアグラフ'),
    html.Div(children='スコア経緯を検索したいプレイヤーを選択してください'),
    html.Br(),
    dcc.Dropdown(id='player-data'),
    dcc.Graph(id='graph-content'),
    html.H2(children='個人スコアサマリー'),
    html.Div(
        children='タイトル行クリックでソート、ドラッグで各列の移動やサイズ変更可能です'
    ),
    html.Div(children='偏差値: 平均スコア+平均順位を合わせた偏差'),
    html.Br(),
    html.Div(id='tscore-table')
]


@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-data', 'value'),
    Input('gamematch', 'value'),
    Input('player-data', 'value'),
    prevent_initial_call=True
)
def display_score_graph(file, match, player):
    df = readfile(file, match)
    dff = df[df.player == player]
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    fig.add_trace(
        go.Scatter(
            x=dff['gameid'],
            y=dff['score'],
            name="スコア",
        ),
    )
    fig.add_trace(
        go.Scatter(
            x=dff['gameid'],
            y=dff['rank'],
            name="順位"),
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


# Automatically closed keyboard for smartphone
clientside_callback(
    """
    function(value) {
        // Remove focus from the dropdown element
        document.activeElement.blur();
    }
    """,
    Input('dropdown-data', 'value'),
    Input('player-data', 'value'),
    prevent_initial_call=True
)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
