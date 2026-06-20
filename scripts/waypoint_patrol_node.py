#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry

class WaypointPatrolNode(Node):
    def __init__(self):
        super().__init__('waypoint_patrol_node')
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0
        
        # تم تعديل المسار ليكون في منتصف الممرات لتجنب الاصطدام بالرفوف
        self.waypoints = [
    (3.47, -7.31),
    (4.03, 6.10),
    (7.00, 7.00),
    (10.50, 8.00),   # safe distance from fire
]
        self.current_waypoint = 0
        
        # State machine for waypoint behavior
        self.STATE_MOVING = 0
        self.STATE_PAUSING = 1
        self.STATE_FINISHED = 2  # حالة جديدة: التوقف عند إنهاء المهمة
        self.state = self.STATE_MOVING
        self.pause_counter = 0
        self.pause_duration = 10  # 1 second at 0.1s timer
        
        # Control parameters
        self.WAYPOINT_REACH_DISTANCE = 0.25 
        self.WAYPOINT_SLOW_DISTANCE = 1.5    
        self.MAX_LINEAR_VELOCITY = 0.30      
        self.MAX_ANGULAR_VELOCITY = 0.6      
        self.ANGLE_THRESHOLD = 0.15          
        
        self.LARGE_HEADING_ERROR = 0.6       
        self.MODERATE_HEADING_ERROR = 0.15   
        
        self.timer = self.create_timer(0.1, self.control_loop)
        self.get_logger().info('FireGuard Stable Safe-Waypoint Patrol Started')
    
    def odom_callback(self, msg):
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y
        q = msg.pose.pose.orientation
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        self.yaw = math.atan2(siny_cosp, cosy_cosp)
    
    def normalize_angle(self, angle):
        while angle > math.pi:
            angle -= 2.0 * math.pi
        while angle < -math.pi:
            angle += 2.0 * math.pi
        return angle
    
    def next_waypoint(self):
        # التعديل هنا: التوقف عند الوصول لآخر نقطة بدل إعادة المسار
        if self.current_waypoint < len(self.waypoints) - 1:
            self.current_waypoint += 1
        else:
            self.state = self.STATE_FINISHED
            self.get_logger().info('🔥 تم الوصول إلى موقع الحريق بنجاح! الروبوت متوقف الآن.')
    
    def control_loop(self):
        msg = Twist()

        # إذا أنهى الروبوت مهمته، أوقف الحركة تماماً
        if self.state == self.STATE_FINISHED:
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            self.cmd_pub.publish(msg)
            return

        target_x, target_y = self.waypoints[self.current_waypoint]
        
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        target_angle = math.atan2(dy, dx)
        angle_error = self.normalize_angle(target_angle - self.yaw)
        
        if self.state == self.STATE_PAUSING:
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            self.cmd_pub.publish(msg)
            
            self.pause_counter += 1
            if self.pause_counter >= self.pause_duration:
                self.pause_counter = 0
                self.state = self.STATE_MOVING
                self.next_waypoint()
                if self.state != self.STATE_FINISHED:
                    self.get_logger().info(
                        f'✓ Moving to waypoint {self.current_waypoint + 1}/{len(self.waypoints)}'
                    )
            return
        
        if distance < self.WAYPOINT_REACH_DISTANCE:
            self.state = self.STATE_PAUSING
            self.pause_counter = 0
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            self.get_logger().info(
                f'Reached waypoint {self.current_waypoint + 1}: ({target_x}, {target_y})'
            )
            self.cmd_pub.publish(msg)
            return
        
        if distance < self.WAYPOINT_SLOW_DISTANCE:
            linear_velocity = self.MAX_LINEAR_VELOCITY * (distance / self.WAYPOINT_SLOW_DISTANCE)
            linear_velocity = max(linear_velocity, 0.05) 
        else:
            linear_velocity = self.MAX_LINEAR_VELOCITY
        
        angular_velocity = 1.2 * angle_error
        angular_velocity = max(min(angular_velocity, 0.6), -0.6) 
        
        if abs(angle_error) > self.LARGE_HEADING_ERROR:
            msg.linear.x = 0.0
            msg.angular.z = angular_velocity
        elif abs(angle_error) > self.MODERATE_HEADING_ERROR:
            msg.linear.x = linear_velocity * 0.4
            msg.angular.z = angular_velocity
        else:
            msg.linear.x = linear_velocity
            msg.angular.z = angular_velocity
        
        self.cmd_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = WaypointPatrolNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        try:
            stop_msg = Twist()
            stop_msg.linear.x = 0.0
            stop_msg.angular.z = 0.0
            node.cmd_pub.publish(stop_msg)
        except Exception:
            pass
    finally:
        try:
            node.destroy_node()
        except Exception:
            pass
        try:
            if rclpy.ok():
                rclpy.shutdown()
        except Exception:
            pass

if __name__ == '__main__':
    main()
