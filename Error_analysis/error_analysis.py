import numpy as np
import pandas as pd
import glob

DISCARD_OUTLIERS = True
OUTLIERS_THRESHOLD = 1000


file_paths = glob.glob('Datasets/**/*.csv', recursive=True)
dfs = [
    pd.read_csv(f,
                parse_dates=["timestamp"])  # ← parse_dates!
    for f in file_paths
]

big_df = pd.concat(dfs, ignore_index=True)
data = big_df.to_numpy()

errors = data[:, 1] - data[:, 3]
if DISCARD_OUTLIERS:
    mask = np.abs(errors) < OUTLIERS_THRESHOLD
    errors = errors[mask]

abs_err = np.abs(errors)


# General metrics
print("General metrics:")
print("Number of samples:", errors.shape[0])
print(f"Mean: {errors.mean():.1f}  Absolute error mean: {abs_err.mean():.1f}")
print(f"Variance: {errors.var():.1f}  Standard deviation: {np.sqrt(errors.var()):.1f}")
print("Min error:", errors.min(), "Max error:", errors.max())
print("Min absolute error:", abs_err.min(), "Max absolute error:", abs_err.max())
print()

# Per distance metrics
for dist in (940, 1125, 1180, 1220, 1550, 1595):
    print(dist, ":")
    dist_data = data[data[:, 3] == dist]

    dist_errors = dist_data[:, 1] - dist_data[:, 3]
    if DISCARD_OUTLIERS:
        mask = np.abs(dist_errors) < OUTLIERS_THRESHOLD
        dist_errors = dist_errors[mask]

    abs_dist_err = np.abs(dist_errors)

    print("Number of samples:", dist_errors.shape[0])
    print(f"Mean: {dist_errors.mean():.1f}  Absolute error mean: {abs_dist_err.mean():.1f}")
    print(f"Variance: {dist_errors.var():.1f}  Standard deviation: {np.sqrt(dist_errors.var()):.1f}")
    print("Min error:", dist_errors.min(), "Max error:", dist_errors.max())
    print("Min absolute error:", abs_dist_err.min(), "Max absolute error:", abs_dist_err.max())
    print()
