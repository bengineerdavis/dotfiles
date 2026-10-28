"""The systemd service-manager seam for the Lore gateway."""

import yaml

from loreai_service_helpers import TOPIC, render, run_service_command


def test_systemd_command_replaces_adopted_gateway_with_local_mode(tmp_path):
    result = run_service_command(tmp_path, "systemd")
    calls = (tmp_path / "call-log").read_text().splitlines()
    assert calls[:3] == ["start --local", "stop", "start --local"]
    assert result.returncode == 1


def test_systemd_command_supervises_until_gateway_disappears(tmp_path):
    result = run_service_command(tmp_path, "systemd")
    assert result.returncode == 1, result.stderr
    assert (tmp_path / "doctor-count").read_text().strip() == "3"


def test_systemd_unit_escapes_shell_parameter_expansion():
    document = render(
        "lore-gateway.service.j2",
        loreai_env_file="/home/test/.config/loreai/env.zsh",
        loreai_install_dir="/home/test/.local/bin",
        loreai_service_path="/usr/bin:/bin",
        ansible_env={"HOME": "/home/test"},
    )
    assert "$$OPENROUTER_API_KEY" in document


def test_debian_teardown_tolerates_a_missing_service_unit():
    tasks = yaml.safe_load((TOPIC / "tasks" / "remove.yaml").read_text())
    stop = next(task for task in tasks if "stop and disable" in task["name"])
    assert stop["failed_when"] is False
