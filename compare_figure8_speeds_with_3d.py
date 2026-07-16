import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def load_data(filename):
    df = pd.read_csv(filename)
    df = df.apply(pd.to_numeric, errors="coerce").dropna()
    return df


def analyze(df, start_time, end_time):
    tracking_df = df[(df["time"] >= start_time) & (df["time"] <= end_time)]
    error = tracking_df["error"].to_numpy()

    rmse = np.sqrt(np.mean(error ** 2))
    max_error = np.max(error)
    mean_error = np.mean(error)

    return rmse, max_error, mean_error


# Load data
fast_df = load_data("figure8_fast_data.csv")
base_df = load_data("figure8_data.csv")
slow_df = load_data("figure8_slow_data.csv")

# Tracking-only windows
fast_rmse, fast_max, fast_mean = analyze(fast_df, 5.0, 20.0)
base_rmse, base_max, base_mean = analyze(base_df, 5.0, 35.0)
slow_rmse, slow_max, slow_mean = analyze(slow_df, 5.0, 65.0)

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


# -----------------------
# RMSE BAR GRAPH
# -----------------------
plt.figure()
plt.bar(missions, rmse_values)
plt.ylabel("Tracking-only RMSE (m)")
plt.title("Figure-8 Speed Study: RMSE Comparison")
plt.grid(axis="y")
plt.show()


# -----------------------
# MAX ERROR BAR GRAPH
# -----------------------
plt.figure()
plt.bar(missions, max_values)
plt.ylabel("Maximum Tracking Error (m)")
plt.title("Figure-8 Speed Study: Maximum Error Comparison")
plt.grid(axis="y")
plt.show()


# -----------------------
# MEAN ERROR BAR GRAPH
# -----------------------
plt.figure()
plt.bar(missions, mean_values)
plt.ylabel("Mean Tracking Error (m)")
plt.title("Figure-8 Speed Study: Mean Error Comparison")
plt.grid(axis="y")
plt.show()


# -----------------------
# 3D COMPARISON PLOTS
# -----------------------
fig = plt.figure(figsize=(15, 5))

datasets = [
    ("Fast 15s", fast_df, fast_rmse),
    ("Baseline 30s", base_df, base_rmse),
    ("Slow 60s", slow_df, slow_rmse)
]

for i, (title, df, rmse) in enumerate(datasets):
    ax = fig.add_subplot(1, 3, i + 1, projection="3d")

    ax.plot(
        df["actual_x"].to_numpy(),
        df["actual_y"].to_numpy(),
        df["actual_z"].to_numpy(),
        label="Actual"
    )

    ax.plot(
        df["desired_x"].to_numpy(),
        df["desired_y"].to_numpy(),
        df["desired_z"].to_numpy(),
        label="Desired"
    )

    ax.set_title(f"{title}\nRMSE={rmse:.3f} m")
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_zlabel("Z (m)")
    ax.legend()

plt.suptitle("Figure-8 3D Trajectory Tracking Across Speeds")
plt.tight_layout()
plt.show()
