import pytest
from engram_bringup.heartbeat import format_heartbeat


def test_format_heartbeat() -> None:
    assert format_heartbeat('engram', 0) == 'engram alive #0'
    assert format_heartbeat('kip', 42) == 'kip alive #42'


def test_format_heartbeat_rejects_negative_count() -> None:
    with pytest.raises(ValueError):
        format_heartbeat('engram', -1)
