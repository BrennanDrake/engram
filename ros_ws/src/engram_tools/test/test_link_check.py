import math
from collections.abc import Iterator

import pytest
import rclpy
from engram_tools.link_check import Echo, Probe, decode, encode, run_probe, summarize
from rclpy.executors import SingleThreadedExecutor


def test_encode_decode() -> None:
    assert decode(encode(42, 10)) == 42
    assert len(encode(7, 100)) == len('7 ') + 100


def test_summarize() -> None:
    stats = summarize(4, [3.0, 1.0, 2.0])
    assert stats.received == 3
    assert stats.loss_pct == 25.0
    assert (stats.rtt_min_ms, stats.rtt_median_ms, stats.rtt_max_ms) == (1.0, 2.0, 3.0)


def test_summarize_nothing_received() -> None:
    stats = summarize(5, [])
    assert stats.loss_pct == 100.0
    assert math.isnan(stats.rtt_median_ms)


@pytest.fixture
def ros() -> Iterator[None]:
    rclpy.init()
    yield
    rclpy.try_shutdown()


def test_probe_against_echo(ros: None) -> None:
    executor = SingleThreadedExecutor()
    echo = Echo()
    probe = Probe(payload_bytes=64)
    executor.add_node(echo)
    executor.add_node(probe)
    assert probe.wait_for_echo(executor, timeout_s=5.0)

    stats = run_probe(probe, executor, count=20, rate_hz=50.0)

    assert stats.sent == 20
    assert stats.received == 20
    assert stats.rtt_max_ms < 500.0
    echo.destroy_node()
    probe.destroy_node()
