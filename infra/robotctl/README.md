# robotctl

Deploys the robot stack on the Pi (`compose/robot.yml`) and rolls it back.
Standard-library Python only.

```sh
robotctl deploy <sha> [--force]   # pull robot:<sha>, restart, health-check, revert on failure
robotctl rollback                 # back to the previous tag
robotctl status                   # deployed tag, last 3 tags, containers
robotctl logs [service]           # follow logs (default: robot)
```

- `<sha>` is a git sha of `main` (7 to 40 hex characters); images are tagged
  with the first 7.
- **Deploys need the robot docked and charging.** robotctl reads
  `/run/engram/power.json` (`{"docked": true, "charging": true}`), which the BMS
  node will write once E3 lands. Until then every deploy needs `--force`.
- After `docker compose up` it runs `engram_tools health_check` inside the robot
  container, retrying for up to 90 s. If the check never passes it restarts the
  previously deployed tag and exits 1.
- State lives in `/opt/engram/state/`: `history.json` (last 3 tags, newest
  last) and `deploy.log` (one JSON line per deploy, revert or rollback).

## Install on the robot

```sh
sudo mkdir -p /opt/engram && sudo chown "$USER" /opt/engram
cp compose/robot.yml /opt/engram/
cp compose/robot.env.example /opt/engram/.env    # set ENGRAM_REGISTRY
sudo install -m 755 infra/robotctl/robotctl.py /usr/local/bin/robotctl
```

`ENGRAM_DIR` and `ENGRAM_POWER_STATE` override the two paths.

## Tests

```sh
pytest infra/robotctl
```
