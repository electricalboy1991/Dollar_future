# -*- coding: utf-8 -*-
"""
Created on Wed Jun 21 16:39:21 2023

@author: soos.hwang
"""

import requests
import time
import pandas as pd
from datetime import datetime, timedelta

# Your API key here
api_key = 'f6941ac4a40d4635941258966b8f3d9c'

# Define the symbol and interval
symbol = 'usd/krw'
interval = '1min'

# Define the date range
# start_date = datetime.now() - timedelta(days=1)  # 10 year ago
start_date = "2020-04-06 16:34:00"
start_date = datetime(2020, 4, 6, 16, 34, 0)
end_date = datetime.now()

# Empty list to store the data
data = []

## Samsung
proxy_server = "12.26.204.100:8080"
proxies = {"http": proxy_server, 'https': proxy_server}

print('end_date : ', end_date)
# Loop to fetch the data in chunks
cnt = 0
while start_date < end_date:
    # Define the start and end dates for this chunk
    cnt += 1
    print(cnt)
    chunk_start_date = start_date
    chunk_end_date = min(start_date + timedelta(minutes=5000), end_date)  # Limit to 5000 data points

    # Define the API request URL
    url = f'https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&apikey={api_key}&start_date={chunk_start_date.strftime("%Y-%m-%d")}&end_date={chunk_end_date.strftime("%Y-%m-%d")}'

    # Make the API request
    # response = requests.get(url, proxies=proxies, verify=False)
    response = requests.get(url)

    # Append the data to the list
    data.extend(response.json()['values'])

    # Update the start date for the next chunk

    start_date = chunk_start_date + timedelta(minutes=5000)

# Convert the data to a pandas DataFrame
df = pd.DataFrame(data)

# %%

c_df = df.drop_duplicates(['datetime']).sort_values(by=['datetime'])
# %%

c_df.to_csv('n분석_data.csv')


