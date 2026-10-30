# Lima — rootless VMs for Molecule

Installs [Lima](https://lima-vm.io) from verified prebuilt release binaries
into `~/.local`, giving Molecule a real Linux VM on macOS and Linux with **no
sudo, no Vagrant, no privileged networking**.

## Why this exists

The Molecule test harness needs real VMs (systemd, kernel, reboot, sshd) on
every host. Vagrant's macOS installer requires root and a fixed `/opt/vagrant`
path; the `molecule-lima` adapter hardcodes privileged `socket_vmnet`
networking and host mounts. This topic installs Lima directly and drives it
through Molecule's built-in **delegated** driver with QEMU user-mode
networking — rootless on both hosts.

## What it does

- Downloads the pinned Lima release tarball and verifies it against the
  upstream `SHA256SUMS` (both the checksum list and the per-asset digest are
  required).
- Extracts into `~/.local` as the invoking user. No `become`, no sudo.
- Requires an existing QEMU (`qemu-system-aarch64` / `qemu-system-x86_64`) and
  checks the native accelerator: **HVF** on macOS, **KVM** on Linux.
- Teardown removes only the unpacked release files. It never touches `~/.lima`,
  Rancher Desktop, shared QEMU, or any VM.

## Usage

```bash
bash home/dotfiles/executable_run-role.sh lima            # install
bash home/dotfiles/executable_run-role.sh lima remove     # remove release files only
MOLECULE_SCENARIO=debian scripts/run-molecule.sh lima test   # full VM lifecycle
```

QEMU is a prerequisite (`topic_requires: [qemu]`), installed by the host's
package topic — the user-owned `qemu` formula on macOS, `qemu-system` on
Debian. This topic does not install or remove it.

## The Molecule scenario

`molecule/debian/` uses the delegated driver:

- `molecule/shared/create.yml` renders a rootless Lima template (QEMU,
  user-mode networking, no mounts, no container runtime, no forwarded SSH
  agent, digest-pinned Debian 12 cloud image), boots it, and writes Molecule's
  instance config from Lima's generated SSH key. Both this scenario and
  `apps/loreai/molecule/debian-lima` reference the same adapter through
  Molecule's native playbook paths. Topics keep their own preparation,
  converge, runtime verification and preservation checks.
- `converge.yml` installs this topic into a **temporary home** inside
  Molecule's state dir — never your real `~/.local` — and plants a sentinel.
- `side_effect.yml` runs the topic's remove lifecycle and asserts the sentinel
  and QEMU survive, then reinstalls so destroy can reach `limactl`.
- `verify.yml` checks, over SSH, that the guest is Debian 12 on QEMU running
  systemd with a working user manager.
- `molecule/shared/destroy.yml` stops only the scenario VM and its host agent,
  waits for their recorded PIDs to exit, then deletes the VM and temporary
  Lima home. A delete command alone is insufficient: Lima can return while
  those processes still reference the deleted directory.

All Lima state (`LIMA_HOME`) is isolated per scenario run. Because Lima's SSH
socket path must stay under `UNIX_PATH_MAX` (104), the Lima home lives at a
short `/tmp/lima-<sha1>` path (hashed from Molecule's unique ephemeral dir)
rather than the deep worktree path, and is removed on destroy. A run cannot
see or modify your other Lima instances. The instance name is kept short
(`lima-mol`) so the socket path fits within the limit.

## Upgrade

Bump `lima_release_tag` in `defaults/main.yaml` and refresh the
`lima_release_checksums` map from the new release's `SHA256SUMS`.

## Not covered

- macOS guests on Linux hosts.
- Nested KVM (a Linux guest cannot itself prove KVM).
- The `molecule-lima` adapter — evaluated and rejected 2026-10-28; it requires
  privileged shared networking. See DOT-264 for installing it as an optional
  dependency without switching this scenario to it.
