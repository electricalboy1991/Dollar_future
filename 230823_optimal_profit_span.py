# -*- coding: utf-8 -*-

import pandas as pd

df = pd.read_csv('n분석_data.csv')

# %%

import pandas as pd
from datetime import datetime

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

# 시간축으로 오름차순 정렬
cal_df = filtered_df.sort_values(by='datetime')

# %%

close_df = cal_df.close
change_range = [i / 10 for i in range(2, 151)]
# change_range = [i for i in range(1, 10)]
# change_range = [4]

data = []
min_month = 43200

for k in range(17):
    close = close_df[-1:-1 * (k + 1) * min_month:-1]
    for j in range(len(change_range)):
        cnt = 0
        print(k + 1, change_range[j])
        for i in range(len(close)):
            if i == 0:
                std = close.iloc[0]

            if abs(std - close.iloc[i]) >= change_range[j]:
                std = close.iloc[i]
                cnt += 1

        data.append([k + 1, change_range[j], cnt, 5 * (change_range[j] ** 2) * cnt / 2])

find_max = pd.DataFrame(data)
print(find_max)
num = find_max[2].idxmax(axis=1)
print(find_max.loc[num])

# %%

a = 3
p = 10

print((a ** 2) * p / 2)

# 한달 기준 43200분
min_month = 43200

# k = [i for i in range(1, 12)]

for k in range(17):
    tt = close_df[-1:-1 * (k + 1) * min_month:-1]
    print(tt.tail(1))
# %%
find_max = pd.DataFrame(find_max)
find_max.to_csv('N_Max.csv')