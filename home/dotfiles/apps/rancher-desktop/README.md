# {{ app_name }} App Module

_Template directory for dotfile or tool user/system tool config_

Welcome to my {{ app_name }} app module in my local machine provisioning setup!

## Platforms

- **macOS** — installed via Homebrew Cask as the `docker` provider. This is the
  default and runs as part of the main playbook (`--tags provision`/`upgrade`).
  Note: Homebrew is blocked from auto-upgrading the cask (its upgrade shells out
  to `sudo`); Rancher Desktop keeps itself current via its own updater. See
  `apps/homebrew/defaults/main.yaml` (`homebrew_upgrade_cask_exclude`).
- **Linux** — not part of the main playbook (this topic is Darwin-only there).
  The Linux `docker` provider is Docker Engine (`apps/docker`); Rancher Desktop
  here is an optional GUI "playground". Running the standalone runner on a Linux
  host is itself the opt-in (needs `-K` so Ansible can supply the sudo password
  for the apt steps):

  ```sh
  ansible-playbook apps/rancher-desktop/playbook.yaml --tags install -K
  ```

  First-run (manual): ensure KVM access (be in the `kvm` group / have
  `/dev/kvm`), set up a `pass` credential store, then launch the GUI from your
  desktop's app menu. Remove with:

  ```sh
  ansible-playbook apps/rancher-desktop/playbook.yaml --tags remove -K
  ```

## Running as a service

Rancher Desktop is a GUI app that happens to carry a container engine. This
topic inverts that emphasis: the engine runs at login with no window, and
`docker` / `docker compose` are the interface. You should never need to open the
app.

| Setting | Value | Why |
|---|---|---|
| `application.autoStart` | `true` | engine is up before you need it |
| `application.startInBackground` | `true` | no window on login |
| `application.window.quitOnClose` | `false` | closing the window leaves the engine running |

That last one is easy to get backwards — `true` terminates the whole app when
the window closes, which is exactly what a service must not do. Set by
`tasks/service-mode.yaml` via `rdctl`, Rancher's own CLI, so the app persists
the change itself.

### Bringing containers up and down

Through the container CLIs, not through Rancher:

```sh
docker ps                     # what is running
docker compose up -d          # bring a stack up
docker compose down           # and back down
docker run --rm …             # one-shot, removed on exit
```

`docker compose` is the v2 plugin bundled with Rancher (`~/.rd/bin/docker-compose`),
not a separate install. `podman` and `nerdctl` are **not** installed — Rancher
provides the `moby` (dockerd) engine here, and podman would be a second,
independent engine rather than another CLI over this one.

To stop the engine entirely: `rdctl shutdown`. It will come back at next login.

### Kubernetes is a separate, standing cost

`kubernetes.enabled` is **on**, which runs a full control plane — on this
machine that is five permanently resident containers (coredns, traefik,
metrics-server, local-path-provisioner and their pause containers) that exist
whether or not you are using Kubernetes.

This topic deliberately does **not** change it. Running the engine as a service
is about how the app starts; whether you pay for a control plane is a decision
about what you use the machine for. If you only want containers:

```sh
rdctl set --kubernetes.enabled=false
```

Everything in the section above continues to work without it.

## Links

- [project website](https://rancherdesktop.io/) 
- [Linux install docs](https://docs.rancherdesktop.io/getting-started/installation/#linux) 
- [project git repository](https://github.com/rancher-sandbox/rancher-desktop/) 
- [homebrew package](https://formulae.brew.sh/cask/rancher#default) 
- [Docker Desktop Alternatives for M1 Mac](https://alex-moss.medium.com/docker-desktop-alternatives-for-m1-mac-918a2dcda10)


See more in https://github.com/holman/dotfiles