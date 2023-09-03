import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Constants
years = 3
minutes_per_day = 24 * 60
initial_balance = 0
commission = 0.06
df = pd.read_csv('n분석_data.csv')
#
# # Create a data frame excluding holidays and weekends
# df['datetime'] = pd.to_datetime(df['datetime'])
# df['day of the week'] = df['datetime'].dt.day_name()
# weekend = ['Saturday', 'Sunday']
# holidays = ['2020-01-01', '2020-01-24', '2020-01-25', '2020-01-26', '2020-03-01', '2020-04-30',
#             '2020-05-05', '2020-06-06', '2020-08-15', '2020-08-17', '2020-09-30', '2020-10-01',
#             '2020-10-02', '2020-10-03', '2020-10-09', '2020-12-25',
#             '2021-01-01', '2021-02-11', '2021-02-12', '2021-02-13', '2021-03-01', '2021-05-05',
#             '2021-05-19', '2021-06-06', '2021-08-15', '2021-09-20', '2021-09-21', '2021-09-22',
#             '2021-10-03', '2021-10-09', '2021-12-25',
#             '2022-01-01', '2022-01-31', '2022-02-01', '2022-02-02', '2022-03-01', '2022-05-05',
#             '2022-05-08', '2022-06-06', '2022-08-15', '2022-09-09', '2022-09-10', '2022-09-11',
#             '2022-09-12', '2022-10-03', '2022-10-09', '2022-10-10', '2022-12-25',
#             '2023-01-01', '2023-01-21', '2023-01-22', '2023-01-23', '2023-01-24', '2023-03-01',
#             '2023-05-05', '2023-05-27', '2023-06-06']  # List of public holidays
# filtered_day_df = df[~(df['day of the week'].isin(weekend) | df['datetime'].isin(holidays))]
#
# # Set time range to filter
# filtered_day_df['datetime'] = filtered_day_df['datetime'].dt.time
# time_range1_start = pd.to_datetime('09:00').time()
# time_range1_end = pd.to_datetime('15:30').time()
# time_range2_start = pd.to_datetime('18:00').time()
# time_range2_end = pd.to_datetime('04:00').time()
#
# # Filter data corresponding to time range
# filtered_df = filtered_day_df[(filtered_day_df['time'] >= time_range1_start) & (filtered_day_df['time'] <= time_range1_end) |
#                               (filtered_day_df['time'] >= time_range2_start) | (filtered_day_df['time'] <= time_range2_end)]
#

# 수익 계산 함수
def calculate_profit(a, n):
    balance = initial_balance
    contracts = int(n)  # c is fixed to n
    liquidations = 0 # 청산 횟수
    total_num_cont = 0 # 수수료 계산을 위한 전체 계약 수
    short_positions = []
    long_positions = []

    for index, row in df.iterrows():
        price = row['close']

        if price >= 1200 or (price <= 1200 and short_positions):
            # Short position
            for i, short_position in enumerate(short_positions):
                if price <= short_position['target_price']:
                    profit = short_position['target_price']*(a/(1-a)) * contracts
                    balance += profit
                    liquidations += 1
                    short_positions.pop(i)
                    total_num_cont = contracts + total_num_cont
                    break
            if not short_positions:
                target_price = round(price * (1 - a), 4)
                short_positions.append({'target_price': target_price})
                total_num_cont = contracts + total_num_cont
            else:
                if short_positions[-1]['target_price']/(1 - a) + n < price and price >= 1200:
                    # Create a new short position
                    target_price = round(price * (1 - a), 4)
                    short_positions.append({'target_price': target_price})
                    total_num_cont = contracts+total_num_cont
                else:
                    pass

        if price <= 1150 or (price >= 1150 and long_positions):
            for i, long_position in enumerate(long_positions):
                if price >= long_position['target_price']:
                    profit = long_position['target_price']*(a/(a+1)) * contracts
                    balance += profit
                    liquidations += 1
                    long_positions.pop(i)
                    total_num_cont = contracts + total_num_cont
                    break
            if not long_positions:
                target_price = round(price * (1 + a), 4)
                long_positions.append({'target_price': target_price})
                total_num_cont = contracts + total_num_cont
            else:
                if long_positions[-1]['target_price'] / (1 + a) - n > price and price <= 1200:
                    # Create a new short position
                    target_price = round(price * (1 + a), 4)
                    long_positions.append({'target_price': target_price})
                    total_num_cont = contracts + total_num_cont
                else:
                    pass
    return balance, liquidations, total_num_cont


# a는 청산 percent 값
# a_range = np.arange(0.01, 0.035, 0.001)
a_range = np.arange(0.002, 0.030, 0.001) # 1200원 기준 2.4원 ~ 36원
# 포지션 잡는 Grid 기준
# n_range = np.arange(2, 8, 0.1)
n_range = np.arange(2, 8, 0.5)

# # Parameter ranges
# # Profit liquidation percent
# a_range = np.arange(0.005, 0.008, 0.001)
# # Get a position grid for every n distance
# n_range = np.arange(4,5.5, 0.5)

profits = np.zeros((len(a_range), len(n_range)))
num_liquidations_array = np.zeros((len(a_range), len(n_range)))
total_commission_array = np.zeros((len(a_range), len(n_range)))

# a,n에 따라 수익을 계산하기 위한 이중 for문
for i, a in enumerate(a_range):
    for j, n in enumerate(n_range):
        final_balance, num_liquidations, total_num_cont = calculate_profit(a, n)
        total_commission = total_num_cont * commission
        profits[i][j] = final_balance - initial_balance - total_commission
        num_liquidations_array[i][j] = num_liquidations
        total_commission_array[i][j] = total_commission

        print(a, n,num_liquidations,total_commission, profits[i][j])

# 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
A, N = np.meshgrid(a_range, n_range)

surf = ax.plot_surface(A, N, profits, cmap='viridis')

# Label
ax.set_xlabel('a')
ax.set_ylabel('n')
ax.set_zlabel('Profit')
ax.set_title('Profit Simulation')

# Add annotations
for i in range(len(a_range)):
    for j in range(len(n_range)):
        ax.text(a_range[i], n_range[j], profits[i][j], f'Num Liquidations: {num_liquidations_array[i][j]}\nTotal Commission: {total_commission_array[i][j]:.2f}', fontsize=8, ha='center', va='bottom')

plt.show()