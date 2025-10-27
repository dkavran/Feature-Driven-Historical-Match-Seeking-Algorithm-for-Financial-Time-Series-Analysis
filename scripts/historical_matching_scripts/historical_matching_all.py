# Batch launcher for historical day-matching across all tickers found in ../first_order_features_data/.
# Spawns a thread per ticker; each thread starts a separate Python subprocess that runs:
#   ./historical_matching_scripts/historical_matching_individual_ticker.py
#
# Command-line args (in order):
#   1) K_neighbors                      -> int as string (e.g., "10"); passed through to child script
#   2) individual_feature_diff_threshold-> "None"/"null" or float as string; per-second feature % threshold (e.g., "0.1" for 0.1%)
#   3) history_span_start_year          -> "None"/"null" or int year as string (e.g., "2014")
#   4) target_date                      -> "None"/"null" or "YYYY-MM-DD"
#   5) distance_metric             -> one of ["eucledian", "minkowski", "chebyshev"]
#   6) distance_metric_power       -> float as string; Minkowski p (ignored by other metrics)

import os
import pandas as pd
import sys
import multiprocessing
sys.path.append("../")

import subprocess
from threading import Semaphore, Thread

def run_process(ticker, K_neighbors, individual_feature_diff_threshold, history_span_start_year, target_date, distance_metric, distance_metric_power, semaphore):
	with semaphore:
		# Launch the per-ticker matching subprocess.
		subprocess.run(['python', './historical_matching_scripts/historical_matching_individual_ticker.py', ticker, K_neighbors, individual_feature_diff_threshold, history_span_start_year, target_date, distance_metric, distance_metric_power])

if __name__ == "__main__":
	if len(sys.argv) != 7:
		raise Exception("No number of K neighbors, individual feature diff threshold, history span, starting year, distance metric or distance metric power provided in the arguments!")
	else:
		print("--- INPUT PARAMS ---")
		# Display all input parameters with indexes
		for idx, arg in enumerate(sys.argv):
			print(f"{idx}: {arg}")
		print("--------------------")

	folder_path = "../first_order_features_data/"
	K_neighbors = sys.argv[1]
	individual_feature_diff_threshold = sys.argv[2] # "None"/"null" or a non-negative float (string form), e.g., "0.1".
	history_span_start_year = sys.argv[3]
	target_date = sys.argv[4]
	distance_metric = sys.argv[5]
	distance_metric_power = sys.argv[6]

	files = os.listdir(folder_path)
	tickers = [file.rsplit(".", 1)[0] for file in files]
	
	# Create a semaphore to limit the number of subprocesses
	num_cores = multiprocessing.cpu_count()
	max_concurrent_processes = max(2, num_cores - 4) # If (num_cores - 4) [4 reserved for the system] is below 2, then let's use two threads (e.g. in case of strange CPU or OS)
	semaphore = Semaphore(max_concurrent_processes)
	threads = []

	for i, ticker in enumerate(tickers):
		if (i+1) % 25 == 0:
			print("Creating thread to historically match tick days for company #", (i+1), "/", len(tickers), "")

		thread = Thread(target=run_process, args=(ticker, K_neighbors, individual_feature_diff_threshold, history_span_start_year, target_date, distance_metric, distance_metric_power, semaphore))
		thread.start()
		threads.append(thread)

	# Wait for all threads/subprocesses to finish before exiting.
	print("---------------------------------------------------------")
	print("Do not close the shell while this script is not finished!")
	print("---------------------------------------------------------")
	for i, thread in enumerate(threads):
		thread.join()
		if (i+1) % 25 == 0:
			print("--------------------------------------------------------------------")
			print("Finished historical matching for company #", (i+1), "/", len(tickers), "")
			print("--------------------------------------------------------------------")
	print("---------------------------------------------------------")    
	print("All processes for historical matching have completed!")