
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from fake_useragent import UserAgent

ua = UserAgent()
header = {'User-Agent': str(ua.random)}

while 1:
    pair = 'USD'
    BASE_URL = 'https://kr.investing.com/currencies/{}-{}'.format(pair.lower(), 'krw')
    url = Request(BASE_URL, headers=header)
    html = urlopen(url)

    if html.status == 200:
        print('인베스팅')
        soup = BeautifulSoup(html, 'html.parser')
        element = soup.find('span', {'data-test': 'instrument-price-last'})
        print(round(float(element.text.replace(',', '')), 2))

    else:
        req_flag = 1
        # bot.send_message(chat_id=CHK_CHAT_ID, text=str(html.status) + ' 인베스팅 크롤링 실패...')


