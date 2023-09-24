import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load data from the Excel file
file_name = '230925_simulation_result_0.003,0.008,0.001_3,35,1_wholeday'

df = pd.read_excel(file_name+'.xlsx')
# df = pd.read_csv('230906_simulation_result_0.001, 0.009, 0.001_2, 20, 0.1.csv')

# Extract data from columns
x_data = df['a']
y_data = df['n']
z_data = df['short_profits']
# z_data = df['long_profits']

parts = file_name.split(',')
# 2번째 쉼표 뒤의 값을 가져옵니다.
value1_str = parts[2]
# 4번째 쉼표 뒤의 값을 가져옵니다.
value2_str = parts[4]

# '_'를 기준으로 문자열을 분할하여 원하는 값을 추출합니다.
value1 = float(value1_str.split('_')[0])
value2 = float(value2_str.split('_')[0])
average_distance = 0

# Define the size of the averaging window
window_size_x = 1+value1 # 1 + 단위 이동 거리
window_size_y = 1+value2 # 1 + 단위 이동 거리
window_scale = average_distance # 1 + 단위 이동 거리

# Initialize an empty DataFrame for the averaged data
averaged_df = pd.DataFrame()

# Check if z_data is 'short_profits' or 'long_profits'
if z_data.name == 'short_profits':
    target_column = 'short_profits'
elif z_data.name == 'long_profits':
    target_column = 'long_profits'
else:
    raise ValueError("z_data should be either 'short_profits' or 'long_profits'")

# Iterate through the coordinates
for i in range(len(x_data)):
    x = x_data[i]
    y = y_data[i]

    # Define the bounds of the 3x3 area
    x_min = x - window_scale*(window_size_x - 1) / 2
    x_max = x + window_scale*(window_size_x - 1) / 2
    y_min = y - window_scale*(window_size_y - 1) / 2
    y_max = y + window_scale*(window_size_y - 1) / 2

    # Select data within the 3x3 area
    selected_data = df[(df['a'] >= x_min) & (df['a'] <= x_max) & (df['n'] >= y_min) & (df['n'] <= y_max)]

    # Calculate the average of the target_column in the selected area
    averaged_value = selected_data[target_column].mean()

    # Append the averaged value to the new DataFrame
    averaged_df = averaged_df.append({'a': x, 'n': y, target_column: averaged_value}, ignore_index=True)

# Create a 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Create the surface plot directly with x, y, and averaged z data
surf = ax.plot_trisurf(averaged_df['a'], averaged_df['n'], averaged_df[target_column], cmap='viridis')

# Set labels for each axis
ax.set_xlabel('Position liquidation percent')
ax.set_ylabel('Position grid')
ax.set_zlabel(f'Averaged {target_column}')
ax.set_title(f'Averaged {target_column} Simulation')

# Define the output Excel file path
output_excel_file = file_name+'_averaged.xlsx'

# Export the averaged_df DataFrame to an Excel file
averaged_df.to_excel(output_excel_file, index=False)

print(f"Data has been exported to {output_excel_file}")

# Show the plot
plt.show()
