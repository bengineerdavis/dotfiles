"""The launchd/systemd command seams for the Lore gateway."""

import pytest
import yaml

from loreai_service_helpers import TOPIC, render, run_service_command


@pytest.mark.parametrize("manager", ["launchd", "systemd"])
def test_service_replaces_and_supervises_an_adopted_gateway(tmp_path, manager):
    result = run_service_command(tmp_path, manager)
    calls = (tmp_path / "call-log").read_text().splitlines()
    assert calls[:3] == ["start --local", "stop", "start --local"]
    assert (tmp_path / "doctor-count").read_text().strip() == "3"
    assert result.returncode == 1


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
