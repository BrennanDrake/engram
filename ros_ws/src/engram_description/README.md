# engram_description

URDF for the engram robot: the stock TurtleBot3 Waffle from
`turtlebot3_description` with an SO-101 follower arm bolted to the top plate,
plus a launch file that shows it in RViz.

## View it

```sh
cd ros_ws
rosdep install --from-paths src --ignore-src -y   # pulls turtlebot3_description
colcon build --symlink-install --packages-select engram_description
source install/setup.bash
ros2 launch engram_description display.launch.py
```

Sliders for the six arm joints come up next to RViz. Pass `gui:=false` to drop
the sliders, `rviz:=false` to run only `robot_state_publisher`, or
`arm_x:=<metres>` to slide the arm along the robot while checking hole alignment.

## Files

| Path | What |
|---|---|
| `urdf/engram.urdf.xacro` | Top level: includes the Waffle and mounts the arm |
| `urdf/so101_follower.urdf.xacro` | SO-101 follower as a macro (`prefix`, `parent`, `origin`) |
| `meshes/so101/` | SO-101 meshes |
| `launch/display.launch.py` | `robot_state_publisher` + joint sliders + RViz |

The SO-101 macro and meshes come from
[SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100)
`Simulation/SO101/so101_new_calib.urdf` (Apache-2.0). Link and joint names
take a prefix (`arm_` here), and transmissions were removed. Meshes over
15k triangles were decimated to 15k so each stays under the repo's 1 MB file
limit; `base_so101_v2.stl` (the part with the mounting holes) is untouched.

## Arm placement

All in Waffle `base_link`, which sits on the wheel axle with +x forward.

| Axis | Value | Why |
|---|---|---|
| y | 0 | The arm base is symmetric about its own x axis, so this centres it |
| z | 0.0939 m | Waffle top plate surface is 0.0915 m; the arm's `base_link` is 2.4 mm above the underside of its base |
| x | 0.0222 m (`arm_x`) | Arm base spans x = -22.4 to +64.6 mm in its own frame. The LDS ends at x = -3.2 mm, so this leaves 3 mm clearance behind the arm. The pan axis lands at x = 61 mm |
| yaw | 0 | Arm reaches forward |

Hole pattern of the arm base, measured from `base_so101_v2.stl`, in the arm's
`base_link` frame (mm):

- 4 main holes, 5 mm: (x, y) = (55.6, ±27.8) and (-14.2, ±31.8)
- 2 more 5 mm holes at (-1.1, ±15.4)
- Diamond cutouts about 5 x 8.7 mm on a lattice across the base, e.g.
  (16.7, ±15.6), (7.5, ±21.2), (15.3, ±25.1), (24.3, ±19.4), (33.0, ±24.1)

The plate mesh in `turtlebot3_description` does not model the Waffle plate's
hole grid, so `arm_x` is not yet checked against real holes. Once the bolts
are in, set `arm_x` to the measured distance from the wheel axle line to the
arm's `base_link` (pan axis minus 38.8 mm) and update the default.

Known overlaps in the stock model: the arm base overhangs the front edge of
the top plate by about 13 mm, and it overlaps the stock R200 camera at the
front of the Waffle, which engram replaces with the pan-tilt RealSense.
