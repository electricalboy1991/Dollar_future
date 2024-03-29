# -*- coding: utf-8 -*-
"""
Created on Thu Jun  8 15:45:31 2023

@author: soos.hwang
"""

import requests
from bs4 import BeautifulSoup

url = 'https://kin.naver.com/search/list.nhn?query=%ED%8C%8C%EC%9D%B4%EC%8D%AC'

proxy_server = "12.26.204.100:8080"
proxies = {"http":proxy_server,'https':proxy_server}
response = requests.get(url,proxies=proxies,verify=False)

if response.status_code == 200:
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    print(soup)

else :
    print(response.status_code)

#%%

import requests

def get_data_from_api(url, params=None):
    try:
        proxy_server = "12.26.204.100:8080"
        proxies = {"http":proxy_server,'https':proxy_server}
        response = requests.get(url, proxies=proxies,verify=False)
        response.raise_for_status()  # HTTP 오류 검사
        data = response.json()  # JSON 데이터를 파싱하여 파이썬 객체로 변환
        return data
    except requests.exceptions.RequestException as e:
        print("오류 발생:", e)
        return None

# REST API의 엔드포인트 URL
base_url = "https://stats.bis.org/api/v1"

# 임의의 시리즈 ID
# series_id = "XCGB_EA_NCB_GBP_H.V.M5.BA."
flow = "BIS,WS_EER_D"
key = "D.N.N.KR"

# 요청 매개변수 (시작 날짜와 끝 날짜)
period = "startPeriod=2023-01-01"
# period = "startPeriod=2023-01-01&endPeriod=2023-01-20"

# 데이터를 가져올 URL 생성
api_url = f"{base_url}/data/{flow}/{key}/all?{period}"

# 데이터를 가져올 URL 호출
# data = get_data_from_api(api_url, params=params)
data = get_data_from_api(api_url)

if data is not None:
    print('1')
    # 데이터 처리
    print(data)
    # 여기에서 데이터를 사용하는 추가적인 로직을 구현할 수 있습니다.
else:
    print("데이터를 가져오지 못했습니다.")

#%%

