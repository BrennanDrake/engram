# compose

Docker Compose files that run the images from `docker/`.

| File | Where | What it runs |
|---|---|---|
| `robot.yml` | Pi | Robot stack (`network_mode: host`, `restart: unless-stopped`) |
| `dev.yml` | Desktop | Dev container with the source tree mounted |
| `sim.yml` | Desktop | Gazebo TurtleBot3 simulation |
| `sleep.yml` | Desktop | Nightly sleep pipeline |

Nothing is here yet; files arrive with epic E2.
