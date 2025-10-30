# Feature-Driven Historical Match-Seeking Algorithm for Financial Time-Series Analysis
A Python-based module for detecting historical matches in time series of financial market data.
---

The price-series match-seeking algorithm is designed to identify similar price patterns within historical financial time-series datasets. It operates on both raw price data and first-order derived features (e.g., technical analysis indicators).

The provided source code implements the historical pattern-matching module — one component within the complete processing pipeline.

This repository does not include:
- Data acquisition (example raw data is provided in the `/raw_data`),
- Features (e.g. technical indicators) computation (example first-order derived features - EWMAs are provided in the `/first_order_features_data`),
- Analysis and interpretation of the data (prediction).


### Practical Use:
This module locates technically similar points in past data based on the defined set of most recent time bar(s) and their calculated features, enabling pattern recognition and comparative analysis within historical market data.

### Algorithm inputs:
- Financial trading data time series in Yahoo Finance format (Open, High, Low, Close, Volume, Dividends and splits).
- Any number of additional features (e.g., moving averages, custom or complex indicators).
- A target date for which historical matches (i.e., similar dates) are identified.

### Algorithm output:
A list of time signatures in trading history that exhibit a technical state similar to the most recent date (or a user-specified target date).

## Algorithm demonstration

## Step 1: Feature Calculation

**First-order features** are calculated directly from raw trading time-series data.

Examples of first-order features include Exponential Weighted Moving Averages (EWMAs) of closing prices for SMA equivalents of 2-day, 3-day, and 5-day comparative spans, defined as recursive weighting parameter `α = 2/(N+1)`. 

**Second-order features are defined as percentage differences between all combinations of first-order features.**

These are calculated as `((Feature 1 / Feature 2) - 1) x 100`. The total number of second-order features follows the combination formula: `n! / (r! (n-r)!)`, where `n` = number of first-order features and `r` = 2.

These second-order features capture relationships among indicators (e.g., EWMAs) and collectively describe the market’s technical state for each day.

All second-order features must be computed for every record (day) in the historical dataset.

### Example: Calculation of first and second-order features for Apple Inc. ($AAPL) on daily quotes at 14.7.2014

Raw AAPL Close prices

| AAPL | Close price |
|---------------------------|--------------------------:|
|...|...|
|11.07.2014	|	21.0089016	|
|14.07.2014	|	21.28028297	|
|15.07.2014	|	21.03096962	|
|16.07.2014	|	20.91182518	|
|17.07.2014	|	20.53895187	|
|...|...|

Calculated first-order features (EWMAs of Close price)

| AAPL | Close | Close EWMA 2 days | Close EWMA 3 days | Close EWMA 5 days |
|---------------------------|--------------------------:|------------------------:|------------------------:|------------------------:|
| 17. 07. 2014  | 20.53895187                         | 20.68229982                       | 20.76878389                       | 20.85104402                       |

Calculated second-order features (% differences between all combinations of first-order features)

|                       | Last Close | 2 days (% difference) | 3 days (% difference) | 5 days (% difference) |
|-------------------------|-------------------------:|------------------------:|------------------------:|------------------------:|
| Last Close   |             /            |  -0.693098409%          | -1.106620859% | -1.49676837% |
| 2 days   |            /             |         /               | -0.416408619% | -0.809279084% |
| 3 days   |            /             |         /               |           /             | -0.394513272% |                 
| 5 days   |          /               |        /                |           /             |              /          | 

Results in the table above can be interpreted as:
- The closing price was -0.693098409% below the 2 day EWMA, -1.106620859% below the 3 day EWMA and -1.49676837% below the 5 day EWMA.
- 2 day EWMA was -0.416408619% below the 3 day EWMA and -0.809279084% below the 5 day EWMA.
- 3 day EWMA was -0.394513272% below the 5 day EWMA.

### Example: Calculation of second-order features as feature vectors for a set of three random dates and a target date

_(Note: The second-order features in the table above were flattened — i.e., raveled into a single feature vector.)_

