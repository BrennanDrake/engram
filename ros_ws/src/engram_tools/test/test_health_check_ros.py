"""Measure a real publisher in-process."""

from collections.abc import Iterator

import pytest
import rclpy
from engram_tools.health_check import RateProbe, measure_rates
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from std_msgs.msg import String


@pytest.fixture
def ros() -> Iterator[None]:
    rclpy.init()
    yield
    rclpy.try_shutdown()


def test_measures_publisher_rate(ros: None) -> None:
    talker = Node('talker')
    pub = talker.create_publisher(String, 'chatter', 10)
    talker.create_timer(0.05, lambda: pub.publish(String(data='hi')))  # 20 Hz
    probe = RateProbe()
    executor = SingleThreadedExecutor()
    executor.add_node(talker)
    executor.add_node(probe)

    rates = measure_rates(probe, executor, ['/chatter', '/missing'], 2.0, 3.0)

    assert rates['/missing'] is None
    assert rates['/chatter'] is not None
    assert 12.0 < rates['/chatter'] < 25.0
    talker.destroy_node()
    probe.destroy_node()
