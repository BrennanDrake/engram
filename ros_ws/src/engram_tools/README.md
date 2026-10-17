# engram_tools

Operational tools for the robot.

## health_check

Exits 0 when every given topic publishes at or above its minimum rate, 1
otherwise. Used by the robot container's Docker healthcheck and by
`robotctl deploy`.

```sh
ros2 run engram_tools health_check /odom:10 /scan:4 --window 3
ENGRAM_HEALTH_TOPICS="/odom:10 /scan:4" ros2 run engram_tools health_check
```

It subscribes with sensor-data QoS (best effort), which matches both reliable
and best-effort publishers, and counts raw messages without deserializing them.

## link_check

Round-trip latency and loss between the robot and the desktop; see
[docs/networking.md](../../../docs/networking.md).

```sh
ros2 run engram_tools link_check echo                      # on the robot
ros2 run engram_tools link_check probe --count 200 --rate 20   # on the desktop
```
