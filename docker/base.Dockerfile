# Heavy, slow-changing dependencies shared by the robot and dev images.
# Rebuilt only when this file changes; tagged base:<date>-<sha> and base:latest.
FROM ros:jazzy-ros-base

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Versions float with the ROS apt repo; the image tag pins what was built.
# hadolint ignore=DL3008
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    ros-jazzy-apriltag-ros \
    ros-jazzy-foxglove-bridge \
    ros-jazzy-laser-filters \
    ros-jazzy-nav2-bringup \
    ros-jazzy-navigation2 \
    ros-jazzy-opennav-docking \
    ros-jazzy-realsense2-camera \
    ros-jazzy-rmw-zenoh-cpp \
    ros-jazzy-robot-localization \
    ros-jazzy-slam-toolbox \
    ros-jazzy-turtlebot3-bringup \
    ros-jazzy-turtlebot3-description \
    ros-jazzy-turtlebot3-msgs \
  && rm -rf /var/lib/apt/lists/*

# Refresh rosdep once here so child images can resolve keys without network surprises.
RUN rosdep update --rosdistro jazzy

ENV RMW_IMPLEMENTATION=rmw_zenoh_cpp \
    TURTLEBOT3_MODEL=burger
