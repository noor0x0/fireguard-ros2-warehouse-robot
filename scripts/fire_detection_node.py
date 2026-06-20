#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float32


class FireDetectionNode(Node):
    def __init__(self):
        super().__init__('fire_detection_node')

        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.temp_sub = self.create_subscription(
            Float32,
            '/fire_temperature',
            self.temperature_callback,
            10
        )

        self.fire_threshold = 80.0

        self.fire_detected = False
        self.foam_activated = False

        self.get_logger().info('Fire Detection Node Started')
        self.get_logger().info(f'Fire threshold set to {self.fire_threshold:.1f} °C')

    def temperature_callback(self, msg):
        temperature = msg.data

        self.get_logger().info(
            f'Received thermal reading: {temperature:.1f} °C',
            throttle_duration_sec=1.0
        )

        if temperature >= self.fire_threshold and not self.fire_detected:
            self.fire_detected = True
            self.stop_robot()

            self.get_logger().warn('FIRE DETECTED BY THERMAL SENSOR!')
            self.get_logger().warn(f'Temperature exceeded threshold: {temperature:.1f} °C')

            self.activate_foam()

    def stop_robot(self):
        stop_msg = Twist()
        stop_msg.linear.x = 0.0
        stop_msg.angular.z = 0.0
        self.cmd_pub.publish(stop_msg)

    def activate_foam(self):
        if not self.foam_activated:
            self.foam_activated = True
            self.get_logger().warn('FOAM SUPPRESSION ACTIVATED!')
            self.get_logger().warn('FireGuard is spraying non-water foam suppressant.')
            self.get_logger().warn('Mission status: FIRE RESPONSE COMPLETE.')


def main(args=None):
    rclpy.init(args=args)
    node = FireDetectionNode()

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
