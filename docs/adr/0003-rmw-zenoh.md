# ADR-0003: Use rmw_zenoh between robot and desktop

- **Status:** Proposed
- **Date:** 2026-10-17
- **Deciders:** Brennan

## Context

The robot talks to the desktop (heavy inference, debugging, Foxglove) over home
Wi-Fi. The default DDS middleware uses multicast discovery, which is unreliable
and chatty on Wi-Fi. Options are DDS tuned for unicast (Cyclone or Fast DDS with
peer lists or a discovery server) or Zenoh, which is a Tier 1 RMW in Jazzy.

## Decision

Use **`rmw_zenoh_cpp`** on all machines, with the **Zenoh router running on the
robot** so the robot keeps working when the desktop is off.

## Consequences

- No multicast on Wi-Fi; discovery goes through the router on the robot.
- The router is one more process to supervise; it runs in the robot compose
  stack with `restart: unless-stopped`.
- Every machine and container must set `RMW_IMPLEMENTATION=rmw_zenoh_cpp`;
  mixing RMWs on one ROS graph does not work.
- Some third-party tools assume DDS. If one breaks, fall back per tool rather
  than switching the whole robot.

## Alternatives considered

- **Cyclone DDS with unicast peers** — proven, but peer lists must be kept in
  sync by hand and tuning is fiddly.
- **Fast DDS discovery server** — workable, but still DDS traffic patterns over
  Wi-Fi and more config surface.