| Date| Feature 1 | Feature 2 | Feature 3 | Feature 4 | Feature 5 | Feature 6 |
|---------------------------|:---:|--------------------------:|------------------------:|------------------------:|------------------------:|------------------------:|
| 17. 07. 2014   | -0.693098409 |	-1.106620859 |	-1.49676837 |	-0.416408619 |	-0.809279084 |	-0.394513272|
| 19. 06. 2018   | -0.591389462	| -0.976511557|	-1.490361523|	-0.387413218|	-0.904320087|	-0.518917246|
| 06. 04. 2022   |  -0.759950234|	-1.175065897|	-1.50598865|	-0.418294547|	-0.751751335|	-0.334857497|


Features of the target date - **07. 02. 2025**:

| Date| Feature 1 | Feature 2 | Feature 3 | Feature 4 | Feature 5 | Feature 6 |
|---------------------------|:---:|--------------------------:|------------------------:|------------------------:|------------------------:|------------------------:|
| 07. 02. 2025   | -0.77082082 | -1.13401273 | -1.51294041 | -0.36601324 | -0.74788439 | -0.383274

## Step 2: Historical matching

The matching process proceeds as follows:
1. First, certain preconditions must be satisfied. The process begins by calculating the differences between the features of the target date and those of all previous historical dates (denoted as Difference 1, Difference 2, etc.). If any absolute difference exceeds a predefined threshold, or if the sign of any second-order feature differs (positive vs. negative), the date is excluded as a potential match. Otherwise, it is considered a valid match.
2. For each valid match, calculate the selected distance metric between its feature vector and that of the target date.

The best (i.e. closest) K matches are used for further analysis.

### Example: Condition verification (Threshold = 0.15%)

| Date| All feature signs match those of target date | Difference 1 | Difference 2 | Difference 3 | Difference 4 | Difference 5 | Difference 6 | All differences < threshold | Valid match? | Note |
|---------------------------|:---:|--------------------------:|------------------------:|------------------------:|------------------------:|------------------------:|------------------------:|------------------------:|------------------------:|------------------------:|
| 17. 07. 2014   | &check; (all negative signs) | 0.077722411 | 0.027391871 | 0.01617204 | 0.050395379 | 0.061394694 | 0.011239272| &check; | &check; | |
| 19. 06. 2018   | &check; (all negative signs)  |  0.179431358 | 0.157501173 | 0.022578887 | 0.021399978 | 0.156435697 | 0.135643246  | &cross; | &cross; | Differences 1 and 5 are larger than threshold |
| 06. 04. 2022   | &check; (all negative signs)  | 0.010870586|	0.041053167|	0.00695176|	0.052281307|	0.003866945|	0.048416503| &check; | &check; | |


### Example: Distance calculation between second-order features of target date and historical matches (e.g. Minkowski distance metric)

| Date| Distances |
|---------------------------|------------------------:|
| 17. 07. 2014   | 0.083463245060768 |
| 06. 04. 2022  | 0.059935517152546 |

### Interpretation of the example output results

The results indicate that the technical state on 06.04.2022 more closely resembles that on 07.02.2025 (smaller distance) than the state on 17.07.2014.

## Running the Algorithm

Example raw data is provided in the `/raw_data` and first-order derived features in the `/first_order_features_data`.

Requirements:
- Anaconda environment
- Python

The algorithm can be executed from the `/scripts` as: `./run_historical_matching.bat`. If the required environment is missing, it will be created automatically.

Algorithm parameters (used in the `/scripts/run_historical_matching.bat`):
- **K_NEIGHBORS**: Number of most similar matching days to return. Higher values yield more historical matches.
- **INDIVIDUAL_FEATURE_DIFF_THRESHOLD**: Second-order feature percentage (%) tolerance used by the custom distance function.
- **HISTORY_SPAN_START_YEAR**: Starting year for the historical search window. If `None`, use full available history.
- **TARGET_DATE**: Target day to match against in the YYYY-MM-DD form. If `None`, the last available date in the dataset is used.
- **DISTANCE_METRIC**: Distance metric for KNN. Allowed: minkowski, chebyshev, and euclidean.
- **DISTANCE_METRIC_POWER**: Minkowski 'p' power (only used when DISTANCE_METRIC=minkowski). Ignored for other metrics. Larger p emphasizes the largest coordinate differences.