import pandas as pd
import matplotlib.pyplot as plt

# Load data from the CSV file
df = pd.read_csv('230906_simulation_result_0.001, 0.009, 0.001_2, 20, 1.csv')
# df = pd.read_excel('230906_simulation_result_0.001, 0.009, 0.001_2, 20, 1.xlsx')

# Extract data from columns
x_data = df['a']
y_data = df['n']
z_data = df['short_profits']

# Create a 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Create the surface plot directly with x, y, and z data
surf = ax.plot_trisurf(x_data, y_data, z_data, cmap='viridis')

# Set labels for each axis
ax.set_xlabel('Position liquidation percent')
ax.set_ylabel('Position grid')
ax.set_zlabel('short_profits')
ax.set_title('Profit Simulation')

# Show the plot
plt.show()
