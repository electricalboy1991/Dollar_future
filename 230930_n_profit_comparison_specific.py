import pandas as pd
import matplotlib.pyplot as plt
import mplcursors
import numpy as np
from matplotlib import cm

# Load the data
file_path = '230929_simulation_result_0.002,0.008,0.001_0.002,0.01,0.001_3,10,1_wholeday.xlsx'  # Replace with your file path
data = pd.read_excel(file_path)


def plot_individual_profit_mpl(profit_type, a_value, b_value):
    fig, ax = plt.subplots(figsize=(10, 6))

    # Filter the data for the current combination of a and b
    filtered_data = data[(data['a'] == a_value) & (data['b'] == b_value)]

    # Plot the profits with a specific color
    line = ax.plot(filtered_data['n'], filtered_data[profit_type],
                   label=f'a={a_value}, b={b_value}',
                   color='blue')

    # Set the title and labels
    ax.set_title(f'Graph of {profit_type} against n for a={a_value}, b={b_value}')
    ax.set_xlabel('n')
    ax.set_ylabel(profit_type)
    ax.grid(True)

    # Enable cursor interactivity
    mplcursors.cursor(hover=True)


# Specify the a and b values you are interested in
a_value = 0.004
b_value = 0.005

# Call the function to plot the individual graphs with mpl for the specified a and b values
for profit_type in ['short_profits', 'long_profits', 'total_profits']:
    plot_individual_profit_mpl(profit_type, a_value, b_value)

plt.show()  # Move plt.show() outside the function
