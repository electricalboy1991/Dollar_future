import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata

# Specify the file path (the actual path to the Excel file must be entered here)
file_path = 'C:/Users/world/PycharmProjects/Dollar_future/231002_simulation_result_0.002,0.006,0.0005_0.002,0.007,0.0005_3,8,1_wholeday.xlsx'

# Load data from Excel file
data = pd.read_excel(file_path)

# Set the profit type here
profit_type = 'long_profits'  # Change this to 'short_profits' or 'long_profits' or 'total_profit' as needed

# Group the data according to a and b and calculate the average of the specified profit type
grouped_data = data.groupby(['a', 'b'])[profit_type].mean().reset_index()

# Convert data to grid
x = grouped_data['a']
y = grouped_data['b']
z = grouped_data[profit_type]
x_grid, y_grid = np.meshgrid(x.unique(), y.unique())

# Interpolate z values ​​over the grid
z_grid = griddata((x, y), z, (x_grid, y_grid), method='cubic')

# Draw a 2D contour plot
fig, ax = plt.subplots(figsize=(10, 7))
contour = ax.contourf(x_grid, y_grid, z_grid, cmap='viridis', levels=20)
plt.colorbar(contour, ax=ax, label=profit_type)

# Set the label and title
ax.set_xlabel('a')
ax.set_ylabel('b')
ax.set_title(f'2D Contour plot of {profit_type} by a and b')

# show the plot
plt.show()
