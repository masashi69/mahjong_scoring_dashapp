import pandas as pd

mj_df = pd.read_csv('2024_majong_score.csv')


def main():
    for x in mj_df.groupby('player'):
        print(f'{x[0]}')
        print(f'    対局数: {len(x[1])}')
        print(f"    スコア: {x[1]['score'].agg(['mean', 'max', 'min'])}")
        print(f"    平均順位: {x[1]['rank'].agg(['mean'])}")

if __name__ == '__main__':
    main()
