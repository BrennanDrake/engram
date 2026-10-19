"""Check that topics publish at or above their minimum rates.

Usage: ``ros2 run engram_tools health_check /odom:10 /scan:4 [--window 3]``.
With no topics given, ``ENGRAM_HEALTH_TOPICS`` (space-separated) is used.
Exits 0 when every topic is healthy and 1 otherwise, so it works as a Docker
healthcheck and as the gate in ``robotctl deploy``.
"""

import argparse
import os
import sys
import time
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass

import rclpy
from rclpy.executors import Executor, SingleThreadedExecutor
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from rosidl_runtime_py.utilities import get_message

ENV_TOPICS = 'ENGRAM_HEALTH_TOPICS'


@dataclass(frozen=True)
class TopicSpec:
    topic: str
    min_hz: float


def parse_spec(text: str) -> TopicSpec:
    """Parse ``/topic:min_hz``, e.g. ``/odom:10``."""
    topic, sep, rate = text.rpartition(':')
    if not sep or not topic:
        raise ValueError(f'expected /topic:min_hz, got {text!r}')
    min_hz = float(rate)
    if min_hz < 0:
        raise ValueError(f'minimum rate must be non-negative in {text!r}')
    return TopicSpec(topic, min_hz)


def evaluate(specs: Iterable[TopicSpec], rates: Mapping[str, float | None]) -> list[str]:
    """Return one problem per unhealthy topic; ``None`` rate means never discovered."""
    problems = []
    for spec in specs:
        rate = rates.get(spec.topic)
        if rate is None:
            problems.append(f'{spec.topic}: not found')
        elif rate < spec.min_hz:
            problems.append(f'{spec.topic}: {rate:.1f} Hz < {spec.min_hz:g} Hz')
    return problems


class RateProbe(Node):
    """Subscribes to topics of any type and counts the messages that arrive."""

    def __init__(self) -> None:
        super().__init__('health_check')
        self.counts: dict[str, int] = {}

    def _count(self, topic: str) -> None:
        self.counts[topic] += 1

    def subscribe(self, topic: str) -> bool:
        """Subscribe if the topic exists; return whether it does."""
        types = dict(self.get_topic_names_and_types()).get(topic)
        if not types:
            return False
        self.counts[topic] = 0
        self.create_subscription(
            get_message(types[0]),
            topic,
            lambda _msg, t=topic: self._count(t),
            qos_profile_sensor_data,
            raw=True,  # counting only; skip deserialization
        )
        return True


def measure_rates(
    probe: RateProbe,
    executor: Executor,
    topics: Sequence[str],
    window_s: float,
    discover_timeout_s: float,
) -> dict[str, float | None]:
    """Discover ``topics``, then count messages for ``window_s`` seconds."""
    pending = list(topics)
    deadline = time.monotonic() + discover_timeout_s
    while pending and time.monotonic() < deadline:
        pending = [t for t in pending if not probe.subscribe(t)]
        executor.spin_once(timeout_sec=0.1)

    # Give new subscriptions a moment to match publishers before counting.
    settle = time.monotonic() + 0.5
    while time.monotonic() < settle:
        executor.spin_once(timeout_sec=0.05)
    for topic in probe.counts:
        probe.counts[topic] = 0

    end = time.monotonic() + window_s
    while time.monotonic() < end:
        executor.spin_once(timeout_sec=0.05)
    return {t: (probe.counts[t] / window_s if t in probe.counts else None) for t in topics}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('topics', nargs='*', help='/topic:min_hz pairs')
    parser.add_argument('--window', type=float, default=3.0, help='seconds to count')
    parser.add_argument('--timeout', type=float, default=5.0, help='seconds to find topics')
    args = parser.parse_args(argv)

    texts = args.topics or os.environ.get(ENV_TOPICS, '').split()
    if not texts:
        parser.error(f'no topics given and {ENV_TOPICS} is empty')
    specs = [parse_spec(t) for t in texts]

    rclpy.init()
    probe = RateProbe()
    executor = SingleThreadedExecutor()
    executor.add_node(probe)
    try:
        rates = measure_rates(probe, executor, [s.topic for s in specs], args.window, args.timeout)
    finally:
        probe.destroy_node()
        rclpy.try_shutdown()

    problems = evaluate(specs, rates)
    for spec in specs:
        rate = rates[spec.topic]
        shown = 'missing' if rate is None else f'{rate:.1f} Hz'
        print(f'{spec.topic}: {shown} (min {spec.min_hz:g} Hz)')
    if problems:
        print('UNHEALTHY: ' + '; '.join(problems), file=sys.stderr)
        sys.exit(1)
    print('healthy')
