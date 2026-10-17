# infra

Infrastructure for the robot and the home lab.

- `robot/`: Ansible playbook that provisions the Pi from scratch (Ubuntu 24.04
  on the SSD, Docker, udev rules, Tailscale, Wi-Fi power save off).
- udev rules for `/dev/opencr`, `/dev/lidar`, `/dev/so101`, `/dev/head_servos`.
- `robotctl`: deploy, health-check and rollback tool used on the robot.

Secrets (registry tokens, Tailscale key, API keys) never go in this repo.
