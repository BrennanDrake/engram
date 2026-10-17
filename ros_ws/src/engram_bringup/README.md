# engram_bringup

Launch files that start the robot stack, plus a `heartbeat` node that publishes
`engram alive #<n>` on `/heartbeat` (`std_msgs/String`). For now the heartbeat
is the whole stack; it also proves the CI pipeline end to end.

## Parameters

| Name | Default | Meaning |
|---|---|---|
| `robot_name` | `engram` | Name used in the heartbeat payload |
| `rate_hz` | `1.0` | Heartbeat rate |

## Run

```sh
cd ros_ws
colcon build --symlink-install --packages-select engram_bringup
source install/setup.bash
ros2 launch engram_bringup bringup.launch.py
ros2 topic echo /heartbeat   # in a second terminal
```

## Test locally

```sh
cd ros_ws
rosdep install --from-paths src --ignore-src -y
colcon build --packages-select engram_bringup
colcon test --packages-select engram_bringup
colcon test-result --verbose
```

The tests are:

- `test_heartbeat_unit.py`: plain pytest for the payload formatting.
- `test_heartbeat_launch.py`: a `launch_testing` test that starts the node and
  waits for a message on `/heartbeat`.
- `test_xmllint.py`: validates `package.xml` against the ROS schema.
