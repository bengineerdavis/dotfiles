# Molecule host prerequisites

Run Molecule scenarios through `scripts/run-molecule.sh`. The root `mise.toml`
declares host packages, not the application's locked Python dependencies.
Vagrant 2.4.9 and `vagrant-libvirt` 0.12.2 are established by the existing
Linux harness; `vagrant-qemu` 0.7.0 is the measured macOS adapter.

```sh
mise trust ./mise.toml
mise bootstrap packages status
mise bootstrap packages apply --dry-run
mise bootstrap packages apply
```

Run mise as the normal user, never with sudo. Apt and the Vagrant macOS package
may elevate only their package installation; a non-interactive run that needs
a password fails and prints the command for the author. No global mise config,
tools, or services are changed by this project config.

## macOS

Install the user-local provider plugin:

```sh
vagrant plugin install vagrant-qemu
```

The Vagrant cask runs the vendor's package installer, which requires a sudo
password for `/opt/vagrant` and `/usr/local/bin/vagrant`. Mise invokes only
that installer with elevation; it does not run as root or elevate the other
tools. Ansible would have the same privilege requirement for this package.
Raw relocation of the DMG is not a supported rootless alternative: its bundled
helpers retain `/opt/vagrant` paths. The QEMU process and its user-mode VM
network need no root, libvirt daemon, or host network service.

## Debian/Linux

The declarations install distro Vagrant, `vagrant-libvirt`, QEMU, and libvirt.
The existing harness uses `qemu:///system` and KVM. Configure the system service
and grant the invoking user access through the normal host policy:

```sh
sudo systemctl enable --now libvirtd
sudo usermod -aG libvirt "$USER"
```

Start a fresh login session after changing group membership. `/dev/kvm` must
exist; use a KVM-capable host or enable nested KVM on a virtualized host. The
`vagrant-libvirt` plugin needs the distro package's Ruby/libvirt integration;
`libvirt-dev` is declared for plugin builds where required. This is the one
privileged system-service part of the setup.

## Verify and run

```sh
mise doctor project
MOLECULE_SCENARIO=debian scripts/run-molecule.sh loreai test
```

The wrapper selects QEMU and `cloud-image/debian-12` on macOS, libvirt and
`debian/bookworm64` on Linux. Override with `MOLECULE_VM_PROVIDER` and
`MOLECULE_VM_BOX` only for an intentional provider decision. The standard Lore
Debian scenario completed on macOS 2026-10-28 with four verifier tests and VM
teardown. Linux libvirt remains the established harness path, not a claim that
macOS guests run on Linux.

## Teardown

Destroy test VMs through the wrapper's `destroy` verb. Vagrant plugins and boxes
under `~/.vagrant.d` are user-local and may be shared by other projects; do not
remove them as part of deleting a declaration.

Deleting a package declaration does not uninstall the package. Never use a
blanket `brew autoremove`, `apt autoremove`, or package prune as this project's
uninstall method: QEMU, libvirt, and Vagrant may predate the project or serve
another one. Before removing anything, ask the author and record the package's
existing owner and other consumers.

If the author approves removing a package this setup installed, remove only
that package through its package manager. Vagrant's macOS cask has a package
installer, so preview and use its explicit uninstaller rather than assuming
mise's cask prune will remove it. Stop and disable a libvirt service only when
the author explicitly approves removing that shared host capability. Group
changes likewise require a deliberate host-policy decision.
