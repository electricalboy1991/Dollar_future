from alpha_vantage.timeseries import TimeSeries

# Set your Alpha Vantage API key
api_key = 'HWZOMLBRHSJIBIS5'

# Create a TimeSeries instance
ts = TimeSeries(key=api_key)

# Specify the symbol for Dollar Index
symbol = 'DX'

# Retrieve the daily exchange rate data for a year
data, _ = ts.get_daily_adjusted(symbol=symbol, outputsize='full')

# Print the retrieved data
for date, values in data.items():
    print(f"Date: {date}")
    print(f"Open: {values['1. open']}")
    print(f"High: {values['2. high']}")
    print(f"Low: {values['3. low']}")
    print(f"Close: {values['4. close']}")
    print()