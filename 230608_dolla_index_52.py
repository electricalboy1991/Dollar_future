import yfinance as yf
import datetime
import pandas as pd


# Define the ticker symbol for the Dollar Index
ticker_symbol = 'DX-Y.NYB'

# Set the start and end dates
end_date = datetime.datetime.today().strftime('%Y-%m-%d')
start_date = (datetime.datetime.today() - datetime.timedelta(days=365)).strftime('%Y-%m-%d')

# Fetch the Dollar Index data from Yahoo Finance
dollar_index = yf.download(tickers=ticker_symbol, start=start_date, end=end_date)

close_index  = dollar_index['Close']
# Print the retrieved data
print(dollar_index)
print(close_index)


# close_index.to_excel('output.xlsx', index=False)

