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
import yfinance as yf

if platform.system() == 'Windows':
    data_52_index_gap_file_path = "C:\\Users\world\PycharmProjects\Dollar_future\data_52_index_gap.json"
    data_52_index_gap_JP_file_path = "C:\\Users\world\PycharmProjects\Dollar_future\data_52_index_gap_JP.json"
    data_52_dollar_file_path = "C:\\Users\world\PycharmProjects\Dollar_future\data_52_dollar.json"
    data_52_yen_file_path = "C:\\Users\world\PycharmProjects\Dollar_future\data_52_yen.json"
    data_52_index_file_path = "C:\\Users\world\PycharmProjects\Dollar_future\data_52_index.json"
else:
    data_52_index_gap_file_path = "/var/autobot/data_52_index_gap.json"
    data_52_index_gap_JP_file_path = "/var/autobot/data_52_index_gap_JP.json"
    data_52_dollar_file_path = "/var/autobot/data_52_dollar.json"
    data_52_yen_file_path = "/var/autobot/data_52_yen.json"
    data_52_index_file_path = "/var/autobot/data_52_index.json"

reer_url = "https://stats.bis.org/api/v1"
flow = "BIS,WS_EER_D"
key = "D.N.B.KR"
key_JP = "D.N.B.JP"
reer_std, reer_std_JP = 0, 0
GC_basis, GC_basis_JP = 1200, 1050
gap_ratio_aver = 7.996879864
consen_rate, rate_gap_criteria, min_temp = 1200, 3, 0
position_span = 5
range_gap_list = [position_span + i * position_span for i in range(position_span*5)]
range_gap_list_JP = [position_span + i * position_span for i in range(position_span*5)]
position_down_crit_JP = 20
position_down_crit = 25
investment_flag = 1
investment_flag_JP = 1
MA80_flag = 1
#이거 MA로 투자 필터링하는 경우
MA_filter_criteria = 70

sigma_below = 5/5
sigma_above = 4/5
sigma_below_JP = 6/5
sigma_above_JP = 6/7

DX_ratio = 0.6
reer_ratio = 1-DX_ratio

def load_data(url):
    response = requests.get(url)
    return BeautifulSoup(response.text, 'html.parser')

def get_data_frame(soup, data_key):
    reer_table = soup.find_all("obs")
    reer_data = [[item.get("time_period"), item.get("obs_value")] for item in reer_table]
    reer_df = pd.DataFrame(reer_data, columns=['Date', data_key])
    reer_df.set_index('Date', inplace=True)
    return reer_df

def get_currency_data(ticker, start_date, end_date):
    # Fetch data using yfinance
    data = yf.download(ticker, start=start_date, end=end_date)

    # Filter relevant columns (Open, High, Low, Close) and create a new DataFrame
    df = pd.DataFrame(data, columns=["Open", "High", "Low", "Close"])
    df.index = df.index.date
    df.index = df.index.astype("str")
    return df

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


def check_and_send_message(range_gap, range_gap_list, flags, Telegram_str):
    if '$' in Telegram_str:
        nation = '\U0001F4B0 USD'
    else:
        nation = '\U0001F64A YEN'

    # 숏으로 포지션 잡는 단계
    if range_gap > 0:
        for i, gap in enumerate(range_gap_list):
            flag_key = f'flag_{i}'
            if range_gap > gap and flags[flag_key] == 0:
                line_alert.SendMessage_SP(f"[ {nation} 숏 ing \U0001F534 숏 포지션 늘리기 {i+1}]" + Telegram_str)
                flags[flag_key] = 1

        for i, gap in enumerate(range_gap_list):
            flag_key = f'flag_{i+1}'
            if range_gap < gap and flags[flag_key] == 1:
                line_alert.SendMessage_SP(f"[ {nation} 숏 ing \U0001F535 롱 수익화 {i+2}]" + Telegram_str)
                flags[flag_key] = 0

        if range_gap < 1 and flags['flag_0'] ==1 :
            line_alert.SendMessage_SP(f"[ {nation} 숏 ing \U0001F535 롱 수익화 1]" + Telegram_str)
            flags['flag_0'] = 0

    # 롱으로 포지션 잡는 단계
    else:
        for i, gap in enumerate(range_gap_list):
            flag_key = f'flag_{i}'
            if -range_gap > gap and flags[flag_key] == 0:
                line_alert.SendMessage_SP(f"[ {nation} 롱 ing \U0001F535 롱 포지션 늘리기 {i+1}]" + Telegram_str)
                flags[flag_key] = 1

        for i, gap in enumerate(range_gap_list):
            flag_key = f'flag_{i+1}'
            if -range_gap < gap and flags[flag_key] == 1:
                line_alert.SendMessage_SP(f"[ {nation} 롱 ing \U0001F534 숏 수익화 {i+2}]" + Telegram_str)
                flags[flag_key] = 0

        if -range_gap < 1 and flags['flag_0'] ==1 :
            line_alert.SendMessage_SP(f"[ {nation} 롱 ing \U0001F534 숏 수익화 1]" + Telegram_str)
            flags['flag_0'] = 0

