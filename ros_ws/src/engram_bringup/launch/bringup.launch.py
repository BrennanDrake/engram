"""Start the engram robot stack. For now this is just the heartbeat."""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            Node(package='engram_bringup', executable='heartbeat', output='screen'),
        ]
    )
