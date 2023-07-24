def check_and_send_message(range_gap, range_gap_list, flags, Telegram_str):
    if range_gap > 0:
        for i, gap in enumerate(range_gap_list):
            flag_key = f'flag_{i}'
            if range_gap > gap and flags[flag_key] == 0:
                line_alert.SendMessage_SP(f"[ USD 숏으로 벌기 \U0001F534 숏 {i+1}]" + Telegram_str)
                flags[flag_key] = 1

        for i, gap in enumerate(range_gap_list):
            flag_key = f'flag_{i+1}'
            if range_gap < gap and flags[flag_key] == 1:
                line_alert.SendMessage_SP(f"[USD 숏으로 벌기 \U0001F535 롱 {i+2}]" + Telegram_str)
                flags[flag_key] = 0
    else:
        pass