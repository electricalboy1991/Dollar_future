import yfinance as yf

def get_dollar_index():
    ticker = yf.Ticker("DX-Y.NYB")  # Yahoo Finance symbol for the dollar index
    data = ticker.history().tail(1)
    return data

dollar_index_data = get_dollar_index()
realtime_value = dollar_index_data["Close"].values[0]
print("Real-time value of Dollar Index:", realtime_value)
