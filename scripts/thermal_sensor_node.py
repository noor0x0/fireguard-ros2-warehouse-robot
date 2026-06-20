#!/usr/bin/env python3

import math
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from std_msgs.msg import Float32


class ThermalSensorNode(Node):
    def __init__(self):
        super().__init__('thermal_sensor_node')

        self.temp_pub = self.create_publisher(Float32, '/fire_temperature', 10)

        self.odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

        self.fire_x = 12.0
        self.fire_y = 8.0

        self.ambient_temp = 25.0
        self.max_fire_temp = 180.0
        self.heat_radius = 3.0

        self.get_logger().info('Thermal Sensor Simulation Started')

    def odom_callback(self, msg):
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y

        dx = self.fire_x - x
        dy = self.fire_y - y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > self.heat_radius:
            temperature = self.ambient_temp
        else:
            heat_factor = 1.0 - (distance / self.heat_radius)
            temperature = self.ambient_temp + heat_factor * (self.max_fire_temp - self.ambient_temp)

        temp_msg = Float32()
        temp_msg.data = float(temperature)
        self.temp_pub.publish(temp_msg)

        self.get_logger().info(
            f'Thermal reading: {temperature:.1f} °C | Distance to heat source: {distance:.2f} m',
            throttle_duration_sec=1.0
        )


def main(args=None):
    rclpy.init(args=args)
    node = ThermalSensorNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
