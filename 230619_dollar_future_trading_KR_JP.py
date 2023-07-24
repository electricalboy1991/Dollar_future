import dollar_future_fuction as dff
import time
import line_alert #라인,텔레그램 메세지를 보내기 위함!
from pytz import timezone
import sys, os
import traceback
import platform
import json
import numpy as np

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta


if platform.system() == 'Windows':
    data_52_index_gap_JP_file_path = "C:\\Users\world\PycharmProjects\Crypto\data_52_index_gap_JP.json"
else:
    data_52_index_gap_JP_file_path = "/var/autobot/data_52_index_gap_JP.json"

### REER 정보 불러오기 ###
reer_url = "https://stats.bis.org/api/v1"

# Series ID
flow = "BIS,WS_EER_D"
key = "D.N.B.JP"

reer_std = 0
GC_basis = 1030

gap_ratio_aver = 7.996879864
rate_gap_criteria = 3
min_temp = 0

range_gap_list = [3,6,9,12,15,17,20,23,26,29,32,35]
flag_0 = 0
flag_1 = 0
flag_2 = 0
flag_3 = 0
flag_4 = 0
flag_5 = 0
flag_6 = 0
flag_7 = 0
flag_8 = 0
flag_9 = 0
flag_10 = 0

time_info = time.gmtime()
hour = time_info.tm_hour


