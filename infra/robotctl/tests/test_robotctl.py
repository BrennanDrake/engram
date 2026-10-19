import json
import sys
from collections.abc import Sequence
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from robotctl import (
    DeployError,
    Paths,
    PowerState,
    Robot,
    deploy_refusal,
    normalize_tag,
    previous_tag,
    push_tag,
    read_power_state,
    set_env_var,
)


def test_normalize_tag() -> None:
    assert normalize_tag('ABC1234def') == 'abc1234'
    with pytest.raises(DeployError):
        normalize_tag('main')


def test_push_tag_keeps_last_three_and_moves_redeploys_to_front() -> None:
    history: list[str] = []
    for tag in ['a', 'b', 'c', 'd']:
        history = push_tag(history, tag)
    assert history == ['b', 'c', 'd']
    assert push_tag(history, 'b') == ['c', 'd', 'b']


def test_previous_tag() -> None:
    assert previous_tag(['a', 'b']) == 'a'
    with pytest.raises(DeployError):
        previous_tag(['a'])


@pytest.mark.parametrize(
    ('state', 'force', 'allowed'),
    [
        (PowerState(docked=True, charging=True), False, True),
        (PowerState(docked=True, charging=False), False, False),
        (PowerState(docked=False, charging=False), False, False),
        (None, False, False),
        (None, True, True),
        (PowerState(docked=False, charging=False), True, True),
    ],
)
def test_deploy_refusal(state: PowerState | None, force: bool, allowed: bool) -> None:
    assert (deploy_refusal(state, force) is None) == allowed


def test_read_power_state(tmp_path: Path) -> None:
    path = tmp_path / 'power.json'
    assert read_power_state(path) is None
    path.write_text('{"docked": true, "charging": false}')
    assert read_power_state(path) == PowerState(docked=True, charging=False)
    path.write_text('not json')
    assert read_power_state(path) is None


def test_set_env_var_keeps_other_lines(tmp_path: Path) -> None:
    env = tmp_path / '.env'
    env.write_text('ENGRAM_REGISTRY=nas:3300/x\nENGRAM_TAG=old\n')
    set_env_var(env, 'ENGRAM_TAG', 'new1234')
    assert env.read_text() == 'ENGRAM_REGISTRY=nas:3300/x\nENGRAM_TAG=new1234\n'


class FakeDocker:
    """Records compose calls; health checks pass only for tags in ``healthy``."""

    def __init__(self, env: Path, healthy: set[str]) -> None:
        self.env = env
        self.healthy = healthy
        self.started: list[str] = []

    def __call__(self, cmd: Sequence[str]) -> int:
        tag = self.env.read_text().split('ENGRAM_TAG=')[1].strip()
        if 'up' in cmd:
            self.started.append(tag)
        if 'exec' in cmd:
            return 0 if tag in self.healthy else 1
        return 0


@pytest.fixture
def paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Paths:
    power = tmp_path / 'power.json'
    power.write_text('{"docked": true, "charging": true}')
    monkeypatch.setenv('ENGRAM_POWER_STATE', str(power))
    return Paths(tmp_path)


def make_robot(paths: Paths, healthy: set[str]) -> tuple[Robot, FakeDocker]:
    docker = FakeDocker(paths.env, healthy)
    robot = Robot(paths, runner=docker, health_timeout_s=0, sleep=lambda _s: None)
    return robot, docker


def log_results(paths: Paths) -> list[tuple[str, str]]:
    entries = [json.loads(line) for line in paths.log.read_text().splitlines()]
    return [(e['action'], e['result']) for e in entries]


def test_deploy_then_rollback(paths: Paths) -> None:
    robot, docker = make_robot(paths, healthy={'aaaaaaa', 'bbbbbbb'})
    robot.deploy('aaaaaaa')
    robot.deploy('bbbbbbb')
    robot.rollback()
    assert docker.started == ['aaaaaaa', 'bbbbbbb', 'aaaaaaa']
    assert json.loads(paths.history.read_text()) == ['aaaaaaa']
    assert log_results(paths)[-1] == ('rollback', 'ok')


def test_failed_health_check_reverts(paths: Paths) -> None:
    robot, docker = make_robot(paths, healthy={'aaaaaaa'})
    robot.deploy('aaaaaaa')
    with pytest.raises(DeployError, match='health check'):
        robot.deploy('bbbbbbb')
    assert docker.started == ['aaaaaaa', 'bbbbbbb', 'aaaaaaa']
    assert json.loads(paths.history.read_text()) == ['aaaaaaa']
    assert log_results(paths)[-2:] == [('deploy', 'failed'), ('revert', 'ok')]


def test_deploy_refused_when_not_docked(paths: Paths) -> None:
    paths.power.write_text('{"docked": false, "charging": false}')
    robot, docker = make_robot(paths, healthy={'aaaaaaa'})
    with pytest.raises(DeployError, match='docked'):
        robot.deploy('aaaaaaa')
    assert docker.started == []
    robot.deploy('aaaaaaa', force=True)
    assert docker.started == ['aaaaaaa']