if __name__ == "__main__":
    flags = {f'flag_{i}': 0 for i in range(position_span*5+1)}
    flags_JP = {f'flag_{i}': 0 for i in range(position_span*5+1)}
    min_temp = 0
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

                ticker = "KRW=X"  # Ticker for USD/KRW currency pair in yfinance
                ticker_JP = "JPY=X"

                end_date = datetime.today().strftime('%Y-%m-%d')
                start_date = (datetime.today() - timedelta(days=400)).strftime('%Y-%m-%d')

                alpha_df = get_currency_data(ticker, start_date, end_date)
                alpha_df_JP = get_currency_data(ticker_JP, start_date, end_date)

                merged_df = pd.merge(reer_df, alpha_df, left_index=True, right_index=True)
                merged_df_JP = pd.merge(reer_df_JP, alpha_df_JP, left_index=True, right_index=True)

                # merged_df = pd.merge(reer_df, alpha_df)
                # merged_df_JP = pd.merge(reer_df_JP, alpha_df_JP)

                merged_df.REER = merged_df.REER.astype('float')
                merged_df_JP.REER = merged_df_JP.REER.astype('float')
                merged_df.Close = merged_df.Close.astype('float')
                merged_df_JP.Close = merged_df_JP.Close.astype('float')

                reer_gap = merged_df.REER[-255:].mean() * merged_df.Close[-255:].mean() / 10000
                reer_gap_JP= merged_df_JP.REER[-255:].mean() * merged_df_JP.Close[-255:].mean() / 10000

                merged_df['gap'] = merged_df.REER * merged_df.Close / 10000
                merged_df_JP['gap'] = merged_df_JP.REER * merged_df_JP.Close / 10000

                reer_std = (reer_gap/ merged_df.REER[-1] * 10000)
                reer_std_JP = (reer_gap_JP / merged_df_JP.REER[-1] * 10000)

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

            dollar_index_value = dff.get_dollar_index()
            print("Real-time value of Dollar Index:", dollar_index_value)

            if hour == 6 and min == 29 and min_flag == 1 and not time_info.tm_wday >= 5:
                gap_ratio_today = dollar_index_value / usd_to_krw * 100
                gap_ratio_today_JP = dollar_index_value / usd_to_jpy * 100

                dollar_today =  usd_to_krw
                yen_today = usd_to_jpy

                update_data(data_52_index_gap_file_path, gap_ratio_today)
                update_data(data_52_index_gap_JP_file_path, gap_ratio_today_JP)

                update_data(data_52_dollar_file_path , dollar_today)
                update_data(data_52_yen_file_path, yen_today)
                update_data(data_52_index_file_path, dollar_index_value)

                gap_ratio_aver = np.mean(json.load(open(data_52_index_file_path)))/np.mean(json.load(open(data_52_dollar_file_path)))
                gap_ratio_aver_JP = np.mean(json.load(open(data_52_index_file_path)))/np.mean(json.load(open(data_52_yen_file_path)))
            else:
                gap_ratio_aver = np.mean(json.load(open(data_52_index_file_path))) / np.mean(json.load(open(data_52_dollar_file_path)))
                gap_ratio_aver_JP = np.mean(json.load(open(data_52_index_file_path))) / np.mean(json.load(open(data_52_yen_file_path)))

            DX_std = dollar_index_value / gap_ratio_aver
            DX_std_JP = dollar_index_value / gap_ratio_aver_JP

            std = DX_ratio*DX_std + reer_ratio*reer_std
            GC = 0.5 * (std + GC_basis)
            MA = np.mean(json.load(open(data_52_dollar_file_path))[:100])
            print("적정 환율 달러/원 ", std)

            std_JP = std / (DX_ratio*DX_std_JP + reer_ratio*reer_std_JP) * 100
            GC_JP = 0.5 * (std_JP + GC_basis_JP)
            print("적정 환율 Yen/원 ", std_JP)

            range_gap = round(usd_to_krw - std, 2)
            range_gap_JP = round(jpy_to_krw - std_JP, 2)
            Telegram_str = f"\nRange: {range_gap}\n환율: {round(usd_to_krw, 2)}\n적정: {round(std, 2)}"

            if time_info.tm_wday == 5 or (time_info.tm_wday ==6 and hour <21):
                pass
            else:
                if range_gap < 0:
                    if range_gap > -position_down_crit:
                        Telegram_str = " \n# 추가 포지션 : " + str(round(position_span*sigma_below, 1)) + " 개 Long " +" \n# 포지션 : " + str(round(-1 * range_gap * sigma_below, 1)) + " 개 Long " + "\n$ Range : " + str(-1 * range_gap) + " Long" \
                                       + " \n$ 환율 : " + str(round(usd_to_krw, 2)) + " \n$ 적정 : " + str(round(std, 2))+" \n$ GC : " + str(round(GC, 2))+" \n$ MA filter : " + str(round(MA+MA_filter_criteria, 2))
                    else:
                        Telegram_str = " \n# 추가 포지션 : " + str(round(position_span*sigma_above, 1)) + " 개 Long " +" \n# 포지션 : " + str(round(position_down_crit * sigma_below + (-range_gap - position_down_crit) * sigma_above, 1)) + " 개 Long " \
                                       + "\n$ Range : " + str(-1 * range_gap) + " Long" + " \n$ 환율 : " + str(round(usd_to_krw, 2)) + " \n$ 적정 : " + str(round(std, 2))+" \n$ GC : " + str(round(GC, 2))+" \n$ MA filter: " + str(round(MA+MA_filter_criteria, 2))
                else:
                    if range_gap < position_down_crit:
                        Telegram_str = " \n# 추가 포지션 : " + str(round(position_span*sigma_below, 1)) + " 개 Short " +" \n# 포지션 : " + str(round(range_gap * sigma_below, 1)) + " 개 Short " + "\n$ Range :  " + str(range_gap) + " Short" \
                                       + " \n$ 환율 : " + str(round(usd_to_krw, 2)) + " \n$ 적정 : " + str(round(std, 2))+" \n$ GC : " + str(round(GC, 2))+" \n$ MA filter: " + str(round(MA+MA_filter_criteria, 2))
                    else:
                        Telegram_str = " \n# 추가 포지션 : " + str(round(position_span*sigma_above, 1)) + " 개 Short " +" \n# 포지션 : " + str(round(position_down_crit * sigma_below + (range_gap - position_down_crit) * sigma_above, 1)) + " 개 Short " \
                                       + "\n$ Range :  " + str(range_gap) + " Short" + " \n$ 환율 : " + str(round(usd_to_krw, 2)) + " \n$ 적정 : " + str(round(std, 2))+" \n$ GC : " + str(round(GC, 2))+" \n$ MA filter: " + str(round(MA+MA_filter_criteria, 2))

                if range_gap_JP < 0:
                    if range_gap_JP >-position_down_crit_JP:
                        Telegram_str_JP = f"\n# 추가 포지션 : {round(position_span*sigma_below_JP, 1)} 개 Long \n# 포지션: {round(-1*range_gap_JP * sigma_below_JP , 1)} 개 Long\n￥ Range: {-1*range_gap_JP} Long\n￥ 환율: {round(jpy_to_krw, 2)}\n￥ 적정: {round(std_JP, 2)}\n￥ GC: {round(GC_JP, 2)}"
                    else:
                        Telegram_str_JP = f"\n# 추가 포지션 : {round(position_span*sigma_above_JP, 1)} 개 Long \n# 포지션: {round(position_down_crit_JP* sigma_below_JP +(-range_gap_JP-position_down_crit_JP)* sigma_above_JP, 1)} 개 Long\n￥ Range: {-1 * range_gap_JP} Long\n" \
                                          f"￥ 환율: {round(jpy_to_krw, 2)}\n￥ 적정: {round(std_JP, 2)}\n￥ GC: {round(GC_JP, 2)}"
                else:
                    if range_gap_JP <position_down_crit_JP:
                        Telegram_str_JP = f"\n# 추가 포지션 : {round(position_span*sigma_below_JP, 1)} 개 Short \n# 포지션: {round(range_gap_JP * sigma_below_JP, 1)} 개 Short\n￥ Range: {range_gap_JP} Short\n￥ 환율: {round(jpy_to_krw, 2)}\n￥ 적정: {round(std_JP, 2)}\n￥ GC: {round(GC_JP, 2)}"
                    else:
                        Telegram_str_JP = f"\n# 추가 포지션 : {round(position_span*sigma_above_JP, 1)} 개 Short \n# 포지션: {round(position_down_crit_JP* sigma_below_JP +(range_gap_JP-position_down_crit_JP)* sigma_above_JP, 1)} 개 Long\n￥ Range: {-1 * range_gap_JP} Long\n" \
                                          f"￥ 환율: {round(jpy_to_krw, 2)}\n￥ 적정: {round(std_JP, 2)}\n￥ GC: {round(GC_JP, 2)}"

                check_and_send_message(range_gap, range_gap_list, flags, Telegram_str)
                check_and_send_message(range_gap_JP, range_gap_list_JP, flags_JP, Telegram_str_JP)


                if GC < usd_to_krw < std or GC > usd_to_krw > std:
                    line_alert.SendMessage_SP("[ \U0001F4B0 USD 투자 STOP (PV)  \U0001F6A8 ]" + Telegram_str)
                    investment_flag=0
                elif not(GC < usd_to_krw < std or GC > usd_to_krw > std) and investment_flag==0:
                    line_alert.SendMessage_SP("[ \U0001F4B0 USD 투자 START (PV)  \U0001F680 ]" + Telegram_str)
                    investment_flag = 1

                if GC_JP < jpy_to_krw < std_JP or GC_JP > usd_to_krw > std_JP:
                    line_alert.SendMessage_SP("[ \U0001F64A JPY 투자 STOP (PV)  \U0001F6A8 ]" + Telegram_str_JP)
                    investment_flag_JP = 0
                elif not(GC_JP < jpy_to_krw < std_JP or GC_JP > usd_to_krw > std_JP) and investment_flag_JP==0:
                    line_alert.SendMessage_SP("[ \U0001F64A USD 투자 START (PV)  \U0001F680 ]" + Telegram_str_JP)
                    investment_flag_JP = 1

                if np.mean(json.load(open(data_52_dollar_file_path))[:100]) + +MA_filter_criteria <= usd_to_krw:
                    line_alert.SendMessage_SP("[ \U0001F4B0 USD 투자 STOP (MA filter)  \U0001F6A8 ]" + Telegram_str)
                    MA80_flag = 0

                elif np.mean(json.load(open(data_52_dollar_file_path))[:100]) + +MA_filter_criteria > usd_to_krw and MA80_flag==0:
                    line_alert.SendMessage_SP("[ \U0001F4B0 USD 투자 START (MA filter)  \U0001F680 ]" + Telegram_str)
                    MA80_flag = 1

                if min_flag == 1:
                    current_time = datetime.now(timezone('Asia/Seoul'))
                    KR_time = str(current_time)
                    KR_time_sliced = KR_time[:23]
                    line_alert.SendMessage_dollar(f"JPY \U0001F64A{KR_time_sliced}\U0001F64A JPY{Telegram_str_JP}")
                else:
                    continue

                if min_flag == 1:
                    current_time = datetime.now(timezone('Asia/Seoul'))
                    KR_time = str(current_time)
                    KR_time_sliced = KR_time[:23]

                    line_alert.SendMessage_dollar("USD\U0001F4B0" + KR_time_sliced + "\U0001F4B0USD  \n" + Telegram_str)
                else:
                    continue

        except Exception as e:
            time.sleep(5.5)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            err = traceback.format_exc()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            line_alert.SendMessage_Trading(f'[달러 선물 Error]:\n{err}\n[파일]: {fname}\n[라인 넘버]: {exc_tb.tb_lineno}')


