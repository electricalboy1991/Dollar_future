import pandas as pd
import matplotlib.pyplot as plt

comparisonRate = 0.25

file_path = '231121_WonDollarIndexGapData.xlsx'  # Replace with your file path
data = pd.read_excel(file_path)
cleaned_data = data.dropna().copy()

# Step 2: Create a column for the next day's 원 PV
cleaned_data['원 PV_next_day'] = cleaned_data['원 PV'].shift(-1)
cleaned_data['원 PV_2dayslater'] = cleaned_data['원 PV'].shift(-2)

# Condition 1: 원 PV increases and 달러 인덱스 decreases on the same day
condition_1 = (cleaned_data['원 PV'] > cleaned_data['원 PV'].shift(1)) & (cleaned_data['달러 인덱스'] < cleaned_data['달러 인덱스'].shift(1))
# Probability for 원 PV to decrease the next day under condition 1
prob_1 = (cleaned_data[condition_1]['원 PV_next_day'] < cleaned_data[condition_1]['원 PV']).mean()

# Calculate the increase rate of '원 PV'
cleaned_data['원 PV_rate_of_change'] = 100*cleaned_data['원 PV'].pct_change()
cleaned_data['달러 인덱스_rate_of_change'] = 100*cleaned_data['달러 인덱스'].pct_change()

cleaned_data['rate_product_1'] = 100*cleaned_data[condition_1]['원 PV_rate_of_change'] * cleaned_data[condition_1]['달러 인덱스_rate_of_change']

# Step 1: Calculate absolute values of 'rate_product_1'
cleaned_data['abs_rate_product_1'] = cleaned_data['rate_product_1'].abs()

# Step 2: Determine the threshold for the top 20%
threshold_1 = cleaned_data['abs_rate_product_1'].quantile(1-comparisonRate)

# Step 3: Filter the top 50%
top_50_percent_condition_1 = cleaned_data['abs_rate_product_1'] >= threshold_1
# Adding 'top_50_percent_condition_1' as a new column in 'cleaned_data'
cleaned_data['top_50_percent_condition_1'] = top_50_percent_condition_1
# Step 4: Calculate the probability of 'won PV' decreasing
# Assuming 'won PV' column has the value for the current day
prob_decrease = (cleaned_data[top_50_percent_condition_1]['원 PV'] > cleaned_data[top_50_percent_condition_1]['원 PV_next_day']).mean()
count_1 = (cleaned_data[top_50_percent_condition_1]['원 PV'] > cleaned_data[top_50_percent_condition_1]['원 PV_next_day']).value_counts()


# Condition 2: 원 PV decreases and 달러 인덱스 increases on the same day
condition_2 = (cleaned_data['원 PV'] < cleaned_data['원 PV'].shift(1)) & (cleaned_data['달러 인덱스'] > cleaned_data['달러 인덱스'].shift(1))
# Probability for 원 PV to increase the next day under condition 2
prob_2 = (cleaned_data[condition_2]['원 PV_next_day'] > cleaned_data[condition_2]['원 PV']).mean()

cleaned_data['rate_product_2'] = 100*cleaned_data[condition_2]['원 PV_rate_of_change'] * cleaned_data[condition_2]['달러 인덱스_rate_of_change']

# Step 1: Calculate absolute values of 'rate_product_1'
cleaned_data['abs_rate_product_2'] = cleaned_data['rate_product_2'].abs()

# Step 2: Determine the threshold for the top 20%
threshold_2 = cleaned_data['abs_rate_product_2'].quantile(1-comparisonRate)

# Step 3: Filter the top 50%
top_50_percent_condition_2 = cleaned_data['abs_rate_product_2'] >= threshold_2
# Adding 'top_50_percent_condition_1' as a new column in 'cleaned_data'
cleaned_data['top_50_percent_condition_2'] = top_50_percent_condition_2
# Step 4: Calculate the probability of 'won PV' decreasing
# Assuming 'won PV' column has the value for the current day
prob_increase = (cleaned_data[top_50_percent_condition_2]['원 PV'] < cleaned_data[top_50_percent_condition_2]['원 PV_next_day']).mean()
count_2= (cleaned_data[top_50_percent_condition_2]['원 PV'] < cleaned_data[top_50_percent_condition_2]['원 PV_next_day']).value_counts()

print(prob_decrease)
print(prob_increase)


# Plotting a histogram for 'rate_product' within a specific range
plt.figure(figsize=(10, 6))
plt.hist(cleaned_data['abs_rate_product_1'], bins=40, range=(0,100), color='blue', edgecolor='black')
plt.title('Histogram of Rate Product Values (0,100)')
plt.xlabel('Rate Product')
plt.ylabel('Frequency')
plt.grid(True)
plt.show()


print(prob_1,prob_2) # 0.5326370757180157 0.5431145431145431

# Condition 3: 원 PV increases and 달러 인덱스 decreases for two consecutive days
# condition_3 = (cleaned_data['원 PV'] > cleaned_data['원 PV'].shift(1)) & \
#                 (cleaned_data['원 PV'].shift(1)  > cleaned_data['원 PV'].shift(2)) & \
#               (cleaned_data['달러 인덱스'] < cleaned_data['달러 인덱스'].shift(1)) & \
#               (cleaned_data['달러 인덱스'].shift(1) < cleaned_data['달러 인덱스'].shift(2))
# # Probability for 원 PV to decrease the next day under condition 3
# prob_3 = (cleaned_data[condition_3]['원 PV_next_day'] < cleaned_data[condition_3]['원 PV']).mean()
#
# # Condition 4: 원 PV decreases and 달러 인덱스 increases for two consecutive days
# condition_4 = (cleaned_data['원 PV'] < cleaned_data['원 PV'].shift(1)) & \
#                 (cleaned_data['원 PV'].shift(1)  < cleaned_data['원 PV'].shift(2)) & \
#               (cleaned_data['달러 인덱스'] > cleaned_data['달러 인덱스'].shift(1)) & \
#               (cleaned_data['달러 인덱스'].shift(1) > cleaned_data['달러 인덱스'].shift(2))
# # Probability for 원 PV to increase the next day under condition 4
# prob_4 = (cleaned_data[condition_4]['원 PV_next_day'] > cleaned_data[condition_4]['원 PV']).mean()
