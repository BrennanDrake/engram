# docker

Dockerfiles for the images the project builds. CI builds them in
[`images.yml`](../.github/workflows/images.yml) and pushes to GHCR under
`ghcr.io/brennandrake/engram/` ([ADR-0004](../docs/adr/0004-image-flow.md)).

| File | Image | Arch | Purpose |
|---|---|---|---|
| `base.Dockerfile` | `base:<date>-<sha>`, `base:latest` | amd64 + arm64 | ROS 2 Jazzy, TurtleBot3, Nav2, RealSense, Zenoh and other heavy dependencies. Rarely changes. |
| `robot.Dockerfile` | `robot:<sha>`, `robot:main` | arm64 | Our code on top of `base`. Runs on the Pi. |
| `dev.Dockerfile` | `dev:latest` | amd64 | `base` plus Gazebo, TurtleBot3 sim and RViz for the desktop. |
| `sleep.Dockerfile` | `sleep` | amd64 + GPU | Nightly sleep pipeline and training jobs on the desktop GPU (later epic). |

## When images build

- **`base`** is rebuilt only when `base.Dockerfile` (or the workflow) changes.
  On `main` each architecture builds on a native runner and the two are
  combined into one multi-arch tag. A PR that changes it builds it without
  pushing.
- **`robot`** builds on every PR that touches `ros_ws/src/` or its Dockerfile,
  on top of `base:latest`, and is pushed from `main` as `robot:<short sha>`.
- **`dev`** builds when its Dockerfile or `base` changes.

The job summary of each run shows the image sizes. Trivy scans `robot` on
`main` and reports HIGH/CRITICAL findings without failing the build.

## Building locally

```sh
docker build -f docker/base.Dockerfile -t engram-base:local .
```

The ROS apt repository must be reachable from the build.
