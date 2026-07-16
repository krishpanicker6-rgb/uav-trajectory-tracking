# UAV Trajectory Tracking Using ROS 2, PX4, and Gazebo

## Overview
This project evaluates autonomous UAV trajectory tracking in simulation using ROS 2, PX4, and Gazebo. Python scripts generate reference trajectories while PX4's built-in controller tracks the desired path. Tracking performance is analyzed using RMSE and trajectory error metrics.

## Features
- ROS 2 Offboard Control
- PX4 Autopilot
- Gazebo Simulation
- Circle Trajectory
- Square Trajectory
- Figure-8 Trajectory
- RMSE Analysis
- Speed Study

## Software
- Ubuntu
- ROS 2 Humble
- PX4
- Gazebo Classic
- Python

## Results

| Trajectory | RMSE |
|------------|------|
| Circle | 0.518 m |
| Square | 1.194 m |
| Figure-8 | 0.484 m |

## Repository Contents

- `*.py` – ROS 2 trajectory generation and offboard control scripts
- `*.csv` – Logged flight data
- `videos/` – Simulation recordings
- `figures/` – Plots used in the research poster

## Author

Krish Panicker  
Mechanical Engineering  
The Ohio State University
