import pandas as pd

# Create a DataFrame
data = {
    'A': [1, 2, 3],
    'B': [4, 5, 6]
}
df = pd.DataFrame(data)

# Set the index and give it a name
df.index = pd.Index(['X', 'Y', 'Z'], name='Index_Name')

# Print the DataFrame
print(df)