import pandas as pd

mj_df = pd.read_csv('2024_majong_score.csv')


def main():
    for x in mj_df.groupby('player'):
        player_score = x[1]['score']
        player_rank = x[1]['rank']
        p_average = player_score.mean()
        p_max = player_score.max()
        p_min = player_score.min()
        p_rank = player_rank.mean()
        print(f'{x[0]}')
        print(f'    対局数: {len(x[1])}')
        print(f"    平均スコア: {p_average}")
        print(f"    最高スコア: {p_max}")
        print(f"    平均順位: {p_rank}")

if __name__ == '__main__':
    main()
