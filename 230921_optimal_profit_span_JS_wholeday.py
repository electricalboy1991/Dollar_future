import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import time

"""
코드의 시간은 한국 시장 기준으로 변경해서 짬
1200원 보다 처음 시작이 높은데서 시작 -> 청산하고 다시 바로 포지션 잡는 경우 존재 
250만원 공제는 고려 안함
15:30 시간이 없어서, 가장가까운 시간으로 하는 데, 10시 막 이런 것들이 있음
\\\\\//\\\\ 쭉 내려와서 롱 포지션 많이 쌓았다가 -> 쭉 밀고 올라서 청산했는데, 다시 내려가서 포지션 잡을 때 -> 이건 야간 청산 기준으로 손실로 잡힐 수 있음 -> 이거 세금에서 빼줌
"""

# Constants
years = 3
minutes_per_day = 24 * 60
initial_balance = 0
commission = 0.06
GC = 1200
buffer = 0
tax_rate = 0.11
df = pd.read_csv('n분석_data.csv')
df['datetime'] = pd.to_datetime(df['datetime'], format='%y-%m-%d %H:%M')
df['datetime'] = df['datetime'] - pd.Timedelta(hours=1)
df = df[df['datetime'] >= '2020-04-07 09:00:00']


df['요일'] = df['datetime'].dt.day_name()
weekend = ['Sunday']
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
filtered_day_df = filtered_day_df.copy()
filtered_day_df.loc[:, '시간'] = filtered_day_df['datetime'].dt.time
time_range1_start = pd.to_datetime('09:00').time()
time_range1_end = pd.to_datetime('15:30').time()
time_range2_start = pd.to_datetime('18:00').time()
#서머타임 적용시 4시인데, 4시 넘어가면 변동성이 거의 없어서 상관 없을 듯
time_range2_end = pd.to_datetime('04:00').time()

# 시간 범위에 해당하는 데이터 필터링
target_df = filtered_day_df[(filtered_day_df['시간'] >= time_range1_start) & (filtered_day_df['시간'] <= time_range1_end) |
                              (filtered_day_df['시간'] >= time_range2_start) | (filtered_day_df['시간'] <= time_range2_end)]

# '요일'이 'Monday'이면서 '시간'이 09:00:00 이전인 조건
condition1 = ~((target_df['요일'] == 'Monday') & (target_df['시간'] < time(9, 0)))

# '요일'이 'Saturday'이면서 '시간'이 04:00:00 초과인 조건
condition2 = ~((target_df['요일'] == 'Saturday') & (target_df['시간'] > time(4, 0)))
final_condition = condition1 & condition2

target_df = target_df[final_condition]

# a는 청산 percent 값
a_range = np.arange(0.001, 0.010, 0.0001)
# a_range = np.arange(0.01, 0.10, 0.01)

# 포지션 잡는 Grid 기준
n_range = np.arange(3, 10, 0.5)

