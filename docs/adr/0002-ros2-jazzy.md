# ADR-0002: Use ROS 2 Jazzy on Ubuntu 24.04

- **Status:** Proposed
- **Date:** 2026-10-17
- **Deciders:** Brennan

## Context

The robot is a TurtleBot3 with an OpenCR board, LDS lidar and a Raspberry Pi 4.
The MVP needs mapping, Nav2 navigation and autonomous docking. ROS 2 Humble
(Ubuntu 22.04) is TurtleBot3's most-tested distro; Jazzy (Ubuntu 24.04) is the
current LTS, supported until May 2029.

## Decision

Use **ROS 2 Jazzy** on **Ubuntu 24.04** for the robot, the desktop dev image and CI.

## Consequences

- The Nav2 docking server (`opennav_docking`) is built in, so self-charging
  starts from a maintained component instead of custom code.
- Support runs to 2029, past the planned life of the MVP.
- TurtleBot3 Jazzy packages are newer and less battle-tested than Humble's;
  expect to fix or patch a few things in bringup.
- CI uses the official `ros:jazzy` images; Python is 3.12.

## Alternatives considered

- **Humble** — most-tested with TurtleBot3, but no built-in docking server and
  support ends in 2027.
- **Rolling** — moves too fast for a robot meant to run unattended.
