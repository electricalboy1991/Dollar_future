import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load data from the Excel file
df = pd.read_excel('230906_simulation_result_0.001, 0.009, 0.001_2, 20, 0.1.xlsx')
# df = pd.read_csv('230906_simulation_result_0.001, 0.009, 0.001_2, 20, 0.1.csv')

# Extract data from columns
x_data = df['a']
y_data = df['n']
z_data = df['short_profits']

# Define the size of the averaging window
window_size_x = 1.002
window_size_y = 1.2
window_scale = 2
# Initialize an empty DataFrame for the averaged data
averaged_df = pd.DataFrame()

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

    # Calculate the average of 'short_profits' in the selected area
    averaged_value = selected_data['short_profits'].mean()

    # Append the averaged value to the new DataFrame
    averaged_df = averaged_df.append({'a': x, 'n': y, 'short_profits': averaged_value}, ignore_index=True)

# Create a 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Create the surface plot directly with x, y, and averaged z data
surf = ax.plot_trisurf(averaged_df['a'], averaged_df['n'], averaged_df['short_profits'], cmap='viridis')

# Define the output Excel file path
output_excel_file = '230906_simulation_result_0.001, 0.009, 0.001_2, 20, 0.1_averaged.xlsx'

# Export the averaged_df DataFrame to an Excel file
averaged_df.to_excel(output_excel_file, index=False)

print(f"Data has been exported to {output_excel_file}")


# Set labels for each axis
ax.set_xlabel('Position liquidation percent')
ax.set_ylabel('Position grid')
ax.set_zlabel('Averaged short_profits')
ax.set_title('Averaged Profit Simulation')

# Show the plot
plt.show()
