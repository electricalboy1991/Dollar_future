import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.axes_grid1 import make_axes_locatable

# Constants
years = 3
minutes_per_day = 24 * 60
initial_balance = 0
commission = 0.06
GC = 1200
buffer = 0
df = pd.read_csv('n분석_data.csv')

# a는 청산 percent 값
a_range = np.arange(0.001, 0.010, 0.0001)
# a_range = np.arange(0.01, 0.10, 0.01)

# 포지션 잡는 Grid 기준
n_range = np.arange(3, 15, 0.5)

# 수익 계산 함수
def calculate_profit(a, n):
    short_balance = initial_balance
    long_balance = initial_balance
    contracts = n  # c is fixed to n
    liquidations = 0 # 청산 횟수
    total_num_cont = 0 # 수수료 계산을 위한 전체 계약 수
    short_num_cont = 0
    long_num_cont = 0
    short_positions = []
    long_positions = []

    for index, row in df.iterrows():
        short_liquid_flag = 0
        long_liquid_flag = 0
        price = row['close']
        # print(index,price)

        # n 가 있는 이유는 n이 10이랑 1일 때랑 비교 시 단순 1200 기준으로 했을 때 문제가 생기기 때문
        # 1201에서 n 10이여서 short 10개 치는 거랑, n 1이여서 short 1개 치는 거 비교하면 당연히 short 10개 치는 게 수익 많이 나오겠지
        if price > GC +n/2  or (price <= GC+n/2  and short_positions):
            # Short position
            for i, short_position in enumerate(short_positions):
                if price <= short_position['short_target_price']:
                    profit = short_position['short_target_price']*(a/(1-a)) * contracts
                    short_balance += profit
                    liquidations += 1
                    short_positions.pop(i)
                    total_num_cont = contracts + total_num_cont
                    short_num_cont = contracts + short_num_cont
                    # print("숏 청산",index,short_positions,long_positions)
                    short_liquid_flag=1
                    break
            if not short_positions and short_liquid_flag==0:
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

        if price < GC-buffer-n/2  or (price >= GC-buffer-n/2  and long_positions):
            for i, long_position in enumerate(long_positions):
                if price >= long_position['long_target_price']:
                    profit = long_position['long_target_price']*(a/(a+1)) * contracts
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
    short_leftover = len(short_positions)
    long_leftover = len(long_positions)

    return short_balance, long_balance, liquidations, total_num_cont,short_num_cont,long_num_cont,short_leftover,long_leftover


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

# a,n에 따라 수익을 계산하기 위한 이중 for문
for i, a in enumerate(a_range):
    for j, n in enumerate(n_range):
        short_balance, long_balance, num_liquidations, total_num_cont,short_num_cont,long_num_cont,short_leftover,long_leftover = calculate_profit(a, n)
        total_commission = total_num_cont * commission
        short_commission = short_num_cont * commission
        long_commission = long_num_cont * commission
        profits[i][j] = short_balance + long_balance - initial_balance - total_commission
        short_profits[i][j] = short_balance - initial_balance - short_commission
        long_profits[i][j] = long_balance - initial_balance - long_commission
        num_liquidations_array[i][j] = num_liquidations
        total_commission_array[i][j] = total_commission

        print(a, n,num_liquidations,total_commission,short_profits[i][j],long_profits[i][j], profits[i][j],short_leftover,long_leftover)

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

# Create a DataFrame from the lists
data = {
    'A': a_values,
    'N': n_values,
    'Num_Liquidations': num_liquidations_values,
    'Total_Commission': total_commission_values,
    'Short_Profit': short_profit_values,
    'Long_Profit': long_profit_values,
    'Total_Profit': total_profit_values,
    'Short_Leftover': short_leftover_values,
    'Long_Leftover': long_leftover_values
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
#
# # 3D plot
# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')
# N, A = np.meshgrid(n_range, a_range)
# surf = ax.plot_surface(A, N, profits, cmap='viridis')
#
# # Label
# ax.set_xlabel('Position liquidation percent')
# ax.set_ylabel('Position grid')
# ax.set_zlabel('Profit')
# ax.set_title('Profit Simulation')
#
# # 마우스 클릭 이벤트 핸들러
# def on_click(event):
#     if event.inaxes == ax:
#         x, y = event.xdata, event.ydata
#         i = np.searchsorted(a_range, x)
#         j = np.searchsorted(n_range, y)
#
#         # Check if the index is within bounds
#         if 0 <= i < len(a_range) and 0 <= j < len(n_range):
#             a_value = a_range[i]
#             n_value = n_range[j]
#             profit_value = profits[i][j]
#             num_liquidations_value = num_liquidations_array[i][j]
#             total_commission_value = total_commission_array[i][j]
#             print(f'a: {a_value}, n: {n_value}, Profits: {profit_value}, Num Liquidations: {num_liquidations_value}, Total Commission: {total_commission_value}')
#         else:
#             print("Clicked outside the valid range")
#
# # 이벤트 연결
# cid = fig.canvas.mpl_connect('button_press_event', on_click)
#
# plt.show()