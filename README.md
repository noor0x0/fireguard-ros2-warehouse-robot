# FireGuard ROS2 Warehouse Robot

## Overview
FireGuard is a ROS2-based warehouse patrol robot simulation designed to detect fire-related temperature changes and trigger a foam suppression response.

The project was developed using ROS2 Humble and Gazebo Classic. It simulates a mobile robot patrolling a warehouse environment, reading fire temperature data, avoiding obstacles, and responding to dangerous heat levels.

## Project Objectives
- Simulate an indoor warehouse patrol robot.
- Detect high temperature near a fire source.
- Trigger a foam suppression action when temperature exceeds a defined threshold.
- Demonstrate ROS2 communication using nodes, topics, publishers, and subscribers.
- Test robot behavior inside a Gazebo warehouse environment.

## Technologies Used
- ROS2 Humble
- Gazebo Classic
- Python
- URDF
- Xacro
- Launch files
- Linux / Ubuntu 22.04
- RViz / Gazebo simulation tools

## Main Features
- Warehouse simulation environment.
- Differential drive robot model.
- Fire temperature simulation.
- Patrol behavior using waypoints.
- Obstacle-aware movement.
- Foam suppression trigger.
- ROS2 topic-based communication.

## ROS2 Nodes
### Waypoint Patrol Node
Controls the robot movement through predefined warehouse waypoints and handles basic obstacle-aware behavior.

### Thermal Sensor Node
Publishes simulated fire temperature readings based on the robot's distance from the fire source.

### Foam Effect Node
Subscribes to the fire temperature topic and triggers foam suppression when the temperature reaches the threshold.

## Main Topics
- `/cmd_vel` — robot velocity commands
- `/odom` — robot odometry
- `/joint_states` — wheel joint states
- `/robot_description` — robot model description
- `/tf` and `/tf_static` — transform frames
- `/fire_temperature` — simulated fire temperature readings

## Fire Detection Logic
The robot receives temperature readings from the simulated thermal sensor.  
When the temperature reaches or exceeds the defined threshold, the foam suppression behavior is triggered.

Threshold used:

```text
80°C
```
## Project Structure
fireguard-ros2-warehouse-robot/
├── README.md
├── launch/
├── urdf/
├── worlds/
├── scripts/
├── models/
├── images/
└── package.xml

## How to Run
Example launch command:  ros2 launch fireguard_robot fireguard_launch.py
Depending on the local ROS2 workspace setup, the package should be built first using:    
colcon build
source install/setup.bash

## Key Learning Outcomes
Building a ROS2 robot simulation project.
Creating and launching Gazebo worlds.
Writing ROS2 Python nodes.
Using publishers and subscribers.
Working with URDF robot descriptions.
Simulating sensor-based robot behavior.

## Author
Noor Mamoun
IT / AI Student
The Hashemite University
