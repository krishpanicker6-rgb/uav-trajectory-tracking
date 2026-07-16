import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def analyze(filename, start_time, end_time):
    df = pd.read_csv(filename)
    df = df.apply(pd.to_numeric, errors="coerce").dropna()

    tracking_df = df[(df["time"] >= start_time) & (df["time"] <= end_time)]
    error = tracking_df["error"].to_numpy()

    rmse = np.sqrt(np.mean(error ** 2))
    max_error = np.max(error)
    mean_error = np.mean(error)

    return rmse, max_error, mean_error


fast_rmse, fast_max, fast_mean = analyze("figure8_fast_data.csv", 5.0, 20.0)
base_rmse, base_max, base_mean = analyze("figure8_data.csv", 5.0, 35.0)
slow_rmse, slow_max, slow_mean = analyze("figure8_slow_data.csv", 5.0, 65.0)

missions = ["Fast 15s", "Baseline 30s", "Slow 60s"]
rmse_values = [fast_rmse, base_rmse, slow_rmse]
max_values = [fast_max, base_max, slow_max]
mean_values = [fast_mean, base_mean, slow_mean]

print("===== Figure-8 Speed Study =====")
print(f"{'Speed':<15}{'RMSE (m)':<12}{'Max Error (m)':<16}{'Mean Error (m)':<16}")

for i in range(len(missions)):
    print(
        f"{missions[i]:<15}"
        f"{rmse_values[i]:<12.4f}"
        f"{max_values[i]:<16.4f}"
        f"{mean_values[i]:<16.4f}"
    )

plt.figure()
plt.bar(missions, rmse_values)
plt.ylabel("Tracking-only RMSE (m)")
plt.title("Figure-8 Speed Study: RMSE Comparison")
plt.grid(axis="y")
plt.show()

plt.figure()
plt.bar(missions, max_values)
plt.ylabel("Maximum Tracking Error (m)")
plt.title("Figure-8 Speed Study: Maximum Error Comparison")
plt.grid(axis="y")
plt.show()

plt.figure()
plt.bar(missions, mean_values)
plt.ylabel("Mean Tracking Error (m)")
plt.title("Figure-8 Speed Study: Mean Error Comparison")
plt.grid(axis="y")
plt.show()
