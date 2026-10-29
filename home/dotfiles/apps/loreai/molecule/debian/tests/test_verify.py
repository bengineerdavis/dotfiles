"""Final state after the side-effect play tears the topic down twice."""

import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"]
).get_hosts("all")


def home(host) -> str:
    result = host.run('printf %s "$HOME"')
    assert result.rc == 0
    assert result.stdout.strip()
    return result.stdout.strip()


def test_service_unit_is_gone(host):
    unit = host.file(f"{home(host)}/.config/systemd/user/lore-gateway.service")
    assert not unit.exists
    result = host.run("systemctl --user status lore-gateway")
    assert result.rc != 0


def test_gateway_and_binary_are_gone(host):
    assert not host.file(f"{home(host)}/.local/bin/lore").exists
    assert host.run("pgrep -x lore").rc != 0
    for port in (3207, 5673):
        result = host.run(f"curl -fsS http://127.0.0.1:{port}/ui")
        assert result.rc != 0, f"gateway still answers on port {port}"


def test_topic_owned_state_is_gone(host):
    assert not host.file(f"{home(host)}/.config/loreai").exists
    assert not host.file(f"{home(host)}/.local/state/lore").exists


def test_memory_database_is_preserved(host):
    database = host.file(f"{home(host)}/.local/share/lore/lore.db")
    assert database.exists
    assert database.size > 0
