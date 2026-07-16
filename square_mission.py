import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy

from px4_msgs.msg import OffboardControlMode, TrajectorySetpoint, VehicleCommand, VehicleOdometry

import math
import csv
import time


class WaypointMission(Node):

    def __init__(self):
        super().__init__('waypoint_mission')

        # -----------------------
        # QoS (IMPORTANT FIX)
        # -----------------------
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        # -----------------------
        # Publishers
        # -----------------------
        self.offboard_pub = self.create_publisher(
            OffboardControlMode,
            '/fmu/in/offboard_control_mode',
            10
        )

        self.setpoint_pub = self.create_publisher(
            TrajectorySetpoint,
            '/fmu/in/trajectory_setpoint',
            10
        )

        self.cmd_pub = self.create_publisher(
            VehicleCommand,
            '/fmu/in/vehicle_command',
            10
        )

        # -----------------------
        # Subscriber
        # -----------------------
        self.sub = self.create_subscription(
            VehicleOdometry,
            '/fmu/out/vehicle_odometry',
            self.odom_cb,
            qos_profile
        )

        # -----------------------
        # State
        # -----------------------
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_z = 0.0

        self.start_time = time.time()

        self.offboard_counter = 0
        self.mission_done = False
        self.landing = False

        # -----------------------
        # WAYPOINTS (4 points + return)
        # -----------------------
        self.waypoints = [
            (0.0, 0.0, -2.0),
            (2.0, 0.0, -2.0),
            (2.0, 2.0, -2.0),
            (0.0, 2.0, -2.0),
            (0.0, 0.0, -2.0)
        ]

        self.wp_index = 0

        # -----------------------
        # CSV LOGGING
        # -----------------------
        self.file = open("flight_data.csv", "w", newline="")
        self.writer = csv.writer(self.file)

        self.writer.writerow([
            "time",
            "desired_x", "desired_y", "desired_z",
            "actual_x", "actual_y", "actual_z",
            "error"
        ])

        # -----------------------
        # Timer
        # -----------------------
        self.timer = self.create_timer(0.1, self.loop)

        self.get_logger().info("Started mission")

    # -----------------------
    # Odometry
    # -----------------------
    def odom_cb(self, msg):
        self.current_x = msg.position[0]
        self.current_y = msg.position[1]
        self.current_z = msg.position[2]

    # -----------------------
    # Offboard heartbeat
    # -----------------------
    def send_offboard(self):
        msg = OffboardControlMode()
        msg.position = True
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.offboard_pub.publish(msg)

    # -----------------------
    # Setpoint (FIXED TYPE SAFETY)
    # -----------------------
    def send_setpoint(self, x, y, z):
        msg = TrajectorySetpoint()

        # IMPORTANT FIX: must be float + correct type
        msg.position = [float(x), float(y), float(z)]
        msg.yaw = 0.0

        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)

        self.setpoint_pub.publish(msg)

    # -----------------------
    # Arm
    # -----------------------
    def arm(self):
        msg = VehicleCommand()
        msg.command = VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM
        msg.param1 = 1.0
        msg.target_system = 1
        msg.target_component = 1
        msg.from_external = True
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)

        self.cmd_pub.publish(msg)

    # -----------------------
    # Offboard mode
    # -----------------------
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

    # -----------------------
    # LAND command
    # -----------------------
    def land(self):
        msg = VehicleCommand()
        msg.command = VehicleCommand.VEHICLE_CMD_NAV_LAND
        msg.target_system = 1
        msg.target_component = 1
        msg.from_external = True
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)

        self.cmd_pub.publish(msg)

    # -----------------------
    # MAIN LOOP
    # -----------------------
    def loop(self):

        self.send_offboard()

        # safety: need initial setpoints before switching
        if self.offboard_counter == 10:
            self.get_logger().info("Switching to OFFBOARD + ARM")
            self.offboard_mode()
            self.arm()

        self.offboard_counter += 1

        # -----------------------
        # Mission complete → LAND
        # -----------------------
        if self.wp_index >= len(self.waypoints):
            if not self.landing:
                self.get_logger().info("MISSION COMPLETE → LANDING")
                self.land()
                self.landing = True

            self.send_setpoint(0, 0, -2)
            return

        # -----------------------
        # Current waypoint
        # -----------------------
        wx, wy, wz = self.waypoints[self.wp_index]

        self.send_setpoint(wx, wy, wz)

        # -----------------------
        # Error (Euclidean distance)
        # -----------------------
        error = math.sqrt(
            (wx - self.current_x) ** 2 +
            (wy - self.current_y) ** 2 +
            (wz - self.current_z) ** 2
        )

        t = time.time() - self.start_time

        self.writer.writerow([
            t,
            wx, wy, wz,
            self.current_x, self.current_y, self.current_z,
            error
        ])

        print(f"WP {self.wp_index} | error {error:.3f}")

        # -----------------------
        # Switch waypoint
        # -----------------------
        if error < 0.3:
            self.wp_index += 1
            time.sleep(0.3)

    # -----------------------
    # cleanup
    # -----------------------
    def destroy_node(self):
        self.file.close()
        super().destroy_node()


def main():
    rclpy.init()

    node = WaypointMission()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("Stopped")

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
