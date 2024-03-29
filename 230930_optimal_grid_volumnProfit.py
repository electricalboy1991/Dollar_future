import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import time
from datetime import datetime
from scipy.interpolate import griddata

"""
한 밴드 내에서 머물다가 일부만 청산시키고, 밴드를 나가면 ATR 다시 계산함
atr 값이 너무 크다 -> 변동성 크다 -> Grid를 원래 잡던대로 잡음
"""

# a는 청산 percent 값
percent_start = 0.0046
percent_finish = 0.0047
percent_gap = 0.0001
a_range = np.arange(percent_start, percent_finish, percent_gap)
a_range = a_range[:-1]

# b는 청산 percent 값
b_percent_start = 0.0049
b_percent_finish = 0.0050
b_percent_gap = 0.0001
b_range = np.arange(b_percent_start, b_percent_finish, b_percent_gap)
b_range = b_range[:-1]

# 포지션 잡는 Grid 기준
n_start = 3
n_finish = 8
n_gap = 1
n_range = np.arange(n_start, n_finish, n_gap)

# atr coefficient
atr_coeff_start = 1
atr_coeff_finish = 1.1
atr_coeff_gap = 0.1
atr_coeff_range = np.arange(atr_coeff_start, atr_coeff_finish, atr_coeff_gap)
atr_coeff_range = atr_coeff_range[:-1]


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

atr_data = pd.read_excel('USD_KRW 과거 데이터_ATR_new.xlsx')

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
# Convert the datetime column to datetime format
atr_data['datetime'] = pd.to_datetime(atr_data['datetime'], format='%y-%m-%d')

