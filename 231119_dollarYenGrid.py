import dollar_future_fuction as dff
import line_alert
import platform
import time

position_initial = 135.5
position_span = 0.5
range_gap_list = [position_initial + i * position_span for i in range(0,60)]
nation = '\U0001F64A YEN'

if __name__ == "__main__":

    usd_to_jpy = dff.get_exchange_rate_JP()
    print("Current exchange rate (USD to JPY):", usd_to_jpy)
    idealNumPosition = 2 + 2 * round((usd_to_jpy - position_initial) / position_span, 0)


    flags = {f'flag_{i}': 0 for i in range(0,60+1)}
    min_temp = 0
    while True:
        if platform.system() == 'Windows':
            pass
        else:
            time.sleep(5.5)

        if usd_to_jpy > position_initial:
            for i, gap in enumerate(range_gap_list):
                flag_key = f'flag_{i}'
                if usd_to_jpy > gap:
                    if flags[flag_key] == 0:
                        line_alert.SendMessage_SP(f"[ {nation} 롱 ing \U0001F534 롱 포지션 늘리기 {i + 1}]  \n 현재 달러엔 {usd_to_jpy:.2f} \n포지션 갯수 : {idealNumPosition}")
                        flags[flag_key] = 1
                else:
                    break

            for i, gap in enumerate(range_gap_list):
                flag_key = f'flag_{i + 1}'
                if usd_to_jpy < gap and flags[flag_key] == 1:
                    line_alert.SendMessage_SP(f"[ {nation} 롱 ing \U0001F535 청산 수익화 {i + 2}] \n 현재 달러엔 {usd_to_jpy:.2f} \n포지션 갯수 : {idealNumPosition}")
                    flags[flag_key] = 0
                    break
                else:
                    pass

            if usd_to_jpy < 1 and flags['flag_0'] == 1:
                line_alert.SendMessage_SP(f"[ {nation} 롱 ing \U0001F535 청산 수익화 1]")
                flags['flag_0'] = 0

