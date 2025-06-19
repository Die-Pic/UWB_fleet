import numpy as np
import pandas as pd
import glob

file_paths = glob.glob('Datasets/**/*.csv', recursive=True)
dfs = [
    pd.read_csv(f,
                parse_dates=["timestamp"])  # ← parse_dates!
    for f in file_paths
]

big_df = pd.concat(dfs, ignore_index=True)
data = big_df.to_numpy()

errors = data[:, 1] - data[:, 3]
#errors = np.abs(errors)

max_err = errors.max()
print(errors.mean())
print(errors.var())
print(errors.min(), max_err)


for i in range(len(errors)):
    if errors[i] == max_err:
        print(i)
        print(data[i])
