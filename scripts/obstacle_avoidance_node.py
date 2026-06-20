#!/usr/bin/env python3

import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan


class FireGuardPatrolNode(Node):
    def __init__(self):
        super().__init__('fireguard_patrol_node')

        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.scan_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )

        self.front_distance = 10.0
        
        # --- إعدادات آلة الحالات للدورية (Patrol FSM) ---
        self.state = "FORWARD"  # الحالات: FORWARD, PATROL_TURN, AVOID_TURN
        self.state_counter = 0   # العداد يعتمد على تردد الـ Timer (0.1 ثانية)
        
        self.FORWARD_DURATION = 50      # 5 ثوانٍ مشي للأمام
        self.PATROL_TURN_DURATION = 20  # ثانيتان دوران استكشافي

        self.timer = self.create_timer(0.1, self.control_loop)
        self.get_logger().info('FireGuard Official Patrol Node Started')

    def scan_callback(self, msg):
        ranges = list(msg.ranges)
        num_readings = len(ranges)

        if num_readings == 0:
            return

        # تحديد الزاوية الأمامية الحادة (15 قراءة من كل طرف)
        front_ranges = ranges[-15:] + ranges[:15]

        valid_ranges = []
        for r in front_ranges:
            if not math.isinf(r) and not math.isnan(r) and 0.35 < r < 8.0:
                valid_ranges.append(r)

        if valid_ranges:
            self.front_distance = min(valid_ranges)
        else:
            self.front_distance = 10.0

    def control_loop(self):
        msg = Twist()
        
        # --- 1. فحص الطوارئ الفوري (أعلى أولويات النظام) ---
        if self.front_distance < 0.45:
            if self.state != "AVOID_TURN":
                self.get_logger().warn(f'Emergency! Obstacle detected at {self.front_distance:.2f}m. Breaking patrol!')
            self.state = "AVOID_TURN"
            
        # --- 2. إدارة الحالات (State Machine Logic) ---
        if self.state == "AVOID_TURN":
            if self.front_distance < 0.60:
                msg.linear.x = 0.0
                msg.angular.z = 0.35
            else:
                # العودة للمشي وتصفير العداد
                self.state = "FORWARD"
                self.state_counter = 0

        elif self.state == "FORWARD":
            msg.linear.x = 0.08
            msg.angular.z = 0.0
            self.state_counter += 1
            
            if self.state_counter >= self.FORWARD_DURATION:
                self.state = "PATROL_TURN"
                self.state_counter = 0
                self.get_logger().info('Checking flanking paths (Patrol Turn)...')

        elif self.state == "PATROL_TURN":
            msg.linear.x = 0.0
            msg.angular.z = 0.25
            self.state_counter += 1
            
            if self.state_counter >= self.PATROL_TURN_DURATION:
                self.state = "FORWARD"
                self.state_counter = 0
                self.get_logger().info('Resuming forward patrol...')

        # --- 3. طباعة ذكية ومحددة (مرة واحدة كل ثانية فقط لحماية الـ VirtualBox) ---
        log_msg = f'State: {self.state} | Counter: {self.state_counter} | Dist: {self.front_distance:.2f}m'
        self.get_logger().info(log_msg, throttle_duration_sec=1.0)
        
        self.cmd_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = FireGuardPatrolNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        # التعديل الاحترافي لضمان التصفير الكامل الآمن
        stop_msg = Twist()
        stop_msg.linear.x = 0.0
        stop_msg.angular.z = 0.0
        node.cmd_pub.publish(stop_msg)
        node.get_logger().info('FireGuard Patrol Node Stopped Safely')
    finally:
        node.destroy_node()
        # فحص حالة الـ context لمنع أخطاء الـ Invalid Context في التيرمنال
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
