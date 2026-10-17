# ros_ws

The ROS 2 Jazzy colcon workspace. Packages live in `src/` and are prefixed `engram_`.

Planned packages:

| Package | Purpose |
|---|---|
| `engram_bringup` | Launch files and parameters that start the robot |
| `engram_arm_bridge` | SO-101 arm interface |
| `engram_head` | RealSense pan-tilt control |
| `engram_face_ui` | Face and debug UI on the robot screen |
| `engram_docking` | Docking with the Nav2 docking server |
| `engram_semantic_map` | Semantic layer on top of the SLAM map |
| `engram_behaviors` | Patrols and other high-level behaviors |

Build and test (inside the dev container):

```sh
cd ros_ws
colcon build --symlink-install
colcon test && colcon test-result --verbose
```
