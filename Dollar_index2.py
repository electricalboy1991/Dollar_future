from alpha_vantage.foreignexchange import ForeignExchange

# Set your Alpha Vantage API key
api_key = 'HWZOMLBRHSJIBIS5'

# Create a ForeignExchange instance
fx = ForeignExchange(key=api_key)

# Specify the symbol for Dollar Index
from_currency = 'USD'
to_currency = 'DX'

# Specify the desired output size ('compact' or 'full')
output_size = 'full'

# Retrieve the daily exchange rate data for a year
data, _ = fx.get_currency_exchange_daily(from_symbol=from_currency, to_symbol=to_currency, outputsize=output_size)

# Print the retrieved data
for date, values in data.items():
    print(f"Date: {date}")
    print(f"Open: {values['1. open']}")
    print(f"High: {values['2. high']}")
    print(f"Low: {values['3. low']}")
    print(f"Close: {values['4. close']}")
    print()
