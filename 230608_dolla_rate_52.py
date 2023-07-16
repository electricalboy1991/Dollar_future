from alpha_vantage.foreignexchange import ForeignExchange
import datetime

# Set up your Alpha Vantage API key
api_key = 'T0DHVSRQXW800IKR'

# Create an instance of the ForeignExchange class
fx = ForeignExchange(key=api_key)

# Define the base currency and target currency
base_currency = 'USD'
target_currency = 'KRW'

# Set the end date as today and calculate the start date
end_date = datetime.datetime.today().strftime('%Y-%m-%d')
start_date = (datetime.datetime.today() - datetime.timedelta(days=365)).strftime('%Y-%m-%d')

# Retrieve the exchange rate data
data, _ = fx.get_currency_exchange_daily(from_symbol=base_currency, to_symbol=target_currency, outputsize='full')

# Filter the data for the desired date range
filtered_data = {date: value for date, value in data.items() if start_date <= date <= end_date}

# Extract the close prices from the filtered data
close_prices = [float(value['4. close']) for value in filtered_data.values()]

# Print the close prices
print(close_prices)