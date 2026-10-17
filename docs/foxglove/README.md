# Foxglove

The robot runs `foxglove_bridge` (service `foxglove` in `compose/robot.yml`) on
port 8765.

1. In Foxglove, **Open connection > Foxglove WebSocket**, URL
   `ws://<robot IP or Tailscale name>:8765`.
2. **Layouts > Import from file** and pick `engram.json` from this folder: a 3D
   view of `/scan`, `/odom` and `/map` following `base_link`, a speed plot from
   `/odom`, the `/heartbeat` messages and the robot's log.

`/scan` and `/odom` appear once the TurtleBot3 bringup runs (E4). When you
change the layout, export it over `engram.json` so it stays in the repo.
