# Our ROS packages on top of base. Runs on the Pi (arm64), tagged robot:<short sha>.
ARG BASE_IMAGE=ghcr.io/brennandrake/engram/base:latest
FROM ${BASE_IMAGE}

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

WORKDIR /opt/engram/ros_ws
COPY ros_ws/src ./src

# rosdep picks the versions; base already carries the heavy dependencies.
RUN apt-get update \
  && rosdep install --from-paths src --ignore-src -y -q --rosdistro jazzy \
  && rm -rf /var/lib/apt/lists/*

RUN source /opt/ros/jazzy/setup.bash \
  && colcon build --merge-install --event-handlers console_cohesion+ \
  && rm -rf build log

COPY docker/entrypoint.sh /entrypoint.sh

# Lets running code (and later the debug UI) report which commit it is.
ARG GIT_SHA=unknown
ENV ENGRAM_GIT_SHA=${GIT_SHA}

ENTRYPOINT ["/entrypoint.sh"]
CMD ["ros2", "launch", "engram_bringup", "bringup.launch.py"]
