import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    package_name = 'fireguard_robot'
    pkg_share = get_package_share_directory(package_name)
    
    # مسارات ملف الـ World والـ URDF
    world_path = os.path.join(pkg_share, 'worlds', 'fireguard_world.world')
    urdf_path = os.path.join(pkg_share, 'urdf', 'fireguard_robot.urdf')

    # قراءة الـ URDF للروبوت
    with open(urdf_path, 'r') as infp:
        robot_desc = infp.read()

    # تشغيل الـ Robot State Publisher
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc, 'use_sim_time': True}]
    )

    # تشغيل Gazebo
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={'world': world_path}.items()
    )

    # إدخال الروبوت للمحاكاة (Spawn) عند نقطة البداية الفسيحة (0, -8)
    spawn_robot_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'fireguard_robot',
            '-topic', 'robot_description',
            '-x', '0.0',
            '-y', '-8.0',
            '-z', '0.1'
        ],
        output='screen'
    )

    return LaunchDescription([
        robot_state_publisher_node,
        gazebo_launch,
        spawn_robot_node
    ])
