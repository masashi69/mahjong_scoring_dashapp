import pandas as pd
import plotly.figure_factory as ff
import sys

FileName = sys.argv[1]

def CalcDeviationRank(rank):
    # To calcurate deviation of rank
    return abs(4 - rank)

def main():
    mj_df = pd.read_csv(FileName)
    average_score = mj_df['score'].mean()
    average_rank = mj_df['rank'].mean()
    average_rank = CalcDeviationRank(average_rank)

    result = list()

    for ply in mj_df.groupby('player'):
        p_avg_score, p_avg_rank = ply[1][['score', 'rank']].mean()
        p_max = ply[1]['score'].max()

        # To calcurate deviation of rank
        p_avg_rank_abs = CalcDeviationRank(p_avg_rank)

        # T-score
        TScore_s = (p_avg_score - average_score) / mj_df['score'].std() * 10 + 50
        TScore_r = (p_avg_rank_abs - average_rank) / mj_df['rank'].std() * 10 + 50
        TScore = (TScore_s + TScore_r) / 2

        # Round
        p_average = round(p_avg_score, 2)
        p_rank = round(p_avg_rank, 2)
        p_max = round(p_max, 2)
        TScore = round(TScore, 2)

        player_data = (ply[0] ,len(ply[1]) ,p_average ,p_max ,p_rank ,TScore)
        result.append(player_data)    

    headers = ['名前','対局数','平均スコア','最高スコア', \
                '平均順位','雀力偏差値']

    # Shaping output table
    pd.set_option('display.unicode.east_asian_width', True)
    df_result = pd.DataFrame(result, columns=headers)
    df_result.index += 1

    print(df_result)

    fig = ff.create_table(df_result)
    fig.update_layout(autosize=True, title_text='test title')
    fig.update_layout({'margin':{'t':50}})
    fig.write_image('test.png')

if __name__ == '__main__':
    main()
