"""Show the engram URDF in RViz with sliders for the arm joints."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    share = FindPackageShare('engram_description')
    gui = LaunchConfiguration('gui')
    robot_description = ParameterValue(
        Command(
            [
                'xacro ',
                PathJoinSubstitution([share, 'urdf', 'engram.urdf.xacro']),
                ' arm_x:=',
                LaunchConfiguration('arm_x'),
            ]
        ),
        value_type=str,
    )
    return LaunchDescription(
        [
            DeclareLaunchArgument('gui', default_value='true', description='Joint sliders'),
            DeclareLaunchArgument('rviz', default_value='true', description='Start RViz'),
            DeclareLaunchArgument(
                'arm_x', default_value='0.0222', description='Arm x on base_link [m]'
            ),
            Node(
                package='robot_state_publisher',
                executable='robot_state_publisher',
                parameters=[{'robot_description': robot_description}],
            ),
            Node(
                package='joint_state_publisher_gui',
                executable='joint_state_publisher_gui',
                condition=IfCondition(gui),
            ),
            Node(
                package='joint_state_publisher',
                executable='joint_state_publisher',
                condition=UnlessCondition(gui),
            ),
            Node(
                package='rviz2',
                executable='rviz2',
                arguments=['-d', PathJoinSubstitution([share, 'rviz', 'display.rviz'])],
                condition=IfCondition(LaunchConfiguration('rviz')),
            ),
        ]
    )
