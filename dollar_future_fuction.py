import yfinance as yf
import json
import requests
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from fake_useragent import UserAgent
import line_alert

# def get_exchange_rate():
#     ua = UserAgent()
#     header = {'User-Agent': str(ua.random)}
#     pair = 'USD'
#     BASE_URL = 'https://kr.investing.com/currencies/{}-{}'.format(pair.lower(), 'krw')
#     url = Request(BASE_URL, headers=header)
#     html = urlopen(url)
#
#     if html.status == 200:
#         # print('인베스팅')
#         soup = BeautifulSoup(html, 'html.parser')
#         element = soup.find('span', {'data-test': 'instrument-price-last'})
#         exchange_rate = round(float(element.text.replace(',', '')), 2)
#         return exchange_rate
#     else:
#         line_alert.SendMessage_SP("[ \U0001F535 달러/원 인베스팅 크롤링 실패 \U0001F535 ]" )
#         return 2000
#
# def get_exchange_rate_JP():
#     ua = UserAgent()
#     header = {'User-Agent': str(ua.random)}
#     pair = 'JPY'
#     BASE_URL = 'https://kr.investing.com/currencies/{}-{}'.format(pair.lower(), 'usd')
#     url = Request(BASE_URL, headers=header)
#     html = urlopen(url)
#
#     if html.status == 200:
#         # print('인베스팅')
#         soup = BeautifulSoup(html, 'html.parser')
#         element = soup.find('span', {'data-test': 'instrument-price-last'})
#         exchange_rate = 100/round(float(element.text.replace(',', '')), 2)
#         return exchange_rate
#     else:
#         line_alert.SendMessage_SP("[ \U0001F535 엔/달러 인베스팅 크롤링 실패 \U0001F535 ]")
#         return 200
#
# def get_exchange_rate_JP_KR():
#     ua = UserAgent()
#     header = {'User-Agent': str(ua.random)}
#     pair = 'JPY'
#     BASE_URL = 'https://kr.investing.com/currencies/{}-{}'.format(pair.lower(), 'krw')
#     url = Request(BASE_URL, headers=header)
#     html = urlopen(url)
#
#     if html.status == 200:
#         # print('인베스팅')
#         soup = BeautifulSoup(html, 'html.parser')
#         element = soup.find('span', {'data-test': 'instrument-price-last'})
#         exchange_rate = round(float(element.text.replace(',', '')), 2)
#         return exchange_rate
#     else:
#         line_alert.SendMessage_SP("[ \U0001F535 엔/원 인베스팅 크롤링 실패 \U0001F535 ]")
#         return 200
def get_dollar_index():
    ua = UserAgent()
    header = {'User-Agent': str(ua.random)}
    BASE_URL = 'https://kr.investing.com/currencies/us-dollar-index'
    url = Request(BASE_URL, headers=header)
    html = urlopen(url)

    if html.status == 200:
        # print('인베스팅')
        soup = BeautifulSoup(html, 'html.parser')
        element = soup.find('span', class_='arial_26 inlineblock pid-8827-last', id='last_last')
        DX = round(float(element.text.replace(',', '')), 2)
        return DX
    else:
        line_alert.SendMessage_SP("[ \U0001F535 DX 인베스팅 크롤링 실패 \U0001F535 ]")
        return 100

def get_exchange_rate():
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    url = 'https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRWUSD'
    exchange =requests.get(url, headers=headers).json()
    return exchange[0]['basePrice']


# # 야후 파이낸스
# def get_exchange_rate():
#     ticker = yf.Ticker("USDKRW=X")  # Yahoo Finance symbol for USD to PHP exchange rate
#     exchange_rate = ticker.history().tail(1)["Close"].values[0]
#     return exchange_rate

def get_exchange_rate_JP():
    ticker = yf.Ticker("USDJPY=X")  # Yahoo Finance symbol for USD to PHP exchange rate
    exchange_rate = ticker.history().tail(1)["Close"].values[0]
    return exchange_rate

def get_exchange_rate_JP_KR():
    ticker = yf.Ticker("JPYKRW=X")  # Yahoo Finance symbol for USD to PHP exchange rate
    exchange_rate = ticker.history().tail(1)["Close"].values[0]
    return exchange_rate

# def get_dollar_index():
#     ticker = yf.Ticker("DX-Y.NYB")  # Yahoo Finance symbol for the dollar index
#     data = ticker.history().tail(1)
#     return data

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
