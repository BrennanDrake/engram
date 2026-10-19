# infra/robot

Ansible playbook that turns a fresh Ubuntu Server 24.04 (arm64) install on the
Pi's SSD into a robot host. Run it from the desktop over SSH; re-running it
changes nothing.

| Role | What it does |
|---|---|
| `base` | Base packages, admin user in `dialout`, journald capped at 500 MB, 2 GB swap file, Wi-Fi power save off |
| `docker` | Docker Engine + compose plugin from Docker's repo, user in `docker`, NAS registry in `insecure-registries`, log rotation |
| `time` | chrony, preferring the NAS as time source (ROS TF needs synced clocks) |
| `tailscale` | Tailscale installed and, if an auth key is given, joined |

Defaults live in `group_vars/all.yml`.

## Run it

```sh
pipx install ansible-core     # or: pip install --user ansible-core
cd infra/robot
cp inventory.example.yml inventory.yml   # set the Pi's IP; inventory.yml is git-ignored
ssh-copy-id ubuntu@<pi-ip>               # key login, no passwords
ansible-playbook site.yml --ask-become-pass
# First run only, to join the tailnet (the key is never committed):
ansible-playbook site.yml --ask-become-pass -e tailscale_authkey=tskey-auth-...
```

Log out and back in after the first run so the `docker` and `dialout` groups
apply. To check for drift without changing anything, add `--check --diff`.
