# registry-sync

Copies image tags from GHCR into the NAS's Gitea registry so the robot pulls
over the LAN ([ADR-0004](../../docs/adr/0004-image-flow.md)). The workflow is
[`.gitea/workflows/sync-images.yml`](../../.gitea/workflows/sync-images.yml); it
runs on the NAS's Gitea runner every 10 minutes, on each mirrored push to
`main`, and on demand. GitHub ignores `.gitea/`.

What gets copied:

| Image | Tags copied once | Tags re-copied when their digest changes |
|---|---|---|
| `robot` | `<short sha>` | `main` |
| `base` | `<date>-<sha>` (multi-arch) | `latest` |

## One-time setup (on the NAS)

1. The Gitea runner is online (`infra/gitea/` README, step 9).
2. In the Gitea `engram` repository, **Settings > Actions > Variables**:

   | Variable | Example |
   |---|---|
   | `NAS_REGISTRY_PREFIX` | `192.168.1.203:3300/carvinaxe3` |
   | `NAS_REGISTRY_USER` | `carvinaxe3` |
   | `GHCR_USER` | `BrennanDrake` |

3. **Settings > Actions > Secrets** (never in this repo):
   - `GHCR_READ_TOKEN`: a GitHub token with only `read:packages`.
   - `NAS_REGISTRY_TOKEN`: a Gitea access token with `write:package`.
4. Run the workflow once by hand (**Actions > sync-images > Run workflow**) and
   check the log ends with `done: N tag(s) copied`.

If Actions do not run in the pull-mirrored repository (mirrors can be
restricted), create a small regular Gitea repository holding only
`.gitea/workflows/sync-images.yml` and this script, with the same variables
and secrets.

## Running by hand

```sh
crane auth login ghcr.io -u <github user> --password-stdin
crane auth login 192.168.1.203:3300 -u <gitea user> --password-stdin
infra/registry-sync/sync-images.sh ghcr.io/brennandrake/engram 192.168.1.203:3300/carvinaxe3
```