# 수익 계산 함수
def calculate_profit(a,b,n,atr_coeff):
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
    tax_short_total = 0
    tax_long_total = 0
    n_origin = n
    atr_flag=0
    atr_value_before = atr_data['14-day ATR'].mean()

    for index, row in target_df.iterrows():
        short_liquid_flag = 0
        long_liquid_flag = 0
        tax_now = 0
        price = row['close']
        price_open = row['open']
        datetime = row['datetime']
        n=n_origin
        # print(index,price)
        # 해당 날짜의 ATR 값 가져오기
        atr_value_row = atr_data.loc[atr_data['datetime'] == row['datetime'].strftime('%Y-%m-%d'), '14-day ATR']

        if atr_value_row.empty:
            # 매칭되는 값이 없을 때, 해당 datetime 기준 최근 이전 날짜의 값을 가져오기
            previous_valid_date = atr_data[atr_data['datetime'] < row['datetime']].datetime.idxmax()
            if atr_flag==0:
                atr_value = atr_data.loc[previous_valid_date, '14-day ATR']
            else:
                atr_value = atr_value_before
        else:
            if atr_flag==0:
                atr_value = atr_value_row.values[0]
            else:
                atr_value = atr_value_before

        # 특정 범위 확인 및 유연한 그리드 표준 n 값 계산
        if 1090 <= price <= 1110 or 1190 <= price <= 1210 or 1290 <= price <= 1310 or 1390 <= price <= 1410:
            # 해당 날짜의 ATR 값 가져오기
            if atr_value > atr_data['14-day ATR'].mean():
                n = n_origin
                atr_value_before = atr_value
                atr_flag = 1
            else:
                n = n + atr_coeff*(atr_value - atr_data['14-day ATR'].mean()) / atr_data['14-day ATR'].std()
                atr_value_before = atr_value
                atr_flag = 1
        elif 1080 <= price < 1090 or 1110 < price <= 1120 or 1180 <= price < 1190 or 1210 < price <= 1220 or \
                1280 <= price < 1290 or 1310 < price <= 1320 or 1380 <= price < 1390 or 1410 < price <= 1420:
            if atr_value > atr_data['14-day ATR'].mean():
                n = n_origin
                atr_value_before = atr_value
                atr_flag = 1
            else:
                # 해당 날짜의 ATR 값 가져오기
                n = n - atr_coeff*(atr_value - atr_data['14-day ATR'].mean()) / atr_data['14-day ATR'].std()
                atr_value_before = atr_value
                atr_flag = 1
        else:
            # 특정 범위 외의 경우 기본 n 값 사용
            n = n_origin
            atr_flag=0

        # n 가 있는 이유는 n이 10이랑 1일 때랑 비교 시 단순 1200 기준으로 했을 때 문제가 생기기 때문
        # 1201에서 n 10이여서 short 10개 치는 거랑, n 1이여서 short 1개 치는 거 비교하면 당연히 short 10개 치는 게 수익 많이 나오겠지
        if price > GC +n/2  or (price <= GC+n/2  and short_positions):

            # Short position, short position 들어가있는거 다 돌아서 loop돌기
            for i, short_position in enumerate(short_positions):
                if price <= short_position['short_target_price']:
                    if 18 <= datetime.hour <= 23:
                        night_target_price = short_position['price']*(1-b)
                        #일단 종가가 night_target_price보다 낮으면 일단 먹는 거지
                        if price <= night_target_price:
                            target_tax_time = pd.Timestamp(year=datetime.year, month=datetime.month, day=datetime.day, hour=15, minute=30)
                            # tax_close_price = target_df[target_df['datetime'] == target_tax_time]['close'].iloc[0]
                            if target_tax_time in target_df['datetime'].values:
                                tax_close_price = target_df[target_df['datetime'] == target_tax_time]['close'].iloc[0]
                            else:
                                closest_time = target_df[target_df['datetime'] < target_tax_time]['datetime'].max()
                                tax_close_price = target_df[target_df['datetime'] == closest_time]['close'].iloc[0]
                            #환율 점프를 고려해줘야하는 케이스
                            if datetime.hour==18 and datetime.minute ==0:
                                # 시장 오픈 가격도 청산 기준을 만족한다면, 널뛰기 해서 먹기
                                if price_open<= night_target_price :
                                    profit = (short_position['price'] - price_open) * contracts
                                    tax_now = -((price_open - tax_close_price) * contracts * tax_rate)
                                # 시장 오픈 가격은 청산 기준을 만족 못함, but 종가는 만족 -> 지정가로 먹기
                                else:
                                    profit = (short_position['price'] - night_target_price) * contracts
                                    tax_now = -((night_target_price - tax_close_price) * contracts * tax_rate)
                            # 그렇지 않은 경우에는 내가 target 한 만큼만 먹는 게 맞지. 지정가 체결이니까
                            else:
                                profit = (short_position['price'] - night_target_price) * contracts
                                tax_now = -((night_target_price - tax_close_price) * contracts * tax_rate)
                        else:
                            continue
                    elif 0 <= datetime.hour <= 4:
                        night_target_price = short_position['price'] * (1 - b)
                        if price <= night_target_price:
                            one_day_before = datetime - pd.Timedelta(days=1)
                            target_tax_time = pd.Timestamp(year=one_day_before.year, month=one_day_before.month, day=one_day_before.day, hour=15, minute=30)
                            if target_tax_time in target_df['datetime'].values:
                                tax_close_price = target_df[target_df['datetime'] == target_tax_time]['close'].iloc[0]
                            else:
                                closest_time = target_df[target_df['datetime'] < target_tax_time]['datetime'].max()
                                tax_close_price = target_df[target_df['datetime'] == closest_time]['close'].iloc[0]
                            # 실제 청산되어서 세금이 매겨지는 가격은 night_target_price지. price가 아니라. 나는 지정가로 청산시키니까
                            tax_now = -((night_target_price - tax_close_price) * contracts * tax_rate)
                            # 00시 넘어서는 무조건 청산 가격 먹는 거로
                            profit = (short_position['price'] - night_target_price) * contracts
                        else:
                            continue
                    else:
                        #주간 청산 케이스
                        if datetime.hour == 9 and datetime.minute == 0:
                            # open 가가 이미 청산 기준 도달 -> 널뛰기 청산
                            if price_open<= short_position['short_target_price'] :
                                profit = (short_position['price'] - price_open) * contracts
                            # open가는 청산 기준 도달 하지 못했는데, close가 청산 도달
                            else:
                                profit = (short_position['price'] - short_position['short_target_price']) * contracts
                        else:
                            profit = (short_position['price'] - short_position['short_target_price']) * contracts

                        tax_now = 0


                    if tax_now !=0:
                        short_balance = short_balance+profit-tax_now
                        tax_total=tax_total+tax_now
                        tax_short_total=tax_short_total+tax_now
                    else:
                        short_balance = short_balance + profit

                    liquidations += 1
                    short_positions.pop(i)
                    total_num_cont = contracts + total_num_cont
                    short_num_cont = contracts + short_num_cont
                    # print("숏 청산",index,short_positions,long_positions)
                    short_liquid_flag=1
                    break
            # 아무 것도 없는 상태에서 short 포지션 새로 잡기
            if not short_positions and short_liquid_flag==0:
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

                if tax_now != 0:
                    short_balance = short_balance - tax_now
                    tax_total = tax_total + tax_now
                    tax_short_total = tax_short_total + tax_now

                target_price = round(price * (1 - a), 4)
                short_positions.append({'short_target_price': target_price,'datetime': datetime,'price' : price, 'n':n})
                total_num_cont = contracts + total_num_cont
                # print("초기 숏 잡기",index,short_positions,long_positions)
            else:
                #청산 후 바로 포지션 잡아버리는 거 막기 위함
                if not short_positions:
                    pass
                else:
                    if short_positions[-1]['price'] + n < price and price >GC+n/2  :
                        #널 뛰기 진입이 가능 -> 해당 경우 고려
                        if (datetime.hour == 9 and datetime.minute == 0) or (datetime.hour == 18 and datetime.minute == 0):
                            #널 뛰기 진입 가능하며, open가 부터 이미 진입 가격을 넘어버림 -> price_open로 진입
                            if short_positions[-1]['price'] + n < price_open:
                                target_price = round(price_open * (1 - a), 4)
                                short_positions.append({'short_target_price': target_price, 'datetime': datetime, 'price': price_open,'n':n})
                            else:
                                target_price = round((short_positions[-1]['price'] + n) * (1 - a), 4)
                                short_positions.append({'short_target_price': target_price, 'datetime': datetime, 'price': (short_positions[-1]['price'] + n),'n':n})
                        #널뛰기 진입이 불가능 -> 그래서  "short_positions[-1]['price'] + n"
                        else:
                            # 나는 지정가로 그리드 매매 하기 때문에, 딱 그 그리드 경계에서 매도 하는 거임. "그래서  short_positions[-1]['price'] + n"
                            target_price = round((short_positions[-1]['price'] + n) * (1 - a), 4)
                            short_positions.append({'short_target_price': target_price,'datetime': datetime,'price' : (short_positions[-1]['price'] + n),'n':n})
                        total_num_cont = contracts+total_num_cont
                        # print("숏 잡기 추가",index,short_positions,long_positions)
                        if 18 <= datetime.hour <= 23:
                            target_tax_time = pd.Timestamp(year=datetime.year, month=datetime.month, day=datetime.day, hour=15, minute=30)
                            if target_tax_time in target_df['datetime'].values:
                                tax_close_price = target_df[target_df['datetime'] == target_tax_time]['close'].iloc[0]
                            else:
                                closest_time = target_df[target_df['datetime'] < target_tax_time]['datetime'].max()
                                tax_close_price = target_df[target_df['datetime'] == closest_time]['close'].iloc[0]
                            tax_now = (((short_positions[-1]['price']) - tax_close_price) * contracts * tax_rate)
                        elif 0 <= datetime.hour <= 4:
                            one_day_before = datetime - pd.Timedelta(days=1)
                            target_tax_time = pd.Timestamp(year=one_day_before.year, month=one_day_before.month, day=one_day_before.day, hour=15, minute=30)
                            if target_tax_time in target_df['datetime'].values:
                                tax_close_price = target_df[target_df['datetime'] == target_tax_time]['close'].iloc[0]
                            else:
                                closest_time = target_df[target_df['datetime'] < target_tax_time]['datetime'].max()
                                tax_close_price = target_df[target_df['datetime'] == closest_time]['close'].iloc[0]
                            tax_now =  (((short_positions[-1]['price'])-tax_close_price) * contracts * tax_rate)
                        else:
                            tax_now = 0

                        if tax_now != 0:
                            short_balance = short_balance - tax_now
                            tax_total = tax_total + tax_now
                            tax_short_total = tax_short_total + tax_now

        if price < GC-buffer-n/2  or (price >= GC-buffer-n/2  and long_positions):
            for i, long_position in enumerate(long_positions):
                if price >= long_position['long_target_price']:
                    if 18 <= datetime.hour <= 23:
                        night_target_price = long_position['price'] * (1 + b)
                        if price >= night_target_price:
                            target_tax_time = pd.Timestamp(year=datetime.year, month=datetime.month, day=datetime.day, hour=15, minute=30)
                            if target_tax_time in target_df['datetime'].values:
                                tax_close_price = target_df[target_df['datetime'] == target_tax_time]['close'].iloc[0]
                            else:
                                closest_time = target_df[target_df['datetime'] < target_tax_time]['datetime'].max()
                                tax_close_price = target_df[target_df['datetime'] == closest_time]['close'].iloc[0]

                            if datetime.hour == 18 and datetime.minute == 0:
                            # 시장 오픈 가격도 청산 기준을 만족한다면, 널뛰기 해서 먹기
                                if price_open >= night_target_price:
                                    profit= (price_open-long_position['price'])*contracts
                                    tax_now = ((price_open - tax_close_price) * contracts * tax_rate)
                                else:
                                    profit = (night_target_price -long_position['price']) * contracts
                                    tax_now = ((night_target_price - tax_close_price) * contracts * tax_rate)
                            else:
                                profit = (night_target_price - long_position['price']) * contracts
                                tax_now = ((night_target_price - tax_close_price) * contracts * tax_rate)
                        else:

                            continue
                    elif 0 <= datetime.hour <= 4:
                        night_target_price = long_position['price'] * (1 + b)
                        if price >= night_target_price:
                            profit = (night_target_price - long_position['price']) * contracts
                            one_day_before = datetime - pd.Timedelta(days=1)
                            target_tax_time = pd.Timestamp(year=one_day_before.year, month=one_day_before.month, day=one_day_before.day, hour=15, minute=30)
                            if target_tax_time in target_df['datetime'].values:
                                tax_close_price = target_df[target_df['datetime'] == target_tax_time]['close'].iloc[0]
                            else:
                                closest_time = target_df[target_df['datetime'] < target_tax_time]['datetime'].max()
                                tax_close_price = target_df[target_df['datetime'] == closest_time]['close'].iloc[0]
                            tax_now =  ((night_target_price - tax_close_price) * contracts * tax_rate)
                        else:

                            continue
                    else:
                        if datetime.hour == 9 and datetime.minute == 0:
                            # open 가가 이미 청산 기준 도달 -> 널뛰기 청산
                            if price_open >= long_position['long_target_price']:
                                profit = (price_open-long_position['price']) * contracts
                            else:
                                profit = (long_position['long_target_price']-long_position['price']) * contracts
                        else:
                            profit = (long_position['long_target_price']-long_position['price']) * contracts
                        tax_now = 0


                    if tax_now != 0:
                        long_balance = long_balance + profit - tax_now
                        tax_total = tax_total + tax_now
                        tax_long_total = tax_long_total + tax_now
                    else:
                        long_balance = long_balance + profit

                    liquidations += 1
                    long_positions.pop(i)
                    total_num_cont = contracts + total_num_cont
                    long_num_cont = contracts + long_num_cont
                    # print("롱 청산",index,short_positions,long_positions)
                    long_liquid_flag=1
                    break
            if not long_positions and long_liquid_flag==0:
                #포지션이 없을 때는 그냥 close 가격인 price 기준으로 들어가는 거지
                target_price = round(price * (1 + a), 4)
                long_positions.append({'long_target_price': target_price,'datetime': datetime,'price' : price,'n':n})
                total_num_cont = contracts + total_num_cont
                # print("초기 롱 잡기",index,short_positions,long_positions)
                if 18 <= datetime.hour <= 23:
                    target_tax_time = pd.Timestamp(year=datetime.year, month=datetime.month, day=datetime.day, hour=15, minute=30)
                    if target_tax_time in target_df['datetime'].values:
                        tax_close_price = target_df[target_df['datetime'] == target_tax_time]['close'].iloc[0]
                    else:
                        closest_time = target_df[target_df['datetime'] < target_tax_time]['datetime'].max()
                        tax_close_price = target_df[target_df['datetime'] == closest_time]['close'].iloc[0]
                    # 포지션이 없을 때는 그냥 close 가격인 price 기준으로 들어가는 거지
                    tax_now =  -((price - tax_close_price) * contracts * tax_rate)
                elif 0 <= datetime.hour <= 4:
                    one_day_before = datetime - pd.Timedelta(days=1)
                    target_tax_time = pd.Timestamp(year=one_day_before.year, month=one_day_before.month, day=one_day_before.day, hour=15, minute=30)
                    if target_tax_time in target_df['datetime'].values:
                        tax_close_price = target_df[target_df['datetime'] == target_tax_time]['close'].iloc[0]
                    else:
                        closest_time = target_df[target_df['datetime'] < target_tax_time]['datetime'].max()
                        tax_close_price = target_df[target_df['datetime'] == closest_time]['close'].iloc[0]
                    # 포지션이 없을 때는 그냥 close 가격인 price 기준으로 들어가는 거지
                    tax_now =  -((price - tax_close_price) * contracts * tax_rate)
                else:
                    tax_now = 0

                if tax_now != 0:
                    long_balance = long_balance - tax_now
                    tax_total = tax_total + tax_now
                    tax_long_total = tax_long_total + tax_now

            else:
                if not long_positions:
                    pass
                else:
                    if long_positions[-1]['price'] - n > price and price < GC-buffer-n/2 :
                        # 널 뛰기 진입이 가능 -> 해당 경우 고려
                        if (datetime.hour == 9 and datetime.minute == 0) or (datetime.hour == 18 and datetime.minute == 0):
                            # 시장이 새로 열리자 마자 price_open가격이 그리드 기준을 넘어섬 -> 널뛰기 진입 -> price_open가로 진입
                            if long_positions[-1]['price'] - n > price_open:
                                target_price = round(price_open * (1 + a), 4)
                                long_positions.append({'long_target_price': target_price, 'datetime': datetime, 'price': price_open,'n':n})
                            # close 가격은 기준 그리드를 넘어서서 포지션을 잡아야하는데, open은 만족 x -> 기존 그리드 대로 포지션 잡기
                            else:
                                target_price = round((long_positions[-1]['price'] - n) * (1 + a), 4)
                                long_positions.append({'long_target_price': target_price, 'datetime': datetime, 'price': (long_positions[-1]['price'] - n),'n':n})
                        else:
                            # Create a new short position
                            target_price = round((long_positions[-1]['price'] - n) * (1 + a), 4)
                            long_positions.append({'long_target_price': target_price,'datetime': datetime,'price' : (long_positions[-1]['price'] - n),'n':n})
                        total_num_cont = contracts + total_num_cont
                        # print("롱 잡기 추가",index,short_positions,long_positions)
                        if 18 <= datetime.hour <= 23:
                            target_tax_time = pd.Timestamp(year=datetime.year, month=datetime.month, day=datetime.day, hour=15, minute=30)
                            if target_tax_time in target_df['datetime'].values:
                                tax_close_price = target_df[target_df['datetime'] == target_tax_time]['close'].iloc[0]
                            else:
                                closest_time = target_df[target_df['datetime'] < target_tax_time]['datetime'].max()
                                tax_close_price = target_df[target_df['datetime'] == closest_time]['close'].iloc[0]
                            tax_now =  -(((long_positions[-1]['price']) - tax_close_price) * contracts * tax_rate)
                        elif 0 <= datetime.hour <= 4:
                            one_day_before = datetime - pd.Timedelta(days=1)
                            target_tax_time = pd.Timestamp(year=one_day_before.year, month=one_day_before.month, day=one_day_before.day, hour=15, minute=30)
                            if target_tax_time in target_df['datetime'].values:
                                tax_close_price = target_df[target_df['datetime'] == target_tax_time]['close'].iloc[0]
                            else:
                                closest_time = target_df[target_df['datetime'] < target_tax_time]['datetime'].max()
                                tax_close_price = target_df[target_df['datetime'] == closest_time]['close'].iloc[0]
                            tax_now =  -(((long_positions[-1]['price']) - tax_close_price) * contracts * tax_rate)
                        else:
                            tax_now = 0

                        if tax_now != 0:
                            long_balance = long_balance - tax_now
                            tax_total = tax_total + tax_now
                            tax_long_total = tax_long_total + tax_now

    short_leftover = len(short_positions)
    long_leftover = len(long_positions)

    return short_balance, long_balance, liquidations, total_num_cont,short_num_cont,long_num_cont,short_leftover,long_leftover, tax_total, tax_short_total, tax_long_total

