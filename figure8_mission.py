import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy
from px4_msgs.msg import OffboardControlMode, TrajectorySetpoint, VehicleCommand, VehicleOdometry

import math
import csv
import time


class Figure8Mission(Node):

    def __init__(self):
        super().__init__('figure8_mission')

        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        self.offboard_pub = self.create_publisher(OffboardControlMode, '/fmu/in/offboard_control_mode', 10)
        self.setpoint_pub = self.create_publisher(TrajectorySetpoint, '/fmu/in/trajectory_setpoint', 10)
        self.cmd_pub = self.create_publisher(VehicleCommand, '/fmu/in/vehicle_command', 10)

        self.sub = self.create_subscription(
            VehicleOdometry,
            '/fmu/out/vehicle_odometry',
            self.odom_cb,
            qos_profile
        )

        self.current_x = 0.0
        self.current_y = 0.0
        self.current_z = 0.0

        self.counter = 0
        self.start_time = time.time()

        self.altitude = -2.0
        self.amplitude = 2.0
        self.figure8_duration = 30.0
        self.takeoff_hold_time = 5.0

        self.state = "TAKEOFF"
        self.landing_sent = False

        self.csv_file = open("figure8_data.csv", "w", newline="")
        self.csv_writer = csv.writer(self.csv_file)

        self.csv_writer.writerow([
            "time",
            "desired_x",
            "desired_y",
            "desired_z",
            "actual_x",
            "actual_y",
            "actual_z",
            "error"
        ])

        self.timer = self.create_timer(0.1, self.loop)

        self.get_logger().info("Figure-8 mission started")

    def odom_cb(self, msg):
        self.current_x = msg.position[0]
        self.current_y = msg.position[1]
        self.current_z = msg.position[2]

    def send_offboard(self):
        msg = OffboardControlMode()
        msg.position = True
        msg.velocity = False
        msg.acceleration = False
        msg.attitude = False
        msg.body_rate = False
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.offboard_pub.publish(msg)

    def send_setpoint(self, x, y, z):
        msg = TrajectorySetpoint()
        msg.position = [float(x), float(y), float(z)]
        msg.yaw = 0.0
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.setpoint_pub.publish(msg)

    def arm(self):
        msg = VehicleCommand()
        msg.command = VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM
        msg.param1 = 1.0
        msg.target_system = 1
        msg.target_component = 1
        msg.from_external = True
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.cmd_pub.publish(msg)

    def offboard_mode(self):
        msg = VehicleCommand()
        msg.command = VehicleCommand.VEHICLE_CMD_DO_SET_MODE
        msg.param1 = 1.0
        msg.param2 = 6.0
        msg.target_system = 1
        msg.target_component = 1
        msg.from_external = True
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.cmd_pub.publish(msg)

    def land(self):
        msg = VehicleCommand()
        msg.command = VehicleCommand.VEHICLE_CMD_NAV_LAND
        msg.target_system = 1
        msg.target_component = 1
        msg.from_external = True
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.cmd_pub.publish(msg)

    def log_data(self, desired_x, desired_y, desired_z, error):
        elapsed_time = time.time() - self.start_time

        self.csv_writer.writerow([
            elapsed_time,
            desired_x,
            desired_y,
            desired_z,
            self.current_x,
            self.current_y,
            self.current_z,
            error
        ])

        self.csv_file.flush()

    def loop(self):
        self.send_offboard()

        if self.counter == 10:
            self.get_logger().info("Switching to OFFBOARD mode and arming")
            self.offboard_mode()
            self.arm()

        elapsed = time.time() - self.start_time

        if self.state == "TAKEOFF":
            desired_x = 0.0
            desired_y = 0.0
            desired_z = self.altitude

            self.send_setpoint(desired_x, desired_y, desired_z)

            error = math.sqrt(
                (desired_x - self.current_x) ** 2 +
                (desired_y - self.current_y) ** 2 +
                (desired_z - self.current_z) ** 2
            )

            self.log_data(desired_x, desired_y, desired_z, error)
            print(f"TAKEOFF | error {error:.3f}")

            if elapsed > self.takeoff_hold_time and error < 0.4:
                self.state = "FIGURE8"
                self.figure8_start_time = time.time()
                self.get_logger().info("Starting figure-8 trajectory")

        elif self.state == "FIGURE8":
            t = time.time() - self.figure8_start_time

            theta = 2.0 * math.pi * (t / self.figure8_duration)

            # Figure-8 / lemniscate-style path
            desired_x = self.amplitude * math.sin(theta)
            desired_y = self.amplitude * math.sin(theta) * math.cos(theta)
            desired_z = self.altitude

            self.send_setpoint(desired_x, desired_y, desired_z)

            error = math.sqrt(
                (desired_x - self.current_x) ** 2 +
                (desired_y - self.current_y) ** 2 +
                (desired_z - self.current_z) ** 2
            )

            self.log_data(desired_x, desired_y, desired_z, error)
            print(f"FIGURE8 | theta {theta:.2f} | error {error:.3f}")

            if t >= self.figure8_duration:
                self.state = "RETURN"
                self.get_logger().info("Figure-8 complete, returning home")

        elif self.state == "RETURN":
            desired_x = 0.0
            desired_y = 0.0
            desired_z = self.altitude

            self.send_setpoint(desired_x, desired_y, desired_z)

            error = math.sqrt(
                (desired_x - self.current_x) ** 2 +
                (desired_y - self.current_y) ** 2 +
                (desired_z - self.current_z) ** 2
            )

            self.log_data(desired_x, desired_y, desired_z, error)
            print(f"RETURN | error {error:.3f}")

            if error < 0.4:
                self.state = "LAND"
                self.get_logger().info("Returned home, landing")

        elif self.state == "LAND":
            if not self.landing_sent:
                self.land()
                self.landing_sent = True
                self.get_logger().info("Landing command sent")

        self.counter += 1

    def destroy_node(self):
        self.csv_file.close()
        super().destroy_node()


def main():
    rclpy.init()

    node = Figure8Mission()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("Figure-8 mission stopped")

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
