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

Sliders for the six arm joints come up next to RViz. Launch arguments:

| Argument | Default | Meaning |
|---|---|---|
| `top_deck` | `true` | Add the extra deck and stand the arm on it; `false` puts the arm on the Waffle top plate |
| `deck_spacing` | `0.055` | Waffle top plate surface to deck surface [m] |
| `arm_x` | empty | Arm `base_link` x in Waffle `base_link` [m]; empty uses the layout's default |
| `gui` | `true` | Joint sliders |
| `rviz` | `true` | Start RViz |

## Files

| Path | What |
|---|---|
| `urdf/engram.urdf.xacro` | Top level: includes the Waffle and mounts the arm |
| `urdf/so101_follower.urdf.xacro` | SO-101 follower as a macro (`prefix`, `parent`, `origin`) |
| `meshes/so101/` | SO-101 meshes |
| `meshes/waffle/waffle_plate.stl` | One Waffle plate, for the top deck |
| `launch/display.launch.py` | `robot_state_publisher` + joint sliders + RViz |

The SO-101 macro and meshes come from
[SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100)
`Simulation/SO101/so101_new_calib.urdf` (Apache-2.0). Link and joint names
take a prefix (`arm_` here), and transmissions were removed. Meshes over
15k triangles were decimated to 15k so each stays under the repo's 1 MB file
limit; `base_so101_v2.stl` (the part with the mounting holes) is untouched.

## Layout

All in Waffle `base_link`, which sits on the wheel axle with +x forward.

### With the top deck (default)

The LDS stays on the Waffle top plate, which becomes the level below the deck.
`top_deck_link` is the deck's top surface, centred over the Waffle footprint
(x = -0.064 m). The deck uses the same plate as the Waffle's other levels,
cut from `waffle_base.stl` into `meshes/waffle/waffle_plate.stl`; its
standoffs are not modelled yet. `deck_spacing` is top surface to top surface,
like the Waffle's own levels, which are 45 mm apart.

| Item | Value | Why |
|---|---|---|
| Deck surface | z = 0.0915 + `deck_spacing` | 0.1465 m at the default |
| Deck to LDS clearance | 6.5 mm at the default | LDS top is at z = 0.131 m; the ribbed plate's underside is 9 mm below its surface. Stock 45 mm spacing would put the deck 3.5 mm into the LDS; 80 mm (35 + 45 mm spacers) leaves 31.5 mm |
| Arm x | -0.1028 m | Puts the pan axis over the robot's centre and leaves about 110 mm of deck ahead of the arm base for the pan-tilt camera |
| Arm y | 0 | Centred |

### Without the deck (`top_deck:=false`)

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

Known overlaps in the no-deck layout: the arm base overhangs the front edge of
the top plate by about 13 mm, and it overlaps the stock R200 camera at the
front of the Waffle, which engram replaces with the pan-tilt RealSense.
