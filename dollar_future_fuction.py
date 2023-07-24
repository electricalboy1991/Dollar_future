import yfinance as yf
import json
import requests

def get_exchange_rate():
    ticker = yf.Ticker("USDKRW=X")  # Yahoo Finance symbol for USD to PHP exchange rate
    exchange_rate = ticker.history().tail(1)["Close"].values[0]
    return exchange_rate

def get_exchange_rate_JP():
    ticker = yf.Ticker("USDJPY=X")  # Yahoo Finance symbol for USD to PHP exchange rate
    exchange_rate = ticker.history().tail(1)["Close"].values[0]
    return exchange_rate

def get_exchange_rate_JP_KR():
    ticker = yf.Ticker("JPYKRW=X")  # Yahoo Finance symbol for USD to PHP exchange rate
    exchange_rate = ticker.history().tail(1)["Close"].values[0]
    return exchange_rate

def get_dollar_index():
    ticker = yf.Ticker("DX-Y.NYB")  # Yahoo Finance symbol for the dollar index
    data = ticker.history().tail(1)
    return data

def hashkey(datas):
    APP_KEY = "PSM9hB6QskUJju5b2ZnswSNfyBLuN7bwNT6C"
    APP_SECRET = "er9i/53546V3MMu8RfnFuVkVPsChL2bMlfOTQMTPmC6IAJc++Do5qhHFTzngUmk+axlQEGhNnCsr55Kchdf/61caICocHv7Sn9yQy2g0NPPBCFhLIWtlYp9nB6374l4AADNLfdpbrybEYxlWzN/KTwYtqvZcKVvipPfdhBZ2ck7ZJuXJCgU="
    URL_BASE = "https://openapivts.koreainvestment.com:29443"  # 모의투자서비스

    PATH = "uapi/hashkey"
    URL = f"{URL_BASE}/{PATH}"
    headers = {
        'content-Type' : 'application/json',
        'appKey' : APP_KEY,
        'appSecret' : APP_SECRET,
        }

    res = requests.post(URL, headers=headers, data=json.dumps(datas))
    hashkey = res.json()["HASH"]

    return hashkey

def access_token():

    APP_KEY = "PSM9hB6QskUJju5b2ZnswSNfyBLuN7bwNT6C"
    APP_SECRET = "er9i/53546V3MMu8RfnFuVkVPsChL2bMlfOTQMTPmC6IAJc++Do5qhHFTzngUmk+axlQEGhNnCsr55Kchdf/61caICocHv7Sn9yQy2g0NPPBCFhLIWtlYp9nB6374l4AADNLfdpbrybEYxlWzN/KTwYtqvZcKVvipPfdhBZ2ck7ZJuXJCgU="
    URL_BASE = "https://openapivts.koreainvestment.com:29443"  # 모의투자서비스

    headers = {"content-type": "application/json"}
    body = {"grant_type": "client_credentials",
            "appkey": APP_KEY,
            "appsecret": APP_SECRET}

    PATH = "oauth2/tokenP"
    URL = f"{URL_BASE}/{PATH}"

    res = requests.post(URL, headers=headers, data=json.dumps(body))
    ACCESS_TOKEN = res.json()["access_token"]
    return ACCESS_TOKEN
