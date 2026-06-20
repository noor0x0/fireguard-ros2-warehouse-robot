#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class PatrolNode(Node):
    def __init__(self):
        super().__init__('patrol_node')

        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.state = 'forward'
        self.counter = 0

        self.timer = self.create_timer(0.1, self.patrol_loop)

        self.get_logger().info('FireGuard Patrol Node Started')

    def patrol_loop(self):
        msg = Twist()

        if self.state == 'forward':
            msg.linear.x = 0.12
            msg.angular.z = 0.0
            self.counter += 1

            if self.counter > 60:
                self.state = 'turn'
                self.counter = 0

        elif self.state == 'turn':
            msg.linear.x = 0.0
            msg.angular.z = 0.45
            self.counter += 1

            if self.counter > 30:
                self.state = 'forward'
                self.counter = 0

        self.cmd_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = PatrolNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        stop_msg = Twist()
        node.cmd_pub.publish(stop_msg)
        node.get_logger().info('FireGuard Patrol Node Stopped')

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
