import pandas as pd
import matplotlib.pyplot as plt
import mplcursors
import numpy as np
from matplotlib import cm

# Load the data
file_path = '230929_simulation_result_0.002,0.008,0.001_0.002,0.01,0.001_3,10,1_wholeday.xlsx'  # Replace with your file path
data = pd.read_excel(file_path)

# Get the unique values of a and b from the data
unique_a_values = data['a'].unique()
unique_b_values = data['b'].unique()


def plot_individual_profit_mpl(profit_type):
    fig, ax = plt.subplots(figsize=(10, 6))

    # Create a color map to have different colors for different combinations of a and b
    color_map = cm.get_cmap('tab10', len(unique_a_values) * len(unique_b_values))
    color_idx = 0  # Reset color index for each profit type

    # Iterate through all combinations of a and b
    for a_value in unique_a_values:
        for b_value in unique_b_values:
            # Filter the data for the current combination of a and b
            filtered_data = data[(data['a'] == a_value) & (data['b'] == b_value)]
            # Plot the profits with different colors
            line = ax.plot(filtered_data['n'], filtered_data[profit_type],
                           label=f'a={a_value}, b={b_value}',
                           color=color_map(color_idx))
            color_idx += 1  # Increment color index for the next combination

    # Set the title and labels
    ax.set_title(f'Graph of {profit_type} against n for all combinations of a and b')
    ax.set_xlabel('n')
    ax.set_ylabel(profit_type)
    ax.grid(True)

    # Enable cursor interactivity
    mplcursors.cursor(hover=True)


# Call the function to plot the individual graphs with mpl
for profit_type in ['short_profits', 'long_profits', 'total_profits']:
    plot_individual_profit_mpl(profit_type)

plt.show()  # Move plt.show() outside the function
