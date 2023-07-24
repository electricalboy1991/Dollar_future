import dollar_future_fuction as dff
import time
import line_alert
from pytz import timezone
import sys
import os
import traceback
import platform
import json
import numpy as np
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta

if platform.system() == 'Windows':
    data_52_index_gap_file_path = "C:\\Users\world\PycharmProjects\Dollar_future\data_52_index_gap.json"
    data_52_index_gap_JP_file_path = "C:\\Users\world\PycharmProjects\Dollar_future\data_52_index_gap_JP.json"
else:
    data_52_index_gap_file_path = "/var/autobot/data_52_index_gap.json"
    data_52_index_gap_JP_file_path = "/var/autobot/data_52_index_gap_JP.json"

reer_url = "https://stats.bis.org/api/v1"
flow = "BIS,WS_EER_D"
key = "D.N.B.KR"
key_JP = "D.N.B.JP"
reer_std, reer_std_JP = 0, 0
GC_basis, GC_basis_JP = 1200, 1050
gap_ratio_aver = 7.996879864
consen_rate, rate_gap_criteria, min_temp = 1200, 3, 0
range_gap_list = [3,6,9,12,15,17,20,23,26,29,32,35]
range_gap_list_JP = [6 + i * 6 for i in range(20)]
flags = [0] * 20
position_down_crit = 18

def load_data(url):
    response = requests.get(url)
    return BeautifulSoup(response.text, 'html.parser')

def get_data_frame(soup, data_key):
    reer_table = soup.find_all("obs")
    reer_data = [[item.get("time_period"), item.get("obs_value")] for item in reer_table]
    reer_df = pd.DataFrame(reer_data, columns=['Date', data_key])
    reer_df.set_index('Date', inplace=True)
    return reer_df

def get_alpha_data(alpha_api_key, url):
    response = requests.get(url)
    alpha_data = response.json()
    alpha_df = pd.DataFrame(alpha_data["Time Series FX (Daily)"]).T
    alpha_df.columns = ["open", "high", "low", "close"]
    alpha_df = alpha_df.iloc[:400]
    return alpha_df

def get_dollar_index_value(dollar_index_data):
    return dollar_index_data["Close"].values[0]

def update_data(data_path, gap_ratio_today):
    data = list()
    try:
        with open(data_path, 'r', encoding="utf-8") as json_file:
            data = json.load(json_file)
    except Exception as e:
        print(f"Exception: {e}")
    data.pop()
    data.insert(0, gap_ratio_today)
    with open(data_path, 'w') as outfile:
        json.dump(data, outfile)

