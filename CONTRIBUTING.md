# Contributing to engram

Every change reaches `main` through a small pull request that CI has checked
and a human has reviewed. This applies equally to people and to AI agents.

## Workflow

1. Pick or open an issue. Work is tracked as epics (milestones), stories
   (issues) and tasks (sub-issues).
2. Create a branch from `main`:

   | Prefix | For |
   |---|---|
   | `feat/` | New behavior |
   | `fix/` | Bug fixes |
   | `chore/` | Tooling, CI, dependencies, repo housekeeping |
   | `docs/` | Documentation and ADRs only |

   Add the issue number when there is one, for example `feat/42-teleop-node`.
3. Commit using [Conventional Commits](https://www.conventionalcommits.org/):
   `type(scope): summary`, for example `feat(bringup): add lidar launch file`.
   Types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `ci`, `build`.
4. Open a pull request against `main` and fill in the template. Link the issue
   with `Closes #42` (or `Refs #42` when the PR is only part of the issue).
5. CI must be green and the code owner must approve. PRs are **squash-merged**,
   so the PR title becomes the commit on `main` and must follow Conventional
   Commits too.

## Pull request size and scope

- **One concern per PR.** Do not mix a refactor, a feature and a dependency bump.
- Aim for **under ~400 changed lines**. Split larger work into a sequence of
  PRs that each leave `main` working.
- New code comes with tests. Update docs and READMEs when behavior changes.
- If the change alters an architecture decision, add or update an ADR in
  `docs/adr/` and link it from the PR.
- Hands-on work (wiring, printing, measurements) is recorded with photos and
  numbers under `hardware/` or `docs/`.

## Local setup

The quality gates run through [pre-commit](https://pre-commit.com/), the same
way locally and in CI. Once the configuration lands (story S1.2):

```sh
pipx install pre-commit      # or: pip install --user pre-commit
pre-commit install           # run the hooks on every commit
pre-commit run --all-files   # run everything once
```

Build and test ROS packages inside the dev container (arrives with epic E2):

```sh
cd ros_ws
colcon build --symlink-install
colcon test && colcon test-result --verbose
```

Pure-Python code in `cognition/` is tested with `pytest`.

## Secrets

Never commit secrets: registry tokens, Tailscale keys, API keys and Wi-Fi
credentials live in CI secrets or on the host. `.env` files are ignored.