profits = np.zeros((len(a_range), len(b_range), len(n_range), len(atr_coeff_range)))
short_profits = np.zeros((len(a_range), len(b_range), len(n_range), len(atr_coeff_range)))
long_profits = np.zeros((len(a_range), len(b_range), len(n_range), len(atr_coeff_range)))
num_liquidations_array = np.zeros((len(a_range), len(b_range), len(n_range), len(atr_coeff_range)))
total_commission_array = np.zeros((len(a_range), len(b_range), len(n_range), len(atr_coeff_range)))

# Create empty lists to store values
a_values = []
b_values = []
n_values = []
atr_coeff_values = []
num_liquidations_values = []
total_commission_values = []
short_profit_values = []
long_profit_values = []
total_profit_values = []
short_leftover_values = []
long_leftover_values = []
tax_total_values = []
tax_short_total_values = []
tax_long_total_values = []

# a,n에 따라 수익을 계산하기 위한 이중 for문
for i, a in enumerate(a_range):
    for j, n in enumerate(n_range):
        for k, b in enumerate(b_range):
            for jj, atr_coeff in enumerate(atr_coeff_range):
                # if b < a:
                #     continue
                short_balance, long_balance, num_liquidations, total_num_cont,short_num_cont,long_num_cont,short_leftover,long_leftover,tax_total, tax_short_total, tax_long_total \
                    = calculate_profit(a,b,n,atr_coeff)
                total_commission = total_num_cont * commission
                short_commission = short_num_cont * commission
                long_commission = long_num_cont * commission
                profits[i][k][j][jj] = short_balance + long_balance - initial_balance - total_commission
                short_profits[i][k][j][jj] = short_balance - initial_balance - short_commission
                long_profits[i][k][j][jj] = long_balance - initial_balance - long_commission
                num_liquidations_array[i][k][j][jj] = num_liquidations
                total_commission_array[i][k][j][jj] = total_commission


                print(round(a,4),round(b,4), n,round(atr_coeff,1), num_liquidations,round(total_commission,1),round(short_profits[i][k][j][jj],1),round(long_profits[i][k][j][jj],1), round(profits[i][k][j][jj],1),
                      short_leftover,long_leftover,round(tax_total,1), round(tax_short_total,1), round(tax_long_total,1))

                # Append values to lists
                a_values.append(a)
                b_values.append(b)
                n_values.append(n)
                atr_coeff_values.append(atr_coeff)
                num_liquidations_values.append(num_liquidations)
                total_commission_values.append(total_commission)
                short_profit_values.append(short_profits[i][k][j][jj])
                long_profit_values.append(long_profits[i][k][j][jj])
                total_profit_values.append(profits[i][k][j][jj])
                short_leftover_values.append(short_leftover)
                long_leftover_values.append(long_leftover)
                tax_total_values.append(tax_total)
                tax_short_total_values.append(tax_short_total)
                tax_long_total_values.append(tax_long_total)
