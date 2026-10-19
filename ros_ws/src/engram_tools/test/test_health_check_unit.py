import pytest
from engram_tools.health_check import TopicSpec, evaluate, parse_spec


def test_parse_spec() -> None:
    assert parse_spec('/odom:10') == TopicSpec('/odom', 10.0)
    assert parse_spec('/ns/scan:4.5') == TopicSpec('/ns/scan', 4.5)


@pytest.mark.parametrize('text', ['/odom', ':10', '/odom:fast', '/odom:-1'])
def test_parse_spec_rejects_bad_input(text: str) -> None:
    with pytest.raises(ValueError):
        parse_spec(text)


def test_evaluate() -> None:
    specs = [TopicSpec('/odom', 10), TopicSpec('/scan', 4), TopicSpec('/imu', 50)]
    rates = {'/odom': 20.0, '/scan': 3.0, '/imu': None}
    assert evaluate(specs, rates) == ['/scan: 3.0 Hz < 4 Hz', '/imu: not found']


def test_evaluate_all_healthy() -> None:
    assert evaluate([TopicSpec('/odom', 10)], {'/odom': 10.0}) == []
