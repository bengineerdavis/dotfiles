### Added

- Molecule's Lore Debian scenario runs in a real Debian 12 ARM64 VM on macOS
  through Vagrant's QEMU provider; the Linux libvirt/KVM path remains.
- Root `mise.toml` declares per-host VM packages and working-condition checks.
  Host setup documents the privileged Vagrant/Linux libvirt steps and opt-in
  teardown that preserves shared packages.

### Fixed

- Preserve the post-reboot linger baseline outside `/tmp` in the Debian VM
  lifecycle test.
