import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

# Constants
years = 3
minutes_per_day = 24 * 60
initial_balance = 1000000
df = pd.read_csv('n분석_data.csv')

# 공휴일과 주말을 제외한 데이터프레임 생성
df['datetime'] = pd.to_datetime(df['datetime'])
df['요일'] = df['datetime'].dt.day_name()
weekend = ['Saturday', 'Sunday']
holidays = ['2020-01-01', '2020-01-24', '2020-01-25', '2020-01-26', '2020-03-01', '2020-04-30',
            '2020-05-05', '2020-06-06', '2020-08-15', '2020-08-17', '2020-09-30', '2020-10-01',
            '2020-10-02', '2020-10-03', '2020-10-09', '2020-12-25',
            '2021-01-01', '2021-02-11', '2021-02-12', '2021-02-13', '2021-03-01', '2021-05-05',
            '2021-05-19', '2021-06-06', '2021-08-15', '2021-09-20', '2021-09-21', '2021-09-22',
            '2021-10-03', '2021-10-09', '2021-12-25',
            '2022-01-01', '2022-01-31', '2022-02-01', '2022-02-02', '2022-03-01', '2022-05-05',
            '2022-05-08', '2022-06-06', '2022-08-15', '2022-09-09', '2022-09-10', '2022-09-11',
            '2022-09-12', '2022-10-03', '2022-10-09', '2022-10-10', '2022-12-25',
            '2023-01-01', '2023-01-21', '2023-01-22', '2023-01-23', '2023-01-24', '2023-03-01',
            '2023-05-05', '2023-05-27', '2023-06-06']  # 공휴일 목록
filtered_day_df = df[~(df['요일'].isin(weekend) | df['datetime'].isin(holidays))]

# 필터링할 시간 범위 설정
filtered_day_df['시간'] = filtered_day_df['datetime'].dt.time
time_range1_start = pd.to_datetime('09:00').time()
time_range1_end = pd.to_datetime('15:30').time()
time_range2_start = pd.to_datetime('18:00').time()
time_range2_end = pd.to_datetime('04:00').time()

# 시간 범위에 해당하는 데이터 필터링
filtered_df = filtered_day_df[(filtered_day_df['시간'] >= time_range1_start) & (filtered_day_df['시간'] <= time_range1_end) |
                              (filtered_day_df['시간'] >= time_range2_start) | (filtered_day_df['시간'] <= time_range2_end)]

#수익 계산 함수
def calculate_profit(a, n):
    balance = initial_balance
    contracts = int(n)  # c is fixed to n
    liquidations = 0
    position_flag_long = 0
    position_flag_short = 0
    target_price = 0
    gap_short=0
    gap_long=0
    for index, row in filtered_df.iterrows():
        price = row['close']

        if price >= 1200:
            # Short position
            if position_flag_short == 0 or (position_flag_short==1 and price - target_price >(gap_short+n)):
                target_price.append(round(price * (1 - a), 2))
                gap_short = price -target_price
                position_flag_short = 1
        elif price <= 1150 :
            # Short position
            if position_flag_long == 0 or (position_flag_long==1 and target_price - price >(gap_long+n)):
                target_price = round(price * (1 + a), 2)
                gap_long = target_price - price
                position_flag_long = 1
        else:
            pass

        # Short 청산
        if price < target_price and position_flag_short ==1:
            profit = gap_short * contracts
            balance += profit
            liquidations += 1
            position_flag_short = 0

        # Long 청산
        elif price > target_price and position_flag_long ==1:
            profit = gap_long * contracts
            balance += profit
            liquidations += 1
            position_flag_long = 0
        else:
            continue

    return balance, liquidations


# Parameter ranges
# 수익 청산 percent
a_range = np.arange(0.01, 0.035, 0.001)
# n원 거리마다 포지션 그리드로 잡기
n_range = np.arange(2, 8.1, 0.1)

profits = np.zeros((len(a_range), len(n_range)))

# 최적 값 찾기 for 문
for i, a in enumerate(a_range):
    for j, n in enumerate(n_range):
        final_balance, num_liquidations = calculate_profit(a, n)
        profits[i][j] = final_balance - initial_balance
        print(a,n,profits[i][j])

# 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
A, N = np.meshgrid(a_range, n_range)

ax.plot_surface(A, N, profits, cmap='viridis')

# 라벨
ax.set_xlabel('a')
ax.set_ylabel('n')
ax.set_zlabel('Profit')
ax.set_title('Profit Simulation')

plt.show()
