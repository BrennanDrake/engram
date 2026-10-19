#!/bin/bash
# Source ROS and our workspace, then run the given command.
set -e
# shellcheck source=/dev/null
source /opt/ros/jazzy/setup.bash
# shellcheck source=/dev/null
source /opt/engram/ros_ws/install/setup.bash
exec "$@"
