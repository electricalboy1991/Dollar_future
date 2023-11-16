import pandas as pd
from datetime import datetime, timedelta

# Load the OHLC data
file_path = 'n분석_data_columnEdited.csv'  # Replace with your file path
ohlc_data = pd.read_csv(file_path)

# Convert the 'datetime' column to datetime objects
ohlc_data['datetime'] = pd.to_datetime(ohlc_data['datetime'], format='%y-%m-%d %H:%M')
ohlc_data['datetime'] = ohlc_data['datetime'] - pd.Timedelta(hours=1)
# Sort the data by datetime just in case
ohlc_data.sort_values(by='datetime', inplace=True)

# Reset index after sorting
ohlc_data.reset_index(drop=True, inplace=True)

# Function to check for missing data and delete accordingly
def delete_missing_data(df):
    i = 0
    while i < len(df) - 1:
        # Calculate the time difference between consecutive rows
        time_diff = df.iloc[i+1]['datetime'] - df.iloc[i]['datetime']

        # Check if time difference is more than 1 hour
        if time_diff > timedelta(hours=1):
            # Case 1: Missing data after 9 AM
            if df.iloc[i]['datetime'].time() >= datetime.strptime("09:00", "%H:%M").time():
                start_time = datetime.combine(df.iloc[i]['datetime'].date(), datetime.strptime("09:00", "%H:%M").time())
                end_time = datetime.combine(df.iloc[i]['datetime'].date() + timedelta(days=1), datetime.strptime("01:30", "%H:%M").time())
                df = df.drop(df[(df['datetime'] >= start_time) & (df['datetime'] <= end_time)].index)

            # Case 2: Missing data between 0:00 AM and 1:30 AM
            elif datetime.strptime("00:00", "%H:%M").time() <= df.iloc[i]['datetime'].time() <= datetime.strptime("01:30", "%H:%M").time():
                start_time = datetime.combine(df.iloc[i]['datetime'].date() - timedelta(days=1), datetime.strptime("09:00", "%H:%M").time())
                end_time = datetime.combine(df.iloc[i]['datetime'].date(), datetime.strptime("01:30", "%H:%M").time())
                df = df.drop(df[(df['datetime'] >= start_time) & (df['datetime'] <= end_time)].index)

        i += 1

    return df

# Apply the function to the dataframe
ohlc_data_cleaned = delete_missing_data(ohlc_data)

# Export the cleaned data to a new CSV file
output_file_path = '231115_DataFilterForVolatiliyAnalysis_timeSplit.csv'  # Replace with your desired output file path
ohlc_data_cleaned.to_csv(output_file_path, index=False)

print(f"Data exported to {output_file_path}")