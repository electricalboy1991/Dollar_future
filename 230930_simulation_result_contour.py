import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata
import mplcursors

# Specify the file path (the actual path to the Excel file must be entered here)
file_path = 'C:/Users/world/PycharmProjects/Dollar_future/231002_simulation_result_0.0042,0.0054,0.0001_0.0045,0.0064,0.0001_3,8,1_wholeday.xlsx'

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

# Interpolate z values over the grid
z_grid = griddata((x, y), z, (x_grid, y_grid), method='cubic')

# Draw a 2D contour plot
fig, ax = plt.subplots(figsize=(10, 7))
contour = ax.contourf(x_grid, y_grid, z_grid, cmap='viridis', levels=100)  # Increased levels for finer color distinction
plt.colorbar(contour, ax=ax, label=profit_type)

# Scatter the original data points on top of the contour plot
sc = ax.scatter(x, y, c=z, cmap='viridis', alpha=0)

# Set the label and title
ax.set_xlabel('a')
ax.set_ylabel('b')
ax.set_title(f'2D Contour plot of {profit_type} by a and b')

# Find the point of maximum profit in the interpolated data
max_profit_idx = np.unravel_index(np.argmax(z_grid, axis=None), z_grid.shape)
max_profit_x = x_grid[max_profit_idx]
max_profit_y = y_grid[max_profit_idx]
max_profit_value = z_grid[max_profit_idx]

# Mark the point of maximum profit with an asterisk
ax.annotate('*', (max_profit_x, max_profit_y), color='red', fontsize=20, ha='center', va='center')

# Enable interactive tooltips
cursor = mplcursors.cursor(sc, hover=True)

@cursor.connect("add")
def on_add(sel):
    sel.annotation.set_text(f'a: {x.iloc[sel.target.index]}\nb: {y.iloc[sel.target.index]}\n{profit_type}: {z.iloc[sel.target.index]}')

# Show the plot
plt.show()