while True:
    try :

        if platform.system() == 'Windows':
            pass
        else:
            time.sleep(5.5)

        time_info = time.gmtime()
        hour = time_info.tm_hour
        min = time_info.tm_min

        if hour == 8 or reer_std == 0:
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
            alpha_url = f"https://www.alphavantage.co/query?function=FX_DAILY&from_symbol=USD&to_symbol=JPY&outputsize=full&apikey={alpha_api_key}"

            # API 요청
            # proxy_server = "12.26.204.100:8080"
            # proxies = {"http": proxy_server, 'https': proxy_server}
            # alpha_response = requests.get(alpha_url, proxies=proxies, verify=False)
            alpha_response = requests.get(alpha_url)
            alpha_data = alpha_response.json()

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

            reer_std = (merged_df.gap[-255:].median() / merged_df.REER[-1] * 10000)


        if min_temp == min:
            #second time, third time, ...
            min_flag = 0
        else:
            # first time
            min_flag = 1
        min_temp = min

        data_52_index_gap_JP = list()
        try:
            # 이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다.
            with open(data_52_index_gap_JP_file_path, 'r', encoding="utf-8") as json_file:
                data_52_index_gap_JP = json.load(json_file)

        except Exception as e:
            # 처음에는 파일이 존재하지 않을테니깐 당연히 예외처리가 됩니다!
            print("Exception by First 0")

        usd_to_krw = dff.get_exchange_rate()
        print("Current exchange rate (USD to KRW):", usd_to_krw)

        dollar_index_data = dff.get_dollar_index()
        dollar_index_value = dollar_index_data["Close"].values[0]
        print("Real-time value of Dollar Index:", dollar_index_value)

        # 달러 인덱스 갭차이 52주 평균을 넣어주기 위한 코드
        # 주말 걸러내기 위한 flag
        is_weekend = time_info.tm_wday >= 5
        if hour == 6 and min == 29 and min_flag==1 and is_weekend!= True:
            gap_ratio_today=dollar_index_value/usd_to_krw*100
            data_52_index_gap_JP.pop()
            data_52_index_gap_JP.insert(0, gap_ratio_today)
            with open(data_52_index_gap_JP_file_path, 'w') as outfile:
                json.dump(data_52_index_gap_JP, outfile)
            gap_ratio_aver = np.mean(data_52_index_gap_JP)

        else:
            gap_ratio_aver = np.mean(data_52_index_gap_JP)


        DX_std = dollar_index_value / gap_ratio_aver * 100

        std = 0.5*(DX_std+reer_std)
        GC = 0.5*(std+GC_basis)
        print("적정 환율", std)

        range_gap=round(usd_to_krw-std,2)
        Telegram_str = "\nRange : "+str(range_gap) +" \n환율 : "+str(round(usd_to_krw,2))  +" \n적정 : "+str(round(std,2))

        if range_gap >range_gap_list[0] and flag_0 == 0:
            line_alert.SendMessage_SP("[\U0001F534 숏 1]" + Telegram_str)
            flag_0 = 1

        elif range_gap > range_gap_list[1] and flag_1 == 0:
            line_alert.SendMessage_SP("[\U0001F534 숏 2]" + Telegram_str)
            flag_1 = 1

        elif range_gap > range_gap_list[2] and flag_2 == 0:
            line_alert.SendMessage_SP("[\U0001F534 숏 3]" + Telegram_str)
            flag_2 = 1

        elif range_gap > range_gap_list[3] and flag_3 == 0:
            line_alert.SendMessage_SP("[\U0001F534 숏 4]" + Telegram_str)
            flag_3 = 1
        elif range_gap > range_gap_list[4] and flag_4 == 0:
            line_alert.SendMessage_SP("[\U0001F534 숏 5]" + Telegram_str)
            flag_4 = 1
        elif range_gap > range_gap_list[5] and flag_5 == 0:
            line_alert.SendMessage_SP("[\U0001F534 숏 6]" + Telegram_str)
            flag_5 = 1
        elif range_gap > range_gap_list[6] and flag_6 == 0:
            line_alert.SendMessage_SP("[\U0001F534 숏 7]" + Telegram_str)
            flag_6= 1
        elif range_gap > range_gap_list[7] and flag_7 == 0:
            line_alert.SendMessage_SP("[\U0001F534 숏 8]" + Telegram_str)
            flag_7 = 1
        elif range_gap > range_gap_list[8] and flag_8 == 0:
            line_alert.SendMessage_SP("[\U0001F534 숏 9]" + Telegram_str)
            flag_8 = 1
        elif range_gap > range_gap_list[9] and flag_9 == 0:
            line_alert.SendMessage_SP("[\U0001F534 숏 10]" + Telegram_str)
            flag_9 = 1
        elif range_gap > range_gap_list[10] and flag_10 == 0:
            line_alert.SendMessage_SP("[\U0001F534 숏 11]" + Telegram_str)
            flag_10 = 1




        if range_gap < 0 and flag_0 == 1:
            line_alert.SendMessage_SP("[\U0001F535 롱 1]" + Telegram_str)
            flag_0 = 0

        elif range_gap < range_gap_list[0] and flag_1 == 1:
            line_alert.SendMessage_SP("[\U0001F535 롱 2]" + Telegram_str)
            flag_1 = 0

        elif range_gap < range_gap_list[1] and flag_2 == 1:
            line_alert.SendMessage_SP("[\U0001F535 롱 3]" + Telegram_str)
            flag_2 = 0

        elif range_gap < range_gap_list[2] and flag_3 == 1:
            line_alert.SendMessage_SP("[\U0001F535 롱 4]" + Telegram_str)
            flag_3 = 0
        elif range_gap < range_gap_list[3] and flag_4 == 1:
            line_alert.SendMessage_SP("[\U0001F535 롱 5]" + Telegram_str)
            flag_4 = 0
        elif range_gap < range_gap_list[4] and flag_5 == 1:
            line_alert.SendMessage_SP("[\U0001F535 롱 6]" + Telegram_str)
            flag_5 = 0
        elif range_gap < range_gap_list[5] and flag_6 == 1:
            line_alert.SendMessage_SP("[\U0001F535 롱 7]" + Telegram_str)
            flag_6 = 0
        elif range_gap < range_gap_list[6] and flag_7 == 1:
            line_alert.SendMessage_SP("[\U0001F535 롱 8]" + Telegram_str)
            flag_7 = 0
        elif range_gap < range_gap_list[7] and flag_8 == 1:
            line_alert.SendMessage_SP("[\U0001F535 롱 9]" + Telegram_str)
            flag_8 = 0
        elif range_gap < range_gap_list[8] and flag_9 == 1:
            line_alert.SendMessage_SP("[\U0001F535 롱 10]" + Telegram_str)
            flag_9 = 0
        elif range_gap < range_gap_list[9] and flag_10 == 1:
            line_alert.SendMessage_SP("[\U0001F535 롱 11]" + Telegram_str)
            flag_10 = 0

        if min_flag == 1:
            current_time = datetime.now(timezone('Asia/Seoul'))
            KR_time = str(current_time)
            KR_time_sliced = KR_time[:23]

            line_alert.SendMessage_dollar("\U0001F64A" + KR_time_sliced + "\U0001F64A  \n" + Telegram_str)
        else:
            continue

    except Exception as e:
        time.sleep(5.5)
        # 처음에는 파일이 존재하지 않을테니깐 당연히 예외처리가 됩니다!
        exc_type, exc_obj, exc_tb = sys.exc_info()
        err = traceback.format_exc()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

        line_alert.SendMessage_Trading('[달러 선물 Error] : \n' + str(err) + '\n[파일] : ' + str(fname) + '\n[라인 넘버] : ' + str(exc_tb.tb_lineno))
        # line_alert.SendMessage_SP('[에러 김프 2] : \n' + str(err) + '\n[파일] : ' + str(fname) + '\n[라인 넘버] : ' + str(exc_tb.tb_lineno))