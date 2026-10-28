"""The Molecule host bootstrap's configuration contract.

The VM and package installs are external integration checks. These tests
inspect only the declarations and checks that a fresh host must expose.
"""

from pathlib import Path
import tomllib


ROOT = Path(__file__).parents[2]


def test_molecule_host_declares_provider_specific_packages():
    config = tomllib.loads((ROOT / "mise.toml").read_text())
    packages = config["bootstrap"]["packages"]
    assert packages["brew-cask:vagrant"] == {"os": "macos"}
    assert packages["brew:qemu"] == {"os": "macos"}
    for name in (
        "apt:vagrant",
        "apt:vagrant-libvirt",
        "apt:qemu-system",
        "apt:libvirt-daemon-system",
        "apt:libvirt-dev",
    ):
        assert packages[name] == {"os": "linux"}
    assert not (set(config) & {"tools", "env"}), "host packages are not project tools"


def test_molecule_host_checks_fail_on_missing_provider_capability():
    config = tomllib.loads((ROOT / "mise.toml").read_text())
    checks = config["doctor"]["checks"]
    assert "vagrant-qemu" in checks["molecule-vagrant-provider"]["run"]
    assert "vagrant-libvirt" in checks["molecule-vagrant-provider"]["run"]
    libvirt = checks["molecule-libvirt"]
    assert libvirt["os"] == ["linux"]
    assert "qemu:///system" in libvirt["run"]
    assert "/dev/kvm" in libvirt["run"]


def test_molecule_host_teardown_does_not_remove_shared_packages():
    guide = (ROOT / "dotfiles/docs/MOLECULE-HOSTS.md").read_text()
    assert "Never use a\nblanket" in guide
    assert "ask the author" in guide
    assert "Deleting a package declaration does not uninstall" in guide
    assert "Raw relocation" in guide
