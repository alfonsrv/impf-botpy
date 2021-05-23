# Docker Setup 🐋

## Requirements

* Docker
* `docker-compose`

## Setup

* `mv docker/docker-compose.yml .`
* Configure `VNC_PASSWORD` environment variable in `docker-compose.yml`
* `docker-compose up`

The Container is always built during runtime - there is no DockerHub repo to pull images from directly.

## Administration

The container exposes port `6901 (noVNC)`. If you also want to expose `5901 (VNC)` to use your favorite VNC client, 
add `-localhost no :1` to the `vncserver` command in the Dockerfile.

You can access the container's Xserver (Desktop) using VNC or via noVNC, which is essentially a web-based VNC client.
Simply connect to `<ip-addr>:6901` and enter the `VNC_PASSWORD` previously specified. The preconfigured password is
`CHANGEME`.

Reminder: If you're running Docker on a VPS or another remote system, you can forward the port after setting 
`AllowTcpForwarding yes` and `GatewayPorts yes` in your `/etc/ssh/sshd_config` and restarting your ssh server. Forward 
the remote port via: `ssh -L 6901:localhost:6901 root@domain.tld` and access the VNC interface on `127.0.0.1:6901` in 
your web browser.

I highly recommend helping the bot getting to the appointment booking screen manually. For some reason it works when
doing it manually but barely works when letting the bot do it itself.

## Support

⚠ Things may break in Docker environments, especially when using Concurrency. Please note that there is **NO** support
for Docker environments and no in-depth technical troubleshooting. If you're running Docker, you're technically capable 
yourself. Hope you understand. Pull requests welcome.