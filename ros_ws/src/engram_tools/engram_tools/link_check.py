"""Measure ROS round-trip latency and message loss between two machines.

On the robot:    ``ros2 run engram_tools link_check echo``
On the desktop:  ``ros2 run engram_tools link_check probe --count 200 --rate 20``

The probe publishes numbered pings, the echo node sends each one straight back,
and the probe reports loss and round-trip times. Timing uses only the probe's
clock, so the two machines' clocks don't need to agree. One-way latency is
roughly half the round trip.
"""

import argparse
import statistics
import time
from collections.abc import Sequence
from dataclasses import dataclass

import rclpy
from rclpy.executors import Executor, SingleThreadedExecutor
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from std_msgs.msg import String

PING = '/engram/link/ping'
PONG = '/engram/link/pong'


def encode(seq: int, payload_bytes: int) -> str:
    return f'{seq} ' + 'x' * payload_bytes


def decode(data: str) -> int:
    return int(data.split(' ', 1)[0])


@dataclass(frozen=True)
class LinkStats:
    sent: int
    received: int
    loss_pct: float
    rtt_min_ms: float
    rtt_median_ms: float
    rtt_p95_ms: float
    rtt_max_ms: float

    def report(self) -> str:
        return (
            f'sent {self.sent}, received {self.received}, loss {self.loss_pct:.1f}%\n'
            f'round trip ms: min {self.rtt_min_ms:.1f}  median {self.rtt_median_ms:.1f}  '
            f'p95 {self.rtt_p95_ms:.1f}  max {self.rtt_max_ms:.1f}'
        )


def summarize(sent: int, rtts_ms: Sequence[float]) -> LinkStats:
    """Loss and round-trip statistics; RTT fields are NaN when nothing came back."""
    if sent <= 0:
        raise ValueError('sent must be positive')
    received = len(rtts_ms)
    loss = 100.0 * (sent - received) / sent
    if not rtts_ms:
        nan = float('nan')
        return LinkStats(sent, 0, loss, nan, nan, nan, nan)
    ordered = sorted(rtts_ms)
    p95 = ordered[min(len(ordered) - 1, round(0.95 * (len(ordered) - 1)))]
    return LinkStats(sent, received, loss, ordered[0], statistics.median(ordered), p95, ordered[-1])


def qos(best_effort: bool) -> QoSProfile:
    reliability = ReliabilityPolicy.BEST_EFFORT if best_effort else ReliabilityPolicy.RELIABLE
    return QoSProfile(depth=100, reliability=reliability)


class Echo(Node):
    """Republishes every ping as a pong, unchanged."""

    def __init__(self, best_effort: bool = False) -> None:
        super().__init__('link_echo')
        self._pub = self.create_publisher(String, PONG, qos(best_effort))
        self.create_subscription(String, PING, self._pub.publish, qos(best_effort))


class Probe(Node):
    """Sends numbered pings and records the round trip of each pong."""

    def __init__(self, payload_bytes: int = 0, best_effort: bool = False) -> None:
        super().__init__('link_probe')
        self._payload_bytes = payload_bytes
        self._pub = self.create_publisher(String, PING, qos(best_effort))
        self.create_subscription(String, PONG, self._on_pong, qos(best_effort))
        self._sent_at: dict[int, float] = {}
        self.rtts_ms: list[float] = []

    def ping(self, seq: int) -> None:
        self._sent_at[seq] = time.monotonic()
        self._pub.publish(String(data=encode(seq, self._payload_bytes)))

    def _on_pong(self, msg: String) -> None:
        sent_at = self._sent_at.pop(decode(msg.data), None)
        if sent_at is not None:  # ignore duplicates and pongs from other probes
            self.rtts_ms.append(1000.0 * (time.monotonic() - sent_at))

    def wait_for_echo(self, executor: Executor, timeout_s: float) -> bool:
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            if self.count_subscribers(PING) > 0 and self.count_publishers(PONG) > 0:
                return True
            executor.spin_once(timeout_sec=0.1)
        return False


def run_probe(
    probe: Probe, executor: Executor, count: int, rate_hz: float, drain_s: float = 1.0
) -> LinkStats:
    """Send ``count`` pings at ``rate_hz``, wait ``drain_s`` for late pongs, summarize."""
    period = 1.0 / rate_hz
    next_send = time.monotonic()
    for seq in range(count):
        probe.ping(seq)
        next_send += period
        while (remaining := next_send - time.monotonic()) > 0:
            executor.spin_once(timeout_sec=remaining)
    end = time.monotonic() + drain_s
    while time.monotonic() < end:
        executor.spin_once(timeout_sec=0.05)
    return summarize(count, probe.rtts_ms)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('mode', choices=['echo', 'probe'])
    parser.add_argument('--count', type=int, default=200, help='pings to send')
    parser.add_argument('--rate', type=float, default=20.0, help='pings per second')
    parser.add_argument('--payload', type=int, default=0, help='extra bytes per ping')
    parser.add_argument('--best-effort', action='store_true', help='best-effort QoS')
    args = parser.parse_args(argv)

    rclpy.init()
    executor = SingleThreadedExecutor()
    node: Node
    try:
        if args.mode == 'echo':
            node = Echo(args.best_effort)
            executor.add_node(node)
            print(f'echoing {PING} -> {PONG}; Ctrl-C to stop')
            executor.spin()
        else:
            probe = Probe(args.payload, args.best_effort)
            node = probe
            executor.add_node(probe)
            if not probe.wait_for_echo(executor, timeout_s=10.0):
                raise SystemExit('no echo node found; start `link_check echo` on the robot')
            print(run_probe(probe, executor, args.count, args.rate).report())
    except KeyboardInterrupt:
        pass
    finally:
        rclpy.try_shutdown()
