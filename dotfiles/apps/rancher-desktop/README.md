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

## Links

- [project website](https://rancherdesktop.io/) 
- [Linux install docs](https://docs.rancherdesktop.io/getting-started/installation/#linux) 
- [project git repository](https://github.com/rancher-sandbox/rancher-desktop/) 
- [homebrew package](https://formulae.brew.sh/cask/rancher#default) 
- [Docker Desktop Alternatives for M1 Mac](https://alex-moss.medium.com/docker-desktop-alternatives-for-m1-mac-918a2dcda10)


See more in https://github.com/holman/dotfiles