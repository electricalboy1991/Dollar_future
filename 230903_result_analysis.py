import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# Load data from the CSV file
df = pd.read_csv('230905_simulation_result.csv')

# Extract data from columns
x_data = df['a']
y_data = df['n']
z_data = df['profit']

# Create a 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Create the surface plot directly with x, y, and z data
surf = ax.plot_trisurf(x_data, y_data, z_data, cmap='viridis')

# Set labels for each axis
ax.set_xlabel('Position liquidation percent')
ax.set_ylabel('Position grid')
ax.set_zlabel('Profit')
ax.set_title('Profit Simulation')

# Show the plot
plt.show()
