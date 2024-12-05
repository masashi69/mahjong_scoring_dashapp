import pandas as pd

mj_df = pd.read_csv('2024_majong_score.csv')


def main():
    for ply in mj_df.groupby('player'):
        p_avg_score, p_avg_rank = ply[1][['score', 'rank']].mean()
        p_max = ply[1]['score'].max()

        # Round
        p_average = round(p_avg_score, 2)
        p_rank = round(p_avg_rank, 2)
        p_max = round(p_max, 2)

        print(f'{ply[0]}')
        print(f'    対局数: {len(ply[1])}')
        print(f"    平均スコア: {p_average}")
        print(f"    最高スコア: {p_max}")
        print(f"    平均順位  : {p_rank}")

if __name__ == '__main__':
    main()