# 수익 계산 함수
def calculate_profit(a, n):
    short_balance = initial_balance
    long_balance = initial_balance
    contracts = n  # c is fixed to n
    profit = 0
    liquidations = 0 # 청산 횟수
    total_num_cont = 0 # 수수료 계산을 위한 전체 계약 수
    short_num_cont = 0
    long_num_cont = 0
    short_positions = []
    long_positions = []
    tax_total = 0

    for index, row in target_df.iterrows():
        short_liquid_flag = 0
        long_liquid_flag = 0
        tax_now = 0
        price = row['close']
        datetime = row['datetime']
        # print(index,price)

        # n 가 있는 이유는 n이 10이랑 1일 때랑 비교 시 단순 1200 기준으로 했을 때 문제가 생기기 때문
        # 1201에서 n 10이여서 short 10개 치는 거랑, n 1이여서 short 1개 치는 거 비교하면 당연히 short 10개 치는 게 수익 많이 나오겠지
        if price > GC +n/2  or (price <= GC+n/2  and short_positions):

            # Short position, short position 들어가있는거 다 돌아서 loop돌기
            for i, short_position in enumerate(short_positions):
                if price <= short_position['short_target_price']:
                    profit = short_position['short_target_price']*(a/(1-a)) * contracts
                    if datetime.hour >= 18 and datetime.hour <= 23:
                        target_tax_time = pd.Timestamp(year=datetime.year, month=datetime.month, day=datetime.day, hour=15, minute=30)
                        # tax_close_price = target_df[target_df['datetime'] == target_tax_time]['close'].iloc[0]
                        if target_tax_time in target_df['datetime'].values:
                            tax_close_price = target_df[target_df['datetime'] == target_tax_time]['close'].iloc[0]
                        else:
                            closest_time = target_df[target_df['datetime'] < target_tax_time]['datetime'].max()
                            tax_close_price = target_df[target_df['datetime'] == closest_time]['close'].iloc[0]
                        tax_now =  -((price - tax_close_price) * contracts * tax_rate)
                    elif datetime.hour >= 0 and datetime.hour <= 4:
                        one_day_before = datetime - pd.Timedelta(days=1)
                        target_tax_time = pd.Timestamp(year=one_day_before.year, month=one_day_before.month, day=one_day_before.day, hour=15, minute=30)
                        if target_tax_time in target_df['datetime'].values:
                            tax_close_price = target_df[target_df['datetime'] == target_tax_time]['close'].iloc[0]
                        else:
                            closest_time = target_df[target_df['datetime'] < target_tax_time]['datetime'].max()
                            tax_close_price = target_df[target_df['datetime'] == closest_time]['close'].iloc[0]
                        tax_now =  -((price - tax_close_price) * contracts * tax_rate)
                    else:
                        tax_now = 0

                    if tax_now >0:
                        short_balance = short_balance+profit-tax_now
                        tax_total=tax_total+tax_now
                    else:
                        #세금 역으로 -일 때는, profit은 그대로고, 세금은 환급
                        short_balance = short_balance + profit
                        tax_total = tax_total + tax_now
                    liquidations += 1
                    short_positions.pop(i)
                    total_num_cont = contracts + total_num_cont
                    short_num_cont = contracts + short_num_cont
                    # print("숏 청산",index,short_positions,long_positions)
                    short_liquid_flag=1
                    break
            if not short_positions and short_liquid_flag==0:
                if datetime.hour >= 18 and datetime.hour <= 23:
                    target_tax_time = pd.Timestamp(year=datetime.year, month=datetime.month, day=datetime.day, hour=15, minute=30)
                    if target_tax_time in target_df['datetime'].values:
                        tax_close_price = target_df[target_df['datetime'] == target_tax_time]['close'].iloc[0]
                    else:
                        closest_time = target_df[target_df['datetime'] < target_tax_time]['datetime'].max()
                        tax_close_price = target_df[target_df['datetime'] == closest_time]['close'].iloc[0]
                    tax_now =  ((price - tax_close_price) * contracts * tax_rate)
                elif datetime.hour >= 0 and datetime.hour <= 4:
                    one_day_before = datetime - pd.Timedelta(days=1)
                    target_tax_time = pd.Timestamp(year=one_day_before.year, month=one_day_before.month, day=one_day_before.day, hour=15, minute=30)
                    if target_tax_time in target_df['datetime'].values:
                        tax_close_price = target_df[target_df['datetime'] == target_tax_time]['close'].iloc[0]
                    else:
                        closest_time = target_df[target_df['datetime'] < target_tax_time]['datetime'].max()
                        tax_close_price = target_df[target_df['datetime'] == closest_time]['close'].iloc[0]
                    tax_now =  ((price - tax_close_price) * contracts * tax_rate)
                else:
                    tax_now = 0

                if tax_now > 0:
                    short_balance = short_balance - tax_now
                    tax_total = tax_total + tax_now
                else:
                    tax_total = tax_total + tax_now

                target_price = round(price * (1 - a), 4)
                short_positions.append({'short_target_price': target_price})
                total_num_cont = contracts + total_num_cont
                # print("초기 숏 잡기",index,short_positions,long_positions)
            else:
                #청산 후 바로 포지션 잡아버리는 거 막기 위함
                if not short_positions:
                    pass
                else:
                    if short_positions[-1]['short_target_price']/(1 - a) + n < price and price >GC+n/2  :
                        # Create a new short position
                        target_price = round(price * (1 - a), 4)
                        short_positions.append({'short_target_price': target_price})
                        total_num_cont = contracts+total_num_cont
                        # print("숏 잡기 추가",index,short_positions,long_positions)
                        if 18 <= datetime.hour <= 23:
                            target_tax_time = pd.Timestamp(year=datetime.year, month=datetime.month, day=datetime.day, hour=15, minute=30)
                            if target_tax_time in target_df['datetime'].values:
                                tax_close_price = target_df[target_df['datetime'] == target_tax_time]['close'].iloc[0]
                            else:
                                closest_time = target_df[target_df['datetime'] < target_tax_time]['datetime'].max()
                                tax_close_price = target_df[target_df['datetime'] == closest_time]['close'].iloc[0]
                            tax_now =  ((price-tax_close_price) * contracts * tax_rate)
                        elif 0 <= datetime.hour <= 4:
                            one_day_before = datetime - pd.Timedelta(days=1)
                            target_tax_time = pd.Timestamp(year=one_day_before.year, month=one_day_before.month, day=one_day_before.day, hour=15, minute=30)
                            if target_tax_time in target_df['datetime'].values:
                                tax_close_price = target_df[target_df['datetime'] == target_tax_time]['close'].iloc[0]
                            else:
                                closest_time = target_df[target_df['datetime'] < target_tax_time]['datetime'].max()
                                tax_close_price = target_df[target_df['datetime'] == closest_time]['close'].iloc[0]
                            tax_now =  ((price-tax_close_price) * contracts * tax_rate)
                        else:
                            tax_now = 0

                        if tax_now > 0:
                            short_balance = short_balance - tax_now
                            tax_total = tax_total + tax_now
                        else:
                            tax_total = tax_total + tax_now

        if price < GC-buffer-n/2  or (price >= GC-buffer-n/2  and long_positions):
            for i, long_position in enumerate(long_positions):
                if price >= long_position['long_target_price']:
                    profit = long_position['long_target_price']*(a/(a+1)) * contracts
                    if 18 <= datetime.hour <= 23:
                        target_tax_time = pd.Timestamp(year=datetime.year, month=datetime.month, day=datetime.day, hour=15, minute=30)
                        if target_tax_time in target_df['datetime'].values:
                            tax_close_price = target_df[target_df['datetime'] == target_tax_time]['close'].iloc[0]
                        else:
                            closest_time = target_df[target_df['datetime'] < target_tax_time]['datetime'].max()
                            tax_close_price = target_df[target_df['datetime'] == closest_time]['close'].iloc[0]
                        tax_now =  ((price - tax_close_price) * contracts * tax_rate)
                    elif 0 <= datetime.hour <= 4:
                        one_day_before = datetime - pd.Timedelta(days=1)
                        target_tax_time = pd.Timestamp(year=one_day_before.year, month=one_day_before.month, day=one_day_before.day, hour=15, minute=30)
                        if target_tax_time in target_df['datetime'].values:
                            tax_close_price = target_df[target_df['datetime'] == target_tax_time]['close'].iloc[0]
                        else:
                            closest_time = target_df[target_df['datetime'] < target_tax_time]['datetime'].max()
                            tax_close_price = target_df[target_df['datetime'] == closest_time]['close'].iloc[0]
                        tax_now =  ((price - tax_close_price) * contracts * tax_rate)
                    else:
                        tax_now = 0

                    if tax_now > 0:
                        long_balance = long_balance + profit - tax_now
                        tax_total = tax_total + tax_now
                    else:
                        long_balance = long_balance + profit
                        tax_total = tax_total + tax_now

                    long_balance += profit
                    liquidations += 1
                    long_positions.pop(i)
                    total_num_cont = contracts + total_num_cont
                    long_num_cont = contracts + long_num_cont
                    # print("롱 청산",index,short_positions,long_positions)
                    long_liquid_flag=1
                    break
            if not long_positions and long_liquid_flag==0:
                target_price = round(price * (1 + a), 4)
                long_positions.append({'long_target_price': target_price})
                total_num_cont = contracts + total_num_cont
                # print("초기 롱 잡기",index,short_positions,long_positions)
                if 18 <= datetime.hour <= 23:
                    target_tax_time = pd.Timestamp(year=datetime.year, month=datetime.month, day=datetime.day, hour=15, minute=30)
                    if target_tax_time in target_df['datetime'].values:
                        tax_close_price = target_df[target_df['datetime'] == target_tax_time]['close'].iloc[0]
                    else:
                        closest_time = target_df[target_df['datetime'] < target_tax_time]['datetime'].max()
                        tax_close_price = target_df[target_df['datetime'] == closest_time]['close'].iloc[0]
                    tax_now =  -((price - tax_close_price) * contracts * tax_rate)
                elif 0 <= datetime.hour <= 4:
                    one_day_before = datetime - pd.Timedelta(days=1)
                    target_tax_time = pd.Timestamp(year=one_day_before.year, month=one_day_before.month, day=one_day_before.day, hour=15, minute=30)
                    if target_tax_time in target_df['datetime'].values:
                        tax_close_price = target_df[target_df['datetime'] == target_tax_time]['close'].iloc[0]
                    else:
                        closest_time = target_df[target_df['datetime'] < target_tax_time]['datetime'].max()
                        tax_close_price = target_df[target_df['datetime'] == closest_time]['close'].iloc[0]
                    tax_now =  -((price - tax_close_price) * contracts * tax_rate)
                else:
                    tax_now = 0

                if tax_now > 0:
                    long_balance = long_balance - tax_now
                    tax_total = tax_total + tax_now
                else:
                    tax_total = tax_total + tax_now

            else:
                if not long_positions:
                    pass
                else:
                    if long_positions[-1]['long_target_price'] / (1 + a) - n > price and price < GC-buffer-n/2 :
                        # Create a new short position
                        target_price = round(price * (1 + a), 4)
                        long_positions.append({'long_target_price': target_price})
                        total_num_cont = contracts + total_num_cont
                        # print("롱 잡기 추가",index,short_positions,long_positions)
                        if 18 <= datetime.hour <= 23:
                            target_tax_time = pd.Timestamp(year=datetime.year, month=datetime.month, day=datetime.day, hour=15, minute=30)
                            if target_tax_time in target_df['datetime'].values:
                                tax_close_price = target_df[target_df['datetime'] == target_tax_time]['close'].iloc[0]
                            else:
                                closest_time = target_df[target_df['datetime'] < target_tax_time]['datetime'].max()
                                tax_close_price = target_df[target_df['datetime'] == closest_time]['close'].iloc[0]
                            tax_now =  -((price - tax_close_price) * contracts * tax_rate)
                        elif 0 <= datetime.hour <= 4:
                            one_day_before = datetime - pd.Timedelta(days=1)
                            target_tax_time = pd.Timestamp(year=one_day_before.year, month=one_day_before.month, day=one_day_before.day, hour=15, minute=30)
                            if target_tax_time in target_df['datetime'].values:
                                tax_close_price = target_df[target_df['datetime'] == target_tax_time]['close'].iloc[0]
                            else:
                                closest_time = target_df[target_df['datetime'] < target_tax_time]['datetime'].max()
                                tax_close_price = target_df[target_df['datetime'] == closest_time]['close'].iloc[0]
                            tax_now =  -((price - tax_close_price) * contracts * tax_rate)
                        else:
                            tax_now = 0

                        if tax_now > 0:
                            long_balance = long_balance - tax_now
                            tax_total = tax_total + tax_now
                        else:
                            tax_total = tax_total + tax_now

    short_leftover = len(short_positions)
    long_leftover = len(long_positions)

    return short_balance, long_balance, liquidations, total_num_cont,short_num_cont,long_num_cont,short_leftover,long_leftover, tax_total


