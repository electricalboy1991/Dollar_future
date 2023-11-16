import pandas as pd
from datetime import datetime, timedelta

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

# Function to determine the day value based on conditions
def determine_day(row):
    # Convert Timestamp to string in the format '%y-%m-%d %H:%M'
    date_str = row['datetime'].strftime('%y-%m-%d %H:%M')

    # Parsing the datetime string to a datetime object
    date_time_obj = datetime.strptime(date_str, '%y-%m-%d %H:%M')

    # If time is between 00:00 and 01:15, subtract one day
    if date_time_obj.time() >= datetime.strptime("00:00", "%H:%M").time() and date_time_obj.time() <= datetime.strptime("01:15", "%H:%M").time():
        date_time_obj -= timedelta(days=1)

    # Return the date in '%Y-%m-%d' format
    return date_time_obj.strftime('%Y-%m-%d')

def categorize_time(row):
    time = row.time()
    if time >= pd.Timestamp('09:00').time() and time < pd.Timestamp('12:15').time():
        return '9am-12:15pm'
    elif time >= pd.Timestamp('12:15').time() and time < pd.Timestamp('15:30').time():
        return '12:15pm-15:30pm'
    #평상시 22~ 01:30 // 서머타임은 21시 00시30분 (4월 ~ 10월)
    elif time >= pd.Timestamp('22:00').time() or time < pd.Timestamp('01:15').time():
        return 'LtoC time'
    else:
        return 'other'

def largest_time_slot(row):
    if row['LtoC time'] > row['9am-12:15pm'] and row['LtoC time'] > row['12:15pm-15:30pm']:
        return 'LtoC time'
    elif row['9am-12:15pm'] > row['LtoC time'] and row['9am-12:15pm'] > row['12:15pm-15:30pm']:
        return '9am-12:15pm'
    else:
        return '12:15pm-15:30pm'

# Load the OHLC data
# 원본에서 이상한 인덱스만 제거함
file_path = 'n분석_data_columnEdited.csv'  # Replace with your file path
ohlc_data = pd.read_csv(file_path)

# Convert the 'datetime' column to datetime objects
ohlc_data['datetime'] = pd.to_datetime(ohlc_data['datetime'], format='%y-%m-%d %H:%M')
# 한시간 시프트 시키기. 인베스팅이랑 매칭
ohlc_data['datetime'] = ohlc_data['datetime'] - pd.Timedelta(hours=1)
# Sort the data by datetime just in case
ohlc_data.sort_values(by='datetime', inplace=True)

# Reset index after sorting
ohlc_data.reset_index(drop=True, inplace=True)

# 데이터 1시간 이상 비는 날 밀기
ohlc_data_cleaned = delete_missing_data(ohlc_data)


# Convert the 'datetime' column to datetime objects with the correct format
ohlc_data_cleaned['datetime'] = pd.to_datetime(ohlc_data_cleaned['datetime'], format='%Y-%m-%d %H:%M:%S')

# Apply the function to categorize each row
ohlc_data_cleaned['section'] = ohlc_data_cleaned['datetime'].apply(categorize_time)

# Filter out the data that does not fall into the defined time sections
filtered_data = ohlc_data_cleaned[ohlc_data_cleaned['section'] != 'other']

# Apply the function to each row in the DataFrame
filtered_data.loc[:, 'day'] = filtered_data.apply(determine_day, axis=1)

# Convert the 'datetime' column to datetime format for easier manipulation
filtered_data['datetime'] = pd.to_datetime(ohlc_data_cleaned['datetime']).copy()

# Grouping the data by 'day' and 'section'
grouped = filtered_data.groupby(['day', 'section'])

# Finding the maximum value of 'high' and minimum value of 'low' for each group
max_high = grouped['high'].max()
min_low = grouped['low'].min()

# Getting the datetime for the maximum high value and minimum low value
max_high_time = grouped.apply(lambda x: x[x['high'] == x['high'].max()]['datetime'].iloc[0])
min_low_time = grouped.apply(lambda x: x[x['low'] == x['low'].min()]['datetime'].iloc[0])

# Calculating the difference between the maximum high and minimum low
difference = max_high - min_low

# Creating a new DataFrame with the required data
result = pd.DataFrame({
    'Max High': max_high,
    'Max High Time': max_high_time.dt.strftime('%Y-%m-%d %H:%M'),
    'Min Low': min_low,
    'Min Low Time': min_low_time.dt.strftime('%Y-%m-%d %H:%M'),
    'Difference': difference
})

# Resetting index to make 'day' and 'section' columns
result = result.reset_index()


# Pivoting the 'section' column to create a new structure
pivot_result = result.pivot(index='day', columns='section', values='Difference')

# Resetting index to make 'day' a column again
pivot_result = pivot_result.reset_index()

pivot_result_naDrop = pivot_result.dropna()
# Save the pivot result to a new CSV file

pivot_result_naDrop = pivot_result_naDrop.copy()
pivot_result_naDrop['Largest_Time_Slot'] = pivot_result_naDrop.apply(largest_time_slot, axis=1)

pivot_result_naDrop.to_csv('231115_VolatiliyAnalysisRange.csv', index=False)

result_counts = pivot_result_naDrop['Largest_Time_Slot'].value_counts()
# Print the results
print("Number of days when LtoC time is the largest:", result_counts['LtoC time'])
print("Number of days when 9am-12:15pm is the largest:", result_counts['9am-12:15pm'])
print("Number of days when 12:15pm-15:30pm is the largest:", result_counts['12:15pm-15:30pm'])
