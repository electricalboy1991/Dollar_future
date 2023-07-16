import yfinance as yf
import time

def get_exchange_rate():
    ticker = yf.Ticker("USDKRW=X")  # Yahoo Finance symbol for USD to PHP exchange rate
    exchange_rate = ticker.history().tail(1)["Close"].values[0]
    return exchange_rate

def get_dollar_index():
    ticker = yf.Ticker("DX-Y.NYB")  # Yahoo Finance symbol for the dollar index
    data = ticker.history().tail(1)
    return data

gap_ratio_aver = 8.000315361
consen_rate = 1220
rate_gap_criteria = 3
min_temp = 0

time_info = time.gmtime()
hour = time_info.tm_hour
min = time_info.tm_min

if min_temp == min:
    min_flag = 0
else:
    min_flag = 1
min_temp = min

usd_to_krw = get_exchange_rate()
print("Current exchange rate (USD to KRW):", usd_to_krw)

dollar_index_data = get_dollar_index()
dollar_index_value = dollar_index_data["Close"].values[0]
print("Real-time value of Dollar Index:", dollar_index_value)

std_value =dollar_index_value/gap_ratio_aver*100
print("적정 환율", std_value)


# if abs(usd_to_krw-std_value)<rate_gap_criteria:
#
# else:



