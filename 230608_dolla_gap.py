from alpha_vantage.foreignexchange import ForeignExchange
import yfinance as yf
import datetime
import pandas as pd
"""달러/원 환율"""
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


"""달러 인덱스"""
# Define the ticker symbol for the Dollar Index
ticker_symbol = 'DX-Y.NYB'

# Set the start and end dates
end_date = datetime.datetime.today().strftime('%Y-%m-%d')
start_date = (datetime.datetime.today() - datetime.timedelta(days=365)).strftime('%Y-%m-%d')

# Fetch the Dollar Index data from Yahoo Finance
dollar_index = yf.download(tickers=ticker_symbol, start=start_date, end=end_date)

close_index  = dollar_index['Close']
# Print the retrieved data

# print(dollar_index)
# print(close_index)
#
# # Print the close prices
# print(close_prices)

new_dataframe = pd.DataFrame({'OriginalSeries': close_index, 'NewColumn': close_prices})

print(new_dataframe)
