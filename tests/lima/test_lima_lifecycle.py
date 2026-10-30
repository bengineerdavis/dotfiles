"""The Lima topic and its rootless Molecule contract.

These tests check configuration and lifecycle wiring only. The
scenario's public Molecule test is the VM evidence; a missing VM
must not count as a pass.
"""

import pytest
import yaml

# pyrefly: ignore [missing-import]
from payload_seam import PAYLOAD_ROOT

TOPIC = PAYLOAD_ROOT / "dotfiles" / "apps" / "lima"
SCENARIO = TOPIC / "molecule" / "debian"
SHARED = TOPIC / "molecule" / "shared"


def load(relative: str):
    """Load one checked-in YAML document."""
    return yaml.safe_load((TOPIC / relative).read_text())


def test_topic_is_rootless_and_has_complete_lifecycle():
    """Install Lima without claiming another tool's package state."""
    assert load("topic.yml") == {
        "topic_name": "lima",
        "topic_provides": ["limactl"],
        "topic_requires": ["qemu"],
        "topic_os": ["Darwin", "Debian"],
        "topic_tier": "app",
    }
    for name in (
        "tasks/bootstrap.yaml",
        "tasks/prerequisites.yaml",
        "tasks/upgrade.yaml",
        "tasks/install.yaml",
        "tasks/remove.yaml",
        "defaults/main.yaml",
        "playbook.yaml",
        "CHANGELOG.md",
    ):
        assert (TOPIC / name).is_file(), f"missing topic lifecycle file: {name}"
    install = (TOPIC / "tasks/install.yaml").read_text()
    assert "lima_checksums_url" in install
    assert "checksum:" in install
    assert "become: true" not in install
    # No privilege escalation and no package-manager install. Searching
    # the Homebrew bin dir for an existing QEMU binary is allowed.
    assert "brew install" not in install
    assert not any(line.strip().startswith("sudo ") for line in install.splitlines())


def test_qemu_dependency_probes_the_real_system_binary():
    """The dependency token resolves to the real QEMU CLI."""
    defaults = yaml.safe_load(
        (
            TOPIC.parents[1] / "roles" / "topic-resolution" / "defaults" / "main.yaml"
        ).read_text()
    )
    probe = defaults["dependency_probe_binary"]["qemu"]
    assert "command -v qemu-system-aarch64" in probe
    assert "qemu-system-x86_64" in probe
    assert "ansible_facts.architecture" not in probe


def test_release_assets_are_pinned_for_supported_platforms():
    """Every supported release asset has its upstream digest."""
    defaults = load("defaults/main.yaml")
    assert defaults["lima_release_tag"] == "v2.2.1"
    assert "Darwin" in defaults["lima_release_os"]
    assert "Linux" in defaults["lima_release_os"]
    expected_arch = {"arm64": "arm64", "aarch64": "arm64", "x86_64": "x86_64"}
    assert defaults["lima_release_arch"] == (
        "{{ lima_release_architectures[ansible_facts.architecture] }}"
    )
    assert set(defaults["lima_release_architectures"]) == set(expected_arch)
    assert set(defaults["lima_release_checksums"]) == {
        "Darwin-arm64",
        "Darwin-x86_64",
        "Linux-arm64",
        "Linux-x86_64",
    }
    assert all(
        len(value) == 64 and set(value) <= set("0123456789abcdef")
        for value in defaults["lima_release_checksums"].values()
    )


def test_removal_preserves_unowned_and_shared_state():
    """Removal cannot silently delete Lima or QEMU shared state."""
    remove = (TOPIC / "tasks/remove.yaml").read_text()
    assert "lima_delete_instances" not in remove
    assert "lima_delete_state" not in remove
    assert ".lima" in remove
    assert "lima_install_dir }}/limactl" in remove
    assert "lima_install_dir }}/lima" in remove
    assert "lima_install_dir }}/nerdctl.lima" in remove
    assert "lima_install_prefix }}/share/lima" in remove
    assert "lima_install_prefix }}/share/doc/lima" in remove
    assert "lima_install_prefix }}/libexec/lima" in remove
    assert "unarchive" not in remove
    # QEMU must never be a removal *target*; prose naming it is fine.
    assert "qemu-system" not in remove
    assert "homebrew" not in remove.lower()