while True:
    try:
        if platform.system() == 'Windows':
            pass
        else:
            time.sleep(5.5)
        time_info = time.gmtime()
        hour, min = time_info.tm_hour, time_info.tm_min

        if hour == 8 or reer_std == 0:
            current_date = datetime.now().date()
            one_year_ago = current_date - timedelta(days=400)

            print("현재 날짜:", current_date)

            period = f"startPeriod={one_year_ago}"
            reer_api_url = f"{reer_url}/data/{flow}/{key}/all?{period}"
            reer_api_url_JP = f"{reer_url}/data/{flow}/{key_JP}/all?{period}"

            reer_response = requests.get(reer_api_url)
            reer_response_JP = requests.get(reer_api_url_JP)

            if reer_response.status_code == 200:
                soup = BeautifulSoup(reer_response.text, 'html.parser')
                soup_JP = BeautifulSoup(reer_response_JP.text, 'html.parser')
            else:
                print(reer_response.status_code)
                print(reer_response_JP.status_code)

            reer_df = get_data_frame(soup, 'REER')
            reer_df_JP = get_data_frame(soup_JP, 'REER')

            alpha_api_key = "HWZOMLBRHSJIBIS5"
            alpha_url = f"https://www.alphavantage.co/query?function=FX_DAILY&from_symbol=USD&to_symbol=KRW&outputsize=full&apikey={alpha_api_key}"
            alpha_url_JP = f"https://www.alphavantage.co/query?function=FX_DAILY&from_symbol=USD&to_symbol=JPY&outputsize=full&apikey={alpha_api_key}"

            alpha_df = get_alpha_data(alpha_api_key, alpha_url)
            alpha_df_JP = get_alpha_data(alpha_api_key, alpha_url_JP)

            merged_df = pd.merge(reer_df, alpha_df, left_index=True, right_index=True)
            merged_df_JP = pd.merge(reer_df_JP, alpha_df_JP, left_index=True, right_index=True)

            merged_df.REER = merged_df.REER.astype('float')
            merged_df_JP.REER = merged_df_JP.REER.astype('float')
            merged_df.close = merged_df.close.astype('float')
            merged_df_JP.close = merged_df_JP.close.astype('float')

            merged_df['gap'] = merged_df.REER * merged_df.close / 10000
            merged_df_JP['gap'] = merged_df_JP.REER * merged_df_JP.close / 10000

            reer_std = (merged_df.gap[-255:].median() / merged_df.REER[-1] * 10000)
            reer_std_JP = (merged_df_JP.gap[-255:].median() / merged_df_JP.REER[-1] * 10000)

        if min_temp == min:
            min_flag = 0
        else:
            min_flag = 1
        min_temp = min


        usd_to_krw = dff.get_exchange_rate()
        print("Current exchange rate (USD to KRW):", usd_to_krw)

        usd_to_jpy = dff.get_exchange_rate_JP()
        print("Current exchange rate (USD to JPY):", usd_to_jpy)

        jpy_to_krw = 100 * dff.get_exchange_rate_JP_KR()
        print("Current exchange rate (JPY to WON):", jpy_to_krw)

        dollar_index_data = dff.get_dollar_index()
        dollar_index_value = get_dollar_index_value(dollar_index_data)
        print("Real-time value of Dollar Index:", dollar_index_value)

        if hour == 6 and min == 29 and min_flag == 1 and not time_info.tm_wday >= 5:
            gap_ratio_today = dollar_index_value / usd_to_krw * 100
            gap_ratio_today_JP = dollar_index_value / usd_to_jpy * 100
            update_data(data_52_index_gap_file_path, gap_ratio_today)
            update_data(data_52_index_gap_JP_file_path, gap_ratio_today_JP)
            gap_ratio_aver = np.mean(json.load(open(data_52_index_gap_file_path)))
            gap_ratio_aver_JP = np.mean(json.load(open(data_52_index_gap_JP_file_path)))
        else:
            gap_ratio_aver = np.mean(json.load(open(data_52_index_gap_file_path)))
            gap_ratio_aver_JP = np.mean(json.load(open(data_52_index_gap_JP_file_path)))

        DX_std = dollar_index_value / gap_ratio_aver * 100
        DX_std_JP = dollar_index_value / gap_ratio_aver_JP * 100

        std = 0.5 * (DX_std + reer_std)
        GC = 0.5 * (std + GC_basis)
        print("적정 환율 달러/원 ", std)

        std_JP = std / (0.5 * (DX_std_JP + reer_std_JP)) * 100
        GC_JP = 0.5 * (std_JP + GC_basis_JP)
        print("적정 환율 Yen/원 ", std_JP)

        range_gap = round(usd_to_krw - std, 2)
        range_gap_JP = round(jpy_to_krw - std_JP, 2)
        Telegram_str = f"\nRange: {range_gap}\n환율: {round(usd_to_krw, 2)}\n적정: {round(std, 2)}"

        if range_gap_JP < 0:
            if range_gap_JP >-19:
                Telegram_str_JP = f"\n# 포지션: {round(-1*range_gap_JP , 1)} 개 Long\n￥ Range: {-1*range_gap_JP} Long\n￥ 환율: {round(jpy_to_krw, 2)}\n￥ 적정: {round(std_JP, 2)}"
            else:
                Telegram_str_JP = f"\n# 포지션: {round(position_down_crit +(-range_gap_JP-position_down_crit)* 2 / 3, 1)} 개 Long\n￥ Range: {-1 * range_gap_JP} Long\n￥ 환율: {round(jpy_to_krw, 2)}\n￥ 적정: {round(std_JP, 2)}"
        else:
            if range_gap_JP <19:
                Telegram_str_JP = f"\n# 포지션: {round(range_gap_JP , 1)} 개 Short\n￥ Range: {range_gap_JP} Short\n￥ 환율: {round(jpy_to_krw, 2)}\n￥ 적정: {round(std_JP, 2)}"
            else:
                Telegram_str_JP = f"\n# 포지션: {round(position_down_crit +(range_gap_JP-position_down_crit)* 2 / 3, 1)} 개 Long\n￥ Range: {-1 * range_gap_JP} Long\n￥ 환율: {round(jpy_to_krw, 2)}\n￥ 적정: {round(std_JP, 2)}"

        for i in range(20):
            if range_gap_JP > range_gap_list_JP[i] and flags[i] == 0:
                line_alert.SendMessage_SP(f"[JPY '\U0001F534' 숏 {i+1}]{Telegram_str_JP}")
                flags[i] = 1
            elif range_gap_JP < 0 and flags[i] == 1:
                line_alert.SendMessage_SP(f"[JPY '\U0001F535' 롱 {i+1}]{Telegram_str_JP}")
                flags[i] = 0

        if min_flag == 1:
            current_time = datetime.now(timezone('Asia/Seoul'))
            KR_time = str(current_time)
            KR_time_sliced = KR_time[:23]
            line_alert.SendMessage_dollar(f"JPY \U0001F64A{KR_time_sliced}\U0001F64A JPY{Telegram_str_JP}")
        else:
            continue
    except Exception as e:
        time.sleep(5.5)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        err = traceback.format_exc()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        line_alert.SendMessage_Trading(f'[달러 선물 Error]:\n{err}\n[파일]: {fname}\n[라인 넘버]: {exc_tb.tb_lineno}')