# Create a DataFrame from the lists
data = {
    'a': a_values,
    'b': b_values,
    'n': n_values,
    'atr_coeff': atr_coeff_values,
    'num_liquidations': num_liquidations_values,
    'total_commission': total_commission_values,
    'short_profits': short_profit_values,
    'long_profits': long_profit_values,
    'total_profits': total_profit_values,
    'short_leftover': short_leftover_values,
    'long_leftover': long_leftover_values,
    'tax_total': tax_total_values,
    'tax_short_total': tax_short_total_values,
    'tax_long_total': tax_long_total_values
}

df_export = pd.DataFrame(data)

today = datetime.now().strftime('%Y%m%d')[2:]
file_name = f'{today}_simulation_result_VP{percent_start},{percent_finish},{percent_gap}_{b_percent_start},{b_percent_finish},{b_percent_gap}_{n_start},{n_finish},{n_gap}_wholeday.xlsx'
df_export.to_excel(file_name, index=False)

# 엑셀 파일에서 데이터를 불러옵니다
file_path = 'C:/Users/world/PycharmProjects/Dollar_future/'+file_name
data = pd.read_excel(file_path)

# # a와 b에 따라 데이터를 그룹화하고 total_profits의 평균을 계산합니다
# grouped_data = data.groupby(['a', 'b']).total_profits.mean().reset_index()
#
# # 데이터를 그리드로 변환합니다
# x = grouped_data['a']
# y = grouped_data['b']
# z = grouped_data['total_profits']
# x_grid, y_grid = np.meshgrid(x.unique(), y.unique())
#
# # 그리드에 대해 z 값을 보간합니다
# z_grid = griddata((x, y), z, (x_grid, y_grid), method='cubic')
#
# # 2D 컨투어 플롯을 그립니다
# fig, ax = plt.subplots(figsize=(10, 7))
# contour = ax.contourf(x_grid, y_grid, z_grid, cmap='viridis', levels=20)
# plt.colorbar(contour, ax=ax, label='Total Profits')
#
# # 레이블과 제목을 설정합니다
# ax.set_xlabel('a')
# ax.set_ylabel('b')
# ax.set_title('2D Contour plot of Total Profits by a and b')
#
# # 플롯을 보여줍니다
# plt.show()