def test_molecule_uses_delegated_qemu_without_host_access():
    """No container, privileged network, or mounted host home."""
    config = yaml.safe_load((SCENARIO / "molecule.yml").read_text())
    assert config["driver"]["name"] == "default"
    assert config["driver"]["managed"] is True
    assert config["provisioner"]["name"] == "ansible"
    assert config["verifier"]["name"] == "ansible"
    for name in ("create.yml", "destroy.yml", "lima.yaml.j2"):
        assert (SHARED / name).is_file(), name
    lifecycle = "\n".join(
        (SHARED / name).read_text() for name in ("create.yml", "destroy.yml")
    )
    assert "LIMA_HOME" in lifecycle
    assert "limactl" in lifecycle
    assert "instance_config" in lifecycle
    assert "identity_file" in lifecycle
    assert "sshLocalPort" in lifecycle
    assert "socket_vmnet" not in lifecycle
    template = (SHARED / "lima.yaml.j2").read_text()
    assert "vmType: qemu" in template
    assert "containerd:" in template
    assert "system: false" in template
    assert "user: false" in template
    assert "mounts: []" in template
    assert "networks: []" in template
    assert "digest:" in template
    assert "loadDotSSHPubKeys: false" in template
    assert "nestedVirtualization: false" in template
    assert "forwardAgent: false" in template
    assert "name: molecule" in template
    assert "become: true" not in lifecycle


def test_lima_state_is_scenario_local_and_cleanup_is_scoped():
    """Only this scenario's VM and its short Lima home are destroyed.

    Lima's SSH socket must stay under UNIX_PATH_MAX (104), so the Lima
    home lives at a short /tmp path keyed by a hash of the unique
    ephemeral dir.
    """
    for name in ("create.yml", "destroy.yml"):
        text = (SHARED / name).read_text()
        assert "controller/.local" in text
        assert "molecule_ephemeral_directory | hash('sha1')" in text
        assert "item.name" in text
    destroy = (SHARED / "destroy.yml").read_text()
    assert "delete" in destroy
    assert "--force" in destroy
    assert "item.name" in destroy
    assert "rancher" not in destroy.lower()
    assert "rancher" not in destroy.lower()


def test_destroy_reaps_processes_before_deleting_their_state():
    """A delete must not leave a host agent using deleted files."""
    tasks = load("molecule/debian/destroy.yml")[0]["tasks"]
    assert tasks[-1]["name"] == "Remove this scenario's temporary Lima home"
    stop = next(task for task in tasks if "Stop only this scenario" in task["name"])
    assert stop["ansible.builtin.command"]["argv"][1:3] == ["stop", "--tty=false"]
    delete = next(task for task in tasks if "Delete only this scenario" in task["name"])
    assert delete["ansible.builtin.command"]["argv"][1:3] == ["delete", "--force"]
    reap = next(task for task in tasks if "processes to exit" in task["name"])
    script = reap["ansible.builtin.shell"]
    assert "item.stdout_lines" in script
    assert "kill -0" in script
    assert "seq 1 60" in script
    assert "stop --force --tty=false" in script
    assert "exit 1" in script
    assert "ansible.builtin.file" not in reap


def test_public_scenario_exercises_the_topic_and_preserves_sentinel():
    """Prove the topic works and removal leaves unrelated data."""
    converge = (SCENARIO / "converge.yml").read_text()
    assert "apps/lima" in converge
    assert "sentinel" in converge
    assert "lima_install_prefix" in converge
    assert "molecule_ephemeral_directory" in converge
    assert (SCENARIO / "verify.yml").is_file()
    assert (SHARED / "cleanup.yml").is_file()
    assert (SCENARIO / "side_effect.yml").is_file()


@pytest.mark.parametrize(
    ("system", "architecture", "expected"),
    [
        ("Darwin", "arm64", "Darwin-arm64"),
        ("Darwin", "x86_64", "Darwin-x86_64"),
        ("Linux", "aarch64", "Linux-arm64"),
        ("Linux", "x86_64", "Linux-x86_64"),
    ],
)
def test_release_mapping_covers_every_supported_pair(system, architecture, expected):
    """Cover native macOS and Debian architectures."""
    mapping = load("defaults/main.yaml")["lima_release_checksums"]
    release_os = {"Darwin": "Darwin", "Linux": "Linux", "Debian": "Linux"}[system]
    release_arch = {"arm64": "arm64", "aarch64": "arm64", "x86_64": "x86_64"}[
        architecture
    ]
    assert len(mapping[f"{release_os}-{release_arch}"]) == 64
