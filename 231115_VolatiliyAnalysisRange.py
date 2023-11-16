import pandas as pd
from datetime import datetime, timedelta

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

# Load the data
data = pd.read_csv('231115_DataFilterForVolatiliyAnalysis_timeSplit.csv')

# Convert the 'datetime' column to datetime objects with the correct format
data['datetime'] = pd.to_datetime(data['datetime'], format='%Y-%m-%d %H:%M:%S')

# Apply the function to categorize each row
data['section'] = data['datetime'].apply(categorize_time)

# Filter out the data that does not fall into the defined time sections
filtered_data = data[data['section'] != 'other']

# Apply the function to each row in the DataFrame
filtered_data.loc[:, 'day'] = filtered_data.apply(determine_day, axis=1)

# Convert the 'datetime' column to datetime format for easier manipulation
filtered_data['datetime'] = pd.to_datetime(data['datetime']).copy()

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