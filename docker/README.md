# docker

Dockerfiles for the images the project builds.

| File | Image | Arch | Purpose |
|---|---|---|---|
| `base.Dockerfile` | `base` | arm64 | ROS 2 Jazzy, TurtleBot3, RealSense and other heavy dependencies. Rarely changes. |
| `robot.Dockerfile` | `robot:<git-sha>` | arm64 | Our code on top of `base`. Runs on the Pi. |
| `dev.Dockerfile` | `dev` | x86 | Same ROS setup plus Gazebo (TurtleBot3 sim) for the desktop. |
| `sleep.Dockerfile` | `sleep` | x86 + GPU | Nightly sleep pipeline and training jobs on the desktop GPU. |

Nothing is here yet; images arrive with epic E2.
