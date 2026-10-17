"""Publish a periodic heartbeat so other nodes and the UI can tell the robot stack is up."""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

TOPIC = 'heartbeat'


def format_heartbeat(robot_name: str, count: int) -> str:
    """Return the heartbeat payload for the given beat number."""
    if count < 0:
        raise ValueError('count must be non-negative')
    return f'{robot_name} alive #{count}'


class Heartbeat(Node):
    """Publishes ``<robot_name> alive #<n>`` on ``heartbeat`` at ``rate_hz``."""

    def __init__(self) -> None:
        super().__init__('heartbeat')
        self._robot_name = str(self.declare_parameter('robot_name', 'engram').value)
        rate_hz = float(self.declare_parameter('rate_hz', 1.0).value)
        if rate_hz <= 0.0:
            raise ValueError('rate_hz must be positive')
        self._count = 0
        self._pub = self.create_publisher(String, TOPIC, 10)
        self.create_timer(1.0 / rate_hz, self._beat)

    def _beat(self) -> None:
        self._pub.publish(String(data=format_heartbeat(self._robot_name, self._count)))
        self._count += 1


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = Heartbeat()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()
