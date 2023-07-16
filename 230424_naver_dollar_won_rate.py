import requests
from bs4 import BeautifulSoup

url = "https://finance.naver.com/marketindex/exchangeDailyQuote.nhn?marketindexCd=FX_USDKRW"
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")

# find the exchange rate value
exchange_rate = soup.find("td", class_="num").get_text()

print("Today's dollar-won exchange rate is:", exchange_rate)