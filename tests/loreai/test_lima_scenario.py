"""LoreAI reuses the rootless Lima adapter, not a copied lifecycle."""

from pathlib import Path

import yaml

# pyrefly: ignore [missing-import]
from payload_seam import PAYLOAD_ROOT

LIMA = PAYLOAD_ROOT / "dotfiles/apps/lima/molecule"
LOREAI = PAYLOAD_ROOT / "dotfiles/apps/loreai/molecule/debian-lima"
SHARED = LIMA / "shared"


def load_scenario(path: Path) -> dict:
    """Read one scenario's structured configuration."""
    return yaml.safe_load((path / "molecule.yml").read_text())


def test_both_scenarios_reference_the_same_lima_adapter():
    """Provider lifecycle has one owner, not two shallow copies."""
    for scenario in (LIMA / "debian", LOREAI):
        config = load_scenario(scenario)
        assert config["driver"] == {
            "name": "default",
            "managed": True,
        }, f"unexpected VM driver in {scenario.parent.name}"
        playbooks = config["provisioner"]["playbooks"]
        for action in ("create", "destroy"):
            assert playbooks[action] == f"../../../lima/molecule/shared/{action}.yml", (
                f"{scenario.parent.name} must reference the shared {action} playbook"
            )
            assert (scenario / playbooks[action]).resolve().is_file()
        assert "shared_state" not in config
    for name in ("create.yml", "destroy.yml", "cleanup.yml", "lima.yaml.j2"):
        assert (SHARED / name).is_file()
        if name.endswith(".yml"):
            assert config["provisioner"]["playbooks"][name[:-4]] == (
                f"../../../lima/molecule/shared/{name}"
            )


def test_loreai_scenario_runs_the_topic_before_removal():
    """Prepare and verify the real role before teardown."""
    config = load_scenario(LOREAI)
    sequence = config["scenario"]["test_sequence"]
    assert sequence.index("prepare") < sequence.index("converge")
    assert sequence.index("verify") < sequence.index("side_effect")
    assert "vagrant" not in yaml.safe_dump(config)
    assert (LOREAI / "prepare.yml").is_file()
    assert "apps/loreai" in (LOREAI / "converge.yml").read_text()


def test_loreai_verifies_service_health_and_local_http():
    """Verify systemd ownership and a local HTTP GET."""
    verify = yaml.safe_load((LOREAI / "verify.yml").read_text())[0]
    commands = [
        task["ansible.builtin.command"]["argv"]
        for task in verify["tasks"]
        if "ansible.builtin.command" in task
    ]
    assert ["systemctl", "--user", "is-active", "lore-gateway"] in commands
    assert ["systemctl", "--user", "is-enabled", "lore-gateway"] in commands
    requests = [
        task["ansible.builtin.uri"]
        for task in verify["tasks"]
        if "ansible.builtin.uri" in task
    ]
    assert any(
        request["url"] == "http://127.0.0.1:3207/ui"
        and request["method"] == "GET"
        and request["status_code"] == 200
        for request in requests
    )


def test_loreai_removal_is_idempotent_and_preserves_memory():
    """Two removals preserve the planted memory sentinel."""
    removal = (LOREAI / "side_effect.yml").read_text()
    assert removal.count("ansible.builtin.include_role") == 2
    assert "molecule-test-preserved" in removal
    assert "molecule-test-preserved" in (LOREAI / "verify.yml").read_text()


def test_loreai_platform_has_a_distinct_short_scoped_name():
    """Parallel scenarios must not share VM names or state."""
    platform = load_scenario(LOREAI)["platforms"][0]
    assert platform["name"] == "lore-mol"
    assert platform["image"].startswith("https://cloud.debian.org/")
    assert platform["arm64_image"].startswith("https://cloud.debian.org/")
