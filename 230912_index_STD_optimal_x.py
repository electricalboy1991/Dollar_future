import pandas as pd
from sklearn.metrics import mean_squared_error
from math import sqrt
import matplotlib.pyplot as plt

# Load the Excel data into a DataFrame
data = pd.read_excel('optimal_std_cross_validation.xlsx')
data['index_std'] = 0.0  # Create a new column 'index_std' to store the calculated values
shift_days = 0

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

rangeMin =200
rangeMax = 300
rangeGap = 10
# Loop through different values of x//x는 average 내는 기간
for x in range(rangeMin,rangeMax,rangeGap):
    k=0
    for i in range(x, len(data)):
        data.loc[x + k, 'index_std'] = data.loc[i, 'dollar index'] / (data.loc[i - x:i - 1, 'dollar index'].mean() / data.loc[i - x:i - 1, 'won PV'].mean())

        k=k+1
    forIndex +=1
    # data['index_std'] = data.apply(lambda row: data.loc[row.name - x:row.name]['dollar index'].mean() /
    #                                    data.loc[row.name - x:row.name]['won PV'].mean(), axis=1)

    #예측력 평가를 위해 shift_days만큼 shift
    data['index_std_shift'] = data['index_std'].shift(shift_days)
    data['index_std_shift'] = data['index_std_shift'].fillna(0)
    rmse = calculate_rmse(data.loc[data['index_std_shift'] != 0]['won PV'], data.loc[data['index_std_shift'] != 0]['index_std_shift'])
    print(x,rmse)

    rmse_values.append(rmse)
    x_values.append(x)

    if forIndex != int((rangeMax-rangeMin)/rangeGap):
        data['index_std'] = 0.0

    if rmse < best_rmse:
        best_rmse = rmse
        best_x = x

    # Initialize a variable to count the number of crossings
    crossings = 0

    # Loop through the data to count crossings
    for i in range(1, len(data)):
        if (data.loc[i, 'index_std_shift'] > data.loc[i - 1, 'index_std_shift'] and
            data.loc[i, 'won PV'] < data.loc[i - 1, 'won PV']) or \
                (data.loc[i, 'index_std_shift'] < data.loc[i - 1, 'index_std_shift'] and
                 data.loc[i, 'won PV'] > data.loc[i - 1, 'won PV']):
            crossings += 1

    print(f"Number of crossings between 'index_std_shift' and 'won PV': {crossings}")
    crossings_values.append(crossings)

# kk = 0
# for ii in range(best_x, len(data)):
#     data.loc[best_x + kk, 'index_std'] = data.loc[ii, 'dollar index'] / (data.loc[ii - best_x:ii - 1, 'dollar index'].mean() / data.loc[ii - best_x:ii - 1, 'won PV'].mean())
#     kk = kk + 1
#
# print(f"The optimal x value with the lowest RMSE is {best_x} (RMSE: {best_rmse})")

# Plotting the RMSE values
plt.figure(figsize=(10, 6))
plt.plot(x_values, rmse_values, marker='o', linestyle='-', color='r')
plt.title('Index RMSE vs. x Value')
plt.xlabel('x Value')
plt.ylabel('RMSE')
plt.grid(True)
plt.show()


# Plotting 'PV', 'index_std_shift', and 'index_std' values vs. Date
plt.figure(figsize=(10, 6))
plt.plot(data.index, data['won PV'], label='PV', linestyle='-', color='g')
plt.plot(data.index, data['index_std_shift'], label='index_std_shift', linestyle='-', color='b')
plt.plot(data.index, data['index_std'], label='index_std', linestyle='-', color='r')
plt.title('PV, index_std_shift, and index_std vs. Date')
plt.xlabel('Date')
plt.ylabel('Values')
plt.grid(True)
plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
plt.legend()
plt.show()