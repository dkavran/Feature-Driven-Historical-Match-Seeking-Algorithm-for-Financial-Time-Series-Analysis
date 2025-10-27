# Utilities for deriving "second-order" features from first-order daily features (e.g. EWMAs on Close price).
# Second-order features are percentage differences between all pairwise combinations
# of first-order features on the same date.

import numpy as np
import pandas as pd
from itertools import combinations

def calculate_percentage_difference(a, b):
    if a != 0 and b != 0:  # Avoid division by zero
        return ((a - b) / b) * 100 # Same as ((a / b) - 1) * 100
    return 0  # Handle the case where a or b is 0

def calculate_percentage_differences_for_all_combinations(arr):
    percentage_differences = []
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            percentage_differences.append(calculate_percentage_difference(arr[i], arr[j]))
    return percentage_differences

def calculate_second_order_features(df):
    # START: Create columns names for second order features
    column_names = df.columns[1:]

    column_name_combinations = [f"feature_{comb_index + 1}_matrix_{col1}_vs_{col2}" for comb_index, (col1, col2) in enumerate(combinations(column_names, 2))]

    df_matrix = pd.DataFrame(columns=["date"] + column_name_combinations) #dodaj datum v dataframe
    # END

    # START: Iterate over rows/daily ticks and calculate second order features
    row_counter = 0
    for i, row in df.iterrows():
        date = row["date"]

        data = np.array(row[1:].values, dtype=np.float32)

        if (
            np.sum(np.isnan(data)) > 0
        ):  # SAFETY CHECK: if any NaN values (that means some feature is not present; possible for e.g. the very first daily ticks without EWMAs for longer periods of time), skip this ror
            continue

        # Calculation of the second order features as percentage difference between all combinations of first order features (e.g. EWMAs)
        perc_diffs = calculate_percentage_differences_for_all_combinations(data)

        # Append the computed vector of second order features for this date.
        df_matrix.loc[row_counter] = [date] + perc_diffs
        row_counter += 1 
    # END   

    return df_matrix