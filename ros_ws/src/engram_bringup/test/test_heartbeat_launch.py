"""Launch the bringup and check that a heartbeat arrives on the topic."""

import time
import unittest

import launch
import launch_ros.actions
import launch_testing.actions
import pytest
import rclpy
from std_msgs.msg import String


@pytest.mark.launch_test
def generate_test_description() -> launch.LaunchDescription:
    heartbeat = launch_ros.actions.Node(
        package='engram_bringup',
        executable='heartbeat',
        parameters=[{'rate_hz': 10.0}],
    )
    return launch.LaunchDescription([heartbeat, launch_testing.actions.ReadyToTest()])


class TestHeartbeat(unittest.TestCase):
    def setUp(self) -> None:
        rclpy.init()
        self.node = rclpy.create_node('heartbeat_listener')

    def tearDown(self) -> None:
        self.node.destroy_node()
        rclpy.shutdown()

    def test_heartbeat_is_published(self) -> None:
        received: list[str] = []
        self.node.create_subscription(String, 'heartbeat', lambda m: received.append(m.data), 10)
        deadline = time.monotonic() + 10.0
        while not received and time.monotonic() < deadline:
            rclpy.spin_once(self.node, timeout_sec=0.1)
        self.assertTrue(received, 'no heartbeat within 10 s')
        self.assertRegex(received[0], r'^engram alive #\d+$')
