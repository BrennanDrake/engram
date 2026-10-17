# Desktop development image (amd64): base plus simulation, visualization and
# the tools CI uses, so lint and tests run here exactly as in CI.
ARG BASE_IMAGE=ghcr.io/brennandrake/engram/base:latest
FROM ${BASE_IMAGE}

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# hadolint ignore=DL3008
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    gdb \
    git \
    python3-pip \
    ros-dev-tools \
    ros-jazzy-nav2-rviz-plugins \
    ros-jazzy-rqt-graph \
    ros-jazzy-rqt-tf-tree \
    ros-jazzy-rviz2 \
    ros-jazzy-turtlebot3-gazebo \
    sudo \
  && rm -rf /var/lib/apt/lists/*

# Same pre-commit version as CI (.github/workflows/lint.yml).
RUN pip3 install --no-cache-dir --break-system-packages pre-commit==4.7.0

# The ubuntu base image already has user "ubuntu" with UID 1000, which matches
# the usual desktop user, so files created in the mounted repo stay yours.
RUN echo "ubuntu ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/ubuntu \
  && chmod 0440 /etc/sudoers.d/ubuntu \
  && echo "source /opt/ros/jazzy/setup.bash" >> /home/ubuntu/.bashrc

USER ubuntu
WORKDIR /workspaces/engram
