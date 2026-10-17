# Robot to desktop networking

ROS 2 traffic uses `rmw_zenoh` ([ADR-0003](adr/0003-rmw-zenoh.md)). Each
machine runs one Zenoh router; every node on that machine talks to its local
router, and the routers talk to each other.

| Machine | Router | Config |
|---|---|---|
| Robot | `zenoh-router` service in `compose/robot.yml` | rmw_zenoh defaults: listens on `tcp/[::]:7447` (LAN and Tailscale) |
| Desktop | `zenoh-router` service in `compose/dev.yml` | `compose/robot-link.yml` adds `connect/endpoints=["tcp/<robot>:7447"]` via `ZENOH_CONFIG_OVERRIDE` |

Start the desktop side linked to the robot:

```sh
ENGRAM_ROBOT_HOST=192.168.1.50 docker compose -f compose/dev.yml -f compose/robot-link.yml up -d
docker compose -f compose/dev.yml exec dev ros2 topic list   # should show the robot's topics
```

Over Tailscale, use the robot's Tailscale IP or MagicDNS name instead.

## Measuring the link

`engram_tools link_check` sends numbered pings that the robot echoes back,
and reports loss and round-trip time using only the desktop's clock.

```sh
# robot
docker compose -f /opt/engram/robot.yml exec robot /entrypoint.sh ros2 run engram_tools link_check echo
# desktop (dev container)
ros2 run engram_tools link_check probe --count 600 --rate 20 --payload 1000
ros2 run engram_tools link_check probe --count 600 --rate 20 --payload 1000 --best-effort
```

Run it from each room the robot will patrol (T2.3.4) and add the results to
the table below, then to [ADR-0003](adr/0003-rmw-zenoh.md) as its evidence.

| Date | Room / link | QoS | Payload | Loss | RTT median | RTT p95 |
|---|---|---|---|---|---|---|
| | | | | | | |
