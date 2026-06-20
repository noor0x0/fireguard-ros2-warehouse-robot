#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from gazebo_msgs.srv import SpawnEntity


class FoamEffectNode(Node):
    def __init__(self):
        super().__init__('foam_effect_node')

        self.temp_sub = self.create_subscription(
            Float32,
            '/fire_temperature',
            self.temperature_callback,
            10
        )

        self.spawn_client = self.create_client(SpawnEntity, '/spawn_entity')

        self.fire_threshold = 80.0
        self.foam_spawned = False

        self.get_logger().info('Foam Visual Effect Node Started')

    def temperature_callback(self, msg):
        temperature = msg.data

        if temperature >= self.fire_threshold and not self.foam_spawned:
            self.foam_spawned = True
            self.get_logger().warn('Foam visual effect activated!')
            self.spawn_foam()

    def spawn_foam(self):
        if not self.spawn_client.wait_for_service(timeout_sec=5.0):
            self.get_logger().error('Spawn service not available.')
            return

        foam_sdf = """
        <sdf version="1.6">
  <model name="foam_suppression_cloud">
    <static>true</static>

    <link name="foam_link">

      <visual name="foam_blanket_main">
        <pose>0 0 0.08 0 0 0</pose>
        <geometry>
          <cylinder>
            <radius>1.35</radius>
            <length>0.10</length>
          </cylinder>
        </geometry>
        <material>
          <ambient>0.95 0.95 0.90 0.95</ambient>
          <diffuse>0.95 0.95 0.90 0.95</diffuse>
        </material>
      </visual>

      <visual name="foam_blanket_inner">
        <pose>0.15 -0.1 0.16 0 0 0</pose>
        <geometry>
          <cylinder>
            <radius>0.85</radius>
            <length>0.08</length>
          </cylinder>
        </geometry>
        <material>
          <ambient>1 1 1 0.9</ambient>
          <diffuse>1 1 1 0.9</diffuse>
        </material>
      </visual>

      <visual name="foam_puff_small_1">
        <pose>-0.45 0.35 0.22 0 0 0</pose>
        <geometry>
          <sphere>
            <radius>0.22</radius>
          </sphere>
        </geometry>
        <material>
          <ambient>1 1 1 0.85</ambient>
          <diffuse>1 1 1 0.85</diffuse>
        </material>
      </visual>

      <visual name="foam_puff_small_2">
        <pose>0.50 -0.25 0.22 0 0 0</pose>
        <geometry>
          <sphere>
            <radius>0.18</radius>
          </sphere>
        </geometry>
        <material>
          <ambient>0.95 0.95 0.90 0.85</ambient>
          <diffuse>0.95 0.95 0.90 0.85</diffuse>
        </material>
      </visual>

    </link>
  </model>
</sdf>
        """

        request = SpawnEntity.Request()
        request.name = 'foam_suppression_cloud'
        request.xml = foam_sdf
        request.robot_namespace = ''
        request.initial_pose.position.x = 12.0
        request.initial_pose.position.y = 8.0
        request.initial_pose.position.z = 0.05
        request.initial_pose.position.z = 0.02
        future = self.spawn_client.call_async(request)
        future.add_done_callback(self.spawn_response)

    def spawn_response(self, future):
        try:
            result = future.result()
            if result.success:
                self.get_logger().warn('Foam cloud spawned successfully.')
            else:
                self.get_logger().warn(f'Foam spawn failed: {result.status_message}')
        except Exception as e:
            self.get_logger().error(f'Foam spawn error: {e}')


def main(args=None):
    rclpy.init(args=args)
    node = FoamEffectNode()

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
