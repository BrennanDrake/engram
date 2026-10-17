#!/usr/bin/env python3
"""Deploy, roll back and inspect the robot stack on the Pi.

    robotctl deploy <sha> [--force]   pull robot:<sha>, restart, health-check, revert on failure
    robotctl rollback                 return to the previously deployed tag
    robotctl status                   show the deployed tag, history and containers
    robotctl logs [service]           follow container logs

Works on the compose project in ENGRAM_DIR (default /opt/engram: robot.yml and
.env). Keeps the last 3 tags in state/history.json and appends every action to
state/deploy.log (JSON lines). Standard library only, so it runs on a bare host.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

KEEP_TAGS = 3
SHA_RE = re.compile(r'^[0-9a-f]{7,40}$')
HEALTH_CMD = ['/entrypoint.sh', 'ros2', 'run', 'engram_tools', 'health_check']

Runner = Callable[[Sequence[str]], int]


class DeployError(Exception):
    """A deploy step failed; the message is shown to the user."""


def normalize_tag(sha: str) -> str:
    """Images are tagged with the 7-character short sha."""
    sha = sha.strip().lower()
    if not SHA_RE.match(sha):
        raise DeployError(f'not a git sha: {sha!r}')
    return sha[:7]


# --- tag history -----------------------------------------------------------


def push_tag(history: list[str], tag: str, keep: int = KEEP_TAGS) -> list[str]:
    """Return history with ``tag`` as the current (last) entry, at most ``keep`` long."""
    return ([t for t in history if t != tag] + [tag])[-keep:]


def previous_tag(history: list[str]) -> str:
    """The tag before the current one."""
    if len(history) < 2:
        raise DeployError('no previous tag to roll back to')
    return history[-2]


# --- power gate ------------------------------------------------------------


@dataclass(frozen=True)
class PowerState:
    docked: bool
    charging: bool


def read_power_state(path: Path) -> PowerState | None:
    """Read the state file the BMS node writes (E3); None when unavailable."""
    try:
        data = json.loads(path.read_text())
        return PowerState(docked=bool(data['docked']), charging=bool(data['charging']))
    except (OSError, ValueError, KeyError, TypeError):
        return None


def deploy_refusal(state: PowerState | None, force: bool) -> str | None:
    """Why a deploy must not start now, or None if it may."""
    if force:
        return None
    if state is None:
        return 'battery state unknown (no BMS node yet); use --force to deploy anyway'
    if not (state.docked and state.charging):
        return 'robot must be docked and charging to deploy; use --force to override'
    return None


# --- files -----------------------------------------------------------------


def set_env_var(path: Path, key: str, value: str) -> None:
    """Set ``key=value`` in a .env file, keeping every other line."""
    lines = path.read_text().splitlines() if path.exists() else []
    out = [line for line in lines if not line.startswith(f'{key}=')]
    out.append(f'{key}={value}')
    path.write_text('\n'.join(out) + '\n')


@dataclass
class Paths:
    root: Path

    @property
    def compose(self) -> Path:
        return self.root / 'robot.yml'

    @property
    def env(self) -> Path:
        return self.root / '.env'

    @property
    def history(self) -> Path:
        return self.root / 'state' / 'history.json'

    @property
    def log(self) -> Path:
        return self.root / 'state' / 'deploy.log'

    @property
    def power(self) -> Path:
        return Path(os.environ.get('ENGRAM_POWER_STATE', '/run/engram/power.json'))


def load_history(paths: Paths) -> list[str]:
    try:
        return [str(t) for t in json.loads(paths.history.read_text())]
    except (OSError, ValueError):
        return []


def save_history(paths: Paths, history: list[str]) -> None:
    paths.history.parent.mkdir(parents=True, exist_ok=True)
    paths.history.write_text(json.dumps(history) + '\n')


def log_event(paths: Paths, **fields: object) -> None:
    paths.log.parent.mkdir(parents=True, exist_ok=True)
    entry = {'time': datetime.now(UTC).isoformat(timespec='seconds'), **fields}
    with paths.log.open('a') as f:
        f.write(json.dumps(entry) + '\n')


# --- actions ---------------------------------------------------------------


def run(cmd: Sequence[str]) -> int:
    return subprocess.call(list(cmd))


class Robot:
    def __init__(
        self,
        paths: Paths,
        runner: Runner = run,
        health_timeout_s: float = 90.0,
        health_retry_s: float = 10.0,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.paths = paths
        self.runner = runner
        self.health_timeout_s = health_timeout_s
        self.health_retry_s = health_retry_s
        self.sleep = sleep

    def compose(self, *args: str) -> int:
        return self.runner(['docker', 'compose', '-f', str(self.paths.compose), *args])

    def start(self, tag: str) -> None:
        set_env_var(self.paths.env, 'ENGRAM_TAG', tag)
        if self.compose('pull', '--quiet') != 0:
            raise DeployError(f'could not pull robot:{tag}')
        if self.compose('up', '-d', '--remove-orphans') != 0:
            raise DeployError(f'could not start robot:{tag}')

    def healthy(self) -> bool:
        deadline = time.monotonic() + self.health_timeout_s
        while True:
            if self.compose('exec', '-T', 'robot', *HEALTH_CMD) == 0:
                return True
            if time.monotonic() + self.health_retry_s > deadline:
                return False
            self.sleep(self.health_retry_s)

    def deploy(self, sha: str, force: bool = False) -> None:
        tag = normalize_tag(sha)
        refusal = deploy_refusal(read_power_state(self.paths.power), force)
        if refusal:
            log_event(self.paths, action='deploy', tag=tag, result='refused', reason=refusal)
            raise DeployError(refusal)
        history = load_history(self.paths)
        previous = history[-1] if history else None
        try:
            self.start(tag)
            if not self.healthy():
                raise DeployError(f'robot:{tag} failed its health check')
        except DeployError as err:
            log_event(self.paths, action='deploy', tag=tag, result='failed', reason=str(err))
            if previous:
                print(f'{err}; reverting to {previous}', file=sys.stderr)
                self.start(previous)
                log_event(self.paths, action='revert', tag=previous, result='ok')
            raise
        save_history(self.paths, push_tag(history, tag))
        log_event(self.paths, action='deploy', tag=tag, result='ok', forced=force)
        print(f'robot:{tag} deployed and healthy')

    def rollback(self) -> None:
        history = load_history(self.paths)
        tag = previous_tag(history)
        self.start(tag)
        ok = self.healthy()
        save_history(self.paths, history[:-1])
        log_event(self.paths, action='rollback', tag=tag, result='ok' if ok else 'unhealthy')
        if not ok:
            raise DeployError(f'rolled back to robot:{tag}, but it failed its health check')
        print(f'rolled back to robot:{tag}')

    def status(self) -> None:
        history = load_history(self.paths)
        print(f'deployed: {history[-1] if history else "nothing yet"}')
        print(f'history:  {" ".join(reversed(history)) or "-"} (newest first)')
        self.compose('ps')


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog='robotctl', description='Deploy the robot stack.')
    sub = parser.add_subparsers(dest='command', required=True)
    deploy = sub.add_parser('deploy', help='deploy robot:<sha>')
    deploy.add_argument('sha')
    deploy.add_argument('--force', action='store_true', help='skip the docked-and-charging check')
    sub.add_parser('rollback', help='return to the previous tag')
    sub.add_parser('status', help='show what is deployed')
    logs = sub.add_parser('logs', help='follow container logs')
    logs.add_argument('service', nargs='?', default='robot')
    args = parser.parse_args(argv)

    robot = Robot(Paths(Path(os.environ.get('ENGRAM_DIR', '/opt/engram'))))
    try:
        if args.command == 'deploy':
            robot.deploy(args.sha, force=args.force)
        elif args.command == 'rollback':
            robot.rollback()
        elif args.command == 'status':
            robot.status()
        else:
            return robot.compose('logs', '-f', '--tail', '100', args.service)
    except DeployError as err:
        print(f'robotctl: {err}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
