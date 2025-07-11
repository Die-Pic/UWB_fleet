import numpy as np
import pandas as pd
import glob
import matplotlib.pyplot as plt

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


# Delete outliers
if DISCARD_OUTLIERS:
    errors = data[:, 1] - data[:, 3]
    mask = np.abs(errors) < OUTLIERS_THRESHOLD

    data = data[mask]
    big_df = big_df[mask].reset_index(drop=True)

# Calculate stuff
def correlation(x, y):
    return (
                ((x - x.mean()) * (y - y.mean())).sum() /
                (len(x)-1)
            ) / (x.std(ddof=1) * y.std(ddof=1))

errors = data[:, 1] - data[:, 3]
abs_err = np.abs(errors)
corr_err_fp = correlation(errors, data[:, 5])
corr_err_rx = correlation(errors, data[:, 6])
corr_err_powDiff = correlation(errors, data[:, 6] - data[:, 5])
corr_relErr_dist = correlation(errors/data[:, 3], data[:, 3])



# General metrics
print("General metrics:")
print("Number of samples:", errors.shape[0])
print(f"Mean: {errors.mean():.1f}  Absolute error mean: {abs_err.mean():.1f}")
print(f"Variance: {errors.var():.1f}  Standard deviation: {np.sqrt(errors.var()):.1f}")
print("Min error:", errors.min(), "Max error:", errors.max())
print("Min absolute error:", abs_err.min(), "Max absolute error:", abs_err.max())
print("Correlation error/fp_power:", corr_err_fp)
print("Correlation error/rx_power:", corr_err_rx)
print("Correlation error/powDiff:", corr_err_powDiff)
print("Correlation error/dist:", corr_relErr_dist)
print()

# Per distance metrics
distances = np.array([550, 620, 700, 820, 940, 1125, 1180, 1220, 1300, 1375, 1440, 1550, 1595, 1700, 1710, 1880, 1900, 1915])
mean = []
for dist in distances:
    print(dist, ":")
    dist_data = data[data[:, 3] == dist]

    dist_err = dist_data[:, 1] - dist_data[:, 3]
    abs_dist_err = np.abs(dist_err)
    mean.append(dist_err.mean())

    print("Number of samples:", dist_err.shape[0])
    print(f"Mean: {dist_err.mean():.1f}  Absolute error mean: {abs_dist_err.mean():.1f}")
    print(f"Variance: {dist_err.var():.1f}  Standard deviation: {np.sqrt(dist_err.var()):.1f}")
    print("Min error:", dist_err.min(), "Max error:", dist_err.max())
    print("Min absolute error:", abs_dist_err.min(), "Max absolute error:", abs_dist_err.max())
    print()

mean = np.array(mean)
plt.xlabel("X")
plt.ylabel("Y")
plt.grid(True)
plt.plot(distances, mean)
plt.show()