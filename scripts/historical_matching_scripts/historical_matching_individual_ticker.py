# KNN-based search for historical "most similar" days using second-order features.
# Expects a precomputed first-order-features CSV per ticker under ../first_order_features_data/.
# Command-line args (in order):
#   1) ticker: str
#   2) K_neighbors: int  -> how many most similar matching days to return
#   3) individual_feature_diff_threshold: "None"/"null" or float (percentage, e.g., 0.1 for 0.1%)
#   4) history_span_start_year: "None"/"null" or int (e.g., 2010) to limit the historical window
#   5) target_date: "None"/"null" or YYYY-MM-DD; if None, uses the last date in the data
#   6) distance_metric: one of ["eucledian", "minkowski", "chebyshev"]
#   7) distance_metric_power: float; only used for "minkowski" (the p parameter)
#
# Outputs a CSV of matched days (date-ascending) into ./results/<target_date>/<ticker>.csv

import traceback
import pandas as pd
import sys
import numpy as np
import os
from sklearn.neighbors import NearestNeighbors

sys.path.append("./")
from utils_knn import (
    custom_knn_metric,
)

from utils_features import (
    calculate_second_order_features
)

match_not_appropriate_distance = 999999

def save_df_to_disk(df: pd.DataFrame, folder_path: str, file_name: str, separator=";", date_format: str = None):
	save_file_path = os.path.join(folder_path, file_name + ".csv")

	if not os.path.exists(folder_path):
		os.makedirs(folder_path)

	df.to_csv(save_file_path, sep=separator, encoding='utf-8', date_format=date_format)
	print("Results for", file_name, "saved into:", save_file_path)

if __name__ == "__main__":
    if len(sys.argv) != 8:
        raise Exception(
            "No ticker symbol, number of K neighbors, individual diff feature threshold, starting year, target date, distance metric or distance metric power provided in the arguments!"
        )

    ticker = sys.argv[1]
    K_neighbors = int(sys.argv[2]) # K number of nearest/most similar neighbors (i.e. matching days) to retrieve
    individual_feature_diff_threshold = sys.argv[3] # Per-second order feature percentage (%) threshold in the custom KNN distance metric function; "None"/"null" or float >= 0.0.

    # Normalize the threshold argument: default to 0.1% if unspecified.
    if (
        individual_feature_diff_threshold == "null"
        or individual_feature_diff_threshold == "None"
    ):  # Set the default threshold
        individual_feature_diff_threshold = 0.1 # Default: 0.1%
        print(
            "Using default individual feature diff threshold of:",
            individual_feature_diff_threshold,
            "%",
        )
    else:
        individual_feature_diff_threshold = float(
            individual_feature_diff_threshold
        )

    history_span_start_year = sys.argv[4]  # Starting year for searching the matching days; "None"/"null" or an int year (>= 1970 recommended).
    if history_span_start_year == "null" or history_span_start_year == "None":
        history_span_start_year = None
    else:
        history_span_start_year = int(history_span_start_year)
        
    target_date = sys.argv[5] # Target day to match against; "None"/"null" or YYYY-MM-DD.
    distance_metric = sys.argv[6] # One of ["eucledian", "minkowski", "chebyshev"] (string must match exactly).
    distance_metric_power = sys.argv[7] # p for Minkowski; ignored for other metrics.

    available_distance_metrics = ["euclidean", "minkowski", "chebyshev"]

    folder_path = "../first_order_features_data/"

    try:
        if distance_metric not in ["euclidean", "minkowski", "chebyshev"]:
            raise Exception("Incorrect distance metric - available only:", ''.join(available_distance_metrics))
        
        distance_metric_power = float(distance_metric_power)

        # START: Load first order features
        path = os.path.join(folder_path, ticker + ".csv")

        df = pd.read_csv(
            path,
            delimiter=";",
            index_col=0,
            parse_dates=["date"],
            date_format="%Y-%m-%d",
        )

        # Optionally limit history by start year.
        if history_span_start_year is not None:
            df["year"] = df["date"].dt.year
            df = df[df["year"] >= history_span_start_year]
            df = df.drop(columns="year")

        # If target_date is unspecified, use the last available date in the file.
        if target_date == "null" or target_date == "None":
            target_date = pd.to_datetime(str(df.tail(1)["date"].values[0])).strftime("%Y-%m-%d")
        
        save_folder_path = "./results/" + target_date
        # END

        # START: Calculate second order features
        df_matrix = calculate_second_order_features(df)
        # END

        # START: Remove dates after the target date
        if target_date != "null" and target_date != "None":
            df_matrix = df_matrix[df_matrix["date"] <= pd.Timestamp(target_date)]
        
        last_date = df_matrix.tail(1)["date"].values[0]  # SAFETY CHECK: last day in df should not be equal to the target_date
        if pd.Timestamp(last_date) != pd.Timestamp(target_date):
            raise Exception("ERROR: Last date should be:", target_date, "instead it is:", last_date)
        # END

        # START: K-nearest neighbors (KNN) search
        # Extract all days, except the target_date, which is last
        day_ticks_points = df_matrix.loc[:, df_matrix.columns != "date"].values[:-1]
        
        # Extract last/target day
        target_day_tick_point = df_matrix.loc[:, df_matrix.columns != "date"].values[-1]

        # Object with parameters for the custom KNN distance function:
        # - "match_not_appropriate_distance" is the distance interpreted as "no match".
        # - "threshold" is the per-second order feature percentage tolerance inside the metric.
        # - "distance_metric" selects the distance formula.
        # - "distance_metric_power" is the Minkowski p (ignored otherwise).
        metric_params = {
            "match_not_appropriate_distance": match_not_appropriate_distance,
            "threshold": individual_feature_diff_threshold,
            "distance_metric": distance_metric,
            "distance_metric_power": distance_metric_power
        }

        # Store all days, except the last/target day, inside the KNN object
        nbrs = NearestNeighbors(
            n_neighbors=K_neighbors,
            metric=custom_knn_metric,
            metric_params=metric_params
        ).fit(day_ticks_points)

        # Use KNN to find K closest matched days
        # 1. Query K-nearest days to the last/target day

        distances, indices = nbrs.kneighbors( # Returns distances and indices of K closest days to the last/target day
            target_day_tick_point.reshape((1, -1))
        )

        # 2. Filter out any days that the KNN distance metric flagged as "no match"
        # by comparing their distance to match_not_appropriate_distance threshold.
        close_points = indices[0, :]
        close_points_distances = distances[0, :]
        if match_not_appropriate_distance is not None:
            close_points = close_points[
                close_points_distances < match_not_appropriate_distance
            ]
            close_points_distances = close_points_distances[
                close_points_distances < match_not_appropriate_distance
            ]

        df_close_points = df_matrix.iloc[close_points].copy()
        df_close_points["distance"] = close_points_distances

        # 3. Sort matched closest days by date
        df_close_points.sort_values(by="date", ascending=True, inplace=True) #sortiraj izhodni dataframe po datumih
        df_close_points.reset_index(inplace=True)

        # 4. Keep all columns except 'index'
        del df_close_points['index']

        if df_close_points.shape[0] == 0:
            print(
                "For ticker:",
                ticker,
                "there was no found matches in history! Results for this ticker are skipped and not saved..."
            )
        else:
            # Save to file
            save_df_to_disk(df_close_points, save_folder_path, ticker)
    except Exception as e:
        print("An error occurred:")
        traceback.print_exc()
