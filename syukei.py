import pandas as pd

def CalcDeviationRank(rank):
    # To calcurate deviation of rank
    return abs(4 - rank)

def main():
    mj_df = pd.read_csv('2024_majong_score.csv')
    average_score = mj_df['score'].mean()
    average_rank  = mj_df['rank'].mean()
    average_rank = CalcDeviationRank(average_rank)

    for ply in mj_df.groupby('player'):
        p_avg_score, p_avg_rank = ply[1][['score', 'rank']].mean()
        p_max = ply[1]['score'].max()

        # To calcurate deviation of rank
        p_avg_rank_abs = CalcDeviationRank(p_avg_rank)

        # T-score
        TScore_s = (p_avg_score - average_score ) / mj_df['score'].std() * 10 + 50
        TScore_r = (p_avg_rank_abs  - average_rank ) / mj_df['rank'].std() * 10 + 50
        TScore = (TScore_s + TScore_r) / 2

        # Round
        p_average = round(p_avg_score, 2)
        p_rank = round(p_avg_rank, 2)
        p_max = round(p_max, 2)
        TScore = round(TScore)

        print(f'{ply[0]}')
        print(f'    対局数: {len(ply[1])}')
        print(f"    平均スコア: {p_average}")
        print(f"    最高スコア: {p_max}")
        print(f"    平均順位  : {p_rank}")
        print(f"    スコア&ランク偏差値: {TScore}")

if __name__ == '__main__':
    main()
