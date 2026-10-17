# compose

Docker Compose files that run the images from `docker/`.

| File | Where | What it runs |
|---|---|---|
| `robot.yml` | Pi | Robot stack (`network_mode: host`, `restart: unless-stopped`) |
| `dev.yml` | Desktop | Dev container with the source tree mounted |
| `sim.yml` | Desktop | Gazebo TurtleBot3 simulation |
| `sleep.yml` | Desktop | Nightly sleep pipeline |

## robot.yml

Runs on the Pi from `/opt/engram/` next to a `.env` (see
`robot.env.example`). `robotctl` sets `ENGRAM_TAG` there and restarts the
stack; by hand it is:

```sh
docker compose -f robot.yml pull && docker compose -f robot.yml up -d
docker compose -f robot.yml ps      # robot shows (healthy) once topics flow
```

Two services share the robot image: `zenoh-router` (the `rmw_zenohd` router
every ROS node connects to) and `robot` (`ros2 launch engram_bringup
bringup.launch.py`). The robot service mounts `/dev` with cgroup rules for
serial and USB devices, so `/dev/opencr` and friends keep working across
replugs, and stores maps, episodes and config under `/srv/engram/` on the SSD.

A third service, `foxglove`, runs `foxglove_bridge` on port 8765 for
[Foxglove](https://foxglove.dev/); see `docs/foxglove/`.

Its healthcheck runs `engram_tools health_check` against
`ENGRAM_HEALTH_TOPICS` (default `/heartbeat:0.5` until the TurtleBot3 bringup
lands, then `/odom:10 /scan:4`).
