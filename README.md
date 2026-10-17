# engram

A home companion robot that simulates cognition: it learns from its day,
consolidates memories in a nightly "sleep", and forgets what no longer matters.

The platform is a widened TurtleBot3 (Raspberry Pi 4 on an SSD, OpenCR, LDS
lidar) with an SO-101 arm and a RealSense camera on a pan-tilt head, running
ROS 2 Jazzy in containers.

## Layout

| Path | Contents |
|---|---|
| [`docker/`](docker/) | Dockerfiles for the base, robot, dev and sleep images |
| [`compose/`](compose/) | Compose files for the robot, dev, sim and sleep stacks |
| [`ros_ws/src/`](ros_ws/) | ROS 2 packages (`engram_*`) |
| [`cognition/`](cognition/) | Memory store, experiments and the sleep pipeline (pure Python) |
| [`dock_firmware/`](dock_firmware/) | ESP32 charging dock controller |
| [`opencr_firmware/`](opencr_firmware/) | TurtleBot3 OpenCR firmware fork with safety additions |
| [`infra/`](infra/) | Pi provisioning, udev rules, `robotctl` |
| [`docs/`](docs/) | ADRs, safety checklists, runbooks |
| [`training/`](training/) | LeRobot configs and eval scripts |
| [`hardware/`](hardware/) | CAD, wiring, BOM, build photos |

## Quick start

Coming soon: the dev container and simulation arrive with epic E2.

## Contributing

Every change arrives as a small pull request that CI checks and a human
reviews. See `CONTRIBUTING.md` (coming next).

## License

[Apache-2.0](LICENSE)
