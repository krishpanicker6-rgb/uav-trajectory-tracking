import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Tracking-only values you already computed
missions = ["Square", "Circle", "Figure-8"]

rmse_values = [1.1935, 0.5180, 0.4839]
max_error_values = [2.1550, 0.8607, 0.7804]
mean_error_values = [1.0195, 0.5143, 0.4691]

# -----------------------
# Print table
# -----------------------
print("===== Tracking-Only Mission Comparison =====")
print(f"{'Mission':<12}{'RMSE (m)':<12}{'Max Error (m)':<16}{'Mean Error (m)':<16}")

for i in range(len(missions)):
    print(
        f"{missions[i]:<12}"
        f"{rmse_values[i]:<12.4f}"
        f"{max_error_values[i]:<16.4f}"
        f"{mean_error_values[i]:<16.4f}"
    )

# -----------------------
# RMSE bar chart
# -----------------------
plt.figure()
plt.bar(missions, rmse_values)
plt.ylabel("Tracking-Only RMSE (m)")
plt.title("Tracking-Only RMSE Comparison")
plt.grid(axis="y")
plt.show()

# -----------------------
# Max error bar chart
# -----------------------
plt.figure()
plt.bar(missions, max_error_values)
plt.ylabel("Maximum Tracking Error (m)")
plt.title("Maximum Tracking Error Comparison")
plt.grid(axis="y")
plt.show()

# -----------------------
# Mean error bar chart
# -----------------------
plt.figure()
plt.bar(missions, mean_error_values)
plt.ylabel("Mean Tracking Error (m)")
plt.title("Mean Tracking Error Comparison")
plt.grid(axis="y")
plt.show()
