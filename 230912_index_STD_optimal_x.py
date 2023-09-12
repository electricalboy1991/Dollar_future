import pandas as pd
from sklearn.metrics import mean_squared_error
from math import sqrt
import matplotlib.pyplot as plt

# Load the Excel data into a DataFrame
data = pd.read_excel('optimal_std_cross_validation.xlsx')
data['index_std'] = 0.0  # Create a new column 'index_std' to store the calculated values

# Define a function to calculate RMSE
def calculate_rmse(y_true, y_pred):
    return sqrt(mean_squared_error(y_true, y_pred))

# Initialize variables to store the best RMSE and corresponding x
best_rmse = float('inf')
best_x = None

rmse_values = []  # List to store RMSE values for plotting
x_values = []

# Loop through different values of x
for x in range(100, 600):
    k=0
    for i in range(x, len(data)):
        data.loc[x + k, 'index_std'] = data.loc[i, 'dollar index'] / (data.loc[i - x:i - 1, 'dollar index'].mean() / data.loc[i - x:i - 1, 'won PV'].mean())

        k=k+1
    # data['index_std'] = data.apply(lambda row: data.loc[row.name - x:row.name]['dollar index'].mean() /
    #                                    data.loc[row.name - x:row.name]['won PV'].mean(), axis=1)
    rmse = calculate_rmse(data.loc[data['index_std'] != 0]['won PV'], data.loc[data['index_std'] != 0]['index_std'])
    print(x,rmse)

    rmse_values.append(rmse)
    x_values.append(x)

    data['index_std'] = 0.0

    if rmse < best_rmse:
        best_rmse = rmse
        best_x = x

kk = 0
for ii in range(best_x, len(data)):
    data.loc[best_x + kk, 'index_std'] = data.loc[ii, 'dollar index'] / (data.loc[ii - best_x:ii - 1, 'dollar index'].mean() / data.loc[ii - best_x:ii - 1, 'won PV'].mean())
    kk = kk + 1

print(f"The optimal x value with the lowest RMSE is {best_x} (RMSE: {best_rmse})")

# Plotting the RMSE values
plt.figure(figsize=(10, 6))
plt.plot(x_values, rmse_values, marker='o', linestyle='-', color='b')
plt.title('Index RMSE vs. x Value')
plt.xlabel('x Value')
plt.ylabel('RMSE')
plt.grid(True)
plt.show()