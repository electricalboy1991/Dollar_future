import requests
import telegram
import asyncio
import sys

telegram_token_Log = '5751723602:AAEjojgFOutl4ffbDghL_urHx10ijEwkBeU'
telegram_id_Log = '5781986806'

telegram_token_SP = '5720042932:AAGnqMeLtxh3y-z_RcBywA3bJ7LF5cMxrZo'
telegram_id_SP = '5781986806'

telegram_token_Summary1minute = '5462808910:AAGDKsBtsM4B5Lc93rdfS3wX_YjvBnl-tYg'
telegram_id_Summary1minute = '5781986806'

telegram_token_1hourRSI = '5665272058:AAGwNJm80OfDarnzbqAp_ZLwAau3QRTYai8'
telegram_id_1hourRSI = '5781986806'

telegram_token_BV = '6044269270:AAG43ub5Pm6BlnRfngXbZZQq97oxRgg8JnY'
telegram_id_BV = '5781986806'

telegram_token_dollar = '6289628521:AAFzC4vFEzOjliBXoIN6ivsXcWx-Z1ljTic'
telegram_id_dollar = '5781986806'




#메세지를 보냅니다.
def SendMessage_Trading(msg):
    try:

        TARGET_URL = 'https://notify-api.line.me/api/notify'
        TOKEN = 'sINSUIhAuhPg4hIq1lMgtVcswlx4PL22DTLspAwAvsh' #여러분의 값으로 변경

        response = requests.post(
            TARGET_URL,
            headers={
                'Authorization': 'Bearer ' + TOKEN
            },
            data={
                'message': msg
            }
        )

    except Exception as ex:
        print(ex)

def SendMessage_Log(message):
    try:
        py_ver = int(f"{sys.version_info.major}{sys.version_info.minor}")
        if py_ver > 37 and sys.platform.startswith('win'):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        # 텔레그램 메세지 발송
        bot = telegram.Bot(telegram_token_Log)
        # res = bot.sendMessage(chat_id=telegram_id_Log, text=message)
        asyncio.run(bot.send_message(chat_id=telegram_id_Log, text=message))
        # return res

    # ----------------------------------------
    # 모든 함수의 공통 부분(Exception 처리)
    # ----------------------------------------
    except Exception:
        raise

def SendMessage_SP(message):
    try:
        py_ver = int(f"{sys.version_info.major}{sys.version_info.minor}")
        if py_ver > 37 and sys.platform.startswith('win'):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        # 텔레그램 메세지 발송
        bot = telegram.Bot(telegram_token_SP)
        # res = bot.sendMessage(chat_id=telegram_id_SP, text=message)
        asyncio.run(bot.send_message(chat_id=telegram_id_SP, text=message))
        # return res

    # ----------------------------------------
    # 모든 함수의 공통 부분(Exception 처리)
    # ----------------------------------------
    except Exception:
        raise


def SendMessage_Summary1minute(message):
    try:
        py_ver = int(f"{sys.version_info.major}{sys.version_info.minor}")
        if py_ver > 37 and sys.platform.startswith('win'):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        # 텔레그램 메세지 발송
        bot = telegram.Bot(telegram_token_Summary1minute)
        # res = bot.sendMessage(chat_id=telegram_id_Summary1minute, text=message)
        asyncio.run(bot.send_message(chat_id=telegram_id_Summary1minute, text=message))


        # return res

    # ----------------------------------------
    # 모든 함수의 공통 부분(Exception 처리)
    # ----------------------------------------
    except Exception:
        raise

def SendMessage_1hourRSI(message):
    try:
        py_ver = int(f"{sys.version_info.major}{sys.version_info.minor}")
        if py_ver > 37 and sys.platform.startswith('win'):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        # 텔레그램 메세지 발송
        bot = telegram.Bot(telegram_token_1hourRSI)
        # res = bot.sendMessage(chat_id=telegram_id_1hourRSI, text=message)
        asyncio.run(bot.send_message(chat_id=telegram_id_1hourRSI, text=message))


        # return res

    # ----------------------------------------
    # 모든 함수의 공통 부분(Exception 처리)
    # ----------------------------------------
    except Exception:
        raise

def SendMessage_BV(message):
    try:
        py_ver = int(f"{sys.version_info.major}{sys.version_info.minor}")
        if py_ver > 37 and sys.platform.startswith('win'):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        # 텔레그램 메세지 발송
        bot = telegram.Bot(telegram_token_BV)
        # res = bot.sendMessage(chat_id=telegram_id_BV, text=message)
        asyncio.run(bot.send_message(chat_id=telegram_id_BV, text=message))


        # return res

    # ----------------------------------------
    # 모든 함수의 공통 부분(Exception 처리)
    # ----------------------------------------
    except Exception:
        raise

def SendMessage_dollar(message):
    try:
        py_ver = int(f"{sys.version_info.major}{sys.version_info.minor}")
        if py_ver > 37 and sys.platform.startswith('win'):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        # 텔레그램 메세지 발송
        bot = telegram.Bot(telegram_token_dollar)
        # res = bot.sendMessage(chat_id=telegram_id_BV, text=message)
        asyncio.run(bot.send_message(chat_id=telegram_id_dollar, text=message))


        # return res

    # ----------------------------------------
    # 모든 함수의 공통 부분(Exception 처리)
    # ----------------------------------------
    except Exception:
        raise