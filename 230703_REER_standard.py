# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 16:31:06 2023

@author: soos.hwang
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta

### REER 정보 불러오기 ###
# REST API의 엔드포인트 URL
reer_url = "https://stats.bis.org/api/v1"

# Series ID
flow = "BIS,WS_EER_D"
key = "D.N.B.KR"

# 현재 날짜 가져오기
current_date = datetime.now().date()

# 1년 전 날짜 계산
one_year_ago = current_date - timedelta(days=400)

print("현재 날짜:", current_date)

# 요청 매개변수 (날짜)
period = f"startPeriod={one_year_ago}"

# 데이터를 가져올 URL 생성
reer_api_url = f"{reer_url}/data/{flow}/{key}/all?{period}"

# proxy_server = "12.26.204.100:8080"
# proxies = {"http": proxy_server, 'https': proxy_server}
# reer_response = requests.get(reer_api_url, proxies=proxies, verify=False)
reer_response = requests.get(reer_api_url)


if reer_response.status_code == 200:
    html = reer_response.text
    soup = BeautifulSoup(html, 'html.parser')

else:
    print(reer_response.status_code)

reer_table = soup.find_all("obs")  # 원하는 테이블을 찾는 방법을 적절하게 변경하세요

reer_data = []
for i in range(len(reer_table)):
    reer_data.append([reer_table[i].get("time_period"), reer_table[i].get("obs_value")])

# Pandas DataFrame으로 변환
reer_df = pd.DataFrame(reer_data, columns=['Date', 'REER'])

### 환율 정보 불러오기 ###
# Alpha Vantage API 키
alpha_api_key = "HWZOMLBRHSJIBIS5"

# Alpha Vantage API 엔드포인트 URL
alpha_url = f"https://www.alphavantage.co/query?function=FX_DAILY&from_symbol=USD&to_symbol=KRW&outputsize=full&apikey={alpha_api_key}"
alpha_url_index = f"https://www.alphavantage.co/query?function=FX_DAILY&from_symbol=USD&to_symbol=DX&outputsize=full&apikey={alpha_api_key}"

# API 요청
# proxy_server = "12.26.204.100:8080"
# proxies = {"http": proxy_server, 'https': proxy_server}
# alpha_response = requests.get(alpha_url, proxies=proxies, verify=False)
alpha_response = requests.get(alpha_url)
alpha_data = alpha_response.json()


alpha_index_response = requests.get(alpha_url_index)
alpha_index_data = alpha_index_response.json()



# JSON 데이터를 DataFrame으로 변환
alpha_df = pd.DataFrame(alpha_data["Time Series FX (Daily)"]).T

# 열 이름 변경
alpha_df.columns = ["open", "high", "low", "close"]

# 가장 최근 400일 데이터 선택
alpha_df = alpha_df.iloc[:400]

reer_df.set_index('Date', inplace=True)
merged_df = pd.merge(reer_df, alpha_df, left_index=True, right_index=True)

merged_df.REER = merged_df.REER.astype('float')
merged_df.close = merged_df.close.astype('float')
merged_df['gap'] = merged_df.REER * merged_df.close / 10000

proper_value = (merged_df.gap[-255:].median() / merged_df.REER[-1] * 10000 + 1200) / 2
print('REER 최신 날짜 : ', reer_data[-1][0])
print(proper_value, proper_value - 1261)


