from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, RegisterEventHandler, TimerAction
from launch.event_handlers import OnProcessStart
from launch.substitutions import Command, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue
import os
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg_share = FindPackageShare(package='motivon_pkg').find('motivon_pkg')
    default_model_path = os.path.join(pkg_share, 'urdf', 'Robot_SimplifiedCAD.urdf')
    mesh_path = os.path.join(pkg_share, 'meshes')
    robot_controllers = PathJoinSubstitution([pkg_share, 'config', 'controllers.yaml'])
    world_file_path = os.path.join(pkg_share, 'world', 'my_world.sdf')

    robot_desc = ParameterValue(
        Command(['xacro ', default_model_path, ' mesh_path:=file://', mesh_path]), 
        value_type=str
    )

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_desc, 'use_sim_time': True}],
        output='screen'
    )

    # Gazebo launch
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('ros_gz_sim'),
            'launch',
            'gz_sim.launch.py'
        )]),
        launch_arguments={'gz_args': f'-r -v 4 {world_file_path}'}.items())

    # ROS2 Control node
    control_node = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[{'robot_description': robot_desc}, robot_controllers, {"use_sim_time": True}],
        output='screen',
    )

    # Gazebo spawn robot entity with delay
    node_gz_spawn_entity = TimerAction(
        period=3.0,
        actions=[
            Node(
                package='ros_gz_sim',
                executable='create',
                output='screen',
                arguments=['-topic', 'robot_description',
                        '-name', 'Robot_SimplifiedCAD',
                        '-x', '0.0',
                        '-y', '0.0',
                        '-z', '0.5',
                        '-R', '0.0',
                        '-P', '0.0',
                        '-Y', '0.0'
                ],
                parameters=[{"use_sim_time": True}]
            )
        ]
    )

    # Bridge Node
    bridge_gz = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            # General
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            # Gazebo Control
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
            '/imu@sensor_msgs/msg/Imu[gz.msgs.IMU',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
        ],
        remappings=[
            ('/world/my_world/model/Robot_SimplifiedCAD/joint_state', 'joint_states'),
        ],
        output='screen'
    )

    # Controller spawner for joint state broadcaster
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
    )

    # Controller spawner for diff drive controller
    diff_drive_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["diff_drive_controller"],
    )

    # Delay spawners to ensure control_node is ready
    delayed_joint_state_broadcaster_spawner = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=control_node,
            on_start=[joint_state_broadcaster_spawner],
        )
    )

    delayed_diff_drive_controller_spawner = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=control_node,
            on_start=[diff_drive_controller_spawner],
        )
    )

    return LaunchDescription([
        gazebo,
        robot_state_publisher_node,
        control_node,
        node_gz_spawn_entity,
        bridge_gz,
        delayed_joint_state_broadcaster_spawner,
        delayed_diff_drive_controller_spawner,
    ])
