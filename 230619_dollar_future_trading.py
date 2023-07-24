import dollar_future_fuction as dff
import time
import line_alert
from datetime import datetime
from pytz import timezone
import sys
import os
import traceback
import platform
import json
import numpy as np

if platform.system() == 'Windows':
    data_52_index_gap_file_path = "C:\\Users\world\PycharmProjects\Crypto\data_52_index_gap.json"
else:
    data_52_index_gap_file_path = "/var/autobot/data_52_index_gap.json"

def read_data_52_index_gap():
    try:
        with open(data_52_index_gap_file_path, 'r', encoding="utf-8") as json_file:
            return json.load(json_file)
    except Exception as e:
        # First time or file does not exist
        return []

def calculate_range_and_telegram_str(usd_to_krw, dollar_index_value, data_52_index_gap):
    gap_ratio_aver = np.mean(data_52_index_gap)
    std_value = dollar_index_value / gap_ratio_aver * 100
    range_gap = round(usd_to_krw - std_value, 2)
    position_down_crit = 24

    if range_gap < 0:
        if range_gap >-26:
            Telegram_str = " \n# 포지션 : " + str(round(-1 * range_gap * 4 / 3, 1)) + " 개 Long " + "\n$ Range : " + str(-1 * range_gap) + " Long" + " \n$ 환율 : " + str(round(usd_to_krw, 2)) + " \n$ 적정 : " + str(round(std_value, 2))
        else:
            Telegram_str = " \n# 포지션 : " + str(round(position_down_crit * 4 / 3+(-range_gap-position_down_crit)*5/6, 1)) + " 개 Long " + "\n$ Range : " + str(-1 * range_gap) + " Long" + " \n$ 환율 : " + str(round(usd_to_krw, 2)) + " \n$ 적정 : " + str(round(std_value, 2))
    else:
        if range_gap < 26:
            Telegram_str = " \n# 포지션 : " + str(round(range_gap * 4 / 3, 1)) + " 개 Short " + "\n$ Range :  " + str(range_gap) + " Short" + " \n$ 환율 : " + str(round(usd_to_krw, 2)) + " \n$ 적정 : " + str(round(std_value, 2))
        else:
            Telegram_str = " \n# 포지션 : " + str(round(position_down_crit * 4 / 3+(range_gap-position_down_crit)*5/6, 1))+ " 개 Short " + "\n$ Range :  " + str(range_gap) + " Short" + " \n$ 환율 : " + str(round(usd_to_krw, 2)) + " \n$ 적정 : " + str(round(std_value, 2))

    return range_gap, Telegram_str

def check_and_send_message(range_gap, range_gap_list, flags, Telegram_str):
    for i, gap in enumerate(range_gap_list):
        flag_key = f'flag_{i}'
        if range_gap > gap and flags[flag_key] == 0:
            line_alert.SendMessage_SP(f"[USD \U0001F534 숏 {i+1}]" + Telegram_str)
            flags[flag_key] = 1

    for i, gap in enumerate(range_gap_list):
        flag_key = f'flag_{i}'
        if range_gap < gap and flags[flag_key] == 1:
            line_alert.SendMessage_SP(f"[USD \U0001F535 롱 {i+1}]" + Telegram_str)
            flags[flag_key] = 0

range_gap_list = [6 + i * 6 for i in range(20)]

if __name__ == "__main__":
    flags = {f'flag_{i}': 0 for i in range(20)}
    min_temp = 0

    while True:
        try:
            if platform.system() == 'Windows':
                pass
            else:
                time.sleep(5.5)

            time_info = time.gmtime()
            hour = time_info.tm_hour
            min = time_info.tm_min

            if min_temp == min:
                min_flag = 0
            else:
                min_flag = 1
            min_temp = min

            data_52_index_gap = read_data_52_index_gap()

            usd_to_krw = dff.get_exchange_rate()
            print("Current exchange rate (USD to KRW):", usd_to_krw)

            dollar_index_data = dff.get_dollar_index()
            dollar_index_value = dollar_index_data["Close"].values[0]
            print("Real-time value of Dollar Index:", dollar_index_value)

            if hour == 6 and min == 29 and min_flag == 1 and time_info.tm_wday < 5:
                gap_ratio_today = dollar_index_value / usd_to_krw * 100
                data_52_index_gap.pop()
                data_52_index_gap.insert(0, gap_ratio_today)
                with open(data_52_index_gap_file_path, 'w') as outfile:
                    json.dump(data_52_index_gap, outfile)

            range_gap, Telegram_str = calculate_range_and_telegram_str(usd_to_krw, dollar_index_value, data_52_index_gap)

            check_and_send_message(range_gap, range_gap_list, flags, Telegram_str)

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

            line_alert.SendMessage_Trading('[달러 선물 Error] : \n' + str(err) + '\n[파일] : ' + str(fname) + '\n[라인 넘버] : ' + str(exc_tb.tb_lineno))
