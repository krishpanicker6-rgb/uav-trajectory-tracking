import pandas as pd
import numpy as np

df = pd.read_csv("flight_data.csv")
df = df.apply(pd.to_numeric, errors="coerce").dropna()

# Adjust if needed based on your square graph
start_time = 4.0
end_time = 14.0

tracking_df = df[(df["time"] >= start_time) & (df["time"] <= end_time)]

error = tracking_df["error"].to_numpy()

rmse = np.sqrt(np.mean(error ** 2))
max_error = np.max(error)
mean_error = np.mean(error)

print("===== Square Tracking-Only Results =====")
print(f"Time window: {start_time} s to {end_time} s")
print(f"Tracking-only RMSE: {rmse:.4f} m")
print(f"Tracking-only Max Error: {max_error:.4f} m")
print(f"Tracking-only Mean Error: {mean_error:.4f} m")
print(f"Samples used: {len(error)}")
