import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata
import mplcursors

file_path = '231026_simulation_result_0.0025,0.007,0.0001_0.0025,0.007,0.0001_0.005,0.0055,0.0005_wholeday.xlsx'
data = pd.read_excel(file_path)

# file_path = '231027_simulation_result_0.005,0.012,0.001_0.005,0.012,0.001_0.005,0.0055,0.0005_wholeday.csv'
# data = pd.read_csv(file_path)

# Set the profit type here
profit_type = 'short_profits'  # Change this as needed

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
contour = ax.contourf(x_grid, y_grid, z_grid, cmap='viridis', levels=100)
plt.colorbar(contour, ax=ax, label=profit_type)

# Scatter the original data points on top of the contour plot
sc = ax.scatter(x, y, c=z, cmap='viridis', alpha=0)

# Set the label and title
ax.set_xlabel('a')
ax.set_ylabel('b')
ax.set_title(f'2D Contour plot of {profit_type} by a and b')

# Find the points of the top 30 maximum profits in the interpolated data
sorted_indices = np.argsort(z_grid, axis=None)[::-1]
top_30_indices = sorted_indices[:30]

# Different markers and colors for top 30 points
markers = ['*', 'o', 's', '^', 'D', 'p', 'X', 'v', '<', '>', 'H', '+', '1', '2', '3', '4', '|', '_', '8', 'x', '*', 'o', 's', '^', 'D', 'p', 'X', 'v', '<', '>']
colors = ['red', 'blue', 'green', 'purple', 'orange', 'pink', 'cyan', 'brown', 'yellow', 'black', 'lime', 'navy', 'maroon', 'teal', 'magenta', 'grey', 'olive', 'turquoise', 'indigo', 'gold', 'coral', 'tan', 'silver', 'chocolate', 'plum', 'peru', 'lavender', 'beige', 'azure', 'slategray']

for rank, (idx, marker, color) in enumerate(zip(top_30_indices, markers, colors), start=1):
    max_profit_idx = np.unravel_index(idx, z_grid.shape)
    max_profit_x = x_grid[max_profit_idx]
    max_profit_y = y_grid[max_profit_idx]
    ax.scatter(max_profit_x, max_profit_y, marker=marker, color=color, s=100, label=f'Rank {rank}')

# Enable interactive tooltips
cursor = mplcursors.cursor(sc, hover=True)

@cursor.connect("add")
def on_add(sel):
    if sel.target.index in top_30_indices:
        sel.annotation.set_text(f'a: {x.iloc[sel.target.index]}\nb: {y.iloc[sel.target.index]}\n{profit_type}: {z.iloc[sel.target.index]}')
    else:
        sel.annotation.set_text(f'a: {x.iloc[sel.target.index]}\nb: {y.iloc[sel.target.index]}\n{profit_type}: {z.iloc[sel.target.index]}')

ax.legend(loc='upper right')

# Show the plot
plt.show()
