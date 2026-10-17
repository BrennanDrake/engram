# ADR-0005: Python 3.12 by default, C++17 where latency needs it

- **Status:** Proposed
- **Date:** 2026-10-17
- **Deciders:** Brennan

## Context

Most nodes are glue, behaviors and cognition logic, where development speed
matters more than raw speed. A few paths (sensor processing, control loops)
may need tighter latency. Most code is written by agents and reviewed by
Brennan, so strict, automated checks matter.

## Decision

- **Python 3.12** (Jazzy's version) for nodes and cognition by default.
- **C++17** only where a measured latency or CPU problem calls for it.
- Tooling, all run through pre-commit locally and in CI:
  ruff (lint and format), mypy `--strict`, clang-format, yamllint,
  check-xml plus `ament_xmllint` in `colcon test`, hadolint, shellcheck,
  markdownlint and codespell. cppcheck and clang-tidy are added with the
  first C++ code.
- Tests: pytest for pure Python, `colcon test` with `launch_testing` for ROS packages.

## Consequences

- One language for most of the codebase keeps reviews fast.
- mypy `--strict` needs a few relaxations because rclpy ships without type stubs.
- A C++ package needs a short justification in its PR.

## Alternatives considered

- **C++ by default** — faster, but slower to write and review for little gain on a Pi-class robot.
- **flake8/black/isort** — ruff replaces all three with one fast tool.
