from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():

    pkg_path = get_package_share_directory('fireguard_robot')

    urdf_file = os.path.join(pkg_path, 'urdf', 'fireguard_robot.urdf')
    world_file = os.path.join(pkg_path, 'worlds', 'fireguard_world.world')

    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()

    return LaunchDescription([

        # Robot State Publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': robot_desc,
                'use_sim_time': True
            }]
        ),

        # Gazebo Server
        ExecuteProcess(
            cmd=[
                'gzserver',
                '--verbose',
                '-s',
                'libgazebo_ros_factory.so',
                world_file
            ],
            output='screen'
        ),

        # Spawn Robot
        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            arguments=[
                '-entity', 'fireguard_robot',
                '-topic', 'robot_description',
                '-x', '0',
                '-y', '-9',
                '-z', '0.2'
            ],
            output='screen'
        )
    ])
