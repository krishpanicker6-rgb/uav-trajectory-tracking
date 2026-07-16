import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv("flight_data.csv")
df = df.apply(pd.to_numeric, errors="coerce").dropna()

time = df["time"].to_numpy()
error = df["error"].to_numpy()

rmse = np.sqrt(np.mean(error ** 2))
max_error = np.max(error)

print(f"Square RMSE: {rmse:.4f} m")
print(f"Square Max Error: {max_error:.4f} m")

plt.figure()
plt.plot(time, error)
plt.xlabel("Time (s)")
plt.ylabel("Tracking Error (m)")
plt.title("Square Mission Tracking Error vs Time")
plt.grid(True)
plt.show()

fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")

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

ax.set_xlabel("X (m)")
ax.set_ylabel("Y (m)")
ax.set_zlabel("Z (m)")
ax.set_title("Square Mission 3D Trajectory Tracking")
ax.legend()

plt.show()
