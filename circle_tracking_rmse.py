import pandas as pd
import numpy as np

df = pd.read_csv("circle_data.csv")
df = df.apply(pd.to_numeric, errors="coerce").dropna()

# Adjust if needed based on your circle graph
start_time = 5.0
end_time = 30.0

tracking_df = df[(df["time"] >= start_time) & (df["time"] <= end_time)]

error = tracking_df["error"].to_numpy()

rmse = np.sqrt(np.mean(error ** 2))
max_error = np.max(error)
mean_error = np.mean(error)

print("===== Circle Tracking-Only Results =====")
print(f"Time window: {start_time} s to {end_time} s")
print(f"Tracking-only RMSE: {rmse:.4f} m")
print(f"Tracking-only Max Error: {max_error:.4f} m")
print(f"Tracking-only Mean Error: {mean_error:.4f} m")
print(f"Samples used: {len(error)}")
