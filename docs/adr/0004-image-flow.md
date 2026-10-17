# ADR-0004: Build images in GitHub Actions, push to GHCR, mirror to the NAS

- **Status:** Proposed
- **Date:** 2026-10-17
- **Deciders:** Brennan

## Context

Robot code ships as container images. GitHub is the main repo and runs CI. The
robot should pull from the LAN (fast, works when the internet is down), but
GitHub-hosted runners cannot reach the NAS registry at 192.168.1.203. Gitea on
the NAS can run jobs inside the LAN.

## Decision

1. GitHub Actions builds `robot:<git-sha>` (arm64, native runner) and pushes it to **GHCR**.
2. A **Gitea Actions runner on the NAS** copies release tags from GHCR into the
   **NAS registry**.
3. The robot pulls **only from the NAS registry** (`robotctl deploy <sha>`).

## Consequences

- Hosted CI never needs a way into the home network.
- Deploys work during internet outages once the image is mirrored.
- Two registries to keep tidy; the NAS keeps only recent and released tags.
- The NAS registry is plain HTTP, so Docker on the robot needs it in
  `insecure-registries` (LAN only).

## Alternatives considered

- **Robot pulls from GHCR directly** — simpler, but deploys depend on the
  internet and every pull crosses the WAN.
- **Self-hosted GitHub runner on the LAN pushing to the NAS** — exposes a
  machine on the home network to jobs from GitHub.
- **Build on the NAS** — x86 N5105 can't build arm64 images at a useful speed.
