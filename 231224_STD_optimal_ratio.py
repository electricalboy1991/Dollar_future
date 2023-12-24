import pandas as pd
from sklearn.metrics import mean_squared_error
from math import sqrt
import matplotlib.pyplot as plt

# Load the Excel data into a DataFrame
data = pd.read_excel('optimal_std_cross_validation.xlsx')
data['index_std'] = 0.0  # Create a new column 'index_std' to store the calculated values
shift_days_index = 0
shift_days_reer = 10

# 2행부터 760행까지 삭제// 2000년 이후를 보기 위함임
data = data.drop(index=range(0, 759))
data['new_index'] = range(0, len(data))
data = data.set_index('new_index')

# Define a function to calculate RMSE
def calculate_rmse(y_true, y_pred):
    return sqrt(mean_squared_error(y_true, y_pred))

# Initialize variables to store the best RMSE and corresponding x
best_rmse = float('inf')
best_x = None

rmse_values = []  # List to store RMSE values for plotting
crossings_values = []
x_values = []

forIndex = 0
x = 260
k=0

for i in range(x, len(data)):
    data.loc[x + k, 'index_std'] = data.loc[i, 'dollar index'] / (data.loc[i - x:i - 1, 'dollar index'].mean() / data.loc[i - x:i - 1, 'won PV'].mean())

    k=k+1

k=0
for i in range(x, len(data)):
    data.loc[x + k, 'reer_std'] = (data.loc[i - x:i - 1, 'won BIS 64'].mean() * data.loc[i - x:i - 1, 'won PV'].mean())/data.loc[i, 'won BIS 64']

    k=k+1
# data['reer_std'] = data.apply(lambda row: data.loc[row.name - x:row.name]['won BIS 64'].mean() /
#                                    data.loc[row.name - x:row.name]['won PV'].mean(), axis=1)
data['reer_std_shift'] = data['reer_std'].shift(shift_days_reer)
data['reer_std_shift'] = data['reer_std_shift'].fillna(0)

#예측력 평가를 위해 shift_days만큼 shift
data['index_std_shift'] = data['index_std'].shift(shift_days_index)
data['index_std_shift'] = data['index_std_shift'].fillna(0)
# rmse = calculate_rmse(data.loc[data['index_std_shift'] != 0]['won PV'], data.loc[data['index_std_shift'] != 0]['index_std_shift'])

# Initialize variables for tracking the best RMSE and the corresponding n
best_rmse = float('inf')
best_n = None

# Iterate over n from 0.1 to 0.9
for n in [i * 0.1 for i in range(1, 10)]:
    # Create a new column based on the current n
    data['combined'] = n * data['index_std_shift'] + (1 - n) * data['reer_std_shift']

    # Calculate RMSE
    current_rmse = calculate_rmse(data['won PV'], data['combined'])

    # Update the best RMSE and n if the current RMSE is lower
    if current_rmse < best_rmse:
        best_rmse = current_rmse
        best_n = n

# Print the best n and its corresponding RMSE
print(f"Best n: {best_n}, with RMSE: {best_rmse}")


# # Plotting the RMSE values
# plt.figure(figsize=(10, 6))
# plt.plot(x_values, rmse_values, marker='o', linestyle='-', color='r')
# plt.title('Index RMSE vs. x Value')
# plt.xlabel('x Value')
# plt.ylabel('RMSE')
# plt.grid(True)
# plt.show()
#
#
# # Plotting 'PV', 'index_std_shift', and 'index_std' values vs. Date
# plt.figure(figsize=(10, 6))
# plt.plot(data.index, data['won PV'], label='PV', linestyle='-', color='g')
# plt.plot(data.index, data['index_std_shift'], label='index_std_shift', linestyle='-', color='b')
# plt.plot(data.index, data['index_std'], label='index_std', linestyle='-', color='r')
# plt.title('PV, index_std_shift, and index_std vs. Date')
# plt.xlabel('Date')
# plt.ylabel('Values')
# plt.grid(True)
# plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
# plt.legend()
# plt.show()