# # a는 청산 percent 값
# a_range = np.arange(0.001, 0.015, 0.001) # 1200원 기준 1.2원 ~ 18원
# # 포지션 잡는 Grid 기준
# n_range = np.arange(2, 20, 0.1)

# # Parameter ranges
# # Profit liquidation percent
# a_range = np.arange(0.005, 0.008, 0.001)
# # Get a position grid for every n distance
# n_range = np.arange(4,5.5, 0.5)

profits = np.zeros((len(a_range), len(n_range)))
short_profits = np.zeros((len(a_range), len(n_range)))
long_profits = np.zeros((len(a_range), len(n_range)))
num_liquidations_array = np.zeros((len(a_range), len(n_range)))
total_commission_array = np.zeros((len(a_range), len(n_range)))

# Create empty lists to store values
a_values = []
n_values = []
num_liquidations_values = []
total_commission_values = []
short_profit_values = []
long_profit_values = []
total_profit_values = []
short_leftover_values = []
long_leftover_values = []
tax_total_values = []

# a,n에 따라 수익을 계산하기 위한 이중 for문
for i, a in enumerate(a_range):
    for j, n in enumerate(n_range):
        short_balance, long_balance, num_liquidations, total_num_cont,short_num_cont,long_num_cont,short_leftover,long_leftover,tax_total = calculate_profit(a, n)
        total_commission = total_num_cont * commission
        short_commission = short_num_cont * commission
        long_commission = long_num_cont * commission
        profits[i][j] = short_balance + long_balance - initial_balance - total_commission
        short_profits[i][j] = short_balance - initial_balance - short_commission
        long_profits[i][j] = long_balance - initial_balance - long_commission
        num_liquidations_array[i][j] = num_liquidations
        total_commission_array[i][j] = total_commission

        print(a, n,num_liquidations,total_commission,short_profits[i][j],long_profits[i][j], profits[i][j],short_leftover,long_leftover,tax_total)

        # Append values to lists
        a_values.append(a)
        n_values.append(n)
        num_liquidations_values.append(num_liquidations)
        total_commission_values.append(total_commission)
        short_profit_values.append(short_profits[i][j])
        long_profit_values.append(long_profits[i][j])
        total_profit_values.append(profits[i][j])
        short_leftover_values.append(short_leftover)
        long_leftover_values.append(long_leftover)
        tax_total_values.append(tax_total)
# Create a DataFrame from the lists
data = {
    'a': a_values,
    'n': n_values,
    'num_liquidations': num_liquidations_values,
    'total_commission': total_commission_values,
    'short_profits': short_profit_values,
    'long_profits': long_profit_values,
    'total_profits': total_profit_values,
    'short_leftover': short_leftover_values,
    'long_leftover': long_leftover_values,
    'tax_total': tax_total_values
}

df_export = pd.DataFrame(data)

# Export the DataFrame to an Excel filess
df_export.to_excel('230910_simulation_result_0.001, 0.010, 0.0001_3, 15, 0.5_short_long수수료고려.xlsx', index=False)

# 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
N,A = np.meshgrid(n_range,a_range)

# surf = ax.plot_surface(A, N, profits, cmap='viridis')
surf = ax.plot_surface(A, N, profits, cmap='viridis')
# Label\
ax.set_xlabel('Position liquidation percent')
ax.set_ylabel('Position grid')
ax.set_zlabel('Profit')
ax.set_title('Profit Simulation')
plt.show()
