# Lima changelog

## Unreleased

- Add rootless, checksum-verified Lima installation for macOS and Debian.
- Use QEMU on both hosts, with explicit HVF/KVM capability checks.
- Keep teardown limited to the installed release files; preserve all VMs and shared QEMU.
- Add a delegated Molecule scenario with a digest-pinned Debian guest and no host mounts or privileged networking. The existing `molecule-lima` adapter was evaluated and rejected on 2026-10-28 because it requires privileged shared networking and mounts. Molecule's built-in delegated interface avoids a new driver dependency.
