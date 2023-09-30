import os
import matplotlib.pyplot as plt
import pandas as pd

# Global variable to keep track of the tooltip
tooltip = None


def display_tooltip(event):
    global tooltip
    if event.inaxes:
        x = round(event.xdata, 4)
        y = round(event.ydata, 4)
        # If the tooltip is None, create a new tooltip
        if tooltip is None:
            tooltip = plt.text(event.xdata, event.ydata, f'x: {x}\ny: {y}',
                               bbox=dict(boxstyle="round,pad=0.5", fc="yellow", alpha=0.75))
        # If the tooltip already exists, remove it
        else:
            tooltip.remove()
            tooltip = None
        plt.draw()  # Redraw the plot to show/hide the tooltip


def plot_graphs(variable):
    # List of file paths
    file_paths = [
        'C:/Users/world/PycharmProjects/Dollar_future/230923_simulation_result_0.001,0.010,0.0001_3,10,0.5_wholeday.xlsx',
        'C:/Users/world/PycharmProjects/Dollar_future/230924_simulation_result_0.001,0.01,0.0001_3,10,0.5_half.xlsx',
        'C:/Users/world/PycharmProjects/Dollar_future/230923_simulation_result_0.001,0.010,0.0001_3,10,0.5_daytime.xlsx'
    ]

    # Initialize an empty DataFrame to store the mean values for each file
    all_mean_values = pd.DataFrame()

    # Loop through each file path, read the data, calculate the mean values, and store the results
    for file_path in file_paths:
        # Load the data
        data = pd.read_excel(file_path)

        # Check if the variable exists in the data columns
        if variable not in data.columns:
            print(f"The variable '{variable}' is not found in the data.")
            return

        # Calculate the mean values
        mean_values = data.groupby('a').agg({variable: 'mean'}).reset_index()

        # Get the file name without extension for the legend
        file_name = os.path.splitext(os.path.basename(file_path))[0]

        # Store the mean values along with the file name (for the legend) in the DataFrame
        mean_values['file_name'] = file_name

        # Append the mean values of the current file to the DataFrame
        all_mean_values = all_mean_values.append(mean_values, ignore_index=True)

    # Create a new figure
    plt.figure(figsize=(10, 6))

    # Loop through each file name and plot the corresponding data
    for file_name in all_mean_values['file_name'].unique():
        # Filter the data for the current file name
        filtered_data = all_mean_values[all_mean_values['file_name'] == file_name]

        # Plot the data
        plt.plot(filtered_data['a'], filtered_data[variable], marker='o', label=file_name)

    # Add title, labels, legend, and grid
    plt.title(f'Mean {variable} vs a (Different Scenarios)')
    plt.xlabel('a')
    plt.ylabel(f'Mean {variable}')
    plt.legend(title='Scenario')
    plt.grid(True)

    # Connect the mouse button press event to your custom function
    plt.connect('button_press_event', display_tooltip)

    plt.show()


# Call the function with the desired variable
plot_graphs('short_profits')
plot_graphs('long_profits')
plot_graphs('total_profits')