# Custom distance/metric helpers for KNN over second-order feature vectors.
# Logic:
# - Before computing a distance, we optionally enforce two gating conditions:
#   (1) Direction/sign alignment for every feature: np.all(np.sign(x) == np.sign(y))
#   (2) Absolute difference per second order feature <= threshold: np.all(np.abs(x - y) <= threshold)
# - If gating passes (or threshold is None), compute the requested distance.
# - If gating fails, return a large distance to indicate "no match".

import numpy as np
from scipy.spatial.distance import minkowski, euclidean, cityblock, chebyshev

def custom_distance(x, y, match_not_appropriate_distance, threshold, distance_metric, distance_metric_power): # x and y are two vectors of second order features of two different days
    # Gating: (1) Check if the sign/direction/momentum is the same between x and y for each second order feature (e.g. combination of EWMAs ratios) with "np.all(np.sign(x) == np.sign(y))"
    # and (2) that the element-wise absolute differences between second order features are within the threshold with "np.all(np.abs(x - y) <= threshold)"
    if threshold is None or (np.all(np.sign(x) == np.sign(y)) and np.all(np.abs(x - y) <= threshold)):        
        # Euclidean distance
        if distance_metric == "euclidean":
            return np.linalg.norm(x - y)
        
        # Minkowski distance
        # Reference: https://en.wikipedia.org/wiki/Minkowski_distance
        # power = 1  -> Manhattan distance
        # power = 2  -> Euclidean distance
        # power -> ∞ -> Chebyshev distance
        elif distance_metric == "minkowski":
            return minkowski(x, y, p = distance_metric_power) # Larger power 'p' (e.g., using power = 4 or higher) emphasizes the largest coordinate-wise deviations.

        # Chebyshev distance
        elif distance_metric == "chebyshev":
            return chebyshev(x, y)
        
    else:
        # Gating failed: return the "no match" distance (very large value).
        return match_not_appropriate_distance

# Wrapper function to pass additional parameters with **kwargs to the distance function 
def custom_knn_metric(x, y, **kwargs):
    match_not_appropriate_distance = kwargs.get('match_not_appropriate_distance', 999999) # Very large value for symbolizing not appropriate match
    threshold = kwargs.get('threshold', 0.1)  # Default per-second order feature threshold if set to 0.1 (== 0.1%)
    distance_metric = kwargs.get('distance_metric', 'euclidean')
    distance_metric_power = kwargs.get('distance_metric_power', 3)
    return custom_distance(x, y, match_not_appropriate_distance, threshold, distance_metric, distance_metric_power)