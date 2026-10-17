# compose

Docker Compose files that run the images from `docker/`.

| File | Where | What it runs |
|---|---|---|
| `robot.yml` | Pi | Robot stack (`network_mode: host`, `restart: unless-stopped`) |
| `dev.yml` | Desktop | Dev container with the source tree mounted |
| `sim.yml` | Desktop | Gazebo TurtleBot3 simulation |
| `sleep.yml` | Desktop | Nightly sleep pipeline |

Nothing is here yet; files arrive with epic E2.

## dev.yml and sim.yml (desktop)

Both use the `dev` image and need the
[NVIDIA container toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
for the GPU.

```sh
xhost +local:docker                                   # once per login, for RViz/Gazebo windows
docker compose -f compose/sim.yml up                  # router + dev shell + Gazebo house world
docker compose -f compose/dev.yml exec dev bash       # a shell next to it; try `rviz2`
```

`dev.yml` alone gives the shell and a Zenoh router without the simulator.
The sim uses the stock TurtleBot3 Burger and house world until our widened
base has its own URDF.
